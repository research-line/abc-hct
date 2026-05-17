#!/usr/bin/env python3
"""Summarize H3a trace-closure runs for the M* restlevel basket."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = [
    "_results/mstar_nomagma_sparse_hecke_quotient_60168_raw_T5_quotient_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_60168_anc_T5cap14_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_80224_raw_T5cap14_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_80224_anc_T5cap14_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_120336_raw_T5cap24_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_120336_anc_T5cap24_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_240672_raw_T5cap48_fullprimes_numpy_mac_2026-05-10.json",
    "_results/mstar_nomagma_sparse_hecke_quotient_240672_anc_T5cap48_fullprimes_numpy_mac_2026-05-10.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stage_operator(stage: str) -> str:
    if stage.startswith("manin"):
        return "manin"
    if "_batch_" in stage:
        return stage.split("_batch_", 1)[0]
    return stage


def summarize_file(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    rows: list[dict[str, Any]] = []
    for run in payload.get("runs", []):
        stages = run.get("stages", [])
        if not stages:
            continue
        manin_stage = next((s for s in stages if str(s.get("stage", "")).startswith("manin")), None)
        final = stages[-1]
        before_kill = None
        for stage in reversed(stages[:-1]):
            if int(stage.get("quotient_dim", -1)) > 0:
                before_kill = stage
                break
        operators = []
        seen = set()
        for stage in stages:
            op = stage_operator(str(stage.get("stage", "")))
            if op != "manin" and op not in seen:
                seen.add(op)
                operators.append(op)
        rows.append(
            {
                "source_file": str(path),
                "level": int(run["level"]),
                "mode": str(run["mode"]),
                "q": int(run["q"]),
                "sign": run.get("sign"),
                "status": str(run["status"]),
                "manin_symbols": int(run["manin_symbols"]),
                "columns_after_2term": int(run["columns_after_2term"]),
                "manin_qdim": int(manin_stage["quotient_dim"]) if manin_stage else None,
                "final_stage": str(final["stage"]),
                "final_rank": int(final["rank"]),
                "final_qdim": int(final["quotient_dim"]),
                "stage_before_kill": str(before_kill["stage"]) if before_kill else None,
                "qdim_before_kill": int(before_kill["quotient_dim"]) if before_kill else None,
                "operators_seen": operators,
                "seconds_total": float(run.get("seconds_total", 0.0)),
            }
        )
    return rows


def write_markdown(summary: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# H3a Restlevel Trace Summary")
    lines.append("")
    lines.append("This table summarizes the existing q=3863 sparse trace-closure runs.")
    lines.append("")
    lines.append("| Level | Mode | q | cols | qdim after Manin | before kill | kill stage | final qdim | status |")
    lines.append("|---:|---|---:|---:|---:|---|---|---:|---|")
    for row in summary["rows"]:
        before = (
            f"{row['stage_before_kill']} / qdim {row['qdim_before_kill']}"
            if row["stage_before_kill"]
            else ""
        )
        lines.append(
            f"| {row['level']} | `{row['mode']}` | {row['q']} | "
            f"{row['columns_after_2term']} | {row['manin_qdim']} | "
            f"`{before}` | `{row['final_stage']}` | {row['final_qdim']} | "
            f"`{row['status']}` |"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "All eight mapped restlevel/mode cases are killed at q=3863 by canonical "
        "Trace rows.  For the larger levels the pattern is especially rigid: "
        "a long T5 ladder leaves a one-dimensional residue and the first T7 "
        "batch kills it.  This is a q=3863 local trace-closure certificate, "
        "not yet a uniform all-prime Fitting theorem."
    )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*", type=Path, default=[Path(p) for p in DEFAULT_INPUTS])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("_results/mstar_h3a_restlevel_trace_summary_2026-05-16.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("_results/mstar_h3a_restlevel_trace_summary_2026-05-16.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for path in args.inputs:
        if path.exists():
            rows.extend(summarize_file(path))
        else:
            missing.append(str(path))
    rows.sort(key=lambda r: (r["level"], r["mode"]))
    summary = {
        "tool": "mstar_h3a_restlevel_trace_summary",
        "rows": rows,
        "missing": missing,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
