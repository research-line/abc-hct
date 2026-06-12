#!/usr/bin/env python3
"""Audit RC3c independent source-row rank witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DATE = "2026-05-12"


class SparseIncrementalRank:
    def __init__(self, ncols: int, p: int, pivot_strategy: str = "max"):
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0

    def add(self, raw_row: dict[int, int]) -> bool:
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in self.basis:
                factor = value
                for c, v in self.basis[pivot].items():
                    new = (row.get(c, 0) - factor * v) % p
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, p)
                self.basis[pivot] = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                self.rank += 1
                return True
        return False


@dataclass
class SourceAudit:
    manifest: str
    level: int | None
    mode: str | None
    sign: int | None
    q: int | None
    ncols: int
    source_row_count: int
    recomputed_rank: int
    rank_method: str
    transcript_checked: bool
    source_rows_bound: int
    checks_ok: bool
    problems: list[str]


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_manifest(path: Path) -> Path:
    if path.is_dir():
        return path / "manifest.json"
    return path


def canonical_row(row: dict[int, int]) -> str:
    return ",".join(f"{int(c)}:{int(row[c])}" for c in sorted(row) if int(row[c]))


def transcript_index_for(
    source_manifest_path: Path,
    transcript_root: Path | None,
    problems: list[str],
) -> tuple[bool, dict[tuple[str, int], str]]:
    if transcript_root is None:
        return False, {}
    transcript_dir = transcript_root / source_manifest_path.parent.name
    transcript_manifest = transcript_dir / "manifest.json"
    if not transcript_manifest.exists():
        problems.append(f"missing transcript manifest: {transcript_manifest}")
        return True, {}
    try:
        payload = json.loads(transcript_manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"transcript manifest unreadable: {exc}")
        return True, {}

    index: dict[tuple[str, int], str] = {}
    for stage in payload.get("stages", []):
        stage_name = str(stage.get("stage", ""))
        file_name = str(stage.get("row_hash_index_file", ""))
        if not stage_name or not file_name:
            problems.append(f"transcript stage missing row hash index: {stage_name or '<unknown>'}")
            continue
        path = transcript_dir / file_name
        if not path.exists():
            problems.append(f"missing row hash index: {path}")
            continue
        expected_hash = stage.get("row_hash_index_sha256")
        if expected_hash and file_hash(path) != expected_hash:
            problems.append(f"row hash index sha256 mismatch: {file_name}")
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except Exception as exc:
                    problems.append(f"{file_name}:{line_no}: invalid json: {exc}")
                    continue
                idx = int(record.get("stage_row_index", -1))
                digest = str(record.get("row_line_sha256", ""))
                if idx < 0 or not digest:
                    problems.append(f"{file_name}:{line_no}: malformed row hash record")
                    continue
                index[(stage_name, idx)] = digest
    return True, index


def sage_matrix_rank(rows: list[dict[int, int]], ncols: int, q: int) -> int:
    from sage.all import GF, matrix  # type: ignore

    field = GF(q)
    entries: dict[tuple[int, int], Any] = {}
    for i, row in enumerate(rows):
        for col, val in row.items():
            entries[(i, int(col))] = field(int(val) % q)
    mat = matrix(field, len(rows), ncols, entries, sparse=True)
    return int(mat.rank())


def audit_manifest(path: Path, transcript_root: Path | None = None, rank_method: str = "sparse-order") -> SourceAudit:
    manifest_path = resolve_manifest(path)
    problems: list[str] = []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return SourceAudit(str(manifest_path), None, None, None, None, -1, 0, 0, rank_method, False, 0, False, [f"manifest unreadable: {exc}"])

    q = int(payload.get("q", -1))
    ncols = int(payload.get("ncols", -1))
    pivot_strategy = str(payload.get("pivot_strategy", ""))
    if q != 3863:
        problems.append("unexpected q")
    if ncols <= 0:
        problems.append("invalid ncols")
    if pivot_strategy not in {"max", "min"}:
        problems.append("invalid pivot_strategy")
    if payload.get("witness_type") != "independent_source_rows":
        problems.append("unexpected witness_type")

    rows_file = str(payload.get("rows_file", ""))
    rows_path = manifest_path.parent / rows_file
    if not rows_file or not rows_path.exists():
        problems.append("missing rows_file")
        records: list[dict[str, Any]] = []
    else:
        if file_hash(rows_path) != payload.get("rows_file_sha256"):
            problems.append("rows_file_sha256 mismatch")
        records = []
        with rows_path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except Exception as exc:
                    problems.append(f"line {line_no}: invalid json: {exc}")

    seen_ids: set[str] = set()
    ranker = SparseIncrementalRank(ncols, q, pivot_strategy) if rank_method == "sparse-order" else None
    source_nnz = 0
    transcript_checked, transcript_index = transcript_index_for(manifest_path, transcript_root, problems)
    source_rows_bound = 0
    parsed_rows: list[dict[int, int]] = []
    for idx, record in enumerate(records):
        row_id = str(record.get("row_id", ""))
        if not row_id:
            problems.append(f"record {idx}: missing row_id")
        if row_id in seen_ids:
            problems.append(f"record {idx}: duplicate row_id")
        seen_ids.add(row_id)
        row_data = record.get("row")
        if not isinstance(row_data, list) or not row_data:
            problems.append(f"record {idx}: empty/non-list row")
            continue
        row: dict[int, int] = {}
        for item in row_data:
            if not isinstance(item, list) or len(item) != 2:
                problems.append(f"record {idx}: malformed row entry")
                continue
            col, val = int(item[0]), int(item[1]) % q
            if col < 0 or col >= ncols:
                problems.append(f"record {idx}: column out of range")
            if val == 0:
                problems.append(f"record {idx}: zero coefficient")
            row[col] = val
        stage = str(record.get("stage", ""))
        stage_row_index = int(record.get("stage_row_index", -1))
        claimed_line_hash = record.get("row_line_sha256")
        if claimed_line_hash:
            line = f"{stage}\t{stage_row_index}\t{canonical_row(row)}\n"
            recomputed_line_hash = hashlib.sha256(line.encode("utf-8")).hexdigest()
            if recomputed_line_hash != claimed_line_hash:
                problems.append(f"record {idx}: row_line_sha256 mismatch")
        elif transcript_checked:
            problems.append(f"record {idx}: missing row_line_sha256 for transcript binding")
        if transcript_checked and claimed_line_hash:
            indexed_hash = transcript_index.get((stage, stage_row_index))
            if indexed_hash == claimed_line_hash:
                source_rows_bound += 1
            else:
                problems.append(f"record {idx}: source row not bound to transcript index")
        source_nnz += len(row)
        parsed_rows.append(row)
        if ranker is not None and not ranker.add(row):
            problems.append(f"record {idx}: exported row is dependent in verifier order")

    if rank_method == "sparse-order":
        recomputed_rank = ranker.rank if ranker is not None else 0
    elif rank_method == "sage-matrix":
        try:
            recomputed_rank = sage_matrix_rank(parsed_rows, ncols, q)
        except Exception as exc:
            recomputed_rank = -1
            problems.append(f"sage-matrix rank failed: {exc}")
    else:
        recomputed_rank = -1
        problems.append(f"unknown rank_method: {rank_method}")

    if int(payload.get("source_row_count", -1)) != len(records):
        problems.append("manifest source_row_count differs from row count")
    if int(payload.get("source_row_nnz", -1)) != source_nnz:
        problems.append("manifest source_row_nnz differs from row nnz")
    if recomputed_rank != ncols:
        problems.append("source rows do not prove full rank")

    return SourceAudit(
        manifest=str(manifest_path),
        level=payload.get("level"),
        mode=payload.get("mode"),
        sign=payload.get("sign"),
        q=payload.get("q"),
        ncols=ncols,
        source_row_count=len(records),
        recomputed_rank=recomputed_rank,
        rank_method=rank_method,
        transcript_checked=transcript_checked,
        source_rows_bound=source_rows_bound,
        checks_ok=not problems,
        problems=problems,
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# RC3c Source-Row Witness Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "| Level | Mode | Sign | ncols | Source rows | Recomputed rank | Method | Bound rows | Checks | Manifest |",
        "|---:|---|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for item in payload["manifests"]:
        checks = "ok" if item["checks_ok"] else "PROBLEM"
        lines.append(
            f"| {item['level']} | {item['mode']} | {item['sign']} | "
            f"{item['ncols']} | {item['source_row_count']} | "
            f"{item['recomputed_rank']} | {item['rank_method']} | "
            f"{item['source_rows_bound']} | "
            f"{checks} | `{Path(item['manifest']).name}` |"
        )
    if any(not item["checks_ok"] for item in payload["manifests"]):
        lines.extend(["", "## Problems", ""])
        for item in payload["manifests"]:
            for problem in item["problems"]:
                lines.append(f"- `{Path(item['manifest']).name}`: {problem}")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This audit recomputes the rank of exported original source rows over "
            "GF(3863). It proves full rank for those rows and keeps row IDs for "
            "binding to the transcript layer. When `--transcript-root` is supplied, "
            "it also checks the per-row transcript hash index.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--transcript-root", type=Path)
    parser.add_argument("--rank-method", choices=["sparse-order", "sage-matrix"], default="sparse-order")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    audits = [audit_manifest(path, args.transcript_root, args.rank_method) for path in args.inputs]
    payload = {
        "date": DATE,
        "manifests": [asdict(audit) for audit in audits],
        "all_checks_ok": all(audit.checks_ok for audit in audits),
    }
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0 if payload["all_checks_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
