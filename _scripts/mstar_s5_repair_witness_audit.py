#!/usr/bin/env python3
"""Audit S5 fixed-quotient repair witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def canonical_row(row: dict[int, int], q: int) -> str:
    return ",".join(
        f"{int(col)}:{int(row[col]) % q}"
        for col in sorted(row)
        if int(row[col]) % q
    )


def load_rows(rows_path: Path, q: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with rows_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            row: dict[int, int] = {}
            for col, value in record["row"]:
                value_i = int(value) % q
                if value_i:
                    row[int(col)] = value_i
            record["_row_dict"] = row
            record["_line_no"] = line_no
            records.append(record)
    return records


def transcript_index(transcript_dir: Path | None) -> dict[tuple[str, int], str]:
    if transcript_dir is None:
        return {}
    manifest_path = transcript_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    index: dict[tuple[str, int], str] = {}
    for stage in payload.get("stages", []):
        stage_name = str(stage["stage"])
        file_name = stage.get("row_hash_index_file")
        if not file_name:
            continue
        path = transcript_dir / str(file_name)
        expected_sha = stage.get("row_hash_index_sha256")
        if expected_sha and file_sha256(path) != expected_sha:
            raise RuntimeError(f"row hash index sha mismatch: {path}")
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                index[(stage_name, int(record["stage_row_index"]))] = str(record["row_line_sha256"])
    return index


def sage_rank(records: list[dict[str, Any]], ncols: int, q: int, prime: int) -> int:
    from sage.all import GF, matrix  # type: ignore

    field = GF(prime)
    entries: dict[tuple[int, int], Any] = {}
    for i, record in enumerate(records):
        for col, value in record["_row_dict"].items():
            reduced = symmetric_lift(value, q) % prime
            if reduced:
                entries[(i, int(col))] = field(reduced)
    mat = matrix(field, len(records), ncols, entries, sparse=True)
    return int(mat.rank())


def audit(case_dir: Path, transcript_dir: Path | None) -> dict[str, Any]:
    manifest_path = case_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    q = int(manifest["q"])
    prime = int(manifest["repair_prime"])
    ncols = int(manifest["ncols"])
    rows_path = case_dir / str(manifest["rows_file"])
    problems: list[str] = []
    if file_sha256(rows_path) != manifest.get("rows_file_sha256"):
        problems.append("rows_file_sha256 mismatch")
    records = load_rows(rows_path, q)
    seen_ids: set[str] = set()
    index = transcript_index(transcript_dir)
    bound = 0
    for record in records:
        row_id = str(record.get("row_id", ""))
        if not row_id:
            problems.append(f"line {record['_line_no']}: missing row_id")
        if row_id in seen_ids:
            problems.append(f"duplicate row_id: {row_id}")
        seen_ids.add(row_id)
        stage = str(record.get("stage", ""))
        stage_row_index = int(record.get("stage_row_index", -1))
        claimed = str(record.get("row_line_sha256", ""))
        recomputed = hashlib.sha256(
            f"{stage}\t{stage_row_index}\t{canonical_row(record['_row_dict'], q)}\n".encode("utf-8")
        ).hexdigest()
        if claimed != recomputed:
            problems.append(f"line {record['_line_no']}: row_line_sha256 mismatch")
        if index:
            if index.get((stage, stage_row_index)) == claimed:
                bound += 1
            else:
                problems.append(f"line {record['_line_no']}: row not bound to transcript")
    rank = sage_rank(records, ncols, q, prime)
    if rank != ncols:
        problems.append("repair rows do not prove full rank")
    if len(records) != int(manifest["repair_row_count"]):
        problems.append("repair_row_count mismatch")
    return {
        "case_dir": str(case_dir),
        "transcript_dir": str(transcript_dir) if transcript_dir else None,
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "sign": manifest.get("sign"),
        "q": q,
        "repair_prime": prime,
        "ncols": ncols,
        "repair_row_count": len(records),
        "rank": rank,
        "full_rank": rank == ncols,
        "transcript_checked": transcript_dir is not None,
        "rows_bound_to_transcript": bound,
        "checks_ok": not problems,
        "problems": problems,
    }


def write_markdown(result: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 Repair Witness Audit",
        "",
        "| Level | Mode | Sign | Prime | ncols | Rows | Rank | Transcript rows bound | Checks |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| {result['level']} | {result['mode']} | {result['sign']} | "
            f"{result['repair_prime']} | {result['ncols']} | "
            f"{result['repair_row_count']} | {result['rank']} | "
            f"{result['rows_bound_to_transcript']} | {result['checks_ok']} |"
        ),
        "",
    ]
    if result["problems"]:
        lines.append("## Problems")
        lines.append("")
        for problem in result["problems"]:
            lines.append(f"- {problem}")
        lines.append("")
    else:
        lines.append("No problems found.")
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--transcript-dir", type=Path)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.case_dir, args.transcript_dir)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result, args.out_md)
    return 0 if result["checks_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
