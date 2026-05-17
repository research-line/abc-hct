#!/usr/bin/env python3
"""Build the T-Manin quotient projection pi_N from a split-last witness.

The RC3 residue witness columns live after S/I quotient.  The T-Manin source
rows inside mixed_rows.jsonl span the remaining relation subspace.  This script
row-reduces those T rows over F_q and uses the free columns as quotient
coordinates:

    pi_N : V_SI -> V_SI / <T-Manin>.

It then projects Hecke source rows and the repair row into the quotient.  For
N=109 this should explain the observed 27 -> 9 dimension drop before any Sage
intersection-pairing comparison is attempted.
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


def sparse_pairs_to_dict(row_pairs: list[list[int]], q: int) -> dict[int, int]:
    return {int(c): int(v) % q for c, v in row_pairs if int(v) % q}


class SparseRowBasis:
    def __init__(self, q: int):
        self.q = int(q)
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0

    def add_dict(self, raw_row: dict[int, int]) -> bool:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot = max(row)
            value = row[pivot] % q
            if pivot in self.basis:
                factor = value
                for c, v in self.basis[pivot].items():
                    new = (row.get(c, 0) - factor * v) % q
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, q)
                self.basis[pivot] = {
                    c: (v * inv) % q for c, v in row.items() if (v * inv) % q
                }
                self.rank += 1
                return True
        return False

    def reduce_dict(self, raw_row: dict[int, int]) -> dict[int, int]:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot_candidates = [c for c in row if c in self.basis]
            if not pivot_candidates:
                break
            pivot = max(pivot_candidates)
            factor = row[pivot] % q
            for c, v in self.basis[pivot].items():
                new = (row.get(c, 0) - factor * v) % q
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row


def sparse_rank(rows: list[dict[int, int]], q: int) -> int:
    basis = SparseRowBasis(q)
    for row in rows:
        basis.add_dict(row)
    return basis.rank


def dot(row: dict[int, int], vector: dict[int, int], q: int) -> int:
    return sum((int(v) * vector.get(int(c), 0)) for c, v in row.items()) % q


def load_phi(phi_json: Path | None) -> dict[int, int] | None:
    if phi_json is None:
        return None
    data = json.loads(phi_json.read_text(encoding="utf-8"))
    result = data["results"][0] if "results" in data else data
    entries = result.get("phi_entries_mod_q")
    if entries is None:
        return None
    return {int(c): int(v) for c, v in entries}


def summarize_projected_row(row: dict[int, int], q: int, limit: int = 16) -> dict[str, Any]:
    support = sorted(row)
    return {
        "support_size": len(support),
        "support": support[:limit],
        "coefficients_signed": [signed_lift(row[c], q) for c in support[:limit]],
        "truncated": len(support) > limit,
    }


def row_entries_mod_q(row: dict[int, int]) -> list[list[int]]:
    return [[int(c), int(row[c])] for c in sorted(row)]


def row_entries_signed(row: dict[int, int], q: int) -> list[list[int]]:
    return [[int(c), signed_lift(row[c], q)] for c in sorted(row)]


def diagnose(case_dir: Path, phi_json: Path | None = None) -> dict[str, Any]:
    manifest = read_manifest(case_dir)
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    rows = list(iter_rows(case_dir))

    t_rows = [
        row for row in rows
        if (row.get("row_metadata") or {}).get("source_kind") == "manin_T"
    ]
    hecke_source_rows = [
        row for row in rows
        if row.get("origin") == "source"
        and (row.get("row_metadata") or {}).get("source_kind") == "hecke"
    ]
    repair_row = next((row for row in rows if row.get("origin") == "repair_only"), None)
    if repair_row is None:
        raise ValueError("repair row not found")

    t_basis = SparseRowBasis(q)
    independent_t_rows = 0
    for row in t_rows:
        if t_basis.add_dict(sparse_pairs_to_dict(row["row"], q)):
            independent_t_rows += 1

    pivot_columns = sorted(t_basis.basis)
    free_columns = [c for c in range(ncols) if c not in t_basis.basis]
    quotient_dim = len(free_columns)
    free_col_to_qcol = {c: i for i, c in enumerate(free_columns)}

    def project_to_quotient(record: dict[str, Any]) -> dict[int, int]:
        reduced = t_basis.reduce_dict(sparse_pairs_to_dict(record["row"], q))
        projected: dict[int, int] = {}
        for col, value in reduced.items():
            if col not in free_col_to_qcol:
                raise RuntimeError(f"pivot column survived T-reduction: {col}")
            projected[free_col_to_qcol[col]] = int(value) % q
        return projected

    projected_hecke = [project_to_quotient(row) for row in hecke_source_rows]
    projected_repair = project_to_quotient(repair_row)
    hecke_rank = sparse_rank(projected_hecke, q)
    rank_with_repair = sparse_rank(projected_hecke + [projected_repair], q)

    phi = load_phi(phi_json)
    phi_checks: dict[str, Any] = {"available": phi is not None}
    if phi is not None:
        induced_phi_on_free = {
            free_col_to_qcol[c]: phi.get(c, 0) % q for c in free_columns if phi.get(c, 0) % q
        }
        t_nonzero = 0
        hecke_nonzero = 0
        for row in t_rows:
            if dot(sparse_pairs_to_dict(row["row"], q), phi, q):
                t_nonzero += 1
        for row in hecke_source_rows:
            if dot(sparse_pairs_to_dict(row["row"], q), phi, q):
                hecke_nonzero += 1
        phi_repair = dot(sparse_pairs_to_dict(repair_row["row"], q), phi, q)
        phi_checks = {
            "available": True,
            "induced_phi_entries_mod_q": [
                [int(c), int(induced_phi_on_free[c]) % q]
                for c in sorted(induced_phi_on_free)
            ],
            "induced_phi_entries_signed": [
                [int(c), signed_lift(induced_phi_on_free[c], q)]
                for c in sorted(induced_phi_on_free)
            ],
            "induced_phi_support": sorted(induced_phi_on_free),
            "induced_phi_coefficients_signed": [
                signed_lift(induced_phi_on_free[c], q) for c in sorted(induced_phi_on_free)
            ],
            "t_rows_nonzero_pairings": t_nonzero,
            "hecke_source_nonzero_pairings": hecke_nonzero,
            "repair_pairing_signed": signed_lift(phi_repair, q),
            "repair_pairing_nonzero": phi_repair != 0,
        }

    return {
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "ncols": ncols,
        "t_rows": len(t_rows),
        "t_rank": t_basis.rank,
        "independent_t_rows": independent_t_rows,
        "quotient_dim": quotient_dim,
        "pivot_columns": pivot_columns,
        "free_columns": free_columns,
        "sage_sign_plus_expected_dim": manifest.get("sage_sign_plus_expected_dim", 9)
        if int(manifest.get("level", 0)) == 109 else None,
        "quotient_matches_n109_sage_dim": quotient_dim == 9
        if int(manifest.get("level", 0)) == 109 else None,
        "hecke_source_rows": len(hecke_source_rows),
        "projected_hecke_rank": hecke_rank,
        "projected_rank_with_repair": rank_with_repair,
        "repair_adds_quotient_rank": rank_with_repair > hecke_rank,
        "projected_repair_summary": summarize_projected_row(projected_repair, q),
        "projected_repair_entries_mod_q": row_entries_mod_q(projected_repair),
        "projected_repair_entries_signed": row_entries_signed(projected_repair, q),
        "projected_hecke_rows_mod_q": [row_entries_mod_q(row) for row in projected_hecke],
        "phi_checks": phi_checks,
    }


def write_md(result: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# H3a pi_N Projection from Witness",
        "",
        "Builds `pi_N : V_SI -> V_SI/<T-Manin>` from the T-Manin rows already",
        "present in the split-last witness.",
        "",
        "```text",
        f"case:                      {result['case_dir']}",
        f"level/mode/q:              {result['level']} / {result['mode']} / {result['q']}",
        f"ncols in V_SI:             {result['ncols']}",
        f"T rows / T rank:           {result['t_rows']} / {result['t_rank']}",
        f"quotient dim:              {result['quotient_dim']}",
        f"free columns:              {result['free_columns']}",
        f"pivot columns:             {result['pivot_columns']}",
        f"N=109 matches Sage dim 9:  {result['quotient_matches_n109_sage_dim']}",
        f"Hecke source rows:         {result['hecke_source_rows']}",
        f"rank pi(Hecke source):     {result['projected_hecke_rank']}",
        f"rank plus pi(repair):      {result['projected_rank_with_repair']}",
        f"repair adds rank:          {result['repair_adds_quotient_rank']}",
        "```",
        "",
        "## Projected repair row",
        "",
        "```text",
        f"{result['projected_repair_summary']}",
        "```",
        "",
    ]
    phi = result["phi_checks"]
    if phi.get("available"):
        lines.extend([
            "## Induced dual phi on quotient",
            "",
            "```text",
            f"induced support:              {phi['induced_phi_support']}",
            f"induced coefficients signed:  {phi['induced_phi_coefficients_signed']}",
            f"T-row nonzero pairings:       {phi['t_rows_nonzero_pairings']}",
            f"Hecke-source nonzero pairings:{phi['hecke_source_nonzero_pairings']}",
            f"repair pairing signed:        {phi['repair_pairing_signed']}",
            f"repair pairing nonzero:       {phi['repair_pairing_nonzero']}",
            "```",
            "",
        ])
    lines.extend([
        "## Interpretation",
        "",
        "For N=109 the T-Manin rows reconstruct the missing basis bridge from",
        "the RC3 S/I column space to a 9-dimensional quotient.  This does not",
        "yet identify Sage's modular-symbol basis, but it supplies the first",
        "half of `pi_N` and turns the Loop-315 blocker into a concrete finite",
        "linear algebra object.",
        "",
    ])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--phi-json", type=Path)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = diagnose(args.case_dir, args.phi_json)
    args.out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(result, args.out_md)
    print(json.dumps({
        "quotient_dim": result["quotient_dim"],
        "projected_hecke_rank": result["projected_hecke_rank"],
        "repair_adds_rank": result["repair_adds_quotient_rank"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
