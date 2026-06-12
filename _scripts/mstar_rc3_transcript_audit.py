#!/usr/bin/env python3
"""Audit RC3a row-transcript hash manifests.

RC3a does not yet prove a rank claim. It fixes the generated row stream by
recording per-stage SHA256 digests. This verifier checks that the manifest and
digest files are internally consistent before the artifacts are promoted to
stronger pivot-witness work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DATE = "2026-05-12"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass
class ManifestAudit:
    manifest: str
    manifest_sha256: str
    level: int | None
    mode: str | None
    sign: int | None
    q: int | None
    certificate_version: str
    stage_count: int
    total_rows_added: int
    total_nnz_added: int
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


def audit_manifest(path: Path) -> ManifestAudit:
    manifest_path = resolve_manifest(path)
    problems: list[str] = []
    payload: dict[str, Any] = {}
    manifest_digest = ""
    try:
        manifest_digest = file_hash(manifest_path)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return ManifestAudit(
            manifest=str(manifest_path),
            manifest_sha256=manifest_digest,
            level=None,
            mode=None,
            sign=None,
            q=None,
            certificate_version="",
            stage_count=0,
            total_rows_added=0,
            total_nnz_added=0,
            checks_ok=False,
            problems=[f"manifest unreadable: {exc}"],
        )

    cert_version = str(payload.get("certificate_version", ""))
    if not cert_version.startswith("rc3a-row-transcript"):
        problems.append("unexpected certificate_version")

    q = payload.get("q")
    if q != 3863:
        problems.append("unexpected coefficient field q")

    stages = payload.get("stages")
    if not isinstance(stages, list):
        stages = []
        problems.append("stages is not a list")

    seen_stage_names: set[str] = set()
    seen_files: set[str] = set()
    total_rows = 0
    total_nnz = 0
    for idx, stage in enumerate(stages):
        if not isinstance(stage, dict):
            problems.append(f"stage {idx}: not an object")
            continue
        stage_name = str(stage.get("stage", ""))
        sha_file = str(stage.get("sha256_file", ""))
        expected = str(stage.get("row_transcript_sha256", ""))
        rows_added = int(stage.get("rows_added", -1))
        nnz_added = int(stage.get("nnz_added", -1))

        if not stage_name:
            problems.append(f"stage {idx}: missing stage name")
        if stage_name in seen_stage_names:
            problems.append(f"stage {idx}: duplicate stage name {stage_name}")
        seen_stage_names.add(stage_name)

        if rows_added < 0:
            problems.append(f"stage {idx}: rows_added negative")
        else:
            total_rows += rows_added
        if nnz_added < 0:
            problems.append(f"stage {idx}: nnz_added negative")
        else:
            total_nnz += nnz_added

        if not HEX64_RE.match(expected):
            problems.append(f"stage {idx}: invalid row_transcript_sha256")

        if not sha_file:
            problems.append(f"stage {idx}: missing sha256_file")
            continue
        if sha_file in seen_files:
            problems.append(f"stage {idx}: duplicate sha256_file {sha_file}")
        seen_files.add(sha_file)
        digest_path = manifest_path.parent / sha_file
        if not digest_path.exists():
            problems.append(f"stage {idx}: missing digest file {sha_file}")
            continue
        actual = digest_path.read_text(encoding="utf-8").strip()
        if actual != expected:
            problems.append(f"stage {idx}: digest file mismatch {sha_file}")
        if file_hash(digest_path) == "":
            problems.append(f"stage {idx}: digest file hash unexpectedly empty")

    return ManifestAudit(
        manifest=str(manifest_path),
        manifest_sha256=manifest_digest,
        level=payload.get("level"),
        mode=payload.get("mode"),
        sign=payload.get("sign"),
        q=payload.get("q"),
        certificate_version=cert_version,
        stage_count=len(stages),
        total_rows_added=total_rows,
        total_nnz_added=total_nnz,
        checks_ok=not problems,
        problems=problems,
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines: list[str] = [
        "# RC3a Transcript Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "| Level | Mode | Sign | Stages | Rows added | Checks | Manifest |",
        "|---:|---|---:|---:|---:|---|---|",
    ]
    for item in payload["manifests"]:
        checks = "ok" if item["checks_ok"] else "PROBLEM"
        lines.append(
            f"| {item['level']} | {item['mode']} | {item['sign']} | "
            f"{item['stage_count']} | {item['total_rows_added']} | "
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
            "This audit verifies RC3a hash-manifest consistency only. It does "
            "not recompute Manin rows and does not yet verify a pivot/rank "
            "witness.",
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
