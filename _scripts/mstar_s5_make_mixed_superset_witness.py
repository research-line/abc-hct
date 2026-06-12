#!/usr/bin/env python3
"""Build a minimal mixed S5 row-superset witness.

The RC3d source witness is square and full rank for many primes, but drops
rank for a few small primes.  The p=2 repair witness shows that adding the
T7 boundary row and an adjacent T5 row repairs those defects, although using
the p=2 square replacement minor can create new drops elsewhere.

This script writes a rectangular witness consisting of all source rows plus
repair-only rows from a repair witness.  A rectangular full-rank scan is the
right diagnostic for the row module: it preserves source full-rank primes and
tests whether the added repair rows kill the exceptional defects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))


def load_rows(case_dir: Path, rows_key: str = "rows_file") -> list[dict[str, Any]]:
    manifest = read_manifest(case_dir)
    rows_path = case_dir / str(manifest[rows_key])
    rows = []
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def normalize_record(record: dict[str, Any], origin: str) -> dict[str, Any]:
    return {
        "origin": origin,
        "row_id": str(record["row_id"]),
        "stage": str(record["stage"]),
        "stage_row_index": int(record["stage_row_index"]),
        "row_line_sha256": str(record.get("row_line_sha256", "")),
        "row": [[int(col), int(value)] for col, value in record["row"]],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-case-dir", type=Path, required=True)
    parser.add_argument("--repair-case-dir", type=Path, required=True)
    parser.add_argument("--out-case-dir", type=Path, required=True)
    parser.add_argument("--rows-file", default="mixed_rows.jsonl")
    parser.add_argument(
        "--include-repair-row-id",
        action="append",
        default=[],
        help="Optional repair-only row id to include. Repeatable. If omitted, all repair-only rows are included.",
    )
    args = parser.parse_args()

    source_manifest = read_manifest(args.source_case_dir)
    repair_manifest = read_manifest(args.repair_case_dir)
    if int(source_manifest["ncols"]) != int(repair_manifest["ncols"]):
        raise ValueError("source and repair ncols differ")
    if int(source_manifest["q"]) != int(repair_manifest["q"]):
        raise ValueError("source and repair q differ")

    source_rows_raw = load_rows(args.source_case_dir)
    repair_rows_raw = load_rows(args.repair_case_dir)

    source_ids = {str(row["row_id"]) for row in source_rows_raw}
    source_rows = [normalize_record(row, "source") for row in source_rows_raw]
    include_filter = set(args.include_repair_row_id)
    repair_only = [
        normalize_record(row, "repair_only")
        for row in repair_rows_raw
        if str(row["row_id"]) not in source_ids
        and (not include_filter or str(row["row_id"]) in include_filter)
    ]

    args.out_case_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_case_dir / args.rows_file
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in source_rows + repair_only:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    manifest = {
        "certificate_version": "s5-mixed-superset-witness-1",
        "witness_type": "source_plus_repair_only_rows",
        "source_case_dir": str(args.source_case_dir),
        "repair_case_dir": str(args.repair_case_dir),
        "q": int(source_manifest["q"]),
        "ncols": int(source_manifest["ncols"]),
        "columns_after_2term": int(source_manifest["ncols"]),
        "level": int(source_manifest.get("level", repair_manifest.get("level", 0))),
        "mode": str(source_manifest.get("mode", repair_manifest.get("mode", ""))),
        "sign": int(source_manifest.get("sign", repair_manifest.get("sign", 0))),
        "rows_file": args.rows_file,
        "rows_file_sha256": file_sha256(rows_path),
        "source_row_count": len(source_rows),
        "repair_only_row_count": len(repair_only),
        "mixed_row_count": len(source_rows) + len(repair_only),
        "square": len(source_rows) + len(repair_only) == int(source_manifest["ncols"]),
        "repair_only_row_ids": [row["row_id"] for row in repair_only],
        "include_repair_row_id_filter": sorted(include_filter),
    }
    (args.out_case_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
