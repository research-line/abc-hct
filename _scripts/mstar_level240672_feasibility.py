"""Loop 96 feasibility probe for a level-240672 mod-3863 Hecke test.

The script intentionally avoids building the full modular-symbol Hecke module
unless a small timed smoke test succeeds.  It records dimension data, Sturm
bound scale, old-level structure, and the practical size of a direct
mod-3863 projector computation.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from sage.all import divisors, euler_phi, factor, kronecker_symbol, prime_divisors, prime_range


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_level240672_feasibility_{DATE}.json"

N = 240_672
Q = 3863
WEIGHT = 2


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def safe_int(value: Any) -> int:
    return int(value)


def index_gamma0(level: int) -> int:
    out = level
    for p in prime_divisors(level):
        out = out * (int(p) + 1) // int(p)
    return int(out)


def cusp_count(level: int) -> int:
    total = 0
    for d in divisors(level):
        d = int(d)
        total += int(euler_phi(math.gcd(d, level // d)))
    return total


def elliptic_order2_count(level: int) -> int:
    if level % 4 == 0:
        return 0
    out = 1
    for p in prime_divisors(level):
        out *= 1 + int(kronecker_symbol(-4, int(p)))
    return int(out)


def elliptic_order3_count(level: int) -> int:
    if level % 9 == 0:
        return 0
    out = 1
    for p in prime_divisors(level):
        out *= 1 + int(kronecker_symbol(-3, int(p)))
    return int(out)


def genus_x0(level: int) -> int:
    mu = index_gamma0(level)
    c = cusp_count(level)
    e2 = elliptic_order2_count(level)
    e3 = elliptic_order3_count(level)
    genus = Fraction(1, 1) + Fraction(mu, 12) - Fraction(e2, 4) - Fraction(e3, 3) - Fraction(c, 2)
    return int(genus)


def num_divisors(n: int) -> int:
    out = 1
    for _p, e in factor(n):
        out *= int(e) + 1
    return out


def new_dimensions_for_divisors(level: int) -> dict[int, int]:
    new_dim: dict[int, int] = {}
    for d in sorted(int(x) for x in divisors(level)):
        total = genus_x0(d)
        old = 0
        for m, dim_new in new_dim.items():
            if m < d and d % m == 0:
                old += num_divisors(d // m) * dim_new
        new_dim[d] = total - old
    return new_dim


def gamma0_dimension_data(level: int) -> dict[str, Any]:
    idx = index_gamma0(level)
    genus = genus_x0(level)
    new_dim = NEW_DIMS.get(level)
    out: dict[str, Any] = {
        "level": level,
        "factor": factor_string(level),
        "index": idx,
        "sturm_bound_weight2": safe_int(math.floor(WEIGHT * idx / 12)),
        "prime_factors": [int(p) for p in prime_divisors(level)],
        "cusps": cusp_count(level),
        "elliptic_order2_points": elliptic_order2_count(level),
        "elliptic_order3_points": elliptic_order3_count(level),
        "genus": genus,
        "dimension_cusp_forms": genus,
        "dimension_new_cusp_forms": new_dim,
        "dimension_old_cusp_forms": None if new_dim is None else genus - new_dim,
    }
    return out


def old_level_table(level: int) -> list[dict[str, Any]]:
    rows = []
    for d in divisors(level):
        d = int(d)
        if d == level:
            continue
        if level % d:
            continue
        row = gamma0_dimension_data(d)
        ratio = level // d
        row["level_ratio_N_over_M"] = ratio
        row["degeneracy_multiplicity_tau_N_over_M"] = num_divisors(ratio)
        if isinstance(row.get("dimension_new_cusp_forms"), int):
            row["oldspace_contribution_at_N"] = row["dimension_new_cusp_forms"] * row["degeneracy_multiplicity_tau_N_over_M"]
        else:
            row["oldspace_contribution_at_N"] = None
        rows.append(row)
    rows.sort(key=lambda item: int(item.get("oldspace_contribution_at_N", 0) or 0), reverse=True)
    return rows


NEW_DIMS = new_dimensions_for_divisors(N)


def main() -> None:
    main_level = gamma0_dimension_data(N)
    old_levels = old_level_table(N)
    sturm = int(main_level["sturm_bound_weight2"])
    good_primes_to_sturm = [int(p) for p in prime_range(2, sturm + 1) if N % int(p) != 0]
    hasse_unique_limit = (Q / 4.0) ** 2

    payload = {
        "date": DATE,
        "purpose": "Feasibility probe for a full level-240672 Hecke/modular-symbol test modulo 3863.",
        "level": N,
        "q": Q,
        "main_level": main_level,
        "divisor_count": len(divisors(N)),
        "proper_old_level_count": len(old_levels),
        "old_levels_top_by_new_dimension": old_levels[:20],
        "old_levels_with_positive_new_dimension_count": sum(
            1 for row in old_levels if isinstance(row.get("dimension_new_cusp_forms"), int) and row["dimension_new_cusp_forms"] > 0
        ),
        "sturm_trace_scale": {
            "sturm_bound_weight2": sturm,
            "good_primes_up_to_sturm": len(good_primes_to_sturm),
            "first_good_primes": good_primes_to_sturm[:20],
            "last_good_prime_to_sturm": good_primes_to_sturm[-1] if good_primes_to_sturm else None,
            "hasse_abs_trace_difference_lt_q_for_p_less_than": hasse_unique_limit,
            "sturm_bound_below_hasse_unique_limit": sturm < hasse_unique_limit,
            "meaning": (
                "For p below (q/4)^2, congruence of two rational elliptic trace sequences mod q "
                "forces integer equality at that p by Hasse bounds. This does not identify "
                "non-rational higher-dimensional factors."
            ),
        },
        "timed_modular_symbols_smoke_tests": [
            {
                "status": "skipped",
                "reason": "The first version of this script timed out under an outer 240s timeout before producing JSON; direct ModularSymbols construction is deferred.",
            }
        ],
        "interpretation": {
            "direct_full_projector_risk": (
                "A direct mod-q Hecke projector at N=240672 must work in a space of the size "
                "reported by dimension_cusp_forms/genus and across thousands of Sturm primes."
            ),
            "next_viable_paths": [
                "Use a dedicated modular-symbol/Hecke decomposition with persistence and timeouts.",
                "Target possible old levels one by one instead of materializing the full level.",
                "Formulate an abstract M* envelope absorbing global congruence primes such as 3863.",
            ],
        },
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps({
        "main_level": main_level,
        "positive_old_levels": payload["old_levels_with_positive_new_dimension_count"],
        "sturm_trace_scale": payload["sturm_trace_scale"],
        "smoke": payload["timed_modular_symbols_smoke_tests"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
