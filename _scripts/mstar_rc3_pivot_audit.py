#!/usr/bin/env python3
"""Audit RC3b smoke-grade pivot witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DATE = "2026-05-12"


@dataclass
class PivotAudit:
    manifest: str
    level: int | None
    mode: str | None
    sign: int | None
    q: int | None
    witness_type: str
    ncols: int
    pivot_count: int
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


def audit_manifest(path: Path) -> PivotAudit:
    manifest_path = resolve_manifest(path)
    problems: list[str] = []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return PivotAudit(
            manifest=str(manifest_path),
            level=None,
            mode=None,
            sign=None,
            q=None,
            witness_type="",
            ncols=-1,
            pivot_count=0,
            checks_ok=False,
            problems=[f"manifest unreadable: {exc}"],
        )

    q = int(payload.get("q", -1))
    ncols = int(payload.get("ncols", -1))
    strategy = str(payload.get("pivot_strategy", ""))
    witness_type = str(payload.get("witness_type", ""))
    if q != 3863:
        problems.append("unexpected q")
    if ncols <= 0:
        problems.append("invalid ncols")
    if strategy not in {"max", "min"}:
        problems.append("invalid pivot_strategy")
    if witness_type != "full_sparse_basis":
        problems.append("unexpected witness_type")

    rows_file = str(payload.get("rows_file", ""))
    rows_path = manifest_path.parent / rows_file
    if not rows_file or not rows_path.exists():
        problems.append("missing rows_file")
        records: list[dict[str, Any]] = []
    else:
        actual_hash = file_hash(rows_path)
        if actual_hash != payload.get("rows_file_sha256"):
            problems.append("rows_file_sha256 mismatch")
        records = []
        with rows_path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except Exception as exc:
                    problems.append(f"row {line_no}: invalid json: {exc}")

    pivots: set[int] = set()
    for idx, record in enumerate(records):
        pivot = int(record.get("pivot", -1))
        row = record.get("row")
        if not isinstance(row, list) or not row:
            problems.append(f"record {idx}: empty/non-list row")
            continue
        coeffs: dict[int, int] = {}
        for item in row:
            if not isinstance(item, list) or len(item) != 2:
                problems.append(f"record {idx}: malformed row entry")
                continue
            col, val = int(item[0]), int(item[1]) % q
            if col < 0 or col >= ncols:
                problems.append(f"record {idx}: column out of range")
            if val == 0:
                problems.append(f"record {idx}: zero coefficient")
            coeffs[col] = val
        if pivot in pivots:
            problems.append(f"record {idx}: duplicate pivot {pivot}")
        pivots.add(pivot)
        if coeffs.get(pivot) != 1:
            problems.append(f"record {idx}: pivot coefficient is not 1")
        if coeffs:
            expected_pivot = max(coeffs) if strategy == "max" else min(coeffs)
            if pivot != expected_pivot:
                problems.append(f"record {idx}: pivot does not match strategy")

    manifest_pivot_count = int(payload.get("pivot_count", -1))
    if manifest_pivot_count != len(records):
        problems.append("manifest pivot_count differs from row count")
    if len(pivots) != ncols:
        problems.append("pivot count does not prove full rank")

    return PivotAudit(
        manifest=str(manifest_path),
        level=payload.get("level"),
        mode=payload.get("mode"),
        sign=payload.get("sign"),
        q=payload.get("q"),
        witness_type=witness_type,
        ncols=ncols,
        pivot_count=len(pivots),
        checks_ok=not problems,
        problems=problems,
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# RC3b Pivot Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "| Level | Mode | Sign | ncols | Pivots | Checks | Manifest |",
        "|---:|---|---:|---:|---:|---|---|",
    ]
    for item in payload["manifests"]:
        checks = "ok" if item["checks_ok"] else "PROBLEM"
        lines.append(
            f"| {item['level']} | {item['mode']} | {item['sign']} | "
            f"{item['ncols']} | {item['pivot_count']} | {checks} | "
            f"`{Path(item['manifest']).name}` |"
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
            "This audit verifies a full sparse pivot basis exported by the "
            "Python ranker. It proves full rank for the exported basis, but "
            "does not yet independently derive that basis from the Manin/Hecke "
            "row transcript.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    audits = [audit_manifest(path) for path in args.inputs]
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
