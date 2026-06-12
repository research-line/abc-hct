#!/usr/bin/env python3
"""CQ-4: Exakt-Dimensions-Cross-Check — Production Solver vs. Canonical Sage.

Tests whether the production solver's qdim EXACTLY matches the canonical
Sage eigenspace dimension at known levels. This closes the gap between:
- CQ-3 v1 (exact dimension, but canonical Sage path, not production solver)
- CQ-3 v2.1 (production solver path, but only checks qdim>0 vs qdim=0)

CQ-4 bridges both: runs the PRODUCTION SOLVER and checks EXACT qdim match
against the canonical Sage eigenspace computation.

Tests (Tier 1 — trivial new_dim, sanity):
  Level 11: newform 11.2.a.a, new_dim=1, expect qdim=1
  Level 14: newform 14.2.a.a, new_dim=1, expect qdim=1
  Level 33: newform 33.2.a.a, new_dim=1, expect qdim=1

Tests (Tier 2 — MULTI-DIM POSITIVE SELECTION, the discriminating regime):
  Level 219: 3||219, new_dim=13, rational newform, expect qdim=1
  Level 201: 3||201, new_dim=11, rational newform, expect qdim=1
  Level 291: 3||291, new_dim=17, rational newform, expect qdim=1
  Level 269: prime, new_dim=22, rational newform, expect qdim=1
  Level 233: prime, new_dim=19, rational newform, expect qdim=1

Usage (Mac Studio):
  export PATH=/Users/lukas/mamba/envs/sage/bin:$PATH
  cd /Users/lukas/compute/abc_hct
  python cq4_exact_dimension_crosscheck.py 2>&1 | tee cq4_output.log
"""
import os, sys, time, json, tempfile
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
if os.path.isdir("_scripts"):
    sys.path.insert(0, "_scripts")

from sage.all import GF, Gamma0, ModularSymbols, identity_matrix, block_matrix

import mstar_nomagma_sparse_hecke_quotient as solver

Q_MOD = 3863

TESTS = [
    # Tier 1: trivial new_dim (sanity checks)
    {
        "label": "Level 11 (11.2.a.a, new_dim=1)",
        "level": 11,
        "eigenvalues": {2: -2, 3: -1, 5: 1, 7: -2},
        "primes": [2, 3, 5, 7],
    },
    {
        "label": "Level 14 (14.2.a.a, new_dim=1)",
        "level": 14,
        "eigenvalues": {2: -1, 3: -2, 5: 0, 13: -4},
        "primes": [2, 3, 5, 13],
    },
    {
        "label": "Level 33 (33.2.a.a, 3||N, new_dim=1)",
        "level": 33,
        "eigenvalues": {2: 1, 3: -1, 5: -2, 7: 4, 11: 1},
        "primes": [2, 3, 5, 7, 11],
    },
    # Tier 2: MULTI-DIM POSITIVE SELECTION (the discriminating regime)
    # Eigenvalues sourced from Sage Newforms(Gamma0(M), 2), verified qdim=1 canonical
    {
        "label": "Level 219 (3||219, new_dim=13, rational newform)",
        "level": 219,
        "eigenvalues": {2: -2, 3: -1, 5: -1, 7: 2, 11: -4, 13: -2},
        "primes": [2, 3, 5, 7, 11, 13],
    },
    {
        "label": "Level 201 (3||201, new_dim=11, rational newform)",
        "level": 201,
        "eigenvalues": {2: -2, 3: -1, 5: 0, 7: 0, 11: -6, 13: 4},
        "primes": [2, 3, 5, 7, 11, 13],
    },
    {
        "label": "Level 291 (3||291, new_dim=17, rational newform)",
        "level": 291,
        "eigenvalues": {2: -2, 3: -1, 5: 3, 7: -2, 11: 0, 13: -4},
        "primes": [2, 3, 5, 7, 11, 13],
    },
    {
        "label": "Level 269 (prime, new_dim=22, rational newform)",
        "level": 269,
        "eigenvalues": {2: 0, 3: 0, 5: 1, 7: -4, 11: -3, 13: 2},
        "primes": [2, 3, 5, 7, 11, 13],
    },
    {
        "label": "Level 233 (prime, new_dim=19, rational newform)",
        "level": 233,
        "eigenvalues": {2: 1, 3: -2, 5: 2, 7: 4, 11: 6, 13: 6},
        "primes": [2, 3, 5, 7, 11, 13],
    },
]


def canonical_sage_qdim(level, eigenvalues, primes, q=Q_MOD):
    """Compute qdim via canonical Sage path: ModularSymbols -> cuspidal -> new -> hecke_matrix."""
    MS = ModularSymbols(Gamma0(level), 2, sign=1)
    CS = MS.cuspidal_subspace()
    NS = CS.new_subspace()
    n = NS.dimension()
    if n == 0:
        return 0, n

    Fq = GF(q)
    rows_list = []
    for p in sorted(primes):
        ap = eigenvalues[p]
        Tp = NS.hecke_matrix(p)
        Tp_mod = Tp.change_ring(Fq)
        Ip = identity_matrix(Fq, n)
        rows_list.append(Tp_mod - ap * Ip)

    big = block_matrix([[r] for r in rows_list])
    ker = big.right_kernel()
    return ker.dimension(), n


def production_solver_qdim(level, eigenvalues, primes):
    """Run production solver and extract exact qdim."""
    original_frey_ap = solver.frey_ap

    def patched_frey_ap(mode, p):
        if p in eigenvalues:
            return eigenvalues[p]
        return original_frey_ap(mode, p)

    solver.frey_ap = patched_frey_ap

    with tempfile.TemporaryDirectory() as tmpdir:
        out_json = os.path.join(tmpdir, "result.json")
        argv = [
            "--backend", "sage",
            "--levels", str(level),
            "--modes", "raw",
            "--primes", *[str(p) for p in primes],
            "--q", str(Q_MOD),
            "--sign", "1",
            "--hecke-family", "cremona",
            "--rank-engine", "quotient-numpy-dense",
            "--pivot-strategy", "max",
            "--progress",
            "--out-json", out_json,
        ]

        try:
            solver.main(argv)
        except SystemExit:
            pass

        solver.frey_ap = original_frey_ap

        try:
            with open(out_json, "r") as f:
                result = json.load(f)
        except Exception as e:
            return -1, str(e)

    runs = result.get("runs", [])
    if not runs:
        return -1, "no runs"

    run = runs[0]
    stages = run.get("stages", [])
    if stages:
        last_stage = stages[-1]
        return last_stage.get("quotient_dim", -1), None
    return -1, "no stages"


if __name__ == "__main__":
    print("=" * 70)
    print("CQ-4: EXAKT-DIMENSIONS-CROSS-CHECK")
    print("Production Solver vs. Canonical Sage Eigenspace")
    print(f"q = {Q_MOD}")
    print("=" * 70)
    print()

    all_pass = True
    results = []

    for test in TESTS:
        label = test["label"]
        level = test["level"]
        eigenvalues = test["eigenvalues"]
        primes = test["primes"]

        print(f"--- {label} ---")
        print(f"  Eigenvalues: {eigenvalues}")
        print(f"  Primes: {primes}")

        t0 = time.time()
        sage_qdim, new_dim = canonical_sage_qdim(level, eigenvalues, primes)
        t_sage = time.time() - t0
        print(f"  Canonical Sage: qdim={sage_qdim}, new_dim={new_dim} ({t_sage:.1f}s)")

        t0 = time.time()
        prod_qdim, err = production_solver_qdim(level, eigenvalues, primes)
        t_prod = time.time() - t0
        if err:
            print(f"  Production:     ERROR: {err}")
            status = "ERROR"
            all_pass = False
        else:
            print(f"  Production:     qdim={prod_qdim} ({t_prod:.1f}s)")
            if sage_qdim == prod_qdim:
                status = "MATCH"
                print(f"  -> MATCH (both qdim={sage_qdim})")
            else:
                status = "MISMATCH"
                all_pass = False
                print(f"  -> MISMATCH! Sage={sage_qdim}, Production={prod_qdim}")

        results.append({
            "label": label,
            "level": level,
            "sage_qdim": sage_qdim,
            "prod_qdim": prod_qdim,
            "new_dim": new_dim,
            "status": status,
        })
        print()
        sys.stdout.flush()

    print("=" * 70)
    print("CQ-4 SUMMARY")
    print("=" * 70)
    for r in results:
        v = r["status"]
        print(f"  [{v}] {r['label']}: Sage={r['sage_qdim']}, Prod={r['prod_qdim']} (new_dim={r['new_dim']})")
    print()
    tier2 = [r for r in results if r["new_dim"] >= 10]
    tier2_pass = all(r["status"] == "MATCH" and r["sage_qdim"] == 1 for r in tier2)

    if all_pass:
        print("ALL TESTS MATCHED")
        if tier2_pass and tier2:
            print(f"Tier 2 ({len(tier2)} levels, new_dim 11-22): production solver selects")
            print("EXACTLY the same 1-dim subspace as canonical Sage from multi-dim new spaces.")
            print("This is the discriminating regime — assembly faithfulness confirmed.")
        else:
            print("Production solver matches canonical Sage at all tested levels.")
    else:
        print("*** MISMATCH DETECTED ***")
        print("The production solver disagrees with canonical Sage on exact qdim!")
        print("This would indicate an assembly bug (Dragon D1).")

    sys.exit(0 if all_pass else 1)
