#!/usr/bin/env python3
"""Re-modularize a splitlast witness for a second residue prime q'.

After `qb3_integer_lift_check.py` confirms `max_abs_signed < q/2`, the
source matrix can be safely interpreted as an integer matrix.  This
script builds a new "synthetic splitlast" directory with:
- the original integer entries re-reduced modulo q'
- a new manifest.json with q' instead of q
- the same rows file structure (mixed_rows.jsonl)

The output directory can then be fed to the standard Wiedemann pipeline
without any code modification (the Wiedemann script reads q from manifest).

Usage:
    python qb3_remod_witness.py <case_dir> --q-prime 5077 --out-dir <new_case_dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def signed_lift(value: int, q: int) -> int:
    v = value % q
    if v > q // 2:
        v -= q
    return v


def remod(case_dir: Path, q_prime: int, out_dir: Path, max_safe_check: bool = True) -> dict:
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    q_orig = int(manifest["q"])
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))

    if q_prime == q_orig:
        raise ValueError(f"q_prime ({q_prime}) must differ from original q ({q_orig})")

    if q_prime < 2:
        raise ValueError(f"q_prime must be >= 2, got {q_prime}")

    # Safety: ensure original values are small enough that signed lift is unique
    max_abs_seen = 0
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for _col, value in row["row"]:
                v = signed_lift(int(value), q_orig)
                if abs(v) > max_abs_seen:
                    max_abs_seen = abs(v)

    if max_safe_check and max_abs_seen >= q_orig // 2:
        raise RuntimeError(
            f"Integer lift unsafe: max |v| = {max_abs_seen} >= q/2 = {q_orig // 2}. "
            "Run qb3_integer_lift_check.py first to verify safety."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    new_rows_path = out_dir / "mixed_rows.jsonl"

    rows_written = 0
    with rows_path.open("r", encoding="utf-8") as handle_in, \
         new_rows_path.open("w", encoding="utf-8") as handle_out:
        for line in handle_in:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            new_row_entries = []
            for col, value in row["row"]:
                v_int = signed_lift(int(value), q_orig)
                v_new = v_int % q_prime
                if v_new:
                    new_row_entries.append([int(col), int(v_new)])
            new_row = dict(row)
            new_row["row"] = new_row_entries
            handle_out.write(json.dumps(new_row, ensure_ascii=False) + "\n")
            rows_written += 1

    # New manifest
    new_manifest = dict(manifest)
    new_manifest["q"] = q_prime
    new_manifest["rows_file"] = "mixed_rows.jsonl"
    new_manifest["remod_from_q"] = q_orig
    new_manifest["remod_max_abs_original"] = max_abs_seen
    new_manifest["remod_source_dir"] = str(case_dir)

    # Hash new rows file
    sha = hashlib.sha256()
    with new_rows_path.open("rb") as h:
        for chunk in iter(lambda: h.read(1024 * 1024), b""):
            sha.update(chunk)
    new_manifest["rows_file_sha256"] = sha.hexdigest()

    (out_dir / "manifest.json").write_text(
        json.dumps(new_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "case_dir": str(case_dir),
        "q_orig": q_orig,
        "q_prime": q_prime,
        "max_abs_original": max_abs_seen,
        "rows_written": rows_written,
        "out_dir": str(out_dir),
        "manifest_path": str(out_dir / "manifest.json"),
        "rows_path": str(new_rows_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--q-prime", type=int, required=True,
                        help="New residue prime q' (must differ from original q)")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path,
                        help="Where to write the report JSON (optional)")
    parser.add_argument("--skip-safety-check", action="store_true",
                        help="Skip max|v|<q/2 verification (dangerous, only for testing)")
    args = parser.parse_args()

    result = remod(args.case_dir, args.q_prime, args.out_dir,
                   max_safe_check=not args.skip_safety_check)
    if args.out_json:
        args.out_json.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
