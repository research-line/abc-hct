"""Integral-lattice probe for the G1/P1' Hecke quotient.

This is the first structured follow-up after the pure F_ell quotient norm
collapsed to zero/nonzero.  Sage's ModularSymbols implementation requires a
field, so we work over QQ and use the observed integral coordinate lattice in
the modular-symbol basis.  For the small active cases this gives integer Hecke
matrices and integer symbol coordinates.

The diagnostic quotient is

    Z^d / sum_q (T_q - a_q(E)) Z^d

with optional local U_p-style operators.  We report Smith-normal-form invariant
factors and the l-adic order of the Frey and control cosets.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "_data" / "g1_maxideal_projection_requirements_2026-05-09.json"
OUTPUT = ROOT / "_results" / "g1_integral_lattice_quotient_probe_2026-05-09.json"


def load_sage():
    try:
        from sage.all import (  # type: ignore
            EllipticCurve,
            Gamma0,
            GF,
            ModularSymbols,
            QQ,
            VectorSpace,
            ZZ,
            gcd,
            identity_matrix,
            lcm,
            matrix,
            next_prime,
            vector,
        )
    except Exception as exc:  # pragma: no cover - used outside Sage
        return None, str(exc)
    return {
        "EllipticCurve": EllipticCurve,
        "Gamma0": Gamma0,
        "GF": GF,
        "ModularSymbols": ModularSymbols,
        "QQ": QQ,
        "VectorSpace": VectorSpace,
        "ZZ": ZZ,
        "gcd": gcd,
        "identity_matrix": identity_matrix,
        "lcm": lcm,
        "matrix": matrix,
        "next_prime": next_prime,
        "vector": vector,
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
            return int(getattr(M, name)())
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


def valuation(n: int, p: int) -> int:
    n = abs(int(n))
    if n == 0:
        return 10**9
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v


def content(values: list[int]) -> int:
    g = 0
    for value in values:
        g = math.gcd(g, abs(int(value)))
    return g


def integer_row_entries(row) -> tuple[list[int], int]:
    den = 1
    for x in row:
        den = int(den * x.denominator() // math.gcd(den, int(x.denominator())))
    return [int(den * x) for x in row], den


def matrix_generators(A, orientation: str) -> tuple[list[list[int]], list[int]]:
    generators: list[list[int]] = []
    denoms: list[int] = []
    iterable = A.rows() if orientation == "row" else A.columns()
    for vec in iterable:
        entries, den = integer_row_entries(list(vec))
        generators.append(entries)
        denoms.append(den)
    return generators, denoms


def vector_entries(v) -> tuple[list[int], int]:
    return integer_row_entries(list(v))


def coset_data(sage, V_right, invariants: list[int], rank: int, d: int, ell: int, entries: list[int]) -> dict:
    ZZ = sage["ZZ"]
    vector = sage["vector"]
    gcd = sage["gcd"]
    lcm = sage["lcm"]
    x = vector(ZZ, entries)
    y = x * V_right
    coords = [int(t) for t in list(y)]
    free_tail = coords[rank:d]
    free_content = content(free_tail)
    finite = all(t == 0 for t in free_tail)
    component_orders: list[int] = []
    ell_component_exponents: list[int] = []
    if finite:
        order = ZZ(1)
        for diag, coord in zip(invariants, coords[:rank]):
            diag = abs(int(diag))
            coord = int(coord)
            if diag <= 1:
                comp = 1
            else:
                comp = diag // int(gcd(diag, coord))
            component_orders.append(int(comp))
            ell_component_exponents.append(valuation(comp, ell))
            order = lcm(order, comp)
        order_int = int(order)
        ell_exp = valuation(order_int, ell)
    else:
        order_int = None
        ell_exp = None
    return {
        "finite_order": bool(finite),
        "smith_coordinates": coords,
        "free_tail": free_tail,
        "free_content": free_content,
        "order": order_int,
        "ell_order_exponent": ell_exp,
        "component_orders": component_orders,
        "ell_component_exponents": ell_component_exponents,
    }


def quotient_summary(sage, generators: list[list[int]], ell: int, vectors: dict[str, list[int]]) -> dict:
    ZZ = sage["ZZ"]
    matrix = sage["matrix"]
    d = len(next(iter(vectors.values()))) if vectors else (len(generators[0]) if generators else 0)
    R = matrix(ZZ, generators) if generators else matrix(ZZ, 0, d)
    D, _U, V_right = R.smith_form()
    diag_len = min(D.nrows(), D.ncols())
    invariants = [abs(int(D[i, i])) for i in range(diag_len) if int(D[i, i]) != 0]
    rank = len(invariants)
    ell_primary_exponents = [valuation(x, ell) for x in invariants if x % ell == 0]
    cosets = {
        name: coset_data(sage, V_right, invariants, rank, d, ell, entries)
        for name, entries in vectors.items()
    }
    return {
        "relation_rank": int(rank),
        "free_rank": int(d - rank),
        "invariant_factors": invariants,
        "ell_primary_exponents": ell_primary_exponents,
        "ell_primary_rank": len(ell_primary_exponents),
        "max_ell_primary_exponent": max(ell_primary_exponents) if ell_primary_exponents else 0,
        "cosets": cosets,
    }


def select_operators(sage, E, ell: int, n: int, max_hecke: int, local_ops: bool) -> tuple[list[int], list[int], list[dict]]:
    F = sage["GF"](ell)
    M0 = sage["ModularSymbols"](sage["Gamma0"](n), 2, sign=0, base_ring=F)
    M = cuspidal_module(M0)
    d = module_dimension(M)
    V = sage["VectorSpace"](F, d)
    W = V
    I = sage["identity_matrix"](F, d)
    used_primes: list[int] = []
    local_primes: list[int] = []
    trace: list[dict] = []

    for q in prime_list(sage, max_hecke):
        if math.gcd(q, ell * n) != 1:
            continue
        try:
            aq = F(int(E.ap(q)))
            K = (hecke_matrix(M, q) - aq * I).right_kernel()
            W = W.intersection(K)
            used_primes.append(q)
            trace.append({"operator": "T", "q": q, "a_q_mod_ell": int(aq), "localized_dim": int(W.dimension())})
        except Exception as exc:
            trace.append({"operator": "T", "q": q, "error": str(exc)})
        if W.dimension() <= 1 and len(used_primes) >= 3:
            break

    if local_ops:
        for p in prime_divisors(n):
            if p == ell:
                continue
            try:
                ap = F(int(E.ap(p)))
                K = (hecke_matrix(M, p) - ap * I).right_kernel()
                W = W.intersection(K)
                local_primes.append(p)
                trace.append({"operator": "U", "q": p, "a_q_mod_ell": int(ap), "localized_dim": int(W.dimension())})
            except Exception as exc:
                trace.append({"operator": "U", "q": p, "error": str(exc)})
    return used_primes, local_primes, trace


def symbol_vector(sage, M, numerator: int, c: int) -> tuple[list[int], int]:
    QQ = sage["QQ"]
    symbol = M.modular_symbol([QQ(0), QQ(numerator) / QQ(c)])
    return vector_entries(M.coordinate_vector(symbol))


def summarize_controls(cosets: list[dict], frey_exp: int | None, frey_content: int) -> dict:
    finite = [item for item in cosets if item["finite_order"]]
    exps = [item["ell_order_exponent"] for item in finite if item["ell_order_exponent"] is not None]
    contents = [int(item["free_content"]) for item in cosets]
    return {
        "finite_count": len(finite),
        "min_ell_order_exponent": min(exps) if exps else None,
        "max_ell_order_exponent": max(exps) if exps else None,
        "mean_ell_order_exponent": (sum(exps) / len(exps)) if exps else None,
        "count_ge_frey_ell_exponent": (
            sum(1 for exp in exps if frey_exp is not None and exp >= frey_exp)
            if frey_exp is not None
            else None
        ),
        "count_le_frey_ell_exponent": (
            sum(1 for exp in exps if frey_exp is not None and exp <= frey_exp)
            if frey_exp is not None
            else None
        ),
        "min_free_content": min(contents) if contents else None,
        "max_free_content": max(contents) if contents else None,
        "mean_free_content": (sum(contents) / len(contents)) if contents else None,
        "count_ge_frey_free_content": sum(1 for value in contents if value >= frey_content),
        "count_le_frey_free_content": sum(1 for value in contents if value <= frey_content),
        "count_eq_frey_free_content": sum(1 for value in contents if value == frey_content),
    }


def run_case(sage, case: dict, max_hecke: int, max_controls: int, local_ops: bool) -> dict:
    QQ = sage["QQ"]
    ell = int(case["ell"])
    a = int(case["a"])
    b = int(case["b"])
    c = int(case["c"])
    n = int(case["N_cond"])
    E = frey_curve(sage, a, b)
    actual_n = int(E.conductor())
    if actual_n != n:
        n = actual_n

    hecke_primes, local_primes, selection_trace = select_operators(sage, E, ell, n, max_hecke, local_ops)
    M = sage["ModularSymbols"](sage["Gamma0"](n), 2, sign=0, base_ring=QQ)
    d = module_dimension(M)
    I = sage["identity_matrix"](QQ, d)

    row_generators: list[list[int]] = []
    column_generators: list[list[int]] = []
    denominator_lcms: list[int] = []
    operators = [("T", q) for q in hecke_primes] + [("U", p) for p in local_primes]
    operator_trace: list[dict] = []
    for kind, q in operators:
        A = hecke_matrix(M, q) - int(E.ap(q)) * I
        rows, row_denoms = matrix_generators(A, "row")
        cols, col_denoms = matrix_generators(A, "column")
        row_generators.extend(rows)
        column_generators.extend(cols)
        denominator_lcms.extend(row_denoms)
        denominator_lcms.extend(col_denoms)
        operator_trace.append(
            {
                "operator": kind,
                "q": q,
                "a_q": int(E.ap(q)),
                "row_denominator_lcm": math.lcm(*row_denoms) if row_denoms else 1,
                "column_denominator_lcm": math.lcm(*col_denoms) if col_denoms else 1,
            }
        )

    controls = residue_controls(a, c, max_controls)
    symbol_entries: dict[str, list[int]] = {}
    symbol_denoms: dict[str, int] = {}
    frey_entries, frey_denom = symbol_vector(sage, M, a, c)
    symbol_entries["frey"] = frey_entries
    symbol_denoms["frey"] = frey_denom
    for r in controls:
        entries, den = symbol_vector(sage, M, r, c)
        symbol_entries[f"control_{r}"] = entries
        symbol_denoms[f"control_{r}"] = den

    row_summary = quotient_summary(sage, row_generators, ell, symbol_entries)
    column_summary = quotient_summary(sage, column_generators, ell, symbol_entries)

    row_controls = [
        {"r": r, **row_summary["cosets"][f"control_{r}"]}
        for r in controls
    ]
    column_controls = [
        {"r": r, **column_summary["cosets"][f"control_{r}"]}
        for r in controls
    ]
    row_frey = row_summary["cosets"]["frey"]
    column_frey = column_summary["cosets"]["frey"]

    return {
        "label": case["label"],
        "a": a,
        "b": b,
        "c": c,
        "ell": ell,
        "N_cond": n,
        "D_ell": int(case["D_ell"]),
        "module_dimension_QQ": d,
        "hecke_primes_used": hecke_primes,
        "local_primes_used": local_primes,
        "selection_trace_mod_ell": selection_trace,
        "operator_trace_QQ": operator_trace,
        "all_operator_denominators_integral": all(x == 1 for x in denominator_lcms),
        "all_symbol_denominators_integral": all(x == 1 for x in symbol_denoms.values()),
        "symbol_denominators": symbol_denoms,
        "row_quotient": {k: v for k, v in row_summary.items() if k != "cosets"},
        "column_quotient": {k: v for k, v in column_summary.items() if k != "cosets"},
        "frey_row_coset": row_frey,
        "frey_column_coset": column_frey,
        "control_row_stats": summarize_controls(
            row_controls, row_frey["ell_order_exponent"], row_frey["free_content"]
        ),
        "control_column_stats": summarize_controls(
            column_controls, column_frey["ell_order_exponent"], column_frey["free_content"]
        ),
        "controls": [
            {
                "r": r,
                "row": row_summary["cosets"][f"control_{r}"],
                "column": column_summary["cosets"][f"control_{r}"],
            }
            for r in controls
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(INPUT))
    parser.add_argument("--output", default=str(OUTPUT))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-hecke", type=int, default=97)
    parser.add_argument("--controls", type=int, default=24)
    parser.add_argument("--local-ops", action="store_true")
    args = parser.parse_args()

    sage, error = load_sage()
    if sage is None:
        result = {"status": "blocked", "reason": "SageMath is required.", "import_error": error}
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
        results.append(run_case(sage, case, args.max_hecke, args.controls, args.local_ops))

    output = {
        "status": "ok",
        "purpose": "Integral lattice Smith-normal-form probe for the G1/P1' Hecke quotient.",
        "offset": args.offset,
        "cases_run": len(results),
        "local_ops": bool(args.local_ops),
        "note": "Uses QQ modular symbols and the observed integer coordinate lattice; diagnostic, not a canonical integral model proof.",
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
