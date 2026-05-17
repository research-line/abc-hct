#!/usr/bin/env python3
"""H3a residue-line functional diagnostic.

Reads the T7 repair row from each splitlast residue-line witness
(_results/h3a_residue_line_witness_*_splitlast) and decodes it as a
finite-support functional on the affine cusp-fan prefix.  Reports the
support, the signed coefficients (mod q lifted to [-q/2, q/2]) and the
column-to-symbol mapping.

The goal is to identify the cokernel residue line of D_5 = T_5 - a_5
on the cusp-fan F_d as a canonical boundary/cusp functional, i.e. to
turn the per-witness numerical observation into a closed-form statement
matching the CFR-4 conjecture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def signed_lift(value: int, q: int) -> int:
    """Lift residue mod q to the symmetric range (-q/2, q/2]."""
    v = value % q
    if v > q // 2:
        v -= q
    return v


def symbol_for_column(col: int) -> str:
    """Column k corresponds to the affine cusp-fan basis as follows.

    Convention from MG_h3a_prefix_block_canonicalization_attack_2026-05-16:
        col 0   = e_inf  = (0,1)
        col k+1 = e_k    = (1,k)   for k >= 0.
    """
    if col == 0:
        return "e_inf=(0,1)"
    return f"e_{col - 1}=(1,{col - 1})"


def load_manifest(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))


def find_repair_row(case_dir: Path) -> dict[str, Any] | None:
    manifest = load_manifest(case_dir)
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    target = manifest.get("repair_only_row_id")
    if not target:
        return None
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("origin") == "repair_only" and row.get("row_id") == target:
                return row
    return None


def diagnose_case(case_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(case_dir)
    repair = find_repair_row(case_dir)
    q = int(manifest["q"])
    if repair is None:
        return {
            "case_dir": str(case_dir),
            "level": manifest.get("level"),
            "mode": manifest.get("mode"),
            "q": q,
            "found_repair": False,
        }

    raw = [(int(c), int(v)) for c, v in repair["row"]]
    raw.sort()
    cols = [c for c, _ in raw]
    coeffs_signed = [signed_lift(v, q) for _, v in raw]
    symbols = [symbol_for_column(c) for c in cols]

    support_is_prefix = cols == list(range(len(cols)))
    is_compact = max(cols) < 16 if cols else False

    leading_on_e_inf = bool(cols and cols[0] == 0)
    leading_coeff = coeffs_signed[0] if coeffs_signed else None

    return {
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "found_repair": True,
        "repair_row_id": repair.get("row_id"),
        "manin_symbol_index": (repair.get("row_metadata") or {}).get(
            "manin_symbol_index"
        ),
        "hecke_prime": (repair.get("row_metadata") or {}).get("hecke_prime"),
        "hecke_ap": (repair.get("row_metadata") or {}).get("hecke_ap"),
        "support_columns": cols,
        "support_symbols": symbols,
        "coefficients_mod_q": [v for _, v in raw],
        "coefficients_signed": coeffs_signed,
        "support_size": len(cols),
        "support_is_consecutive_prefix": support_is_prefix,
        "support_is_compact_prefix_block": is_compact,
        "leading_on_e_inf": leading_on_e_inf,
        "leading_coefficient_signed": leading_coeff,
        "supports_boundary_functional_hypothesis": (
            support_is_prefix and is_compact and leading_on_e_inf
            and leading_coeff is not None and leading_coeff == 2
        ),
    }


def compare_cases(diagnoses: list[dict[str, Any]]) -> dict[str, Any]:
    """Cross-case consistency check."""
    valid = [d for d in diagnoses if d.get("found_repair")]
    if not valid:
        return {"cases": 0, "consistent_support": None, "consistent_signature": None}

    supports = [tuple(d["support_columns"]) for d in valid]
    sigs = [tuple(d["coefficients_signed"]) for d in valid]
    return {
        "cases": len(valid),
        "consistent_support": len(set(supports)) == 1,
        "common_support": list(supports[0]) if len(set(supports)) == 1 else None,
        "consistent_signature": len(set(sigs)) == 1,
        "signatures": {
            f"{d['level']}/{d['mode']}": d["coefficients_signed"] for d in valid
        },
    }


def write_markdown(
    diagnoses: list[dict[str, Any]], comparison: dict[str, Any], out_md: Path
) -> None:
    lines = [
        "# H3a Residue-Line Functional Diagnostic",
        "",
        "Decodes the T7 repair row of each splitlast witness as a finite-",
        "support functional on the affine cusp-fan prefix.  Convention:",
        "column 0 = `e_inf = (0,1)`, column k+1 = `e_k = (1,k)`.",
        "",
    ]

    for d in diagnoses:
        lines.append(f"## {d['level']}/{d['mode']}")
        lines.append("")
        if not d.get("found_repair"):
            lines.append("Repair row not found.")
            lines.append("")
            continue
        lines.append("```text")
        lines.append(f"witness:               {d['case_dir']}")
        lines.append(f"q:                     {d['q']}")
        lines.append(f"row id:                {d['repair_row_id']}")
        lines.append(f"hecke prime / ap:      {d['hecke_prime']} / {d['hecke_ap']}")
        lines.append(f"manin symbol index:    {d['manin_symbol_index']}")
        lines.append(f"support size:          {d['support_size']}")
        lines.append(f"support columns:       {d['support_columns']}")
        lines.append(f"support symbols:       {d['support_symbols']}")
        lines.append(f"coefficients (mod q):  {d['coefficients_mod_q']}")
        lines.append(f"coefficients (signed): {d['coefficients_signed']}")
        lines.append(
            f"consecutive prefix:    {d['support_is_consecutive_prefix']}"
        )
        lines.append(
            f"compact prefix block:  {d['support_is_compact_prefix_block']}"
        )
        lines.append(
            f"leading on e_inf=2:    {d['supports_boundary_functional_hypothesis']}"
        )
        lines.append("```")
        lines.append("")

    lines.append("## Cross-case comparison")
    lines.append("")
    lines.append("```text")
    lines.append(f"cases compared:        {comparison['cases']}")
    lines.append(f"consistent support:    {comparison['consistent_support']}")
    if comparison.get("common_support") is not None:
        lines.append(f"common support:        {comparison['common_support']}")
    lines.append(f"consistent signature:  {comparison['consistent_signature']}")
    if comparison.get("signatures"):
        lines.append("signatures (per case):")
        for name, sig in comparison["signatures"].items():
            lines.append(f"  {name}: {sig}")
    lines.append("```")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "If support is the consecutive prefix `[0, 1, ..., k]` and the leading"
    )
    lines.append(
        "coefficient on `e_inf` equals 2, the repair row is consistent with a"
    )
    lines.append(
        "canonical Boundary/Cusp functional `phi` whose value on `e_inf` is the"
    )
    lines.append(
        "Eisenstein/cuspidal weight `T5-a5` contributes via `(p+1-a_p)`."
    )
    lines.append(
        "Any per-level variation visible only in higher-index coefficients then"
    )
    lines.append(
        "reflects the T-Manin 3-term reduction acting at the affine prefix tail,"
    )
    lines.append(
        "and is fixed by the canonical Manin S/I/T-relations at that level."
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "case_dirs",
        nargs="+",
        type=Path,
        help="Splitlast witness case directories (each containing manifest.json + mixed_rows.jsonl).",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    diagnoses = [diagnose_case(p) for p in args.case_dirs]
    comparison = compare_cases(diagnoses)
    report = {"diagnoses": diagnoses, "comparison": comparison}

    if args.out_json:
        args.out_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.out_md:
        write_markdown(diagnoses, comparison, args.out_md)
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
