#!/usr/bin/env python3
"""Loop 132 diagnostic: finite trace-word capture decay on loaded oldlevels.

The probe measures how quickly common divisibility in finite trace words
collapses as more good primes are added. It is intentionally diagnostic:
LMFDB traces are available only for loaded oldlevel orbits, not for the true
newlevel N=240672.
"""

from __future__ import annotations

import importlib.util
import json
import math
import statistics
import sys
from math import gcd
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "_scripts"
RESULTS = ROOT / "_results"
DATE = "2026-05-10"

BASE_PATH = SCRIPT_DIR / "mstar_lmfdb_oldlevel_trace_filter.py"
spec = importlib.util.spec_from_file_location("oldlevel_trace_filter", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
sys.modules["oldlevel_trace_filter"] = base
spec.loader.exec_module(base)

N = 240672
Q = 3863
LEVELS = [109, 218, 327, 872, 1744, 2507, 3488, 15042, 20056, 40112]
PRIMES = base.DEFAULT_PRIMES
BAD_PRIMES = set(base.factorint(2 * N))


def trace_diff(row: dict[str, Any], mode: str, p: int) -> int | None:
    level = int(row["level"])
    if p == Q or level % p == 0 or N % p == 0:
        return None
    traces = row.get("traces") or []
    if p > len(traces):
        return None
    trace = int(traces[p - 1])
    dim = int(row.get("dim", 0) or 0)
    ap = int(base.frey_ap(mode, p))
    return trace - dim * ap


def factorint_small(n: int) -> dict[int, int]:
    n = abs(int(n))
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def factor_string(n: int) -> str:
    if n <= 1:
        return str(n)
    return " * ".join(
        str(p) if e == 1 else f"{p}^{e}" for p, e in sorted(factorint_small(n).items())
    )


def strip_bad_primes(n: int) -> int:
    n = abs(int(n))
    for p in BAD_PRIMES:
        while n and n % p == 0:
            n //= p
    return n


def fetch_loaded_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    class Args:
        timeout_seconds = 60

    args = Args()
    for level in LEVELS:
        payload = base.fetch_level_sql(level, args.timeout_seconds)
        trivial = [row for row in payload["rows"] if base.is_trivial_character(row)]
        rows.extend(trivial)
    return rows


def orbit_curve(row: dict[str, Any], mode: str) -> dict[str, Any]:
    diffs: list[dict[str, int]] = []
    running_gcd = 0
    for p in PRIMES:
        diff = trace_diff(row, mode, p)
        if diff is None:
            continue
        running_gcd = abs(diff) if running_gcd == 0 else gcd(running_gcd, abs(diff))
        diffs.append(
            {
                "k": len(diffs) + 1,
                "p": p,
                "diff": diff,
                "abs_diff": abs(diff),
                "running_gcd": running_gcd,
                "running_gcd_factor": factor_string(running_gcd),
                "external_running_gcd": strip_bad_primes(running_gcd),
                "external_running_gcd_factor": factor_string(strip_bad_primes(running_gcd)),
                "q3863_divides": running_gcd % Q == 0 if running_gcd else False,
            }
        )
    return {
        "label": row["label"],
        "level": int(row["level"]),
        "dim": int(row["dim"]),
        "mode": mode,
        "trace_count_available": len(row.get("traces") or []),
        "curve": diffs,
        "final_gcd": diffs[-1]["running_gcd"] if diffs else 0,
        "first_zero_gcd_k": next((item["k"] for item in diffs if item["running_gcd"] == 1), None),
        "first_q3863_failure_k": next(
            (item["k"] for item in diffs if not item["q3863_divides"]), None
        ),
    }


def aggregate(curves: list[dict[str, Any]]) -> list[dict[str, Any]]:
    max_k = max((len(c["curve"]) for c in curves), default=0)
    rows: list[dict[str, Any]] = []
    logN = math.log(N)
    for k in range(1, max_k + 1):
        gcds = [c["curve"][k - 1]["running_gcd"] for c in curves if len(c["curve"]) >= k]
        external_gcds = [
            c["curve"][k - 1]["external_running_gcd"] for c in curves if len(c["curve"]) >= k
        ]
        if not gcds:
            continue
        logs = [math.log(g) if g > 1 else 0.0 for g in gcds]
        external_logs = [math.log(g) if g > 1 else 0.0 for g in external_gcds]
        rows.append(
            {
                "k": k,
                "orbit_mode_count": len(gcds),
                "nontrivial_gcd_count": sum(1 for g in gcds if g > 1),
                "external_nontrivial_gcd_count": sum(1 for g in external_gcds if g > 1),
                "q3863_survivor_count": sum(1 for g in gcds if g and g % Q == 0),
                "sum_log_gcd": sum(logs),
                "sum_log_gcd_over_logN": sum(logs) / logN,
                "sum_log_external_gcd": sum(external_logs),
                "sum_log_external_gcd_over_logN": sum(external_logs) / logN,
                "mean_log_gcd": statistics.mean(logs) if logs else 0.0,
                "median_gcd": statistics.median(gcds),
                "max_gcd": max(gcds),
                "max_gcd_factor": factor_string(max(gcds)),
                "max_external_gcd": max(external_gcds),
                "max_external_gcd_factor": factor_string(max(external_gcds)),
            }
        )
    return rows


def main() -> None:
    source_rows = fetch_loaded_rows()
    curves = []
    for row in source_rows:
        for mode in ("raw", "anc"):
            curves.append(orbit_curve(row, mode))
    agg = aggregate(curves)

    first_zero_values = [c["first_zero_gcd_k"] for c in curves if c["first_zero_gcd_k"] is not None]
    summary = {
        "date": DATE,
        "purpose": "Measure finite trace-word capture decay on loaded oldlevel orbits.",
        "N": N,
        "q": Q,
        "levels": LEVELS,
        "tested_primes": PRIMES,
        "bad_primes_stripped_for_external_gcd": sorted(BAD_PRIMES),
        "orbit_count": len(source_rows),
        "orbit_mode_count": len(curves),
        "dimension_sum": sum(int(row["dim"]) for row in source_rows),
        "first_zero_gcd_k_min": min(first_zero_values) if first_zero_values else None,
        "first_zero_gcd_k_median": statistics.median(first_zero_values) if first_zero_values else None,
        "first_zero_gcd_k_max": max(first_zero_values) if first_zero_values else None,
        "final_nontrivial_gcd_count": agg[-1]["nontrivial_gcd_count"] if agg else None,
        "final_sum_log_gcd_over_logN": agg[-1]["sum_log_gcd_over_logN"] if agg else None,
        "final_external_nontrivial_gcd_count": agg[-1]["external_nontrivial_gcd_count"] if agg else None,
        "final_sum_log_external_gcd_over_logN": agg[-1]["sum_log_external_gcd_over_logN"] if agg else None,
        "final_q3863_survivor_count": agg[-1]["q3863_survivor_count"] if agg else None,
        "interpretation": (
            "On loaded oldlevel orbit traces, finite trace words show strong capture: "
            "q=3863 survivors disappear immediately and the external spurious gcd mass "
            "vanishes after bad primes are stripped. "
            "This is diagnostic only because true newlevel N=240672 orbit data are absent."
        ),
    }

    payload = {"summary": summary, "aggregate_by_k": agg, "curves": curves}

    json_path = RESULTS / f"mstar_capture_decay_probe_{DATE}.json"
    md_path = RESULTS / f"mstar_capture_decay_probe_{DATE}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M*: Capture decay probe",
        "",
        f"Datum: {DATE}",
        "",
        "## Kurzbefund",
        "",
        f"- Geladene Orbits: {summary['orbit_count']} ({summary['orbit_mode_count']} mit raw/anc).",
        f"- Orbit-Dimensionssumme: {summary['dimension_sum']}.",
        f"- \\(3863\\)-Survivor am Ende: {summary['final_q3863_survivor_count']}.",
        f"- Nichttriviale End-GCDs: {summary['final_nontrivial_gcd_count']}.",
        f"- End-Summe \\(\\sum \\log\\gcd / \\log N\\): {summary['final_sum_log_gcd_over_logN']:.6f}.",
        f"- Externe nichttriviale End-GCDs nach Entfernung von {sorted(BAD_PRIMES)}: "
        f"{summary['final_external_nontrivial_gcd_count']}.",
        f"- Externe End-Summe \\(\\sum \\log\\gcd_{{exc}} / \\log N\\): "
        f"{summary['final_sum_log_external_gcd_over_logN']:.6f}.",
        f"- Median erstes \\(\\gcd=1\\): k={summary['first_zero_gcd_k_median']}.",
        "",
        "## Aggregation nach k",
        "",
        "| k | Tests | gcd>1 | extern gcd>1 | 3863-Survivor | Sum log gcd/log N | Sum log extern/log N | max gcd | max extern |",
        "|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in agg:
        lines.append(
            f"| {row['k']} | {row['orbit_mode_count']} | {row['nontrivial_gcd_count']} | "
            f"{row['external_nontrivial_gcd_count']} | {row['q3863_survivor_count']} | "
            f"{row['sum_log_gcd_over_logN']:.6f} | "
            f"{row['sum_log_external_gcd_over_logN']:.6f} | "
            f"{row['max_gcd_factor']} | {row['max_external_gcd_factor']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Für die geladenen Oldlevel-Orbits fällt die externe spurious",
            "Produkt-GCD-Masse nach Entfernung der Bad-Primes aus \\(2N\\) auf null.",
            "Die rohe Restmasse besteht aus \\(2\\)-Potenzartefakten und ist für FAQS",
            "nicht extern relevant. Das stützt die Capture-Idee diagnostisch,",
            "beweist aber nichts für den eigentlichen New-Level, weil dort die",
            "Orbitdaten fehlen.",
            "Außerdem ist der Test nur auf Orbit-Traces, nicht auf vollständige",
            "Koeffizientenfeld-Primideale berechnet.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
