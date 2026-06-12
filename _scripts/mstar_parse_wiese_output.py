#!/usr/bin/env python3
"""Parse Magma output from the Wiese/Magma handoff scripts.

Usage:
    python _scripts/mstar_parse_wiese_output.py _results/magma_wiese_smoke.log

The parser is deliberately forgiving: it reads key=value output lines emitted
by the Magma handoff and diagnostic scripts, then summarizes killed/surviving
local factors plus diagnostic checkpoints.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


DATE = "2026-05-10"
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")


def parse_bool(value: str) -> bool | str:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    return value


def parse_value(value: str) -> Any:
    value = value.rstrip(",")
    parsed_bool = parse_bool(value)
    if isinstance(parsed_bool, bool):
        return parsed_bool
    try:
        return int(value)
    except ValueError:
        return value


def parse_kv(line: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    matches = list(KV_RE.finditer(line))
    for idx, match in enumerate(matches):
        key = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(line)
        out[key] = parse_value(line[start:end].strip())
    return out


def parse_log(path: Path) -> dict[str, Any]:
    tests: list[dict[str, Any]] = []
    factor_done: list[dict[str, Any]] = []
    wiese_factors: list[dict[str, Any]] = []
    artin_factors: list[dict[str, Any]] = []
    diag_events: list[dict[str, Any]] = []
    level_events: list[dict[str, Any]] = []
    errors: list[str] = []

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line:
            continue
        if line.startswith("TEST "):
            tests.append(parse_kv(line))
        elif line.startswith("FACTOR_DONE "):
            factor_done.append(parse_kv(line))
        elif line.startswith("WIESE_FACTORS "):
            wiese_factors.append({"raw": line, **parse_kv(line)})
        elif line.startswith("ARTIN_LOCAL_FACTORS "):
            artin_factors.append(parse_kv(line))
        elif line.startswith("DIAG_"):
            diag_events.append({"source_line": line, "event": line.split(" ", 1)[0], **parse_kv(line)})
        elif line.startswith("LEVEL_") or line.startswith("WIESE_") or line.startswith("ARTIN_"):
            level_events.append({"raw": line, **parse_kv(line)})
        elif "Runtime error" in line or "User error" in line or ">>" in line:
            errors.append(line)

    by_factor: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for row in factor_done:
        key = (row.get("tag"), row.get("N"), row.get("factor"))
        by_factor[key] = row

    survivors = [
        row
        for row in factor_done
        if row.get("survives_raw") is True or row.get("survives_anc") is True
    ]
    killed = [
        row
        for row in factor_done
        if row.get("survives_raw") is False and row.get("survives_anc") is False
    ]

    by_level: dict[str, dict[str, int]] = defaultdict(lambda: {"factors": 0, "survivors": 0, "killed": 0})
    for row in factor_done:
        level = str(row.get("N"))
        by_level[level]["factors"] += 1
        if row in survivors:
            by_level[level]["survivors"] += 1
        if row in killed:
            by_level[level]["killed"] += 1

    diag_done = any(row.get("event") == "DIAG_DONE" and row.get("ok") is True for row in diag_events)
    diag_fail = any(row.get("ok") is False for row in diag_events)

    return {
        "date": DATE,
        "log_path": str(path),
        "summary": {
            "diagnostic_rows": len(diag_events),
            "diagnostic_done": diag_done,
            "diagnostic_fail": diag_fail,
            "test_rows": len(tests),
            "factor_done_rows": len(factor_done),
            "survivor_count": len(survivors),
            "killed_factor_count": len(killed),
            "error_count": len(errors),
            "levels": dict(by_level),
        },
        "wiese_factors": wiese_factors,
        "artin_factors": artin_factors,
        "diagnostics": diag_events,
        "tests": tests,
        "factor_done": factor_done,
        "survivors": survivors,
        "errors": errors,
        "level_events_tail": level_events[-40:],
    }


def write_markdown(payload: dict[str, Any], md_out: Path) -> None:
    lines: list[str] = []
    lines.append("# Wiese/Magma-Handoff Parse")
    lines.append("")
    lines.append(f"Log: `{payload['log_path']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = payload["summary"]
    lines.append(f"- Diagnostic rows: {summary['diagnostic_rows']}")
    lines.append(f"- Diagnostic done: {summary['diagnostic_done']}")
    lines.append(f"- Diagnostic fail marker: {summary['diagnostic_fail']}")
    lines.append(f"- Test rows: {summary['test_rows']}")
    lines.append(f"- Factor rows: {summary['factor_done_rows']}")
    lines.append(f"- Survivors: {summary['survivor_count']}")
    lines.append(f"- Fully killed factors: {summary['killed_factor_count']}")
    lines.append(f"- Error lines: {summary['error_count']}")
    lines.append("")
    if payload["diagnostics"]:
        lines.append("## Diagnostics")
        lines.append("")
        lines.append("| Event | Key data |")
        lines.append("|---|---|")
        for row in payload["diagnostics"]:
            key_data = ", ".join(
                f"{key}={value}"
                for key, value in row.items()
                if key not in {"source_line", "event"}
            )
            lines.append(f"| {row.get('event')} | `{key_data}` |")
        lines.append("")
    if payload["wiese_factors"] or payload["artin_factors"]:
        lines.append("## Factor Discovery")
        lines.append("")
        if payload["wiese_factors"]:
            lines.append("| Source | Level | Count | Dims | Generators |")
            lines.append("|---|---:|---:|---|---|")
            for row in payload["wiese_factors"]:
                lines.append(
                    f"| Wiese | {row.get('N')} | {row.get('count')} | "
                    f"`{row.get('dims')}` | `{row.get('generators')}` |"
                )
            lines.append("")
        if payload["artin_factors"]:
            lines.append("| Source | Level | Count |")
            lines.append("|---|---:|---:|")
            for row in payload["artin_factors"]:
                lines.append(f"| Artin | {row.get('N')} | {row.get('count')} |")
            lines.append("")
    lines.append("## Levels")
    lines.append("")
    if summary["levels"]:
        lines.append("| Level | Factors | Killed | Survivors |")
        lines.append("|---:|---:|---:|---:|")
        for level, row in sorted(summary["levels"].items(), key=lambda item: int(item[0])):
            lines.append(f"| {level} | {row['factors']} | {row['killed']} | {row['survivors']} |")
    else:
        lines.append("Keine `FACTOR_DONE`-Zeilen im Log.")
    lines.append("")
    lines.append("## Survivors")
    lines.append("")
    if payload["survivors"]:
        lines.append("| Tag | Level | Factor | Dim | Raw | ANC |")
        lines.append("|---|---:|---:|---:|---|---|")
        for row in payload["survivors"]:
            lines.append(
                f"| {row.get('tag')} | {row.get('N')} | {row.get('factor')} | "
                f"{row.get('dim')} | {row.get('survives_raw')} | {row.get('survives_anc')} |"
            )
    else:
        lines.append("Keine Survivor in den geparsten `FACTOR_DONE`-Zeilen.")
    lines.append("")
    if payload["errors"]:
        lines.append("## Errors")
        lines.append("")
        for err in payload["errors"][:40]:
            lines.append(f"- `{err}`")
        lines.append("")
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    payload = parse_log(args.logfile)
    stem = args.logfile.with_suffix("")
    json_out = args.json_out or stem.with_name(stem.name + "_parsed.json")
    md_out = args.md_out or stem.with_name(stem.name + "_parsed.md")
    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, md_out)
    print(json_out)
    print(md_out)


if __name__ == "__main__":
    main()
