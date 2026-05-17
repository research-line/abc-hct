#!/usr/bin/env python3
"""Audit no-Magma sparse Hecke quotient result JSON files.

This script is intentionally lightweight: it does not recompute ranks. It checks
that saved result artifacts are internally consistent before they are used as
inputs for proof notes or stronger certification runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


DATE = "2026-05-12"
RANK_RE = re.compile(
    r"rank done N=(?P<level>\d+) mode=(?P<mode>\w+) stage=(?P<stage>\S+) "
    r"rank=(?P<rank>\d+) qdim=(?P<qdim>\d+)"
)


@dataclass
class RunAudit:
    file: str
    sha256: str
    backend: str
    level: int
    mode: str
    q: int
    sign: int
    status: str
    final_stage: str
    final_quotient_dim: int
    final_rank: int
    columns_after_2term: int
    stage_count: int
    killed: bool
    checks_ok: bool
    problems: list[str]


@dataclass
class PartialLogAudit:
    file: str
    sha256: str
    last_level: int | None
    last_mode: str | None
    last_stage: str | None
    last_rank: int | None
    last_quotient_dim: int | None
    rank_done_lines: int


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_run_file(path: Path, expected_q: int, expected_sign: int | None) -> list[RunAudit]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    audits: list[RunAudit] = []
    digest = file_hash(path)
    for run in payload.get("runs", []):
        problems: list[str] = []
        stages = run.get("stages") or []
        if not stages:
            problems.append("run has no stages")
            final = {}
        else:
            final = stages[-1]

        ncols = run.get("columns_after_2term")
        prev_rank = -1
        prev_qdim = None
        prev_rows = -1
        prev_nnz = -1
        for idx, stage in enumerate(stages):
            rank = int(stage.get("rank", -1))
            qdim = int(stage.get("quotient_dim", -1))
            rows = int(stage.get("total_rows", -1))
            nnz = int(stage.get("total_nnz", -1))
            if ncols is not None and rank + qdim != int(ncols):
                problems.append(
                    f"stage {idx} {stage.get('stage')}: rank+qdim != columns_after_2term"
                )
            if rank < prev_rank:
                problems.append(f"stage {idx} {stage.get('stage')}: rank decreased")
            if prev_qdim is not None and qdim > prev_qdim:
                problems.append(f"stage {idx} {stage.get('stage')}: qdim increased")
            if rows < prev_rows:
                problems.append(f"stage {idx} {stage.get('stage')}: total_rows decreased")
            if nnz < prev_nnz:
                problems.append(f"stage {idx} {stage.get('stage')}: total_nnz decreased")
            if bool(stage.get("killed")) != (qdim == 0):
                problems.append(f"stage {idx} {stage.get('stage')}: killed flag mismatch")
            prev_rank, prev_qdim, prev_rows, prev_nnz = rank, qdim, rows, nnz

        final_qdim = int(final.get("quotient_dim", -1)) if final else -1
        final_rank = int(final.get("rank", -1)) if final else -1
        status = str(run.get("status"))
        if status == "killed" and final_qdim != 0:
            problems.append("status killed but final quotient dimension is not zero")
        if status != "killed" and final_qdim == 0:
            problems.append("final quotient dimension zero but status is not killed")
        if int(run.get("q", -1)) != expected_q:
            problems.append("unexpected coefficient prime q")
        if expected_sign is not None and int(run.get("sign", 0)) != expected_sign:
            problems.append("unexpected sign")

        audits.append(
            RunAudit(
                file=str(path),
                sha256=digest,
                backend=str(run.get("backend")),
                level=int(run.get("level", -1)),
                mode=str(run.get("mode")),
                q=int(run.get("q", -1)),
                sign=int(run.get("sign", 0)),
                status=status,
                final_stage=str(final.get("stage", "")),
                final_quotient_dim=final_qdim,
                final_rank=final_rank,
                columns_after_2term=int(ncols or -1),
                stage_count=len(stages),
                killed=(final_qdim == 0),
                checks_ok=not problems,
                problems=problems,
            )
        )
    return audits


def audit_partial_log(path: Path) -> PartialLogAudit:
    last: dict[str, Any] | None = None
    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = RANK_RE.search(line)
            if not m:
                continue
            count += 1
            last = m.groupdict()
    return PartialLogAudit(
        file=str(path),
        sha256=file_hash(path),
        last_level=int(last["level"]) if last else None,
        last_mode=str(last["mode"]) if last else None,
        last_stage=str(last["stage"]) if last else None,
        last_rank=int(last["rank"]) if last else None,
        last_quotient_dim=int(last["qdim"]) if last else None,
        rank_done_lines=count,
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append("# No-Magma Result Audit")
    lines.append("")
    lines.append(f"Date: {payload['date']}")
    lines.append("")
    lines.append("## Completed JSON Artifacts")
    lines.append("")
    lines.append("| Level | Mode | Status | Final stage | Final qdim | Checks | File |")
    lines.append("|---:|---|---|---|---:|---|---|")
    for run in payload["runs"]:
        checks = "ok" if run["checks_ok"] else "PROBLEM"
        file_name = Path(run["file"]).name
        lines.append(
            f"| {run['level']} | {run['mode']} | {run['status']} | "
            f"`{run['final_stage']}` | {run['final_quotient_dim']} | "
            f"{checks} | `{file_name}` |"
        )
    if any(not run["checks_ok"] for run in payload["runs"]):
        lines.append("")
        lines.append("## Problems")
        lines.append("")
        for run in payload["runs"]:
            for problem in run["problems"]:
                lines.append(f"- `{Path(run['file']).name}`: {problem}")
    lines.append("")
    lines.append("## Partial Logs")
    lines.append("")
    if payload["partial_logs"]:
        lines.append("| File | Last stage | Last qdim | Rank done lines |")
        lines.append("|---|---|---:|---:|")
        for log in payload["partial_logs"]:
            lines.append(
                f"| `{Path(log['file']).name}` | `{log['last_stage']}` | "
                f"{log['last_quotient_dim']} | {log['rank_done_lines']} |"
            )
    else:
        lines.append("No partial logs supplied.")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This is an artifact-level consistency audit. It does not independently "
        "recompute the ranks and therefore is not yet a proof-grade rank certificate."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--partial-log", action="append", type=Path, default=[])
    parser.add_argument("--expected-q", type=int, default=3863)
    parser.add_argument(
        "--expected-sign",
        type=int,
        choices=[-1, 0, 1],
        default=1,
        help="Expected sign in result JSON; use 0 to skip the sign check.",
    )
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    runs: list[RunAudit] = []
    expected_sign = None if args.expected_sign == 0 else args.expected_sign
    for path in args.inputs:
        runs.extend(audit_run_file(path, args.expected_q, expected_sign))
    partial_logs = [audit_partial_log(path) for path in args.partial_log]

    payload = {
        "date": DATE,
        "runs": [asdict(run) for run in sorted(runs, key=lambda r: (r.level, r.mode, r.file))],
        "partial_logs": [asdict(log) for log in partial_logs],
        "all_completed_checks_ok": all(run.checks_ok for run in runs),
        "all_completed_killed": all(run.killed for run in runs),
    }
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0 if payload["all_completed_checks_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
