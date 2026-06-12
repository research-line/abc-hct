#!/usr/bin/env python3
"""
M-DET Stufe 1a: Rangabfall-Primes des 60168-Witness-Systems (Sage, Mac).

Satz-A-Entscheidungstest (MG_conditional_single_curve_theorem_2026-06-12.md §4):
rank des rc3c-60168-Witness-Systems (31.680 x 31.680, symmetrischer Lift)
ueber GF(p) fuer eine Liste von Primes. Der Modalwert = rank_Q; Primes mit
rank_p < rank_Q sind die Teiler der Pivot-Minoren-Determinante D(W).

Vorhersage (Block-det-Inventar 2026-06-11, Ausnahme-q = {2, 3, 19}):
Rangabfall nur bei {2, 3}-Verwandten (+ evtl. 19, bad primes 23/109).
Trifft das zu, ist D(W) support-lokal -> Satz A wird konkret; tauchen
unerwartete grosse Primes auf, ist die det-Struktur nicht-lokal.

Output: _results/mdet_rank_drop_primes_60168_<date>.{json,md}
"""
import json, sys, time
from datetime import date
from pathlib import Path

WITNESS = Path("_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl")
WQ = 3863
N = 31680
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97, 109, 997, 1009, 3863, 5077]
OUT_JSON = "_results/mdet_rank_drop_primes_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet_rank_drop_primes_60168_{}.md".format(date.today())


def main():
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    print("=== M-DET 1a: rank drops, 60168 witness ===")
    from sage.all import GF, matrix

    half = WQ // 2
    entries = {}
    nrows = 0
    with open(WITNESS) as f:
        for line in f:
            rec = json.loads(line)
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WQ
                if v:
                    entries[(nrows, int(c))] = v
            nrows += 1
    if nrows != 31680:
        print(f"FATAL: {nrows} Zeilen, erwartet 31680 (Witness-Guard). ABBRUCH.")
        return 3
    print(f"[{ts()}] Witness: {nrows} Zeilen, nnz={len(entries)} ({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    results = {}
    for p in PRIMES:
        t1 = time.time()
        Fp = GF(p)
        M = matrix(Fp, nrows, N, {k: Fp(v) for k, v in entries.items()}, sparse=True)
        r = M.rank()
        results[p] = int(r)
        print(f"[{ts()}] p={p}: rank={r} ({time.time()-t1:.0f}s)")
        sys.stdout.flush()

    from collections import Counter
    rank_q = Counter(results.values()).most_common(1)[0][0]
    drops = {p: rank_q - r for p, r in results.items() if r < rank_q}
    report = {"date": str(date.today()), "level": 60168, "nrows": nrows,
              "nnz": len(entries), "primes": PRIMES, "ranks": {str(p): r for p, r in results.items()},
              "rank_Q_modal": rank_q,
              "rank_drop_primes": {str(p): d for p, d in sorted(drops.items())},
              "prediction_block_inventory": [2, 3, 19],
              "verdict_support_local": sorted(drops.keys()) and all(
                  p in (2, 3, 19, 23, 109) for p in drops)}
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# M-DET 1a: Rangabfall-Primes des 60168-Witness-Systems ({})".format(date.today()), ""]
    lines.append("| p | rank_p | Defekt (rank_Q − rank_p) |")
    lines.append("|---|---|---|")
    for p in PRIMES:
        lines.append("| {} | {} | {} |".format(p, results[p], rank_q - results[p]))
    lines.append("")
    lines.append("rank_Q (Modalwert) = {} | Rangabfall-Primes: {} | Block-Inventar-Vorhersage: {{2, 3, 19}} | support-lokal: {}".format(
        rank_q, dict(sorted(drops.items())), report["verdict_support_local"]))
    lines.append("")
    lines.append("Total: {:.0f}s".format(time.time() - t0))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
