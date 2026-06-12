#!/usr/bin/env python3
"""Integer-Liftability check for the Q_B-3 source matrix.

If all source-matrix entries in `mixed_rows.jsonl` are bounded by q/2 in
absolute value (after signed lift), then the matrix can be re-interpreted
as an integer matrix and reduced modulo a second residue prime q'
without re-running the full witness construction.

This script tests the boundedness hypothesis and reports:
- Max absolute value of any signed-lift entry
- Total entries
- Distribution of |value| (small / medium / near q/2)

Usage:
    python qb3_integer_lift_check.py <case_dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def signed_lift(value: int, q: int) -> int:
    v = value % q
    if v > q // 2:
        v -= q
    return v


def check_case(case_dir: Path) -> dict:
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    q = int(manifest["q"])
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))

    max_abs = 0
    total_entries = 0
    bins = {"<=2": 0, "3-10": 0, "11-100": 0, "101-1000": 0, ">1000": 0}
    near_qhalf = 0
    threshold = q // 4  # values above this are "concerning"

    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for col, value in row["row"]:
                v = signed_lift(int(value), q)
                av = abs(v)
                total_entries += 1
                if av > max_abs:
                    max_abs = av
                if av <= 2:
                    bins["<=2"] += 1
                elif av <= 10:
                    bins["3-10"] += 1
                elif av <= 100:
                    bins["11-100"] += 1
                elif av <= 1000:
                    bins["101-1000"] += 1
                else:
                    bins[">1000"] += 1
                if av > threshold:
                    near_qhalf += 1

    pct = {k: round(100 * n / total_entries, 4) if total_entries else 0
           for k, n in bins.items()}

    result = {
        "case_dir": str(case_dir),
        "q": q,
        "q_half": q // 2,
        "total_entries": total_entries,
        "max_abs_signed": max_abs,
        "max_abs_safe_for_lift": max_abs < q // 2,
        "distribution_abs_value": bins,
        "distribution_pct": pct,
        "entries_above_q_quarter": near_qhalf,
        "entries_above_q_quarter_pct": round(100 * near_qhalf / total_entries, 4) if total_entries else 0,
        "verdict": (
            "INTEGER LIFT SAFE: all values |v| < q/2, source matrix reconstructable as integer"
            if max_abs < q // 2
            else f"INTEGER LIFT BLOCKED: some values reach |v| = {max_abs}, not safe"
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()

    result = check_case(args.case_dir)
    if args.out_json:
        args.out_json.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["max_abs_safe_for_lift"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
