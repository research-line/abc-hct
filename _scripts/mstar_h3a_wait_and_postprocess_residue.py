#!/usr/bin/env python3
"""Wait for an RC3c case manifest, then run split-last and verifiers.

The repair stage can be fixed, for example `T_7_minus_0`, or discovered from
the final rank-increasing row.  Auto mode is needed for large H3a jobs where
T5 may already kill the quotient before T7 is reached.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def run_step(cmd: list[str]) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "seconds": time.time() - started,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--out-case-dir", type=Path, required=True)
    parser.add_argument(
        "--expect-stage-prefix",
        help=(
            "Optional fixed repair stage prefix. Use 'auto' or omit it to "
            "accept the final rank-increasing row, subject to any allowed "
            "prefix guards."
        ),
    )
    parser.add_argument(
        "--allowed-repair-stage-prefix",
        action="append",
        default=[],
        help=(
            "Allowed repair stage prefix for auto mode. Can be repeated, e.g. "
            "T_5_minus_2 and T_7_minus_0."
        ),
    )
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--timeout-seconds", type=float, default=0.0)
    parser.add_argument("--status-json", type=Path)
    return parser.parse_args()


def normalized_expect_stage_prefix(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value or value.lower() in {"auto", "none", "any"}:
        return None
    return value


def read_repair_stage(out_case_dir: Path) -> str | None:
    manifest_path = out_case_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    stage = manifest.get("repair_only_stage")
    return str(stage) if stage is not None else None


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    status_path = args.status_json or args.out_prefix.with_suffix(".status.json")
    manifest = args.case_dir / "manifest.json"
    started = time.time()
    expect_stage_prefix = normalized_expect_stage_prefix(args.expect_stage_prefix)

    while not manifest.exists():
        if args.timeout_seconds > 0 and time.time() - started > args.timeout_seconds:
            payload = {
                "status": "timeout",
                "case_dir": str(args.case_dir),
                "waited_seconds": time.time() - started,
            }
            status_path.parent.mkdir(parents=True, exist_ok=True)
            status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(json.dumps(payload))
            return 2
        time.sleep(args.poll_seconds)

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    order_json = args.out_prefix.with_name(args.out_prefix.name + "_order.json")
    order_md = args.out_prefix.with_name(args.out_prefix.name + "_order.md")
    rank_json = args.out_prefix.with_name(args.out_prefix.name + "_rank_verify.json")
    rank_md = args.out_prefix.with_name(args.out_prefix.name + "_rank_verify.md")

    steps: list[dict[str, Any]] = []
    split_cmd = [
        sys.executable,
        str(script_dir / "mstar_h3a_make_residue_line_witness.py"),
        "--source-case-dir",
        str(args.case_dir),
        "--out-case-dir",
        str(args.out_case_dir),
    ]
    if expect_stage_prefix is not None:
        split_cmd.extend(["--expect-repair-stage-prefix", expect_stage_prefix])
    steps.append(run_step(split_cmd))

    actual_repair_stage = read_repair_stage(args.out_case_dir)
    allowed_ok = True
    if steps[-1]["returncode"] == 0 and args.allowed_repair_stage_prefix:
        allowed_ok = bool(
            actual_repair_stage
            and any(
                actual_repair_stage.startswith(prefix)
                for prefix in args.allowed_repair_stage_prefix
            )
        )
        if not allowed_ok:
            steps.append({
                "cmd": ["allowed-repair-stage-prefix-check"],
                "returncode": 1,
                "seconds": 0.0,
                "stdout": "",
                "stderr": (
                    f"repair stage {actual_repair_stage!r} does not match "
                    f"allowed prefixes {args.allowed_repair_stage_prefix!r}"
                ),
            })

    if steps[-1]["returncode"] == 0:
        order_cmd = [
            sys.executable,
            str(script_dir / "mstar_h3a_residue_line_order_certificate.py"),
            str(args.out_case_dir),
            "--out-json",
            str(order_json),
            "--out-md",
            str(order_md),
        ]
        if expect_stage_prefix is not None:
            order_cmd.extend(["--expect-stage-prefix", expect_stage_prefix])
        steps.append(run_step(order_cmd))
    if steps[-1]["returncode"] == 0:
        steps.append(run_step([
            sys.executable,
            str(script_dir / "mstar_h3a_rc3c_witness_verify_rank.py"),
            str(args.out_case_dir),
            "--out-json",
            str(rank_json),
            "--out-md",
            str(rank_md),
        ]))

    ok = all(step["returncode"] == 0 for step in steps)
    payload = {
        "status": "ok" if ok else "failed",
        "case_dir": str(args.case_dir),
        "out_case_dir": str(args.out_case_dir),
        "expect_stage_prefix": expect_stage_prefix,
        "allowed_repair_stage_prefixes": args.allowed_repair_stage_prefix,
        "actual_repair_stage": actual_repair_stage,
        "waited_seconds": time.time() - started,
        "order_json": str(order_json),
        "rank_json": str(rank_json),
        "steps": steps,
    }
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "status_json": str(status_path)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
