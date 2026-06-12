#!/usr/bin/env python3
"""Extract kill_depth values from mstar_nomagma_*.json result files.

A kill_depth is the largest batch number X such that
"T_<p>_minus_<a>_batch_X" appears AND has killed=True OR quotient_dim=0
in the stages list of a run.

Output: a CSV/MD table with one row per (level, mode, sign, operator).

Usage:
    python _scripts/mstar_killdepth_extract.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"
DATE = "2026-05-15"

STAGE_RE_BATCH = re.compile(r"T_(\d+)_minus_(-?\d+)_batch_(\d+)")
STAGE_RE_SIMPLE = re.compile(r"T_(\d+)_minus_(-?\d+)$")


def parse_stage(stage_name):
    m = STAGE_RE_BATCH.match(stage_name)
    if m:
        p, a, batch = m.groups()
        return int(p), int(a), int(batch)
    m = STAGE_RE_SIMPLE.match(stage_name)
    if m:
        p, a = m.groups()
        return int(p), int(a), 1  # treat single-stage as batch=1
    return None


def extract_runs(payload):
    """Yield (level, mode, sign, operator, kill_depth) tuples from one JSON payload."""
    if not isinstance(payload, dict):
        return
    runs = payload.get("runs") or [payload]
    if isinstance(runs, dict):
        runs = [runs]
    for run in runs:
        if not isinstance(run, dict):
            continue
        level = run.get("level")
        mode = run.get("mode")
        sign = run.get("sign")
        stages = run.get("stages") or []
        last_killed = {}
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            stage_name = stage.get("stage", "")
            parsed = parse_stage(stage_name)
            if parsed is None:
                continue
            p, a, batch = parsed
            killed = stage.get("killed", False) or stage.get("quotient_dim") == 0
            key = (p, a)
            if killed:
                # First batch that killed is the kill_depth for this op
                if key not in last_killed:
                    last_killed[key] = batch
        for (p, a), batch in last_killed.items():
            yield {
                "level": level,
                "mode": mode,
                "sign": sign,
                "operator": f"T_{p}-{a}",
                "p": p,
                "a": a,
                "kill_depth": batch,
            }


def main():
    rows = []
    files_scanned = 0
    files_with_runs = 0
    for json_path in sorted(RESULTS.glob("mstar_nomagma_*.json")):
        files_scanned += 1
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Skip {json_path.name}: {e}")
            continue
        before = len(rows)
        for row in extract_runs(payload):
            row["source_file"] = json_path.name
            rows.append(row)
        if len(rows) > before:
            files_with_runs += 1

    # Deduplicate: same (level, mode, sign, operator) -> take max kill_depth
    dedup = {}
    for row in rows:
        key = (row["level"], row["mode"], row["sign"], row["operator"])
        if key not in dedup or row["kill_depth"] > dedup[key]["kill_depth"]:
            dedup[key] = row

    sorted_rows = sorted(
        dedup.values(),
        key=lambda r: (r["level"] or 0, str(r["mode"] or ""), str(r["sign"]), r["p"]),
    )

    # Write JSON
    out_json = RESULTS / f"mstar_killdepth_table_{DATE}.json"
    out_json.write_text(
        json.dumps(
            {
                "date": DATE,
                "files_scanned": files_scanned,
                "files_with_runs": files_with_runs,
                "row_count": len(sorted_rows),
                "rows": sorted_rows,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    # Write MD
    md_lines = [
        f"# kill_depth Datentabelle (Loop 227)",
        "",
        f"Datum: {DATE}",
        f"Files gescannt: {files_scanned}",
        f"Files mit Runs: {files_with_runs}",
        f"Eindeutige Eintraege: {len(sorted_rows)}",
        "",
        "## Tabelle",
        "",
        "| Level | Mode | Sign | Operator | kill_depth | Source |",
        "|-------|------|------|----------|-----------|--------|",
    ]
    for r in sorted_rows:
        md_lines.append(
            f"| {r['level']} | {r['mode']} | {r['sign']} | {r['operator']} | "
            f"{r['kill_depth']} | {r['source_file']} |"
        )
    md_lines.extend([
        "",
        "## Zusammenfassung pro Level",
        "",
        "| Level | log(N) | T_5-2 raw | T_5-2 anc | Andere Operatoren |",
        "|-------|--------|-----------|-----------|---------------------|",
    ])

    import math
    levels = sorted({r["level"] for r in sorted_rows if r["level"] is not None})
    for lvl in levels:
        log_lvl = round(math.log(lvl), 2)
        t5_raw = next(
            (r["kill_depth"] for r in sorted_rows
             if r["level"] == lvl and r["mode"] == "raw" and r["operator"] == "T_5-2"),
            None,
        )
        t5_anc = next(
            (r["kill_depth"] for r in sorted_rows
             if r["level"] == lvl and r["mode"] == "anc" and r["operator"] == "T_5-2"),
            None,
        )
        others = [
            f"{r['mode']}/{r['operator']}={r['kill_depth']}"
            for r in sorted_rows
            if r["level"] == lvl and r["operator"] != "T_5-2"
        ]
        md_lines.append(
            f"| {lvl} | {log_lvl} | {t5_raw or '-'} | {t5_anc or '-'} | "
            f"{', '.join(others) if others else '-'} |"
        )

    out_md = RESULTS / f"mstar_killdepth_table_{DATE}.md"
    out_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Files scanned: {files_scanned}")
    print(f"Files with runs: {files_with_runs}")
    print(f"Unique entries: {len(sorted_rows)}")
    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
