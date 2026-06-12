#!/usr/bin/env python3
"""Loop 222: ord([f]) calculation at the smallest HCT calibrator.

Target
------
For (N, mode, q) = (109, raw, 3863), compute the O-module orders of the
classes [T_p - a_p(E)] in the cotangent module p_E / p_E^2, where
A_E = T_109^{+, raw}_{m_E}^{wedge} is the localization at the Frey
maximal ideal.

This is the discriminating test recommended by the advisor on 2026-05-14
to verify or falsify the heuristic length_O J = O(1) used in
MG_ae_be_construction_2026-05-14.md.

Mathematical setup
------------------
- M = ModularSymbols(Gamma_0(109), weight=2, sign=+1) over ZZ.
- T_p = Hecke matrix on M for p in {5, 7, 11, 13, 2, 3}.
- Frey traces (raw mode): a_5=2, a_7=0, a_11=0, a_13=-6.
- m_E = (3863, T_5-2, T_7-0, T_11-0, T_13+6, W_109-1) in End_Z(M).
- p_E = ker(lambda_E) where lambda_E: A_E -> O is the Frey character.

ord-calculation
---------------
For each generator f_i of p_E:
1. Compute the matrix [f_i] in End_Z(M).
2. Restrict to the lift of the Frey-eigenspace.
3. Compute its image in p_E / p_E^2 via Smith normal form.
4. ord([f_i]) = the q-adic valuation of the smallest invariant factor.

Run
---
Mac Studio (recommended):
    ssh -i ~/.ssh/id_ed25519_mcmc lukas@100.119.69.90 \
      'source ~/.venvs/science/bin/activate && \
       sage -python ~/compute/mstar_ord_calculation_n109.py --mode raw'

Local Sage (fallback):
    sage -python _scripts/mstar_ord_calculation_n109.py --mode raw

Output
------
- _results/mstar_ord_calculation_n109_<DATE>.json  (machine readable)
- _results/mstar_ord_calculation_n109_<DATE>.md   (human readable)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


DATE = "2026-05-14"
DEFAULT_Q = 3863
DEFAULT_N = 109
TEST_PRIMES = [5, 7, 11, 13]
EXTRA_PRIMES = [2, 3]  # for FQ-repair candidates at N=109

FREY_TRACES = {
    "raw": {5: 2, 7: 0, 11: 0, 13: -6},
    "anc": {5: 2, 7: 0, 11: 0, 13: -6},  # identical at 109/218 by mode-transfer
}

# Atkin-Lehner sign for raw / anc mode at level 109
W_109_SIGN = {"raw": 1, "anc": -1}


def progress(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def import_sage():
    """Import Sage modules; return None on failure."""
    try:
        from sage.all import (  # type: ignore
            ModularSymbols,
            Gamma0,
            GF,
            ZZ,
            QQ,
            Matrix,
            identity_matrix,
            block_matrix,
        )
        return {
            "ModularSymbols": ModularSymbols,
            "Gamma0": Gamma0,
            "GF": GF,
            "ZZ": ZZ,
            "QQ": QQ,
            "Matrix": Matrix,
            "identity_matrix": identity_matrix,
            "block_matrix": block_matrix,
        }
    except ImportError as exc:
        print(f"Sage not available: {exc}", file=sys.stderr)
        return None


def q_adic_valuation(n, q):
    """Return the q-adic valuation of integer n; +inf for n=0."""
    if n == 0:
        return float("inf")
    n = abs(int(n))
    v = 0
    while n % q == 0:
        n //= q
        v += 1
    return v


def compute_eigenspace_dimension(M_q, hecke_matrices_q, frey_traces, sage):
    """Compute dim_F_q of intersection of (T_p - a_p)-kernels."""
    identity_matrix = sage["identity_matrix"]
    n = M_q.dimension()
    space = M_q.free_module()
    for p, ap in frey_traces.items():
        T = hecke_matrices_q[p]
        K = (T - int(ap) * identity_matrix(M_q.base_ring(), n)).right_kernel()
        space = space.intersection(K)
        progress(
            f"  After T_{p} - {ap}: eigenspace dim = {space.dimension()}"
        )
    return space


def compute_ord_via_snf(matrix_Z, q, sage):
    """Given an integer matrix M_int, return the q-adic valuation of its
    smallest nonzero invariant factor (Smith normal form elementary divisor).

    For ord([f]) in p/p^2: this is a first approximation; the rigorous
    ord requires restriction to the local component first.
    """
    # Smith normal form
    snf = matrix_Z.smith_form()  # returns (S, U, V) with S diagonal
    diag = snf[0].diagonal() if hasattr(snf[0], "diagonal") else [
        snf[0][i, i] for i in range(min(snf[0].nrows(), snf[0].ncols()))
    ]
    # q-adic valuations of nonzero invariants
    vals = [q_adic_valuation(int(d), q) for d in diag if int(d) != 0]
    return {
        "min_q_val": min(vals) if vals else None,
        "all_q_vals": vals,
        "rank": len([d for d in diag if int(d) != 0]),
        "diag_first_5": [int(d) for d in diag[:5]],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, default=DEFAULT_N)
    parser.add_argument("--q", type=int, default=DEFAULT_Q)
    parser.add_argument(
        "--mode", choices=["raw", "anc"], default="raw"
    )
    parser.add_argument(
        "--sign", type=int, choices=[1, -1, 0], default=1,
        help="Modular symbol sign: +1, -1, or 0 (full)"
    )
    parser.add_argument(
        "--out-json",
        default=None,
        help="Output JSON path (default: _results/mstar_ord_...json)",
    )
    parser.add_argument(
        "--out-md",
        default=None,
        help="Output MD path (default: _results/mstar_ord_...md)",
    )
    args = parser.parse_args()

    sage = import_sage()
    if sage is None:
        print("Cannot run without Sage. Use Mac Studio.", file=sys.stderr)
        sys.exit(2)

    ModularSymbols = sage["ModularSymbols"]
    Gamma0 = sage["Gamma0"]
    GF = sage["GF"]
    ZZ = sage["ZZ"]
    identity_matrix = sage["identity_matrix"]

    N = args.N
    q = args.q
    mode = args.mode
    traces = FREY_TRACES[mode]
    w109 = W_109_SIGN[mode]

    progress(f"N={N}, q={q}, mode={mode}")
    progress(f"Frey traces: {traces}")
    progress(f"W_{N} sign: {w109}")

    # Step 1: ModularSymbols over QQ (Sage requires a field).
    # Hecke matrices on the standard modular-symbol Z-basis are integral.
    progress("Step 1: ModularSymbols over QQ ...")
    QQ = sage["QQ"]
    M_Q = ModularSymbols(
        Gamma0(N), weight=2, base_ring=QQ, sign=args.sign
    )
    dim_M = M_Q.dimension()
    progress(f"  dim_Q(M) = {dim_M}")

    # Step 2: Hecke matrices over QQ, then change to ZZ.
    progress("Step 2: Hecke matrices (QQ -> ZZ) ...")
    T_Z = {}
    for p in TEST_PRIMES + EXTRA_PRIMES:
        progress(f"  Computing T_{p} ...")
        T_Q = M_Q.hecke_matrix(p)
        try:
            T_Z[p] = T_Q.change_ring(ZZ)
        except Exception as exc:
            progress(f"    WARNING: T_{p} not integral over QQ ({exc}); using QQ matrix")
            T_Z[p] = T_Q

    # Step 3: Reduce mod q and find Frey eigenspace
    progress(f"Step 3: Reduce mod {q} and find eigenspace ...")
    M_q = M_Q.change_ring(GF(q))
    T_q = {p: M_q.hecke_matrix(p) for p in TEST_PRIMES}
    eigenspace = compute_eigenspace_dimension(M_q, T_q, traces, sage)
    eigen_dim = eigenspace.dimension()
    progress(f"  Frey eigenspace dim mod q = {eigen_dim}")

    if eigen_dim == 0:
        result = {
            "date": DATE,
            "N": N,
            "q": q,
            "mode": mode,
            "frey_traces": traces,
            "M_dimension": dim_M,
            "frey_eigenspace_dim": 0,
            "verdict": "No Frey eigenspace mod q. Frey maximal ideal does not exist; setup invalid.",
        }
        write_outputs(result, args, mode)
        return

    # Step 4: ord([T_p - a_p]) via Smith normal form
    progress("Step 4: ord([T_p - a_p]) via SNF (over ZZ) ...")
    ord_results = {}
    for p in TEST_PRIMES + EXTRA_PRIMES:
        if p in traces:
            ap = traces[p]
        else:
            # No trace given; treat as candidate r^FQ_p
            ap = 0  # placeholder; for FQ-repair the relation may be more complex
        progress(f"  T_{p} - {ap} ...")
        F = T_Z[p] - int(ap) * identity_matrix(ZZ, dim_M)
        snf_result = compute_ord_via_snf(F, q, sage)
        ord_results[p] = {
            "trace": int(ap),
            "from_traces": p in traces,
            "snf_min_q_val": snf_result["min_q_val"],
            "snf_q_vals": snf_result["all_q_vals"][:10],
            "rank": snf_result["rank"],
            "diag_first_5": snf_result["diag_first_5"],
        }

    # Step 5: Diagnostics
    progress("Step 5: Diagnostics ...")
    diagnostics = {
        "embedding_dim_estimate_F_q": eigen_dim,
        "comment": (
            "ord values are GLOBAL SNF q-valuations of (T_p - a_p) on ZZ-modular "
            "symbols, NOT yet restricted to the local component A_E. They are an "
            "upper bound for the IKM-ord in the cotangent module."
        ),
    }

    # Step 6: Output
    result = {
        "date": DATE,
        "N": N,
        "q": q,
        "mode": mode,
        "frey_traces": traces,
        "W_N_sign": w109,
        "M_dimension": dim_M,
        "frey_eigenspace_dim": eigen_dim,
        "ord_results": {
            str(p): v for p, v in ord_results.items()
        },
        "diagnostics": diagnostics,
        "next_step": (
            "Restrict (T_p - a_p) to the local component A_E (lift of "
            "Frey eigenspace), then recompute SNF for the rigorous IKM-ord. "
            "This requires explicit construction of the localization "
            "T_N_{m_E}^wedge."
        ),
    }
    write_outputs(result, args, mode)


def write_outputs(result, args, mode):
    root = Path(__file__).resolve().parents[1]
    json_path = (
        Path(args.out_json)
        if args.out_json
        else root / "_results" / f"mstar_ord_calculation_n109_{mode}_{DATE}.json"
    )
    md_path = (
        Path(args.out_md)
        if args.out_md
        else root / "_results" / f"mstar_ord_calculation_n109_{mode}_{DATE}.md"
    )

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    progress(f"Wrote JSON: {json_path}")

    md_lines = [
        f"# mstar ord calculation N={result['N']} {mode} q={result['q']}",
        "",
        f"Date: {result['date']}",
        "",
        f"- N = {result['N']}",
        f"- q = {result['q']}",
        f"- mode = {result['mode']}",
        f"- Frey traces: {result['frey_traces']}",
        f"- W_{result['N']} sign: {result.get('W_N_sign', '?')}",
        f"- dim_Z(M) = {result['M_dimension']}",
        f"- Frey eigenspace dim mod q = {result['frey_eigenspace_dim']}",
        "",
        "## ord-Berechnung pro Prim",
        "",
        "| p | trace a_p | from_traces | SNF min q-val | rank | diag_first_5 |",
        "|---|-----------|-------------|---------------|------|--------------|",
    ]
    if "ord_results" in result:
        for p, v in result["ord_results"].items():
            md_lines.append(
                f"| {p} | {v['trace']} | {v['from_traces']} | "
                f"{v['snf_min_q_val']} | {v['rank']} | {v['diag_first_5']} |"
            )
    md_lines.extend([
        "",
        "## Diagnostics",
        "",
        f"- embedding_dim_estimate_F_q = {result.get('diagnostics', {}).get('embedding_dim_estimate_F_q', '?')}",
        "",
        result.get("diagnostics", {}).get("comment", ""),
        "",
        "## Next step",
        "",
        result.get("next_step", ""),
    ])

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    progress(f"Wrote MD: {md_path}")


if __name__ == "__main__":
    main()
