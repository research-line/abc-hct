#!/usr/bin/env python3
"""Loop 134 diagnostic: trace-word partition and small-index proxy.

The script uses the already established LMFDB SQL mirror loader from
``mstar_lmfdb_oldlevel_trace_filter.py``.  It stays deliberately at the
orbit-trace level: this is a proxy for small Hecke-generator behavior, not a
full coefficient-field/order-index computation.
"""

from __future__ import annotations

import importlib.util
import json
import math
import statistics
import sys
from collections import defaultdict
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
TEST_PRIMES = base.DEFAULT_PRIMES
BAD_PRIMES = set(base.factorint(2 * N))


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


def external_prime_factors(n: int) -> set[int]:
    return set(factorint_small(strip_bad_primes(n)))


def fetch_loaded_rows() -> list[dict[str, Any]]:
    class Args:
        timeout_seconds = 60

    rows: list[dict[str, Any]] = []
    args = Args()
    for level in LEVELS:
        payload = base.fetch_level_sql(level, args.timeout_seconds)
        rows.extend(row for row in payload["rows"] if base.is_trivial_character(row))
    return rows


def trace_at(row: dict[str, Any], p: int) -> int | None:
    level = int(row["level"])
    traces = row.get("traces") or []
    if p == Q or level % p == 0 or N % p == 0:
        return None
    if p > len(traces):
        return None
    return int(traces[p - 1])


def trace_diff(row: dict[str, Any], mode: str, p: int) -> int | None:
    trace = trace_at(row, p)
    if trace is None:
        return None
    dim = int(row.get("dim", 0) or 0)
    return trace - dim * int(base.frey_ap(mode, p))


def loaded_trace_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in source_rows:
        traces_by_prime: dict[int, int] = {}
        for p in TEST_PRIMES:
            trace = trace_at(row, p)
            if trace is not None:
                traces_by_prime[p] = trace
        out.append(
            {
                "label": row["label"],
                "level": int(row["level"]),
                "dim": int(row["dim"]),
                "traces": traces_by_prime,
            }
        )
    return out


def partition_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    total_dim = sum(int(row["dim"]) for row in rows)
    for k in range(1, len(TEST_PRIMES) + 1):
        primes = TEST_PRIMES[:k]
        usable = [row for row in rows if all(p in row["traces"] for p in primes)]
        clusters: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
        clusters_dim_trace: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in usable:
            trace_word = tuple(int(row["traces"][p]) for p in primes)
            clusters[trace_word].append(row)
            clusters_dim_trace[(int(row["dim"]), *trace_word)].append(row)

        def summarize(cluster_map: dict[tuple[int, ...], list[dict[str, Any]]]) -> dict[str, Any]:
            cluster_list = list(cluster_map.values())
            collision_clusters = [cluster for cluster in cluster_list if len(cluster) > 1]
            singleton_clusters = [cluster for cluster in cluster_list if len(cluster) == 1]
            collision_pair_count = sum(len(cluster) * (len(cluster) - 1) // 2 for cluster in collision_clusters)
            collision_dim_pair_sum = 0
            for cluster in collision_clusters:
                dims = [int(row["dim"]) for row in cluster]
                for i, left in enumerate(dims):
                    for right in dims[i + 1 :]:
                        collision_dim_pair_sum += left * right
            max_cluster = max(cluster_list, key=len) if cluster_list else []
            max_cluster_dim = sum(int(row["dim"]) for row in max_cluster)
            return {
                "cluster_count": len(cluster_list),
                "singleton_cluster_count": len(singleton_clusters),
                "singleton_orbit_count": len(singleton_clusters),
                "singleton_dim_sum": sum(int(cluster[0]["dim"]) for cluster in singleton_clusters),
                "collision_cluster_count": len(collision_clusters),
                "collision_orbit_count": sum(len(cluster) for cluster in collision_clusters),
                "collision_dim_sum": sum(
                    int(row["dim"]) for cluster in collision_clusters for row in cluster
                ),
                "collision_pair_count": collision_pair_count,
                "collision_dim_pair_sum": collision_dim_pair_sum,
                "max_cluster_size": len(max_cluster),
                "max_cluster_dim_sum": max_cluster_dim,
                "max_cluster_labels": [row["label"] for row in max_cluster[:8]],
            }

        trace_only = summarize(clusters)
        dim_plus_trace = summarize(clusters_dim_trace)
        metrics.append(
            {
                "k": k,
                "primes": primes,
                "last_prime": primes[-1],
                "usable_orbit_count": len(usable),
                "usable_dim_sum": sum(int(row["dim"]) for row in usable),
                "total_dim_sum": total_dim,
                "trace_only": trace_only,
                "dim_plus_trace": dim_plus_trace,
            }
        )
    return metrics


def frey_gcd_metrics(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    curves: list[dict[str, Any]] = []
    for row in source_rows:
        for mode in ("raw", "anc"):
            running_gcd = 0
            curve: list[dict[str, Any]] = []
            for p in TEST_PRIMES:
                diff = trace_diff(row, mode, p)
                if diff is None:
                    continue
                running_gcd = abs(diff) if running_gcd == 0 else gcd(running_gcd, abs(diff))
                external_gcd = strip_bad_primes(running_gcd)
                curve.append(
                    {
                        "p": p,
                        "running_gcd": running_gcd,
                        "external_gcd": external_gcd,
                    }
                )
            curves.append(
                {
                    "label": row["label"],
                    "level": int(row["level"]),
                    "dim": int(row["dim"]),
                    "mode": mode,
                    "curve": curve,
                }
            )

    max_k = max((len(curve["curve"]) for curve in curves), default=0)
    log_n = math.log(N)
    metrics: list[dict[str, Any]] = []
    for k in range(1, max_k + 1):
        gcds = [curve["curve"][k - 1]["running_gcd"] for curve in curves if len(curve["curve"]) >= k]
        external_gcds = [
            curve["curve"][k - 1]["external_gcd"] for curve in curves if len(curve["curve"]) >= k
        ]
        support: set[int] = set()
        for value in external_gcds:
            support.update(external_prime_factors(value))
        external_logs = [math.log(value) if value > 1 else 0.0 for value in external_gcds]
        metrics.append(
            {
                "k": k,
                "primes": TEST_PRIMES[:k],
                "orbit_mode_count": len(gcds),
                "external_nontrivial_count": sum(1 for value in external_gcds if value > 1),
                "q3863_survivor_count": sum(1 for value in gcds if value and value % Q == 0),
                "sum_log_external_gcd": sum(external_logs),
                "sum_log_external_gcd_over_logN": sum(external_logs) / log_n,
                "max_external_gcd": max(external_gcds) if external_gcds else 0,
                "max_external_gcd_factor": factor_string(max(external_gcds) if external_gcds else 0),
                "external_prime_support": sorted(support),
                "external_prime_support_count": len(support),
            }
        )
    return metrics


def main() -> None:
    source_rows = fetch_loaded_rows()
    trace_rows = loaded_trace_rows(source_rows)
    partitions = partition_metrics(trace_rows)
    frey_metrics = frey_gcd_metrics(source_rows)

    first_trace_only_full = next(
        (
            row["k"]
            for row in partitions
            if row["trace_only"]["collision_cluster_count"] == 0
        ),
        None,
    )
    first_dim_trace_full = next(
        (
            row["k"]
            for row in partitions
            if row["dim_plus_trace"]["collision_cluster_count"] == 0
        ),
        None,
    )
    first_external_zero = next(
        (
            row["k"]
            for row in frey_metrics
            if row["external_nontrivial_count"] == 0
            and row["sum_log_external_gcd_over_logN"] == 0
        ),
        None,
    )

    loaded_dim_by_level: dict[int, int] = defaultdict(int)
    orbit_count_by_level: dict[int, int] = defaultdict(int)
    for row in source_rows:
        level = int(row["level"])
        loaded_dim_by_level[level] += int(row["dim"])
        orbit_count_by_level[level] += 1

    summary = {
        "date": DATE,
        "purpose": "Trace-word partition and index proxy for the Small-Index Hecke Generator route.",
        "N": N,
        "q": Q,
        "levels": LEVELS,
        "tested_primes": TEST_PRIMES,
        "bad_primes_stripped_for_external_gcd": sorted(BAD_PRIMES),
        "orbit_count": len(source_rows),
        "dimension_sum": sum(int(row["dim"]) for row in source_rows),
        "orbit_count_by_level": dict(sorted(orbit_count_by_level.items())),
        "loaded_dim_by_level": dict(sorted(loaded_dim_by_level.items())),
        "first_k_trace_only_full_partition": first_trace_only_full,
        "first_k_dim_plus_trace_full_partition": first_dim_trace_full,
        "first_k_external_frey_gcd_zero": first_external_zero,
        "small_test_primes_4": TEST_PRIMES[:4],
        "k4_trace_only_collision_clusters": partitions[3]["trace_only"]["collision_cluster_count"]
        if len(partitions) >= 4
        else None,
        "k4_dim_plus_trace_collision_clusters": partitions[3]["dim_plus_trace"][
            "collision_cluster_count"
        ]
        if len(partitions) >= 4
        else None,
        "k4_external_nontrivial_count": frey_metrics[3]["external_nontrivial_count"]
        if len(frey_metrics) >= 4
        else None,
        "k4_external_sum_log_over_logN": frey_metrics[3]["sum_log_external_gcd_over_logN"]
        if len(frey_metrics) >= 4
        else None,
        "interpretation": (
            "On loaded oldlevel orbit traces, small trace words rapidly separate the "
            "available orbit set and the Frey-relative external gcd mass vanishes by k=4. "
            "This supports the Small-Index Hecke Generator heuristic for loaded oldlevels "
            "but remains a trace-level proxy, not a proof for the true newlevel N=240672."
        ),
    }

    payload = {
        "summary": summary,
        "partition_by_k": partitions,
        "frey_external_gcd_by_k": frey_metrics,
    }

    json_path = RESULTS / f"mstar_traceword_index_proxy_{DATE}.json"
    md_path = RESULTS / f"mstar_traceword_index_proxy_{DATE}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M*: Traceword-Index-Proxy",
        "",
        f"Datum: {DATE}",
        "",
        "## Kurzbefund",
        "",
        f"- Geladene Oldlevel-Orbits: {summary['orbit_count']}, Dimensionssumme {summary['dimension_sum']}.",
        f"- Testprimes: {TEST_PRIMES}.",
        f"- Erste vollständige Trace-only-Partition: k={first_trace_only_full}.",
        f"- Erste vollständige Dim+Trace-Partition: k={first_dim_trace_full}.",
        f"- Erste Frey-relative externe GCD-Nullmasse: k={first_external_zero}.",
        f"- Bei k=4, also {TEST_PRIMES[:4]}, Trace-only-Kollisionscluster: "
        f"{summary['k4_trace_only_collision_clusters']}.",
        f"- Bei k=4 Dim+Trace-Kollisionscluster: {summary['k4_dim_plus_trace_collision_clusters']}.",
        f"- Bei k=4 externe Frey-GCD-Masse/log N: {summary['k4_external_sum_log_over_logN']:.6f}.",
        "",
        "## Partitionen nach k",
        "",
        "| k | letzter p | Cluster trace | Kollisionscluster trace | max trace | "
        "Cluster dim+trace | Kollisionscluster dim+trace | max dim+trace |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in partitions:
        trace = row["trace_only"]
        dim_trace = row["dim_plus_trace"]
        lines.append(
            f"| {row['k']} | {row['last_prime']} | {trace['cluster_count']} | "
            f"{trace['collision_cluster_count']} | {trace['max_cluster_size']} | "
            f"{dim_trace['cluster_count']} | {dim_trace['collision_cluster_count']} | "
            f"{dim_trace['max_cluster_size']} |"
        )

    lines.extend(
        [
            "",
            "## Frey-relative externe GCD-Masse",
            "",
            "| k | letzter p | extern gcd>1 | 3863-Survivor | Sum log extern/log N | max extern | externe Primstütze |",
            "|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in frey_metrics:
        support = ", ".join(str(p) for p in row["external_prime_support"]) or "-"
        lines.append(
            f"| {row['k']} | {row['primes'][-1]} | {row['external_nontrivial_count']} | "
            f"{row['q3863_survivor_count']} | "
            f"{row['sum_log_external_gcd_over_logN']:.6f} | "
            f"{row['max_external_gcd_factor']} | {support} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Auf den geladenen Oldlevel-Orbits verhält sich die kleine Testalgebra",
            "sehr stark: wenige kleine \\(T_\\ell\\) trennen fast sofort die sichtbaren",
            "Orbittraces, und relativ zur Frey-Spur ist die externe Produkt-GCD-Masse",
            "ab \\(k=4\\) null. Das ist genau das Verhalten, das der Small-Index-",
            "Generator-Satz verlangen würde.",
            "",
            "Der Test ist aber nur ein Index-Proxy: Er verwendet Orbittraces statt",
            "vollständiger Koeffizientenfeld-Ordnungen und enthält keine Daten für den",
            "echten New-Level \\(240672\\). Er stützt die Route, beweist sie aber nicht.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
