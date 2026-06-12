#!/usr/bin/env python3
"""Extract normalized HCT metrics from no-Magma result JSON files.

This is the v2 companion to ``mstar_killdepth_extract.py``.  It keeps the
old operator kill-depth idea, but separates it from more stable quantities:

* terminal_kill_stage
* cumulative_hecke_stages
* trace_codim_S
* old_dim_expected_raw
* residual_dim
* old_dim_deficit

The script is intentionally conservative.  It only normalizes oldform mass in
raw mode, where the simple ``sigma_0(N_test/N_E)`` rule is currently justified
by the Conductor-/Oldform-Ledger.  Anc normalization is left null until the
Atkin-Lehner projection is formalized.
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
DATE = "2026-05-15"

STAGE_RE_BATCH = re.compile(r"T_(\d+)_minus_(-?\d+)_batch_(\d+)")
STAGE_RE_SIMPLE = re.compile(r"T_(\d+)_minus_(-?\d+)$")


TRIPLES = {
    "reyssat": {
        "label": "Reyssat",
        "raw_a": 2,
        "raw_b": 3**10 * 109,
        "triple": "(2, 3^10*109, 23^5)",
        "N_E": 240672,
    },
    "5_27": {
        "label": "(5,27)",
        "raw_a": 5,
        "raw_b": 27,
        "triple": "(5, 27, 32)",
        "N_E": 30,
    },
    "1_80": {
        "label": "(1,80)",
        "raw_a": 1,
        "raw_b": 80,
        "triple": "(1, 80, 81)",
        "N_E": 240,
    },
    "1_4374": {
        "label": "(1,4374)",
        "raw_a": 1,
        "raw_b": 4374,
        "triple": "(1, 4374, 4375)",
        "N_E": 3360,
    },
}


def parse_stage(stage_name: str) -> dict[str, int] | None:
    match = STAGE_RE_BATCH.match(stage_name)
    if match:
        p, a, batch = match.groups()
        return {"p": int(p), "a": int(a), "batch": int(batch)}
    match = STAGE_RE_SIMPLE.match(stage_name)
    if match:
        p, a = match.groups()
        return {"p": int(p), "a": int(a), "batch": 1}
    return None


def divisor_count(n: int) -> int:
    if n <= 0:
        return 0
    count = 1
    d = 2
    while d * d <= n:
        exp = 0
        while n % d == 0:
            n //= d
            exp += 1
        if exp:
            count *= exp + 1
        d += 1 if d == 2 else 2
    if n > 1:
        count *= 2
    return count


def infer_triple(source_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    raw_a = payload.get("raw_a")
    raw_b = payload.get("raw_b")
    if raw_a is not None and raw_b is not None:
        for meta in TRIPLES.values():
            if int(raw_a) == meta["raw_a"] and int(raw_b) == meta["raw_b"]:
                return meta
    lowered = source_name.lower()
    for key in ("5_27", "1_80", "1_4374"):
        if key in lowered:
            return TRIPLES[key]
    return TRIPLES["reyssat"]


def final_qdim(run: dict[str, Any]) -> int | None:
    stages = run.get("stages") or []
    if not stages:
        return None
    value = stages[-1].get("quotient_dim")
    return int(value) if value is not None else None


def manin_qdim(run: dict[str, Any]) -> int | None:
    """Dimension after Manin relations, before the Frey trace cuts."""
    stages = run.get("stages") or []
    for stage in stages:
        if stage.get("stage") in {"manin_T_relations_after_SI", "manin_relations"}:
            value = stage.get("quotient_dim")
            return int(value) if value is not None else None
    if stages:
        value = stages[0].get("quotient_dim")
        return int(value) if value is not None else None
    return None


def extract_run(source_name: str, payload: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    meta = infer_triple(source_name, payload)
    level = int(run.get("level"))
    mode = run.get("mode")
    qdim = final_qdim(run)
    qdim_after_manin = manin_qdim(run)
    hecke_stage_count = 0
    terminal_stage = None
    terminal_operator = None
    operator_kill_depth = None

    for stage in run.get("stages") or []:
        parsed = parse_stage(str(stage.get("stage", "")))
        if parsed is None:
            continue
        hecke_stage_count += 1
        killed = bool(stage.get("killed")) or stage.get("quotient_dim") == 0
        if killed and terminal_stage is None:
            terminal_stage = stage.get("stage")
            terminal_operator = f"T_{parsed['p']}-{parsed['a']}"
            operator_kill_depth = parsed["batch"]

    if mode == "raw" and level % int(meta["N_E"]) == 0:
        old_dim_expected_raw = divisor_count(level // int(meta["N_E"]))
    elif mode == "raw":
        old_dim_expected_raw = 0
    else:
        old_dim_expected_raw = None

    if qdim is not None and old_dim_expected_raw is not None:
        residual_dim = max(0, qdim - old_dim_expected_raw)
        old_dim_deficit = max(0, old_dim_expected_raw - qdim)
    else:
        residual_dim = None
        old_dim_deficit = None

    trace_codim_S = (
        max(0, qdim_after_manin - qdim)
        if qdim_after_manin is not None and qdim is not None
        else None
    )

    return {
        "source_file": source_name,
        "label": meta["label"],
        "triple": meta["triple"],
        "N_E": meta["N_E"],
        "N_test": level,
        "q": run.get("q", payload.get("q")),
        "mode": mode,
        "sign": run.get("sign"),
        "status": run.get("status"),
        "qdim_after_manin": qdim_after_manin,
        "qdim_final": qdim,
        "trace_codim_S": trace_codim_S,
        "terminal_kill_stage": terminal_stage,
        "terminal_operator": terminal_operator,
        "operator_kill_depth": operator_kill_depth,
        "cumulative_hecke_stages": hecke_stage_count,
        "old_dim_expected_raw": old_dim_expected_raw,
        "residual_dim": residual_dim,
        "old_dim_deficit": old_dim_deficit,
    }


def source_path(source: str) -> Path:
    path = Path(source)
    if path.is_absolute() or path.exists():
        return path
    if len(path.parts) > 1:
        candidate = ROOT / path
        if candidate.exists():
            return candidate
    return RESULTS / path.name


def collect_rows(pattern: str, sources: list[str] | None = None) -> tuple[list[dict[str, Any]], int, int]:
    rows: list[dict[str, Any]] = []
    files_scanned = 0
    files_with_runs = 0
    if sources:
        paths = [source_path(source) for source in sources]
    else:
        paths = sorted(RESULTS.glob(pattern))
    for path in paths:
        files_scanned += 1
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        runs = payload.get("runs") if isinstance(payload, dict) else None
        if not isinstance(runs, list):
            continue
        before = len(rows)
        for run in runs:
            if isinstance(run, dict) and run.get("level") is not None:
                rows.append(extract_run(path.name, payload, run))
        if len(rows) > before:
            files_with_runs += 1
    return rows, files_scanned, files_with_runs


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    rows = payload["rows"]
    lines = [
        "# M*: Metric Extractor v2",
        "",
        f"Datum: {payload['date']}",
        f"Files gescannt: {payload['files_scanned']}",
        f"Files mit Runs: {payload['files_with_runs']}",
        f"Zeilen: {payload['row_count']}",
        "",
        "## Normalisierte Run-Tabelle",
        "",
        "| Label | N_E | N_test | Mode | manin_dim | trace_codim_S | qdim | old_raw | residual | deficit | terminal | cum stages | Source |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {label} | {N_E} | {N_test} | {mode} | {qdim_after_manin} | "
            "{trace_codim_S} | {qdim_final} | "
            "{old_dim_expected_raw} | {residual_dim} | {old_dim_deficit} | "
            "{terminal} | {cumulative_hecke_stages} | {source_file} |".format(
                label=row["label"],
                N_E=row["N_E"],
                N_test=row["N_test"],
                mode=row["mode"],
                qdim_after_manin="-" if row["qdim_after_manin"] is None else row["qdim_after_manin"],
                trace_codim_S="-" if row["trace_codim_S"] is None else row["trace_codim_S"],
                qdim_final="-" if row["qdim_final"] is None else row["qdim_final"],
                old_dim_expected_raw="-" if row["old_dim_expected_raw"] is None else row["old_dim_expected_raw"],
                residual_dim="-" if row["residual_dim"] is None else row["residual_dim"],
                old_dim_deficit="-" if row["old_dim_deficit"] is None else row["old_dim_deficit"],
                terminal=row["terminal_kill_stage"] or "-",
                cumulative_hecke_stages=row["cumulative_hecke_stages"],
                source_file=row["source_file"],
            )
        )

    raw_rows = [r for r in rows if r["mode"] == "raw"]
    residual_total = sum(int(r["residual_dim"] or 0) for r in raw_rows)
    deficit_total = sum(int(r["old_dim_deficit"] or 0) for r in raw_rows)
    trace_codim_total = sum(int(r["trace_codim_S"] or 0) for r in rows)
    lines.extend(
        [
            "",
            "## Kurzbefund",
            "",
            f"- Raw-Zeilen: {len(raw_rows)}",
            f"- Summe residual_dim: {residual_total}",
            f"- Summe old_dim_deficit: {deficit_total}",
            f"- Summe trace_codim_S über alle Runs: {trace_codim_total}",
            "- `old_dim_expected_raw` ist nur für raw gesetzt; anc bleibt absichtlich offen.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default="mstar_nomagma_*.json")
    parser.add_argument("--sources", nargs="*", help="Explicit result JSON filenames under _results/.")
    parser.add_argument("--out-json", type=Path, default=RESULTS / f"mstar_metric_extractor_v2_{DATE}.json")
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, files_scanned, files_with_runs = collect_rows(args.pattern, args.sources)
    rows.sort(key=lambda r: (str(r["label"]), int(r["N_test"]), str(r["mode"]), str(r["source_file"])))
    payload = {
        "date": DATE,
        "pattern": args.pattern,
        "files_scanned": files_scanned,
        "files_with_runs": files_with_runs,
        "row_count": len(rows),
        "rows": rows,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md = args.out_md or args.out_json.with_suffix(".md")
    write_markdown(payload, out_md)
    print(args.out_json)
    print(out_md)
    print(f"rows={len(rows)} residual_sum={sum(int(r['residual_dim'] or 0) for r in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
