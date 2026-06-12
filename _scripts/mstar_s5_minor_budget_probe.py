#!/usr/bin/env python3
"""S5 determinant-budget diagnostics for source-row witnesses.

The probe does not compute a large determinant.  It measures sparsity and a
Hadamard log2 bound after the same symmetric lift used by the small integral
minor smoke.  This gives a reproducible scale estimate for the exceptional
prime budget in the integral-minor route.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_CASES = [
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N109_raw_sign1",
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N218_raw_sign1",
    "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def analyze_case(case_dir: Path) -> dict[str, Any]:
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    rows_path = case_dir / str(manifest["rows_file"])

    row_count = 0
    nnz_sum = 0
    max_nnz = 0
    l1_sum = 0
    max_l1 = 0
    hadamard_log2 = 0.0

    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        values = [symmetric_lift(int(value), q) for _, value in record["row"]]
        nnz = len(values)
        l1 = sum(abs(value) for value in values)
        l2_square = sum(value * value for value in values)

        row_count += 1
        nnz_sum += nnz
        max_nnz = max(max_nnz, nnz)
        l1_sum += l1
        max_l1 = max(max_l1, l1)
        if l2_square:
            hadamard_log2 += 0.5 * math.log2(l2_square)

    avg_nnz = nnz_sum / row_count if row_count else 0.0
    avg_l1 = l1_sum / row_count if row_count else 0.0
    return {
        "case": case_dir.name,
        "path": str(case_dir),
        "q": q,
        "ncols": ncols,
        "source_rows": row_count,
        "square": row_count == ncols,
        "avg_nnz": avg_nnz,
        "max_nnz": max_nnz,
        "avg_l1_symmetric_lift": avg_l1,
        "max_l1_symmetric_lift": max_l1,
        "hadamard_log2_symmetric_lift_bound": hadamard_log2,
    }


def write_markdown(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# S5 Minor Budget Probe",
        "",
        "This diagnostic reads source-row witnesses, lifts entries from `GF(q)`",
        "to symmetric integer representatives, and reports sparsity plus the",
        "Hadamard log2 determinant bound.  It is a scale probe, not a determinant",
        "or Smith-normal-form certificate.",
        "",
        "| Case | ncols | rows | avg nnz | max nnz | avg l1 | max l1 | Hadamard log2 bound |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in results:
        lines.append(
            f"| {item['case']} | {item['ncols']} | {item['source_rows']} | "
            f"{item['avg_nnz']:.3f} | {item['max_nnz']} | "
            f"{item['avg_l1_symmetric_lift']:.3f} | {item['max_l1_symmetric_lift']} | "
            f"{item['hadamard_log2_symmetric_lift_bound']:.1f} |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The witness rows are very sparse and small after symmetric lift.",
            "- Nevertheless, a generic determinant-minor budget is still far too",
            "  large for a sublogarithmic FAQS bound at `60168`.",
            "- The S5 route therefore needs a stronger structural certificate:",
            "  a small Smith defect, a near-unimodular minor, or a finite",
            "  exceptional-prime recursion rather than a raw Hadamard bound.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", type=Path, default=[Path(p) for p in DEFAULT_CASES])
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    results = [analyze_case(path) for path in args.cases]
    payload = {
        "tool": "mstar_s5_minor_budget_probe",
        "description": "Hadamard-scale diagnostic for S5 integral-minor route",
        "results": results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(results, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
