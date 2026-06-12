"""Budget check for Frey local-type filters in the M-G* projector route.

This script estimates how much a rational local-type filter such as an
Atkin-Lehner sign profile can shrink the ambient newspace before one tries to
build a Hecke idempotent.  It is deliberately conservative: it grants the
maximum possible factor 2^omega(N) from specifying all local signs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "_data" / "anc_hecke_length_budget_2026-05-09.json"
OUTPUT = ROOT / "_data" / "mg_local_type_filter_budget_2026-05-09.json"


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


def gamma0_index(n: int, primes: list[int]) -> float:
    value = float(n)
    for p in primes:
        value *= 1.0 + 1.0 / p
    return value


def row_budget(row: dict) -> dict:
    n_cond = int(row["n_cond"])
    primes = prime_factors(n_cond)
    omega = len(primes)
    log_n = math.log(n_cond)
    index = gamma0_index(n_cond, primes)
    dim_heuristic = index / 12.0
    sign_cells = 2**omega
    filtered_dim_heuristic = dim_heuristic / sign_cells
    log_sign_saving = omega * math.log(2.0)
    return {
        "label": row["label"],
        "n_cond": n_cond,
        "quality": row.get("quality"),
        "omega_n": omega,
        "bad_primes": primes,
        "gamma0_index_heuristic": index,
        "newspace_dimension_heuristic": dim_heuristic,
        "max_atkin_lehner_cells": sign_cells,
        "filtered_dimension_heuristic": filtered_dim_heuristic,
        "log_sign_saving": log_sign_saving,
        "relative_log_saving_vs_log_n": log_sign_saving / log_n if log_n else 0.0,
        "filtered_dimension_power_of_n": (
            math.log(max(filtered_dim_heuristic, 1.0)) / log_n if log_n else 0.0
        ),
    }


def first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % p for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 1
    return primes


def synthetic_primorial_rows() -> list[dict]:
    rows: list[dict] = []
    for omega in [4, 8, 12, 16, 24, 32]:
        primes = first_primes(omega)
        n = 1
        for p in primes:
            n *= p
        index = gamma0_index(n, primes)
        dim = index / 12.0
        sign_cells = 2**omega
        filtered = dim / sign_cells
        log_n = math.log(n)
        rows.append(
            {
                "omega_n": omega,
                "n_primorial": n,
                "log_n": log_n,
                "log_sign_saving": omega * math.log(2.0),
                "relative_log_saving_vs_log_n": omega * math.log(2.0) / log_n,
                "filtered_dimension_power_of_n": math.log(filtered) / log_n,
                "filtered_dimension_heuristic": filtered,
            }
        )
    return rows


def main() -> None:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row_budget(row) for row in source["em1_by_quality"]]

    rel = [r["relative_log_saving_vs_log_n"] for r in rows]
    powers = [r["filtered_dimension_power_of_n"] for r in rows]
    result = {
        "date": "2026-05-09",
        "purpose": "Quantify how far Frey local-type filters can reduce the M-G* projector problem.",
        "interpretation": {
            "atkin_lehner_signs": "Specifying all local signs gives at most a 2^omega(N) rational decomposition factor.",
            "full_2_torsion_mod2": "The mod-2 Eisenstein condition is universal for full rational 2-torsion and is a congruence condition, not a rational Hecke idempotent decomposition.",
            "steinberg_type": "At squarefree odd conductor, Steinberg type is already built into the newspace of exact level N.",
        },
        "summary": {
            "row_count": len(rows),
            "max_relative_log_saving_vs_log_n": max(rel),
            "median_relative_log_saving_vs_log_n": sorted(rel)[len(rel) // 2],
            "min_filtered_dimension_power_of_n": min(powers),
            "median_filtered_dimension_power_of_n": sorted(powers)[len(powers) // 2],
            "conclusion": "Local sign/type filters save only 2^omega(N)=N^o(1) asymptotically; they do not make a full Hecke interpolation projector small enough.",
        },
        "em1_by_quality": rows,
        "synthetic_primorial_stress": synthetic_primorial_rows(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
