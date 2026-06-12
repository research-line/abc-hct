#!/usr/bin/env python3
"""Build an S5 repair certificate bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_file(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "bytes": path.stat().st_size,
        "sha256": file_hash(path),
    }


def collect_tree(path: Path, root: Path) -> dict[str, Any]:
    files = [item for item in sorted(path.rglob("*")) if item.is_file()]
    digest = hashlib.sha256()
    entries = []
    total_bytes = 0
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
        "# S5 Repair Certificate Bundle",
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
        f"- Repair prime: `{cert['repair_prime']}`",
        f"- ncols: `{cert['ncols']}`",
        f"- Repair rows: `{cert['repair_rows']}`",
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
    parser.add_argument("--case", default="N60168_raw_p2_s5_repair")
    parser.add_argument("--result-json", type=Path, required=True)
    parser.add_argument("--result-md", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--audit-md", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--err", type=Path, required=True)
    parser.add_argument("--repair-witness-dir", type=Path, required=True)
    parser.add_argument("--repair-transcript-dir", type=Path, required=True)
    parser.add_argument("--scripts", nargs="*", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    result_payload = load_json(args.result_json)
    audit_payload = load_json(args.audit_json)
    witness_manifest = result_payload["repair_witness"]["manifest"]

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
        ("repair-witness", args.repair_witness_dir),
        ("repair-transcript", args.repair_transcript_dir),
    ]:
        item = collect_tree(path.resolve(), root)
        item["role"] = role
        trees.append(item)

    payload = {
        "tool": "mstar_s5_repair_certificate_bundle",
        "certificate": {
            "case": args.case,
            "claim": "The fixed-quotient S5 repair witness proves full rank modulo 2 for the 60168/raw quotient using T5 batches 1-13 plus T7 batch 1.",
            "level": witness_manifest.get("level"),
            "mode": witness_manifest.get("mode"),
            "sign": witness_manifest.get("sign"),
            "q": witness_manifest.get("q"),
            "repair_prime": witness_manifest.get("repair_prime"),
            "ncols": witness_manifest.get("ncols"),
            "repair_rows": witness_manifest.get("repair_row_count"),
            "audit_rank": audit_payload.get("rank"),
            "audit_checks_ok": bool(audit_payload.get("checks_ok")),
        },
        "files": files,
        "trees": trees,
        "verification_notes": [
            "Result JSON/MD records the fixed-quotient repair computation.",
            "Repair witness tree contains exported independent rows over the fixed GF(3863) quotient.",
            "Repair transcript tree contains per-stage rowhash indexes, including T7 batch 1.",
            "Audit JSON/MD recomputes rank modulo 2 and checks transcript binding.",
            "Run err file is expected to be empty.",
        ],
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
