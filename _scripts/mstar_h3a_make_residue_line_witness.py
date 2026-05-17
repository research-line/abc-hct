#!/usr/bin/env python3
"""Split a full independent-source witness into a residue-line witness.

The intended input is an RC3c independent source witness whose rows are ordered
by rank-increasing discovery.  If the last row is the row that kills a
one-dimensional residue, this script moves it to `repair_only` and keeps the
preceding rows as `source`.
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


def load_rows(case_dir: Path) -> list[dict[str, Any]]:
    manifest = read_manifest(case_dir)
    rows_path = case_dir / str(manifest["rows_file"])
    rows: list[dict[str, Any]] = []
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def normalize_record(record: dict[str, Any], origin: str) -> dict[str, Any]:
    out = {
        "origin": origin,
        "row_id": str(record["row_id"]),
        "stage": str(record["stage"]),
        "stage_row_index": int(record["stage_row_index"]),
        "row_line_sha256": str(record.get("row_line_sha256", "")),
        "row": [[int(col), int(value)] for col, value in record["row"]],
    }
    if "row_metadata" in record:
        out["row_metadata"] = record["row_metadata"]
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-case-dir", type=Path, required=True)
    parser.add_argument("--out-case-dir", type=Path, required=True)
    parser.add_argument("--rows-file", default="mixed_rows.jsonl")
    parser.add_argument(
        "--repair-row-id",
        help="Row id to move to repair_only. Defaults to the final source row.",
    )
    parser.add_argument(
        "--expect-repair-stage-prefix",
        help="Optional guard, e.g. T_7_minus_0, for the repair row stage.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = read_manifest(args.source_case_dir)
    rows = load_rows(args.source_case_dir)
    if not rows:
        raise ValueError("source witness has no rows")

    if args.repair_row_id:
        repair_index = next(
            (idx for idx, row in enumerate(rows) if str(row.get("row_id")) == args.repair_row_id),
            None,
        )
        if repair_index is None:
            raise ValueError(f"repair row id not found: {args.repair_row_id}")
    else:
        repair_index = len(rows) - 1

    repair_row = rows[repair_index]
    if args.expect_repair_stage_prefix:
        stage = str(repair_row.get("stage", ""))
        if not stage.startswith(args.expect_repair_stage_prefix):
            raise ValueError(
                f"repair row stage {stage!r} does not start with "
                f"{args.expect_repair_stage_prefix!r}"
            )

    source_rows = [row for idx, row in enumerate(rows) if idx != repair_index]
    normalized = [
        normalize_record(row, "source") for row in source_rows
    ] + [normalize_record(repair_row, "repair_only")]

    args.out_case_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_case_dir / args.rows_file
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in normalized:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    out_manifest: dict[str, Any] = {
        "certificate_version": "h3a-residue-line-witness-1",
        "witness_type": "source_prefix_plus_single_repair_row",
        "source_case_dir": str(args.source_case_dir),
        "q": int(manifest["q"]),
        "ncols": int(manifest["ncols"]),
        "columns_after_2term": int(manifest.get("columns_after_2term", manifest["ncols"])),
        "level": int(manifest.get("level", 0)),
        "mode": str(manifest.get("mode", "")),
        "sign": manifest.get("sign"),
        "rows_file": args.rows_file,
        "rows_file_sha256": file_sha256(rows_path),
        "original_source_row_count": len(rows),
        "source_row_count": len(source_rows),
        "repair_only_row_count": 1,
        "mixed_row_count": len(normalized),
        "square": len(normalized) == int(manifest["ncols"]),
        "repair_only_row_id": str(repair_row["row_id"]),
        "repair_only_stage": str(repair_row["stage"]),
        "repair_only_original_index": int(repair_index),
        "split_rule": "specified row" if args.repair_row_id else "final source row",
    }
    (args.out_case_dir / "manifest.json").write_text(
        json.dumps(out_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
