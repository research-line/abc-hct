#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (i): Mikro-Cluster-Klassifikation am 60168-Zeugen + C1-Vorbereitung.

Universalitaets-Test der (f)/(g)-Klassifikation vom 240672-Zeugen auf dem
zweiten Level: (1) Gewichtsprofil + Kern w>=0.5 + Komponenten,
(2) Schicht-Signaturen (hier nur maninT + T5, keine U3-Schicht),
(3) Block-Spektren ALLER Mikro-Cluster -> exakte duenne Kerne,
(4) Export der Mikro-Cluster-/Kern-Spalten fuer das Matching gegen die
    bekannten S5-/Paritaets-Kernklassen (C1-Einstieg).
"""

import json
import sys
import time
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix
from scipy.sparse.csgraph import connected_components

SRC = "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 31680
OUT_JSON = "_results/b2_microcluster_60168_c1_match_{}.json".format(date.today())
OUT_MD = "_results/b2_microcluster_60168_c1_match_{}.md".format(date.today())

LAYER_OF = {"manin_T_relations_after_SI": "maninT", "T_5_minus_2": "T5"}
LAYERS = ("maninT", "T5")


def main():
    t0 = time.time()
    rows, cols, vals, row_layer = [], [], [], []
    n = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            row_layer.append(LAYER_OF.get(r["stage"].split("_batch")[0], "?"))
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n); cols.append(c); vals.append(float(v))
            n += 1
    row_layer = np.array(row_layer)
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n, NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    col_nnz = np.diff(A.indptr)
    absA = np.abs(A.data)
    print("A: {}x{}, nnz={} ({:.1f}s)".format(n, NCOLS, A.nnz, time.time() - t0), flush=True)

    C = (A.T @ A).tocoo()
    off = C.row < C.col
    gi, gj, gv = C.row[off], C.col[off], C.data[off]
    gw = np.abs(gv) / (norms[gi] * norms[gj])
    nz = gw > 1e-15
    gi, gj, gw = gi[nz], gj[nz], gw[nz]

    report = {"date": str(date.today()), "level": 60168, "q": Q,
              "matrix": {"rows": int(n), "cols": NCOLS, "nnz": int(A.nnz)},
              "entry_profile": {"frac_abs1": float((absA == 1).mean()),
                                 "frac_abs_le2": float((absA <= 2).mean())},
              "n_edges": int(len(gw)),
              "weight_profile": {
                  "median": float(np.median(gw)),
                  "p99": float(np.quantile(gw, 0.99)),
                  "max": float(gw.max()),
                  "n_ge_05": int((gw >= 0.5).sum()),
                  "n_exact_parallel": int((gw > 1 - 1e-9).sum())}}

    # Mikro-Cluster w >= 0.5
    mh = gw >= 0.5
    hi, hj = gi[mh], gj[mh]
    sub = coo_matrix((np.ones(int(mh.sum())), (hi, hj)), shape=(NCOLS, NCOLS))
    ncomp, labels = connected_components(sub.tocsr(), directed=False)
    counts = np.bincount(labels)
    comp_ids = np.where(counts >= 2)[0]
    comp_size_hist = {}
    for cid in comp_ids:
        k = int(counts[cid])
        comp_size_hist[k] = comp_size_hist.get(k, 0) + 1
    kern_cols = np.unique(np.concatenate([hi, hj])) if len(hi) else np.array([], dtype=int)
    report["kernel_05"] = {
        "n_heavy_edges": int(mh.sum()),
        "n_kernel_cols": int(len(kern_cols)),
        "frac_kernel_cols": float(len(kern_cols) / NCOLS),
        "n_components_ge2": int(len(comp_ids)),
        "comp_size_hist": {str(k): v for k, v in sorted(comp_size_hist.items())},
        "comp_size_max": int(counts[comp_ids].max()) if len(comp_ids) else 0,
    }
    print("Kern 0.5: {} Kanten, {} Spalten, {} Komponenten ({:.1f}s)".format(
        int(mh.sum()), len(kern_cols), len(comp_ids), time.time() - t0), flush=True)

    # Schicht-Signaturen der schweren Kanten
    P = A.copy(); P.data = np.ones_like(P.data)
    Pr = P.tocsr()
    sig = []
    for lay in LAYERS:
        Pl = Pr[row_layer == lay]
        Ml = (Pl.T @ Pl).tocsr()
        sig.append(np.asarray(Ml[hi, hj]).ravel().astype(int))
    sig = np.stack(sig, axis=1)
    keys, kcounts = np.unique(sig, axis=0, return_counts=True)
    top_sig = sorted(zip(keys.tolist(), kcounts.tolist()), key=lambda x: -x[1])[:10]
    report["heavy_edge_layer_signatures_maninT_T5"] = [
        {"sig": k, "count": c} for k, c in top_sig]
    nnz_lo = np.minimum(col_nnz[hi], col_nnz[hj])
    nnz_hi2 = np.maximum(col_nnz[hi], col_nnz[hj])
    pk, pc = np.unique(np.stack([nnz_lo, nnz_hi2], axis=1), axis=0, return_counts=True)
    report["heavy_edge_colnnz_pairs_top"] = [
        {"pair": k, "count": c} for k, c in
        sorted(zip(pk.tolist(), pc.tolist()), key=lambda x: -x[1])[:8]]

    # Block-Spektren aller Mikro-Cluster -> exakte Kerne
    singular = []
    lam_mins = []
    for cid in comp_ids:
        S = np.where(labels == cid)[0]
        Asub = A[:, S].toarray() / norms[S]
        G = Asub.T @ Asub
        ev, evec = np.linalg.eigh(G)
        lam_mins.append(float(ev[0]))
        if ev[0] < 1e-10:
            x = evec[:, 0]
            xs = np.zeros(NCOLS); xs[S] = x / norms[S]
            res = float(np.abs(A @ xs).max())
            singular.append({"cols": S.tolist(), "size": int(len(S)),
                             "kernel_vec": [round(float(t), 4) for t in x],
                             "col_nnz": col_nnz[S].tolist(),
                             "verify_Ax_inf": res})
    lam_mins = np.array(lam_mins) if len(lam_mins) else np.array([1.0])
    report["block_spectra"] = {
        "n_singular": len(singular),
        "singular_blocks": singular,
        "lambda_min_p1": float(np.quantile(lam_mins, 0.01)),
        "lambda_min_median": float(np.median(lam_mins)),
        "n_lt_0.3": int((lam_mins < 0.3).sum()),
    }
    print("Block-Spektren: {} singulaer ({:.1f}s)".format(len(singular), time.time() - t0), flush=True)

    # Export fuer C1-Matching
    report["export_for_c1"] = {
        "kernel_cols_05": kern_cols.tolist(),
        "components": {str(int(cid)): np.where(labels == cid)[0].tolist() for cid in comp_ids},
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(i): Mikro-Cluster am 60168-Zeugen + C1-Vorbereitung ({})".format(date.today()), ""]
    wp = report["weight_profile"]
    lines.append("Matrix {}×{} (nnz {}), Einträge ±1: {:.1%}. Kanten: {} | w-Median {:.4f}, p99 {:.4f}, max {:.4f} | exakt parallel: {}".format(
        n, NCOLS, A.nnz, report["entry_profile"]["frac_abs1"], report["n_edges"],
        wp["median"], wp["p99"], wp["max"], wp["n_exact_parallel"]))
    k5 = report["kernel_05"]
    lines.append("")
    lines.append("**Kern w ≥ 0.5:** {} Kanten, {} Spalten ({:.2%}), {} Komponenten, Größen-Histogramm {} (max {}).".format(
        k5["n_heavy_edges"], k5["n_kernel_cols"], k5["frac_kernel_cols"],
        k5["n_components_ge2"], k5["comp_size_hist"], k5["comp_size_max"]))
    lines.append("")
    lines.append("Schicht-Signaturen (maninT, T₅) top: " + ", ".join(
        "{}×{}".format(tuple(d["sig"]), d["count"]) for d in report["heavy_edge_layer_signatures_maninT_T5"][:6]))
    lines.append("")
    bs = report["block_spectra"]
    lines.append("**Block-Spektren:** {} singulär (echte dünne Kerne); λ_min p1 {:.3f}, median {:.3f}; Blöcke < 0.3: {}.".format(
        bs["n_singular"], bs["lambda_min_p1"], bs["lambda_min_median"], bs["n_lt_0.3"]))
    for s in singular:
        lines.append("- singulär: Spalten {} (nnz {}), Kernvektor {}, ‖Ax‖_∞ = {}".format(
            s["cols"], s["col_nnz"], s["kernel_vec"], s["verify_Ax_inf"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
