#!/usr/bin/env python3
"""CQ-3 Positivkontrolle: End-to-End-Test des qdim-Mechanismus.

Validates that the Hecke quotient pipeline correctly detects qdim=1
for known LMFDB newforms and qdim=0 for wrong eigenvalues.

Tests:
  1. Level 11 (3∤N): correct LMFDB eigenvalues → qdim=1
  2. Level 11: wrong a_3 (+1 statt -1) → qdim=0
  3. Level 14 (3∤N): correct LMFDB eigenvalues → qdim=1
  4. Level 23 (3∤N): rational targets for 2-dim form → qdim=0
  5. Level 33 (3‖N): U_3 independence test
  6. Level 15 (3‖N): U_3 independence test

Usage (Mac Studio):
  export PATH=/Users/lukas/mamba/envs/sage/bin:$PATH
  python cq3_positive_control.py
"""
import os, sys, time
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PATH"] = "/Users/lukas/mamba/envs/sage/bin:" + os.environ.get("PATH", "")

from sage.all import (
    GF, Gamma0, ModularSymbols, CuspForms,
    identity_matrix, block_matrix, matrix
)

Q_MOD = 3863
F = GF(Q_MOD)

TESTS = [
    {
        "label": "Level 11 — correct LMFDB eigenvalues (11.2.a.a)",
        "level": 11,
        "targets": {2: -2, 3: -1, 5: 1, 7: -2},
        "expect_qdim": 1,
    },
    {
        "label": "Level 11 — WRONG a_3 (+1 statt -1)",
        "level": 11,
        "targets": {2: -2, 3: 1, 5: 1, 7: -2},
        "expect_qdim": 0,
    },
    {
        "label": "Level 14 — correct LMFDB eigenvalues (14.2.a.a)",
        "level": 14,
        "targets": {2: -1, 3: -2, 5: 0, 11: 0, 13: -4},
        "expect_qdim": 1,
    },
    {
        "label": "Level 14 — WRONG a_3 (+2 statt -2)",
        "level": 14,
        "targets": {2: -1, 3: 2, 5: 0, 11: 0, 13: -4},
        "expect_qdim": 0,
    },
    {
        "label": "Level 23 — rational target for 2-dim form (no rational newform exists)",
        "level": 23,
        "targets": {2: 0, 3: 0, 5: 0, 7: 0},
        "expect_qdim": 0,
    },
    {
        "label": "Level 33 = 3·11 — U_3 test (3‖N)",
        "level": 33,
        "targets": None,
        "expect_qdim": None,
        "discover": True,
    },
    {
        "label": "Level 15 = 3·5 — U_3 test (3‖N)",
        "level": 15,
        "targets": None,
        "expect_qdim": None,
        "discover": True,
    },
]


def kernel_dim_test(level, target_dict, q=Q_MOD):
    """Compute qdim = dim(ker(stacked (T_p - a_p*I))) on NEW cuspidal subspace."""
    MS = ModularSymbols(Gamma0(level), 2, sign=1)
    CS = MS.cuspidal_subspace()
    NS = CS.new_subspace()
    n = NS.dimension()

    if n == 0:
        return {"new_dim": 0, "qdim": 0, "primes_used": []}

    Fq = GF(q)
    rows_list = []
    primes_used = []
    for p, ap in sorted(target_dict.items()):
        Tp = NS.hecke_matrix(p)
        Tp_mod = Tp.change_ring(Fq)
        Ip = identity_matrix(Fq, n)
        rows_list.append(Tp_mod - ap * Ip)
        primes_used.append(p)

    big = block_matrix([[r] for r in rows_list])
    ker = big.right_kernel()
    return {"new_dim": n, "qdim": ker.dimension(), "primes_used": primes_used}


def discover_eigenvalues(level, q=Q_MOD):
    """For discovery tests: enumerate all newforms and their eigenvalues."""
    S = CuspForms(Gamma0(level), 2, prec=20)
    newforms = S.newforms('a')
    results = []
    for f in newforms:
        K = f.base_ring()
        is_rational = (K.degree() == 1) if hasattr(K, 'degree') else True
        primes = [p for p in [2, 3, 5, 7, 11, 13] if p <= level + 6]
        eigenvals = {}
        for p in primes:
            try:
                ap = f[p]
                eigenvals[p] = int(ap) if is_rational else str(ap)
            except Exception:
                eigenvals[p] = "?"
        results.append({
            "is_rational": is_rational,
            "degree": K.degree() if hasattr(K, 'degree') else 1,
            "eigenvals": eigenvals,
        })
    return results


print("=" * 70)
print("CQ-3 POSITIVKONTROLLE — End-to-End qdim-Mechanismus-Test")
print(f"Working modulo q={Q_MOD}")
print("=" * 70)
print()

all_pass = True
results_summary = []

for test in TESTS:
    label = test["label"]
    level = test["level"]
    print(f"--- {label} ---")
    t0 = time.time()

    if test.get("discover"):
        print(f"  Discovering newforms at level {level}...")
        nfs = discover_eigenvalues(level)
        print(f"  Found {len(nfs)} Galois orbit(s):")
        for i, nf in enumerate(nfs):
            rat_label = "rational" if nf["is_rational"] else f"non-rational (deg {nf['degree']})"
            ev_str = ", ".join(f"a{p}={nf['eigenvals'][p]}" for p in sorted(nf['eigenvals']))
            print(f"    [{i}] ({rat_label}) {ev_str}")

            if nf["is_rational"]:
                rat_eigenvals = {p: v for p, v in nf["eigenvals"].items() if isinstance(v, int)}
                if rat_eigenvals:
                    print(f"  Testing qdim with rational eigenvalues: {rat_eigenvals}")
                    r = kernel_dim_test(level, rat_eigenvals)
                    print(f"  new_dim={r['new_dim']}, qdim={r['qdim']} (primes: {r['primes_used']})")

                    print(f"  Testing WRONG eigenvalues (negate a_3 if present)...")
                    wrong = dict(rat_eigenvals)
                    if 3 in wrong:
                        wrong[3] = -wrong[3]
                        label_wrong = f"a_3 flipped: {wrong[3]}"
                    else:
                        first_p = sorted(wrong.keys())[0]
                        wrong[first_p] = wrong[first_p] + 1
                        label_wrong = f"a_{first_p} shifted"
                    r2 = kernel_dim_test(level, wrong)
                    print(f"  WRONG ({label_wrong}): qdim={r2['qdim']}")

                    status = "PASS" if r["qdim"] == 1 and r2["qdim"] == 0 else "FAIL"
                    print(f"  -> {status}")
                    if status == "FAIL":
                        all_pass = False
                    results_summary.append(
                        f"  {label}: correct→qdim={r['qdim']}, wrong→qdim={r2['qdim']} [{status}]"
                    )

        elapsed = time.time() - t0
        print(f"  ({elapsed:.1f}s)")
        print()
        continue

    targets = test["targets"]
    expect = test["expect_qdim"]

    r = kernel_dim_test(level, targets)
    elapsed = time.time() - t0

    status = "PASS" if r["qdim"] == expect else "FAIL"
    if status == "FAIL":
        all_pass = False

    print(f"  new_dim={r['new_dim']}, qdim={r['qdim']} (expected {expect})")
    print(f"  primes used: {r['primes_used']}")
    print(f"  -> {status} ({elapsed:.1f}s)")
    print()

    results_summary.append(f"  {label}: qdim={r['qdim']} (expected {expect}) [{status}]")

print("=" * 70)
print("CQ-3 SUMMARY")
print("=" * 70)
for line in results_summary:
    print(line)
print()
if all_pass:
    print("ALL TESTS PASSED — qdim mechanism correctly detects qdim=1 and qdim=0")
else:
    print("*** SOME TESTS FAILED ***")
