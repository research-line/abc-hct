#!/usr/bin/env python3
"""Compute the dual residue functional of a split-last witness.

Given a split-last witness with n-1 source rows in n columns, compute a vector
phi in the right nullspace of the source-row matrix over F_q.  Then evaluate
phi on the repair row.  This is the mod-q dual object needed for CFR-3.4:

    source_rows * phi = 0,      repair_row * phi != 0.

The script uses sparse Gaussian elimination with a max-pivot echelon form.
It is meant as a certification/diagnostic tool; it does not prove the
integer or odd-local lift by itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def signed_lift(value: int, q: int) -> int:
    v = value % q
    if v > q // 2:
        v -= q
    return v


def read_manifest(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))


def iter_rows(case_dir: Path):
    manifest = read_manifest(case_dir)
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


class SparseRowBasis:
    def __init__(self, q: int):
        self.q = int(q)
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.rows_seen = 0
        self.max_basis_row_len = 0

    def add(self, row_pairs: list[list[int]]) -> bool:
        q = self.q
        self.rows_seen += 1
        row = {int(c): int(v) % q for c, v in row_pairs if int(v) % q}
        while row:
            pivot = max(row)
            value = row[pivot] % q
            if pivot in self.basis:
                factor = value
                basis_row = self.basis[pivot]
                for c, v in basis_row.items():
                    new = (row.get(c, 0) - factor * v) % q
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, q)
                normalized = {
                    c: (v * inv) % q for c, v in row.items() if (v * inv) % q
                }
                self.basis[pivot] = normalized
                self.rank += 1
                self.max_basis_row_len = max(self.max_basis_row_len, len(normalized))
                return True
        return False

    def solve_null_vector(self, ncols: int, free_col: int | None = None) -> dict[int, int]:
        pivots = set(self.basis)
        free_cols = [c for c in range(ncols) if c not in pivots]
        if not free_cols:
            raise ValueError("matrix has full rank; no free column available")
        if free_col is None:
            free_col = free_cols[0]
        if free_col not in free_cols:
            raise ValueError(f"requested free column {free_col} is not free")

        q = self.q
        x: dict[int, int] = {free_col: 1}
        for pivot in sorted(pivots):
            row = self.basis[pivot]
            total = 0
            for col, value in row.items():
                if col == pivot:
                    continue
                total = (total + value * x.get(col, 0)) % q
            value = (-total) % q
            if value:
                x[pivot] = value
        return x


def dot_vector(row_pairs: list[list[int]], vector: dict[int, int], q: int) -> int:
    total = 0
    for col, value in row_pairs:
        total += int(value) * vector.get(int(col), 0)
    return total % q


def diagnose(case_dir: Path, free_col: int | None = None) -> dict[str, Any]:
    manifest = read_manifest(case_dir)
    q = int(manifest["q"])
    ncols = int(manifest.get("ncols", manifest.get("columns_after_2term")))
    basis = SparseRowBasis(q)
    repair_row: dict[str, Any] | None = None
    source_count = 0
    dependent_source_rows = 0

    for row in iter_rows(case_dir):
        if row.get("origin") == "repair_only":
            repair_row = row
            continue
        if row.get("origin") != "source":
            continue
        source_count += 1
        if not basis.add(row["row"]):
            dependent_source_rows += 1

    if repair_row is None:
        raise ValueError(f"repair row not found in {case_dir}")

    phi = basis.solve_null_vector(ncols=ncols, free_col=free_col)
    repair_pairing = dot_vector(repair_row["row"], phi, q)

    support = sorted(phi)
    phi_entries_signed = [
        [int(col), signed_lift(phi[col], q)] for col in support
    ]
    phi_entries_mod_q = [
        [int(col), int(phi[col]) % q] for col in support
    ]
    prefix_window = list(range(min(16, ncols)))
    prefix_values = {str(c): signed_lift(phi.get(c, 0), q) for c in prefix_window}

    # Verify all source rows against phi in a second streaming pass.
    nonzero_sources = 0
    examples: list[dict[str, Any]] = []
    for row in iter_rows(case_dir):
        if row.get("origin") != "source":
            continue
        value = dot_vector(row["row"], phi, q)
        if value:
            nonzero_sources += 1
            if len(examples) < 8:
                examples.append(
                    {
                        "row_id": row.get("row_id"),
                        "stage": row.get("stage"),
                        "manin_symbol_index": (row.get("row_metadata") or {}).get(
                            "manin_symbol_index"
                        ),
                        "dot_signed": signed_lift(value, q),
                    }
                )

    return {
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "ncols": ncols,
        "source_rows": source_count,
        "source_rank": basis.rank,
        "dependent_source_rows": dependent_source_rows,
        "free_columns": [c for c in range(ncols) if c not in basis.basis],
        "max_basis_row_len": basis.max_basis_row_len,
        "phi_support_size": len(support),
        "phi_support_min": support[0] if support else None,
        "phi_support_max": support[-1] if support else None,
        "phi_entries_signed": phi_entries_signed,
        "phi_entries_mod_q": phi_entries_mod_q,
        "phi_prefix_0_15_signed": prefix_values,
        "source_nonzero_pairings": nonzero_sources,
        "source_annihilated": nonzero_sources == 0,
        "repair_pairing_mod_q": repair_pairing,
        "repair_pairing_signed": signed_lift(repair_pairing, q),
        "repair_pairing_nonzero": repair_pairing != 0,
        "nonzero_examples": examples,
    }


def write_md(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# H3a Residue-Line Dual Nullvector Diagnostic",
        "",
        "Computes the genuine mod-q dual residue functional `phi` as a right",
        "nullvector of the source-row matrix in the split-last witness.",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result['level']}/{result['mode']}",
                "",
                "```text",
                f"case:                       {result['case_dir']}",
                f"q:                          {result['q']}",
                f"ncols:                      {result['ncols']}",
                f"source rows/rank:           {result['source_rows']} / {result['source_rank']}",
                f"dependent source rows:      {result['dependent_source_rows']}",
                f"free columns:               {result['free_columns']}",
                f"max basis row length:       {result['max_basis_row_len']}",
                f"phi support size:           {result['phi_support_size']}",
                f"phi support range:          {result['phi_support_min']}..{result['phi_support_max']}",
                f"phi prefix 0..15:           {result['phi_prefix_0_15_signed']}",
                f"source nonzero pairings:    {result['source_nonzero_pairings']}",
                f"source annihilated:         {result['source_annihilated']}",
                f"repair pairing signed:      {result['repair_pairing_signed']}",
                f"repair pairing nonzero:     {result['repair_pairing_nonzero']}",
                "```",
                "",
            ]
        )
        if result["nonzero_examples"]:
            lines.append("Nonzero source-pairing examples, if any:")
            lines.append("")
            lines.append("| row_id | stage | symbol | dot |")
            lines.append("|---|---|---:|---:|")
            for item in result["nonzero_examples"]:
                lines.append(
                    f"| `{item['row_id']}` | `{item['stage']}` | "
                    f"{item['manin_symbol_index']} | {item['dot_signed']} |"
                )
            lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "A result with `source_annihilated=true` and `repair_pairing_nonzero=true`"
    )
    lines.append(
        "is the mod-q version of CFR-3.4.  It identifies the dual residue line;"
    )
    lines.append(
        "an integer or odd-local proof still has to explain this nullvector"
    )
    lines.append(
        "canonically through Manin S/I/T relations rather than through a single"
    )
    lines.append("finite-field computation.")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dirs", nargs="+", type=Path)
    parser.add_argument("--free-col", type=int)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [diagnose(path, free_col=args.free_col) for path in args.case_dirs]
    if args.out_json:
        args.out_json.write_text(
            json.dumps({"results": results}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.out_md:
        write_md(results, args.out_md)
    if not args.out_json and not args.out_md:
        print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
