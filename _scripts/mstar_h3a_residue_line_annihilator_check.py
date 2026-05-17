#!/usr/bin/env python3
"""Check whether a residue-line candidate annihilates source rows.

The split-last witness has rank n-1 source rows and one repair row.  A true
left residue functional must vanish on every source row and be nonzero on the
repair row.  This diagnostic deliberately tests the naive candidate obtained
from the compact repair-row support itself; failure means that the observed
six-term row is a quotient vector, not yet the dual Manin functional.
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


def dot_sparse(functional: dict[int, int], row_pairs: list[list[int]], q: int) -> int:
    total = 0
    for col, value in row_pairs:
        total += functional.get(int(col), 0) * int(value)
    return total % q


def diagnose(case_dir: Path) -> dict[str, Any]:
    manifest = read_manifest(case_dir)
    q = int(manifest["q"])
    repair_id = str(manifest.get("repair_only_row_id", ""))
    rows = list(iter_rows(case_dir))
    repair = next(
        (
            row
            for row in rows
            if row.get("origin") == "repair_only"
            and (not repair_id or str(row.get("row_id")) == repair_id)
        ),
        None,
    )
    if repair is None:
        raise ValueError(f"repair row not found in {case_dir}")

    functional = {int(col): int(value) % q for col, value in repair["row"]}
    source_rows = [row for row in rows if row.get("origin") == "source"]

    nonzero_examples: list[dict[str, Any]] = []
    nonzero_count = 0
    for row in source_rows:
        value = dot_sparse(functional, row["row"], q)
        if value:
            nonzero_count += 1
            if len(nonzero_examples) < 8:
                nonzero_examples.append(
                    {
                        "row_id": row.get("row_id"),
                        "stage": row.get("stage"),
                        "manin_symbol_index": (row.get("row_metadata") or {}).get(
                            "manin_symbol_index"
                        ),
                        "dot_mod_q": value,
                        "dot_signed": signed_lift(value, q),
                    }
                )

    repair_value = dot_sparse(functional, repair["row"], q)
    return {
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "source_rows": len(source_rows),
        "functional_support": sorted(functional),
        "functional_coefficients_signed": [
            signed_lift(functional[col], q) for col in sorted(functional)
        ],
        "source_nonzero_pairings": nonzero_count,
        "source_annihilated": nonzero_count == 0,
        "repair_pairing_mod_q": repair_value,
        "repair_pairing_signed": signed_lift(repair_value, q),
        "repair_pairing_nonzero": repair_value != 0,
        "nonzero_examples": nonzero_examples,
    }


def write_md(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# H3a Residue-Line Annihilator Check",
        "",
        "This diagnostic tests the naive finite-support candidate obtained from",
        "the split-last repair row itself.  A true left residue functional must",
        "annihilate all source rows and pair nontrivially with the repair row.",
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
                f"source rows:                {result['source_rows']}",
                f"functional support:         {result['functional_support']}",
                f"functional coefficients:    {result['functional_coefficients_signed']}",
                f"source nonzero pairings:    {result['source_nonzero_pairings']}",
                f"source annihilated:         {result['source_annihilated']}",
                f"repair pairing signed:      {result['repair_pairing_signed']}",
                f"repair pairing nonzero:     {result['repair_pairing_nonzero']}",
                "```",
                "",
            ]
        )
        if result["nonzero_examples"]:
            lines.append("First nonzero source pairings:")
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
        "If `source_annihilated` is false, the compact six-term repair row is not"
    )
    lines.append(
        "itself the dual residue functional.  It remains useful as the quotient"
    )
    lines.append(
        "residue vector, but CFR-3.4 must use the dual functional obtained after"
    )
    lines.append(
        "S/I/T-Manin reduction, not a raw dot product against prefix columns."
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dirs", nargs="+", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [diagnose(path) for path in args.case_dirs]
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
