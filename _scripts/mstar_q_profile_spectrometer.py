#!/usr/bin/env python3
"""Summarize q-dependent HCT residual profiles from no-Magma JSON outputs.

The goal is deliberately modest: compare existing runs by their quotient
dimension trajectory.  The output is not an algebraic valuation of an adjoint
congruence module; it is a diagnostic residual profile.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"

STAGE_RE = re.compile(r"T_(\d+)_minus_(-?\d+)_batch_(\d+)")


def resolve_source(source: str) -> Path:
    path = Path(source)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    return RESULTS / path.name


def load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def stage_operator(stage_name: str) -> str | None:
    match = STAGE_RE.match(stage_name)
    if not match:
        return None
    p, a, _batch = match.groups()
    return f"T_{p}-{a}"


def summarize_run(path: Path, payload: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    stages = run.get("stages") or []
    if not stages:
        return {
            "source_file": path.name,
            "error": "no stages",
        }

    manin_stage = stages[0]
    manin_qdim = int(manin_stage.get("quotient_dim", 0))
    final_qdim = int(stages[-1].get("quotient_dim", 0))

    reductions: list[int] = []
    operator_counts: dict[str, int] = {}
    operator_reductions: dict[str, int] = {}
    previous_dim = manin_qdim
    hecke_stages = 0

    for stage in stages[1:]:
        name = str(stage.get("stage", ""))
        op = stage_operator(name)
        if op is None:
            continue
        hecke_stages += 1
        qdim = int(stage.get("quotient_dim", previous_dim))
        reduction = max(0, previous_dim - qdim)
        reductions.append(reduction)
        operator_counts[op] = operator_counts.get(op, 0) + 1
        operator_reductions[op] = operator_reductions.get(op, 0) + reduction
        previous_dim = qdim

    tail = [value for value in reductions[-3:] if value > 0]
    avg_tail_reduction = sum(tail) / len(tail) if tail else 0.0
    estimated_extra_batches = (
        math.ceil(final_qdim / avg_tail_reduction)
        if final_qdim > 0 and avg_tail_reduction > 0
        else 0
    )

    level = int(run.get("level", 0))
    log_level = math.log(level) if level > 1 else None
    return {
        "source_file": path.name,
        "level": level,
        "mode": run.get("mode"),
        "q": run.get("q", payload.get("q")),
        "status": run.get("status"),
        "operators": sorted(operator_counts),
        "operator_counts": operator_counts,
        "operator_reductions": operator_reductions,
        "manin_qdim": manin_qdim,
        "final_qdim": final_qdim,
        "trace_codim_S": max(0, manin_qdim - final_qdim),
        "residual_fraction": final_qdim / manin_qdim if manin_qdim else None,
        "hecke_stages": hecke_stages,
        "stages_per_log_level": hecke_stages / log_level if log_level else None,
        "avg_tail_reduction": avg_tail_reduction,
        "estimated_extra_batches_if_tail_persists": estimated_extra_batches,
    }


def build_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# q-Profile Spectrometer",
        "",
        "Date: 2026-05-15",
        "",
        "Diagnostic only: `qdim` and `trace_codim_S` are quotient-profile metrics, not direct valuations of `Q_ad^exc`.",
        "",
        "| source | q | level | mode | operators | stages | final qdim | trace_codim_S | residual fraction | extra batches (tail estimate) |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        residual = row.get("residual_fraction")
        residual_text = f"{residual:.6f}" if residual is not None else ""
        lines.append(
            "| {source} | {q} | {level} | {mode} | {ops} | {stages} | {final} | {trace} | {residual} | {extra} |".format(
                source=row.get("source_file", ""),
                q=row.get("q", ""),
                level=row.get("level", ""),
                mode=row.get("mode", ""),
                ops=", ".join(row.get("operators") or []),
                stages=row.get("hecke_stages", ""),
                final=row.get("final_qdim", ""),
                trace=row.get("trace_codim_S", ""),
                residual=residual_text,
                extra=row.get("estimated_extra_batches_if_tail_persists", ""),
            )
        )

    lines += [
        "",
        "## Operator reductions",
        "",
    ]
    for row in rows:
        lines.append(f"### {row.get('source_file')}")
        for op, value in sorted((row.get("operator_reductions") or {}).items()):
            count = (row.get("operator_counts") or {}).get(op)
            lines.append(f"- `{op}`: reduction `{value}` over `{count}` batches")
        if row.get("stages_per_log_level") is not None:
            lines.append(f"- stages/log(level): `{row['stages_per_log_level']:.3f}`")
        lines.append("")

    lines += [
        "## Reading",
        "",
        "- `q=3863` is spike-like on `N=60168/raw`: `T_5` alone reaches zero.",
        "- `q=997` is generic-like: `T_5` alone leaves a substantial rest, while `T_5,T_7,T_11,T_13` reduce the rest to `6`.",
        "- The useful invariant is therefore a q-dependent residual profile, not a q-independent kill depth.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="+")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for source in args.sources:
        path = resolve_source(source)
        payload = load_payload(path)
        for run in payload.get("runs") or []:
            rows.append(summarize_run(path, payload, run))

    output = {
        "date": "2026-05-15",
        "kind": "q_profile_spectrometer",
        "rows": rows,
    }

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    out_md.write_text(build_markdown(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
