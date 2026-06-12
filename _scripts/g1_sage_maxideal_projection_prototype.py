"""Sage prototype for the G1/P1' Hecke-maximal-ideal test.

Run inside a Sage Python environment, for example:

    micromamba run -n sage python _scripts/g1_sage_maxideal_projection_prototype.py --limit 5

This is intentionally a Sage script, not plain Python.  It implements the first
executable layer of Loop 80:

1. build the Frey curve E_{a,b};
2. build modular symbols at level N over F_ell;
3. impose Hecke eigenvalue congruences T_q = a_q(E) modulo ell;
4. report the candidate m_ell-local eigenspace dimension;
5. construct the relative modular symbol C_lambda = {0,a/c} in the ambient
   module and test its image in the Hecke-ideal quotient against matched
   denominator controls.

The quotient test is still diagnostic: it uses Hecke operators away from
ell*N and records row/column-orientation results separately.  That is enough to
stop treating EM-3a residues as a maximal-ideal computation, but not yet a
global proof of G1/P1'.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "_data" / "g1_maxideal_projection_requirements_2026-05-09.json"
OUTPUT = ROOT / "_results" / "g1_sage_maxideal_projection_prototype_2026-05-09.json"


def load_sage():
    try:
        from sage.all import (  # type: ignore
            EllipticCurve,
            GF,
            Gamma0,
            ModularSymbols,
            QQ,
            VectorSpace,
            identity_matrix,
            next_prime,
        )
    except Exception as exc:  # pragma: no cover - used outside Sage
        return None, str(exc)
    return {
        "EllipticCurve": EllipticCurve,
        "GF": GF,
        "Gamma0": Gamma0,
        "ModularSymbols": ModularSymbols,
        "QQ": QQ,
        "VectorSpace": VectorSpace,
        "identity_matrix": identity_matrix,
        "next_prime": next_prime,
    }, None


def prime_list(sage, limit: int) -> list[int]:
    result: list[int] = []
    p = 2
    while p <= limit:
        result.append(int(p))
        p = int(sage["next_prime"](p))
    return result


def prime_divisors(n: int) -> list[int]:
    divisors: list[int] = []
    p = 2
    m = n
    while p * p <= m:
        if m % p == 0:
            divisors.append(p)
            while m % p == 0:
                m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        divisors.append(m)
    return divisors


def frey_curve(sage, a: int, b: int):
    # y^2 = x(x-a)(x+b) = x^3 + (b-a)x^2 - ab x
    E = sage["EllipticCurve"](sage["QQ"], [0, b - a, 0, -a * b, 0])
    try:
        return E.global_minimal_model()
    except Exception:
        return E


def cuspidal_module(M):
    for name in ("cuspidal_submodule", "cuspidal_subspace"):
        if hasattr(M, name):
            return getattr(M, name)()
    return M


def module_dimension(M) -> int:
    for name in ("dimension", "rank"):
        if hasattr(M, name):
            value = getattr(M, name)()
            return int(value)
    raise RuntimeError("Cannot determine modular-symbol module dimension")


def hecke_matrix(M, n: int):
    if hasattr(M, "hecke_matrix"):
        return M.hecke_matrix(n)
    if hasattr(M, "hecke_operator"):
        return M.hecke_operator(n).matrix()
    raise RuntimeError("No Hecke matrix/operator method found")


def residue_controls(a: int, c: int, max_controls: int) -> list[int]:
    controls: list[int] = []
    target = a % c
    for r in range(1, c):
        if r == target:
            continue
        if math.gcd(r, c) == 1:
            controls.append(r)
        if len(controls) >= max_controls:
            break
    return controls


def vector_list(v) -> list[int]:
    return [int(x) for x in list(v)]


def vector_weight(v) -> int:
    return sum(1 for x in v if x != 0)


def projective_class(F, coords: list[int]) -> list[int] | None:
    for x in coords:
        if x != 0:
            scale = F(x) ** -1
            return [int(F(y) * scale) for y in coords]
    return None


def quotient_coordinates(sage, V, span, v) -> list[int]:
    Q = V.quotient(span)
    return vector_list(Q(v))


def support_stats(values: list[int]) -> dict:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def quotient_probe(
    sage,
    Mrel,
    E,
    ell: int,
    a: int,
    c: int,
    hecke_primes: list[int],
    local_primes: list[int],
    max_controls: int,
) -> dict:
    F = sage["GF"](ell)
    QQ = sage["QQ"]
    d = module_dimension(Mrel)
    V = sage["VectorSpace"](F, d)
    I = sage["identity_matrix"](F, d)

    row_generators = []
    column_generators = []
    used: list[int] = []
    trace: list[dict] = []

    operators = [("T", q) for q in hecke_primes] + [("U", p) for p in local_primes]
    for op_kind, q in operators:
        try:
            A = hecke_matrix(Mrel, q) - F(int(E.ap(q))) * I
            row_generators.extend(A.rows())
            column_generators.extend(A.columns())
            used.append(q)
            trace.append(
                {
                    "operator": op_kind,
                    "q": q,
                    "a_q_mod_ell": int(F(int(E.ap(q)))),
                    "row_rank": int(V.subspace(row_generators).dimension()),
                    "column_rank": int(V.subspace(column_generators).dimension()),
                }
            )
        except Exception as exc:
            trace.append({"operator": op_kind, "q": q, "error": str(exc)})

    row_span = V.subspace(row_generators)
    column_span = V.subspace(column_generators)

    def symbol_vector(numerator: int):
        symbol = Mrel.modular_symbol([QQ(0), QQ(numerator) / QQ(c)])
        return V(Mrel.coordinate_vector(symbol))

    frey_vector = symbol_vector(a)
    frey_row_nonzero = frey_vector not in row_span
    frey_column_nonzero = frey_vector not in column_span
    frey_row_coords = quotient_coordinates(sage, V, row_span, frey_vector)
    frey_column_coords = quotient_coordinates(sage, V, column_span, frey_vector)
    frey_row_projective = projective_class(F, frey_row_coords)
    frey_column_projective = projective_class(F, frey_column_coords)

    controls = []
    for r in residue_controls(a, c, max_controls):
        v = symbol_vector(r)
        row_coords = quotient_coordinates(sage, V, row_span, v)
        column_coords = quotient_coordinates(sage, V, column_span, v)
        row_projective = projective_class(F, row_coords)
        column_projective = projective_class(F, column_coords)
        controls.append(
            {
                "r": r,
                "row_quotient_nonzero": bool(v not in row_span),
                "column_quotient_nonzero": bool(v not in column_span),
                "support_size": sum(1 for x in v if x != 0),
                "row_quotient_vector": row_coords,
                "column_quotient_vector": column_coords,
                "row_quotient_weight": vector_weight(row_coords),
                "column_quotient_weight": vector_weight(column_coords),
                "row_projective_class": row_projective,
                "column_projective_class": column_projective,
            }
        )

    row_weights = [item["row_quotient_weight"] for item in controls]
    column_weights = [item["column_quotient_weight"] for item in controls]

    return {
        "status": "ok",
        "interpretation": "Relative ambient-module quotient by the Hecke ideal generated by T_q-a_q(E) for q away from ell*N; row and column orientations are both reported.",
        "ambient_dimension": d,
        "hecke_primes_used": used,
        "away_hecke_primes_used": hecke_primes,
        "local_primes_used": local_primes,
        "quotient_row_dimension": int(d - row_span.dimension()),
        "quotient_column_dimension": int(d - column_span.dimension()),
        "rank_trace": trace,
        "frey_symbol": f"{{0,{a}/{c}}}",
        "frey_support_size": sum(1 for x in frey_vector if x != 0),
        "frey_coordinate_vector": vector_list(frey_vector),
        "frey_row_quotient_nonzero": bool(frey_row_nonzero),
        "frey_column_quotient_nonzero": bool(frey_column_nonzero),
        "frey_row_quotient_vector": frey_row_coords,
        "frey_column_quotient_vector": frey_column_coords,
        "frey_row_quotient_weight": vector_weight(frey_row_coords),
        "frey_column_quotient_weight": vector_weight(frey_column_coords),
        "frey_row_projective_class": frey_row_projective,
        "frey_column_projective_class": frey_column_projective,
        "controls_tested": len(controls),
        "control_row_nonzero_count": sum(1 for item in controls if item["row_quotient_nonzero"]),
        "control_column_nonzero_count": sum(1 for item in controls if item["column_quotient_nonzero"]),
        "control_row_weight_stats": support_stats(row_weights),
        "control_column_weight_stats": support_stats(column_weights),
        "control_row_same_projective_count": sum(
            1 for item in controls if item["row_projective_class"] == frey_row_projective
        ),
        "control_column_same_projective_count": sum(
            1 for item in controls if item["column_projective_class"] == frey_column_projective
        ),
        "control_row_weight_le_frey_count": sum(
            1 for item in controls if item["row_quotient_weight"] <= vector_weight(frey_row_coords)
        ),
        "control_column_weight_le_frey_count": sum(
            1 for item in controls if item["column_quotient_weight"] <= vector_weight(frey_column_coords)
        ),
        "controls": controls,
    }


def run_case(
    sage,
    case: dict,
    max_hecke: int,
    max_controls: int,
    cycle_probe_enabled: bool,
    local_ops_enabled: bool,
) -> dict:
    ell = int(case["ell"])
    a = int(case["a"])
    b = int(case["b"])
    n = int(case["N_cond"])
    F = sage["GF"](ell)

    E = frey_curve(sage, a, b)
    actual_n = int(E.conductor())
    if actual_n != n:
        n = actual_n

    M0 = sage["ModularSymbols"](sage["Gamma0"](n), 2, sign=0, base_ring=F)
    M = cuspidal_module(M0)
    d = module_dimension(M)
    V = sage["VectorSpace"](F, d)
    W = V

    used_primes: list[int] = []
    kernel_dims: list[dict] = []
    local_kernel_dims: list[dict] = []
    I = sage["identity_matrix"](F, d)
    for q in prime_list(sage, max_hecke):
        if math.gcd(q, ell * n) != 1:
            continue
        try:
            Tq = hecke_matrix(M, q)
            aq = F(int(E.ap(q)))
            K = (Tq - aq * I).right_kernel()
            W = W.intersection(K)
            used_primes.append(q)
            kernel_dims.append({"q": q, "a_q_mod_ell": int(aq), "localized_dim": int(W.dimension())})
        except Exception as exc:
            kernel_dims.append({"q": q, "error": str(exc)})
        if W.dimension() <= 1 and len(used_primes) >= 3:
            break

    local_primes: list[int] = []
    if local_ops_enabled:
        for p in prime_divisors(n):
            if p == ell:
                continue
            try:
                T_p = hecke_matrix(M, p)
                ap = F(int(E.ap(p)))
                K = (T_p - ap * I).right_kernel()
                W = W.intersection(K)
                local_primes.append(p)
                local_kernel_dims.append(
                    {"p": p, "a_p_mod_ell": int(ap), "localized_dim": int(W.dimension())}
                )
            except Exception as exc:
                local_kernel_dims.append({"p": p, "error": str(exc)})

    if cycle_probe_enabled:
        cycle_probe = quotient_probe(
            sage,
            M0,
            E,
            ell,
            a,
            int(case["c"]),
            used_primes,
            local_primes,
            max_controls,
        )
    else:
        cycle_probe = {"status": "skipped", "reason": "disabled by --no-cycle-probe"}

    return {
        "label": case["label"],
        "a": a,
        "b": b,
        "c": int(case["c"]),
        "ell": ell,
        "N_cond": n,
        "D_ell": int(case["D_ell"]),
        "drop_primes": case["drop_primes"],
        "module_dimension": d,
        "hecke_primes_used": used_primes,
        "local_primes_used": local_primes,
        "kernel_trace": kernel_dims,
        "local_kernel_trace": local_kernel_dims,
        "candidate_m_ell_eigenspace_dimension": int(W.dimension()),
        "stage_b_cycle_quotient_probe": cycle_probe,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(INPUT))
    parser.add_argument("--output", default=str(OUTPUT))
    parser.add_argument("--offset", type=int, default=0, help="skip this many small cases before running")
    parser.add_argument("--limit", type=int, default=5, help="number of small cases to run")
    parser.add_argument("--max-hecke", type=int, default=97, help="largest Hecke prime q to try")
    parser.add_argument("--controls", type=int, default=24, help="matched denominator controls per case")
    parser.add_argument("--no-cycle-probe", action="store_true", help="run Stage A only")
    parser.add_argument("--local-ops", action="store_true", help="also impose local U_p-style operators for p|N, p!=ell")
    args = parser.parse_args()

    sage, error = load_sage()
    if sage is None:
        result = {
            "status": "blocked",
            "reason": "SageMath is required; run this script in a Sage Python environment.",
            "import_error": error,
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 2

    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    small_cases = [case for case in source["active_pairs"] if case["feasibility"] == "small"]
    cases = small_cases[args.offset : args.offset + args.limit]
    results = []
    for case in cases:
        print(f"RUN {case['label']} ell={case['ell']} N={case['N_cond']}", file=sys.stderr, flush=True)
        results.append(
            run_case(
                sage,
                case,
                args.max_hecke,
                args.controls,
                not args.no_cycle_probe,
                args.local_ops,
            )
        )
    output = {
        "status": "ok",
        "purpose": "Stage-A Hecke maximal ideal eigenspace localization for G1/P1'.",
        "offset": args.offset,
        "cases_run": len(results),
        "local_ops": bool(args.local_ops),
        "note": "This reports the m_ell eigenspace cut and a Stage-B ambient quotient probe for C_lambda={0,a/c}.",
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
