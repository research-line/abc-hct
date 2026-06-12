#!/usr/bin/env python3
"""CQ-3 Positivkontrolle v2.1: Production Solver Instrument Test.

Tests the ACTUAL production solver code path (ManinSymbolList + HeilbronnCremona
+ sparse_2term_quotient + incremental rank) at small levels where ground truth
is known from LMFDB.

Strategy: monkeypatch frey_ap() to inject known eigenvalues, then call main()
with the production solver's full pipeline.

Tests (cremona convention):
  1. Level 11 (11.2.a.a): correct eigenvalues → qdim>0
  2. Level 11: wrong a_3 → qdim=0
  3. Level 14 (14.2.a.a): correct eigenvalues → qdim>0
  4. Level 14: wrong a_3 → qdim=0
  5. Level 33 (3*11, 3||N): correct eigenvalues (no p=3) → qdim>0
  6. Level 33: wrong eigenvalues → qdim=0

Gap-1 tests (U_3 discrimination at 3||N):
  7. Level 33 + p=3: correct a_3=-1 (LMFDB) → qdim>0
  8. Level 33 + p=3: flipped a_3=+1 → qdim=0

Gap-2 tests (convention discrimination — standard vs cremona):
  9-11. Level 11/14/33 correct eigenvalues with --hecke-family standard

Usage (Mac Studio):
  export PATH=/Users/lukas/mamba/envs/sage/bin:$PATH
  cd /Users/lukas/compute/abc_hct
  python cq3_production_harness.py 2>&1 | tee cq3_v2.1_output.log
"""
import os, sys, time, json, tempfile
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
if os.path.isdir("_scripts"):
    sys.path.insert(0, "_scripts")

import mstar_nomagma_sparse_hecke_quotient as solver

TESTS_CREMONA = [
    {
        "label": "[cremona] Level 11 — correct LMFDB eigenvalues (11.2.a.a)",
        "level": 11,
        "eigenvalues": {2: -2, 3: -1, 5: 1, 7: -2},
        "primes": [2, 3, 5, 7],
        "expect_qdim_positive": True,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 11 — WRONG a_3 (+1 statt -1)",
        "level": 11,
        "eigenvalues": {2: -2, 3: 1, 5: 1, 7: -2},
        "primes": [2, 3, 5, 7],
        "expect_qdim_positive": False,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 14 — correct LMFDB eigenvalues (14.2.a.a)",
        "level": 14,
        "eigenvalues": {2: -1, 3: -2, 5: 0, 13: -4},
        "primes": [2, 3, 5, 13],
        "expect_qdim_positive": True,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 14 — WRONG a_3 (+2 statt -2)",
        "level": 14,
        "eigenvalues": {2: -1, 3: 2, 5: 0, 13: -4},
        "primes": [2, 3, 5, 13],
        "expect_qdim_positive": False,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 33 = 3*11, correct LMFDB eigenvalues (33.2.a.a)",
        "level": 33,
        "eigenvalues": {2: 1, 5: -2, 7: 4, 11: 1},
        "primes": [2, 5, 7, 11],
        "expect_qdim_positive": True,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 33 — WRONG a_7 (0 statt 4)",
        "level": 33,
        "eigenvalues": {2: 1, 5: -2, 7: 0, 11: 1},
        "primes": [2, 5, 7, 11],
        "expect_qdim_positive": False,
        "hecke_family": "cremona",
    },
]

TESTS_GAP1_U3 = [
    {
        "label": "[cremona] Level 33 + U_3 — correct a_3=-1 (LMFDB 33.2.a.a)",
        "level": 33,
        "eigenvalues": {2: 1, 3: -1, 5: -2, 7: 4, 11: 1},
        "primes": [2, 3, 5, 7, 11],
        "expect_qdim_positive": True,
        "hecke_family": "cremona",
    },
    {
        "label": "[cremona] Level 33 + U_3 — WRONG a_3=+1 (flipped)",
        "level": 33,
        "eigenvalues": {2: 1, 3: 1, 5: -2, 7: 4, 11: 1},
        "primes": [2, 3, 5, 7, 11],
        "expect_qdim_positive": False,
        "hecke_family": "cremona",
    },
]

TESTS_GAP2_STANDARD = [
    {
        "label": "[standard] Level 11 — correct eigenvalues, WRONG convention",
        "level": 11,
        "eigenvalues": {2: -2, 3: -1, 5: 1, 7: -2},
        "primes": [2, 3, 5, 7],
        "expect_qdim_positive": False,
        "hecke_family": "standard",
    },
    {
        "label": "[standard] Level 14 — correct eigenvalues, WRONG convention",
        "level": 14,
        "eigenvalues": {2: -1, 3: -2, 5: 0, 13: -4},
        "primes": [2, 3, 5, 13],
        "expect_qdim_positive": False,
        "hecke_family": "standard",
    },
    {
        "label": "[standard] Level 33 — correct eigenvalues, WRONG convention",
        "level": 33,
        "eigenvalues": {2: 1, 5: -2, 7: 4, 11: 1},
        "primes": [2, 5, 7, 11],
        "expect_qdim_positive": False,
        "hecke_family": "standard",
    },
]

TESTS = TESTS_CREMONA + TESTS_GAP1_U3 + TESTS_GAP2_STANDARD


def run_test(test):
    """Run one positive-control test through the production solver."""
    label = test["label"]
    level = test["level"]
    eigenvalues = test["eigenvalues"]
    primes = test["primes"]
    expect_positive = test["expect_qdim_positive"]
    hecke_family = test.get("hecke_family", "cremona")

    print(f"\n{'='*70}")
    print(f"TEST: {label}")
    print(f"  Level: {level}")
    print(f"  Eigenvalues: {eigenvalues}")
    print(f"  Primes: {primes}")
    print(f"  Hecke family: {hecke_family}")
    print(f"  Expect qdim > 0: {expect_positive}")
    print(f"{'='*70}")

    original_frey_ap = solver.frey_ap

    def patched_frey_ap(mode, p):
        if p in eigenvalues:
            return eigenvalues[p]
        return original_frey_ap(mode, p)

    solver.frey_ap = patched_frey_ap

    with tempfile.TemporaryDirectory() as tmpdir:
        out_json = os.path.join(tmpdir, "result.json")
        out_md = os.path.join(tmpdir, "result.md")
        argv = [
            "--backend", "sage",
            "--levels", str(level),
            "--modes", "raw",
            "--primes", *[str(p) for p in primes],
            "--q", "3863",
            "--sign", "1",
            "--hecke-family", hecke_family,
            "--rank-engine", "quotient-numpy-dense",
            "--pivot-strategy", "max",
            "--progress",
            "--out-json", out_json,
            "--out-md", out_md,
        ]

        t0 = time.time()
        try:
            solver.main(argv)
        except SystemExit:
            pass
        elapsed = time.time() - t0

        solver.frey_ap = original_frey_ap

        try:
            with open(out_json, "r") as f:
                result = json.load(f)
        except Exception as e:
            print(f"  ERROR reading result: {e}")
            return {"label": label, "status": "ERROR", "error": str(e)}

    runs = result.get("runs", [])
    if not runs:
        print(f"  ERROR: no runs in result")
        return {"label": label, "status": "ERROR", "error": "no runs"}

    run = runs[0]
    stages = run.get("stages", [])
    if stages:
        last_stage = stages[-1]
        qdim = last_stage.get("quotient_dim", -1)
    else:
        qdim = -1

    status_str = run.get("status", "unknown")
    is_positive = qdim > 0

    if expect_positive:
        passed = is_positive
    else:
        passed = not is_positive

    verdict = "PASS" if passed else "FAIL"
    print(f"\n  Result: status={status_str}, qdim={qdim}")
    print(f"  Expected qdim>0: {expect_positive}, Got qdim>0: {is_positive}")
    print(f"  -> {verdict} ({elapsed:.1f}s)")

    return {
        "label": label,
        "level": level,
        "eigenvalues": eigenvalues,
        "qdim": qdim,
        "status": status_str,
        "expect_positive": expect_positive,
        "got_positive": is_positive,
        "passed": passed,
        "elapsed": elapsed,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CQ-3 POSITIVKONTROLLE v2.1 — Production Solver Instrument Test")
    print("Testing the ACTUAL production code path:")
    print("  ManinSymbolList_gamma0 + HeilbronnCremona + sparse_2term_quotient")
    print("  + quotient-numpy-dense rank engine")
    print(f"Working modulo q=3863")
    print()
    print(f"Test groups:")
    print(f"  A. Cremona core tests: {len(TESTS_CREMONA)} tests")
    print(f"  B. Gap-1 U_3 tests:    {len(TESTS_GAP1_U3)} tests")
    print(f"  C. Gap-2 standard:     {len(TESTS_GAP2_STANDARD)} tests")
    print(f"  Total:                  {len(TESTS)} tests")
    print("=" * 70)

    results = []
    for test in TESTS:
        r = run_test(test)
        results.append(r)
        sys.stdout.flush()

    n_cremona = len(TESTS_CREMONA)
    n_gap1 = len(TESTS_GAP1_U3)
    n_gap2 = len(TESTS_GAP2_STANDARD)

    print("\n" + "=" * 70)
    print("CQ-3 v2.1 SUMMARY — Production Solver Path")
    print("=" * 70)
    all_pass = True

    def print_group(title, group_results):
        global all_pass
        print(f"\n  --- {title} ---")
        for r in group_results:
            v = "PASS" if r.get("passed") else "FAIL"
            if not r.get("passed"):
                all_pass = False
            qdim = r.get("qdim", "?")
            elapsed = r.get("elapsed", 0)
            print(f"    [{v}] {r['label']}: qdim={qdim} ({elapsed:.1f}s)")

    print_group("A. Cremona core", results[:n_cremona])
    print_group("B. Gap-1: U_3 discrimination (3||N)", results[n_cremona:n_cremona + n_gap1])
    print_group("C. Gap-2: standard convention", results[n_cremona + n_gap1:])

    print()
    if all_pass:
        print("ALL TESTS PASSED (11/11)")
        print()
        print("A. Production solver (ManinSymbolList + HeilbronnCremona +")
        print("   sparse_2term_quotient + quotient-numpy-dense) correctly returns")
        print("   qdim>0 for known newforms and qdim=0 for wrong eigenvalues.")
        print()
        print("B. U_3 discrimination CONFIRMED: at 3||N, the solver correctly")
        print("   separates a_3=-1 from a_3=+1 via U_3 operator.")
        print()
        print("C. Convention discrimination CONFIRMED: standard coset reps give")
        print("   qdim=0 even for correct eigenvalues. HeilbronnCremona is essential.")
        print("   This earns the 'korrekte Hecke-Wirkung' claim.")
        print()
        print("This validates the INSTRUMENT, not just the mathematical model.")
    else:
        print("*** SOME TESTS FAILED ***")
        print("The production solver does NOT correctly reproduce known results.")
        print("This would invalidate the 240672 computation!")

    sys.exit(0 if all_pass else 1)
