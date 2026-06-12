#!/usr/bin/env python3
"""Build an RC4 certificate bundle manifest.

RC4 is a packaging layer: collect the result, audit, source witness, transcript,
log, and script hashes into one portable manifest so that a reader can verify
which exact artifacts constitute the rank certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_file(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "bytes": path.stat().st_size,
        "sha256": file_hash(path),
    }


def collect_tree(path: Path, root: Path) -> dict[str, Any]:
    files = [p for p in sorted(path.rglob("*")) if p.is_file()]
    digest = hashlib.sha256()
    total_bytes = 0
    entries = []
    for file_path in files:
        item = collect_file(file_path, root)
        entries.append(item)
        total_bytes += int(item["bytes"])
        digest.update(str(item["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return {
        "path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
        "files": entries,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    cert = payload["certificate"]
    lines = [
        "# RC4 Certificate Bundle",
        "",
        f"Case: `{cert['case']}`",
        "",
        "## Claim",
        "",
        cert["claim"],
        "",
        "## Summary",
        "",
        f"- Level: `{cert['level']}`",
        f"- Mode: `{cert['mode']}`",
        f"- Sign: `{cert['sign']}`",
        f"- q: `{cert['q']}`",
        f"- Final stage: `{cert['final_stage']}`",
        f"- Final quotient dimension: `{cert['final_quotient_dim']}`",
        f"- Audit rank: `{cert['audit_rank']}`",
        f"- Audit checks: `{cert['audit_checks_ok']}`",
        "",
        "## Files",
        "",
        "| Role | Path | Bytes | SHA256 |",
        "|---|---|---:|---|",
    ]
    for item in payload["files"]:
        lines.append(f"| {item['role']} | `{item['path']}` | {item['bytes']} | `{item['sha256']}` |")
    lines.extend(["", "## Trees", "", "| Role | Path | Files | Bytes | Tree SHA256 |", "|---|---|---:|---:|---|"])
    for tree in payload["trees"]:
        lines.append(
            f"| {tree['role']} | `{tree['path']}` | {tree['file_count']} | "
            f"{tree['total_bytes']} | `{tree['tree_sha256']}` |"
        )
    lines.extend(["", "## Verification Notes", ""])
    for note in payload["verification_notes"]:
        lines.append(f"- {note}")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--case", default="N60168_raw_sign1_rc3d")
    parser.add_argument("--result-json", type=Path, required=True)
    parser.add_argument("--result-md", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--audit-md", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--err", type=Path, required=True)
    parser.add_argument("--source-witness-dir", type=Path, required=True)
    parser.add_argument("--transcript-dir", type=Path, required=True)
    parser.add_argument("--scripts", nargs="*", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    result_payload = load_json(args.result_json)
    audit_payload = load_json(args.audit_json)
    result = result_payload["runs"][0]
    audit = audit_payload["manifests"][0]
    final_stage = next((stage for stage in reversed(result.get("stages", [])) if stage.get("killed")), None)
    if final_stage is None and result.get("stages"):
        final_stage = result["stages"][-1]
    final_stage = final_stage or {}

    files = []
    for role, path in [
        ("result-json", args.result_json),
        ("result-md", args.result_md),
        ("audit-json", args.audit_json),
        ("audit-md", args.audit_md),
        ("run-log", args.log),
        ("run-err", args.err),
    ]:
        item = collect_file(path.resolve(), root)
        item["role"] = role
        files.append(item)
    for script in args.scripts:
        if script.exists():
            item = collect_file(script.resolve(), root)
            item["role"] = "script"
            files.append(item)

    trees = []
    for role, path in [
        ("source-witness", args.source_witness_dir),
        ("rowhash-transcript", args.transcript_dir),
    ]:
        item = collect_tree(path.resolve(), root)
        item["role"] = role
        trees.append(item)

    payload = {
        "tool": "mstar_rc4_certificate_bundle",
        "certificate": {
            "case": args.case,
            "claim": "The rowhash-bound source-row witness proves full rank of the 60168/raw quotient over GF(3863), so the quotient is zero at the recorded final stage.",
            "level": result.get("level"),
            "mode": result.get("mode"),
            "sign": result.get("sign"),
            "q": result_payload.get("q"),
            "final_stage": final_stage.get("stage"),
            "final_quotient_dim": final_stage.get("quotient_dim"),
            "audit_rank": audit.get("recomputed_rank"),
            "audit_checks_ok": bool(audit.get("checks_ok")) and bool(audit_payload.get("all_checks_ok")),
        },
        "files": files,
        "trees": trees,
        "verification_notes": [
            "Result JSON/MD records the killed quotient and stage history.",
            "Audit JSON/MD recomputes rank with Sage matrix rank and checks transcript binding.",
            "Source-witness tree contains the exported independent original rows.",
            "Transcript tree contains per-stage rowhash indexes and digest files.",
            "Run err file is expected to be empty.",
        ],
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
