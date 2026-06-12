#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 (p) Stufe 1: Kern-Basis mod 2 des 240672-rc3c-Systems + Dimer-Defekt-Profile.

240672 hat keinen p2-Repair-Witness; der rc3c-Kern mod 2 ist >= 48-dim.
Stufe 1: Kernbasis berechnen (Python-Int-Bitmasken-Gauss), fuer jeden
Basisvektor + alle Paar-Summen das manin-Dimer-Defekt-Profil
(#Dreiecke mit m=0; Dimer-Kandidat <=> 0 Defekte) und das m-Gesetz messen.
60168-Praezedenz: v war die Summe der BEIDEN Basisvektoren — Dimer-Vektoren
sitzen in kleinen Kombinationen. Ausgabe als npz fuer Stufe 2.
"""

import json
import sys
import time
from collections import Counter
from datetime import date

import numpy as np

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
N = 126720
OUT_JSON = "_results/b2_kernel_basis_240672_{}.json".format(date.today())
OUT_NPZ = "_results/b2_kernel_basis_240672_{}.npz".format(date.today())


def main():
    t0 = time.time()
    triangles = []
    basis = {}
    nrows = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ent = [(c, (val if val <= Q // 2 else val - Q)) for c, val in r["row"]]
            if r["stage"].startswith("manin"):
                odd = [c for c, val in ent if val % 2 != 0]
                if len(odd) == 3:
                    triangles.append(odd)
            row = 0
            for c, val in ent:
                if val % 2 != 0:
                    row |= (1 << c)
            while row:
                p = row.bit_length() - 1
                if p in basis:
                    row ^= basis[p]
                else:
                    basis[p] = row
                    break
            nrows += 1
            if nrows % 20000 == 0:
                print("  {} Zeilen, Rang {} ({:.1f}s)".format(nrows, len(basis), time.time() - t0), flush=True)
    rank = len(basis)
    free_cols = [c for c in range(N) if c not in basis]
    print("Rang mod 2: {} | Kern-Dim: {} ({:.1f}s)".format(rank, len(free_cols), time.time() - t0), flush=True)

    # Kernvektoren via aufsteigende Substitution -> direkt als uint8-Arrays
    K = len(free_cols)
    KV = np.zeros((K, N), dtype=np.uint8)
    pivots_sorted = sorted(basis)
    for ki, fcol in enumerate(free_cols):
        xbits = 1 << fcol
        for p in pivots_sorted:
            row = basis[p] & ~(1 << p)
            if (row & xbits).bit_count() & 1:
                xbits |= 1 << p
        bb = xbits.to_bytes((N + 7) // 8, "little")
        KV[ki] = np.unpackbits(np.frombuffer(bb, dtype=np.uint8), bitorder="little")[:N]
        if (ki + 1) % 50 == 0:
            print("  Kernvektor {}/{} ({:.1f}s)".format(ki + 1, K, time.time() - t0), flush=True)
    np.savez_compressed(OUT_NPZ, KV=KV)
    print("Kernbasis gespeichert ({:.1f}s)".format(time.time() - t0), flush=True)

    # Defekt-Profile vektorisiert: Dreiecke als Index-Array
    TRI = np.array(triangles, dtype=np.int64)  # (T, 3)
    def defects(x):
        m = x[TRI].sum(axis=1)
        return int((m == 0).sum()), {str(k): int(c) for k, c in zip(*np.unique(m, return_counts=True))}

    profiles = {}
    for i in range(K):
        d, mh = defects(KV[i])
        profiles["k{}".format(i)] = {"support": int(KV[i].sum()), "defects_m0": d, "m_hist": mh}
    singles = sorted(((n, p["defects_m0"]) for n, p in profiles.items()), key=lambda x: x[1])
    print("Einzel: beste Defekte:", singles[:6], flush=True)

    # Alle Paar-Summen (vektorisiert pro Paar)
    pair_best = []
    for i in range(K):
        xi = KV[i]
        for j in range(i + 1, K):
            x = xi ^ KV[j]
            m = x[TRI].sum(axis=1)
            pair_best.append((i, j, int((m == 0).sum())))
    pair_best.sort(key=lambda t_: t_[2])
    print("Paare: beste:", pair_best[:8], "({:.1f}s)".format(time.time() - t0), flush=True)

    # Greedy-Hill-Climb von den 5 besten Starts (Einzel + Paare)
    starts = [KV[int(singles[s][0][1:])].copy() for s in range(min(3, K))]
    for (i, j, _) in pair_best[:3]:
        starts.append(KV[i] ^ KV[j])
    greedy_results = []
    for sx, x0 in enumerate(starts):
        x = x0.copy()
        d0, _ = defects(x)
        improved = True
        path = [d0]
        while improved and d0 > 0:
            improved = False
            best_i, best_d = -1, d0
            for i in range(K):
                d1, _ = defects(x ^ KV[i])
                if d1 < best_d:
                    best_d, best_i = d1, i
            if best_i >= 0:
                x ^= KV[best_i]
                d0 = best_d
                path.append(d0)
                improved = True
        greedy_results.append({"start": sx, "final_defects": d0, "path": path,
                               "support": int(x.sum())})
        print("Greedy start {}: Defekt-Pfad {} (final {})".format(sx, path, d0), flush=True)
        if d0 == 0:
            np.save("_results/b2_dimer_vector_240672_{}.npy".format(date.today()), x)
            print("  DIMER-VEKTOR GEFUNDEN UND GESPEICHERT", flush=True)
            break

    report = {"date": str(date.today()), "rank_mod2": rank, "kernel_dim": K,
              "n_triangles": len(triangles),
              "single_best": singles[:20],
              "pair_best": pair_best[:20],
              "greedy": greedy_results}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("JSON:", OUT_JSON, " total {:.1f}s".format(time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
