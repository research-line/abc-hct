"""Loop 109 scale check for standard Hecke trace/resultant sieves.

The goal is not to compute exact congruence ideals.  It quantifies the size of
the trivial determinant bounds one gets from testing T_p-a_p(E) on large
new/old spaces.  If the bound is already many times log(N), the route cannot
prove HOS-excess without a new Frey-specific integrality/repulsion input.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_trace_sieve_scale_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_trace_sieve_scale_{DATE}.md"

N = 240672
LOG_N = math.log(N)

GOOD_PRIMES = [5, 7, 11, 13, 17, 19, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
LEVEL_DIMS = {
    109: 8,
    218: 10,
    327: 19,
    872: 27,
    1744: 54,
    2507: 199,
    3488: 108,
    15042: 397,
    20056: 594,
    40112: 1188,
    60168: 1188,
    80224: 2376,
    120336: 2376,
}
FULL_LEVEL = {
    "new_dim": 4752,
    "old_dim": 37457,
    "total_dim": 42209,
}


def determinant_log_bound(dim: int, primes: list[int]) -> float:
    # Deligne gives |a_p(g)-a_p(E)| <= 4 sqrt(p) for good p.
    # A crude determinant bound is therefore dim * sum log(4 sqrt(p)).
    return dim * sum(math.log(4.0 * math.sqrt(p)) for p in primes)


def row(name: str, dim: int) -> dict[str, object]:
    bound = determinant_log_bound(dim, GOOD_PRIMES)
    return {
        "name": name,
        "dimension": dim,
        "prime_count": len(GOOD_PRIMES),
        "log_bound": bound,
        "bound_over_logN": bound / LOG_N,
        "bound_over_2logN": bound / (2 * LOG_N),
    }


def main() -> None:
    level_rows = [row(str(level), dim) for level, dim in LEVEL_DIMS.items()]
    aggregate_loaded = row("loaded_oldlevel_sum", sum(LEVEL_DIMS.values()))
    full_rows = [
        row("level_240672_new", FULL_LEVEL["new_dim"]),
        row("level_240672_old", FULL_LEVEL["old_dim"]),
        row("level_240672_total", FULL_LEVEL["total_dim"]),
    ]
    payload = {
        "date": DATE,
        "purpose": "Scale obstruction for standard trace/resultant determinant bounds in HOS-excess.",
        "N": N,
        "logN": LOG_N,
        "target_2logN": 2 * LOG_N,
        "tested_primes": GOOD_PRIMES,
        "formula": "dim * sum_{p in P} log(4*sqrt(p))",
        "interpretation": "This is a crude upper bound for determinant/resultant mass, not an exact congruence computation.",
        "level_rows": level_rows,
        "aggregate_loaded": aggregate_loaded,
        "full_level_rows": full_rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Trace-Sieve Scale Check",
        "",
        f"N = {N}, log N = {LOG_N:.6f}, target 2 log N = {2 * LOG_N:.6f}",
        "",
        "Crude determinant bound:",
        "",
        "\\[",
        "\\log |\\det(T_p-a_p(E))| \\le d\\log(4\\sqrt p).",
        "\\]",
        "",
        "For several primes, multiply/add these bounds. This is deliberately crude:",
        "it measures why ordinary determinant/resultant estimates are too large.",
        "",
        "## Oldlevel Rows",
        "",
        "| Space | dim | bound/logN | bound/(2logN) |",
        "|---:|---:|---:|---:|",
    ]
    for item in level_rows:
        lines.append(
            f"| {item['name']} | {item['dimension']} | "
            f"{float(item['bound_over_logN']):.2f} | {float(item['bound_over_2logN']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Aggregate / Full Level",
            "",
            "| Space | dim | bound/logN | bound/(2logN) |",
            "|---:|---:|---:|---:|",
        ]
    )
    for item in [aggregate_loaded, *full_rows]:
        lines.append(
            f"| {item['name']} | {item['dimension']} | "
            f"{float(item['bound_over_logN']):.2f} | {float(item['bound_over_2logN']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Ordinary trace/resultant determinant bounds scale with the ambient dimension.",
            "They are therefore many orders above the HOS-excess target. A proof needs",
            "a Frey-specific integral repulsion or sparsity theorem, not just effective",
            "multiplicity one or a small-prime trace sieve.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps({"aggregate": aggregate_loaded, "full": full_rows}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
