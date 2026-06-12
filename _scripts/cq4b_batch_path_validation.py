#!/usr/bin/env python3
"""CQ-4b: Batch-Path Validation — Single-Shot vs. Batched Hecke Accumulation.

CQ-4 (v2) confirmed that the production solver's single-shot Hecke path
produces the same qdim as canonical Sage at 8 levels (including 5 multi-dim).

However, the 240672 production run uses the BATCHED path:
  --hecke-batch-size 1000 --hecke-row-order natural --no-stop-on-zero

CQ-4b closes this gap by running the SAME levels through BOTH paths
(single-shot and batched) and verifying identical qdim.

Tests (3 Tier-2 levels spanning key regimes):
  Level 291: 3||291, new_dim=17, batch_size=5 -> ~3-4 batches/prime
  Level 219: 3||219, new_dim=13, batch_size=4 -> ~3-4 batches/prime
  Level 269: prime,  new_dim=22, batch_size=5 -> ~4-5 batches/prime

Usage (Mac Studio):
  export PATH=/Users/lukas/mamba/envs/sage/bin:$PATH
  cd /Users/lukas/compute/abc_hct
  python cq4b_batch_path_validation.py 2>&1 | tee cq4b_output.log
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
    {
        "label": "Level 291 (3||291, new_dim=17)",
        "level": 291,
        "eigenvalues": {2: -2, 3: -1, 5: 3, 7: -2, 11: 0, 13: -4},
        "primes": [2, 3, 5, 7, 11, 13],
        "batch_size": 5,
    },
    {
        "label": "Level 219 (3||219, new_dim=13)",
        "level": 219,
        "eigenvalues": {2: -2, 3: -1, 5: -1, 7: 2, 11: -4, 13: -2},
        "primes": [2, 3, 5, 7, 11, 13],
        "batch_size": 4,
    },
    {
        "label": "Level 269 (prime, new_dim=22)",
        "level": 269,
        "eigenvalues": {2: 0, 3: 0, 5: 1, 7: -4, 11: -3, 13: 2},
        "primes": [2, 3, 5, 7, 11, 13],
        "batch_size": 5,
    },
]


def run_solver(level, eigenvalues, primes, batch_size=0):
    """Run production solver with optional batch mode. Returns (qdim, error_msg)."""
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
            "--hecke-row-order", "natural",
            "--progress",
            "--out-json", out_json,
        ]

        if batch_size > 0:
            argv.extend([
                "--hecke-batch-size", str(batch_size),
                "--no-stop-on-zero",
            ])

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
    print("CQ-4b: BATCH-PATH VALIDATION")
    print("Single-Shot vs. Batched Hecke Accumulation")
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
        batch_size = test["batch_size"]

        print(f"--- {label} ---")
        print(f"  Eigenvalues: {eigenvalues}")
        print(f"  Primes: {primes}")
        print(f"  Batch size: {batch_size}")
        print()

        t0 = time.time()
        single_qdim, err1 = run_solver(level, eigenvalues, primes, batch_size=0)
        t_single = time.time() - t0
        if err1:
            print(f"  Single-shot: ERROR: {err1}")
            all_pass = False
            results.append({"label": label, "status": "ERROR", "error": err1})
            continue
        print(f"  Single-shot: qdim={single_qdim} ({t_single:.1f}s)")

        t0 = time.time()
        batch_qdim, err2 = run_solver(level, eigenvalues, primes, batch_size=batch_size)
        t_batch = time.time() - t0
        if err2:
            print(f"  Batched:     ERROR: {err2}")
            all_pass = False
            results.append({"label": label, "status": "ERROR", "error": err2})
            continue
        print(f"  Batched (bs={batch_size}): qdim={batch_qdim} ({t_batch:.1f}s)")

        if single_qdim == batch_qdim:
            status = "MATCH"
            print(f"  -> MATCH (both qdim={single_qdim})")
        else:
            status = "MISMATCH"
            all_pass = False
            print(f"  -> MISMATCH! Single={single_qdim}, Batched={batch_qdim}")

        results.append({
            "label": label,
            "level": level,
            "single_qdim": single_qdim,
            "batch_qdim": batch_qdim,
            "batch_size": batch_size,
            "status": status,
        })
        print()
        sys.stdout.flush()

    print("=" * 70)
    print("CQ-4b SUMMARY")
    print("=" * 70)
    for r in results:
        v = r["status"]
        if v == "ERROR":
            print(f"  [{v}] {r['label']}: {r.get('error', 'unknown')}")
        else:
            print(f"  [{v}] {r['label']}: single={r['single_qdim']}, batched={r['batch_qdim']} (bs={r['batch_size']})")
    print()

    if all_pass:
        print("ALL TESTS MATCHED")
        print("Batch-path produces identical qdim to single-shot path.")
        print("This validates that the 240672 production run's batched accumulation")
        print("is faithful to the single-shot Hecke computation.")
    else:
        print("*** MISMATCH DETECTED ***")
        print("Batch path disagrees with single-shot path!")
        print("The 240672 production run's batched accumulation may be unfaithful.")

    sys.exit(0 if all_pass else 1)
