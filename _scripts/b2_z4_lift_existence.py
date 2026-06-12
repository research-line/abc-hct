#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (m): Z/4-Lift-Existenz des p2-Kernvektors — exakter F2-Solver.

Frage: Hebt der p2-Kernvektor v (F2, Support 21.128) zu einem Z/4-Kern
vtilde = v + 2w, M vtilde == 0 mod 4?  Mit S1 (Mv == 0 mod 2) ist das
aequivalent zum linearen F2-System

    M w == r (mod 2),   r := (M v mod 4) / 2.

Loesung per bitgepacktem Gauss-Jordan ueber F2 (uint64-Worte, numpy-XOR).
Bei Loesbarkeit wird w extrahiert und vtilde UNABHAENGIG verifiziert
(sparse Integer-Produkt mod 4 == 0). Existenz => Frustrations-Gesetz (G3)
auf rein-+-1-Zeilen wird ein Satz (3-Zeilen-Argument, siehe
MG_b2_p2_frustration_law_2026-06-11.md par.4).
"""

import json
import sys
import time
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix

SRC = "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl"
CK = "_results/mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json"
Q = 3863
N = 31680
OUT_JSON = "_results/b2_z4_lift_existence_{}.json".format(date.today())


def main():
    t0 = time.time()
    rows, cols, vals = [], [], []
    nrows = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            rr = json.loads(line)
            for c, val in rr["row"]:
                val = val if val <= Q // 2 else val - Q
                rows.append(nrows); cols.append(c); vals.append(int(val))
            nrows += 1
    M = csr_matrix(coo_matrix((vals, (rows, cols)), shape=(nrows, N)), dtype=np.int64)
    v = np.zeros(N, dtype=np.int64)
    v[np.array(json.load(open(CK, encoding="utf-8"))["kernel_support"])] = 1

    Mv = np.asarray(M @ v).ravel() % 4
    assert (Mv % 2 == 0).all(), "S1 verletzt?!"
    r = (Mv // 2).astype(np.uint8)  # 0/1
    print("System aufgebaut: r hat {} Einsen von {} ({:.1f}s)".format(
        int(r.sum()), nrows, time.time() - t0), flush=True)

    # --- Bitgepackte augmentierte Matrix [M mod 2 | r] ---
    W = (N + 1 + 63) // 64
    B = np.zeros((nrows, W), dtype=np.uint64)
    Mcoo = M.tocoo()
    odd = (Mcoo.data % 2) != 0
    ri, ci = Mcoo.row[odd], Mcoo.col[odd]
    for k in range(len(ri)):
        B[ri[k], ci[k] >> 6] |= np.uint64(1) << np.uint64(ci[k] & 63)
    rsel = np.where(r == 1)[0]
    B[rsel, N >> 6] |= np.uint64(1) << np.uint64(N & 63)
    print("Bitmatrix gebaut: {} x {} Worte ({:.1f}s)".format(*B.shape, time.time() - t0), flush=True)

    # --- Gauss-Jordan ueber F2 ---
    row_used = np.zeros(nrows, dtype=bool)
    pivot_row_of_col = np.full(N, -1, dtype=np.int64)
    rank = 0
    for col in range(N):
        wi = col >> 6
        bit = np.uint64(1) << np.uint64(col & 63)
        has = (B[:, wi] & bit) != 0
        cand = np.where(has & (~row_used))[0]
        if len(cand) == 0:
            continue
        p = int(cand[0])
        row_used[p] = True
        pivot_row_of_col[col] = p
        rank += 1
        elim = has.copy()
        elim[p] = False
        if elim.any():
            B[elim] ^= B[p]
        if col % 4000 == 0:
            print("  col {} rank {} ({:.1f}s)".format(col, rank, time.time() - t0), flush=True)

    # --- Konsistenz: Nullzeilen mit gesetztem r-Bit? ---
    rbit_wi = N >> 6
    rbit = np.uint64(1) << np.uint64(N & 63)
    mword_mask = np.ones(W, dtype=np.uint64) * np.uint64(0xFFFFFFFFFFFFFFFF)
    # Maske: im letzten M-Wort nur Bits < (N mod 64) zaehlen, r-Bit separat
    zero_m = np.ones(nrows, dtype=bool)
    for wi_ in range(W):
        word = B[:, wi_].copy()
        if wi_ == rbit_wi:
            word &= ~rbit
        zero_m &= (word == 0)
    inconsistent = zero_m & ((B[:, rbit_wi] & rbit) != 0)
    n_inc = int(inconsistent.sum())
    solvable = (n_inc == 0)
    print("Rang mod 2: {} | Kern-Dim: {} | inkonsistente Zeilen: {} -> {} ({:.1f}s)".format(
        rank, N - rank, n_inc, "LOESBAR" if solvable else "UNLOESBAR", time.time() - t0), flush=True)

    result = {"date": str(date.today()), "rank_mod2": int(rank),
              "kernel_dim_mod2": int(N - rank), "r_ones": int(r.sum()),
              "n_inconsistent": n_inc, "z4_lift_exists": bool(solvable)}

    if solvable:
        w = np.zeros(N, dtype=np.int64)
        for col in range(N):
            pr = pivot_row_of_col[col]
            if pr >= 0 and (B[pr, rbit_wi] & rbit) != 0:
                w[col] = 1
        vt = (v + 2 * w) % 4
        check = np.asarray(M @ vt).ravel() % 4
        ok = bool((check == 0).all())
        result["verification_Mvtilde_mod4_zero"] = ok
        result["vtilde_value_counts"] = {str(k): int((vt == k).sum()) for k in range(4)}
        print("VERIFIKATION M*vtilde mod 4 == 0:", ok, flush=True)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("JSON:", OUT_JSON, " total {:.1f}s".format(time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
