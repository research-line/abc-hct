#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (n): Extremwert-Modell v2 — Fenster-Tail statt Ball-Tail.

Korrektur zu (k): Die richtige lokale Einheit ist das Radius-1-Fenster
(Spalte + 0.2-Nachbarn, capped 24) — exakt die Einheit, mit der die
Lokalitaets-Reduktion kappa in [0.26, 0.90] gemessen wurde. Modell:

    lambda_min(Ball s) ~ kappa * min ueber ~s Fenster-lambdas
    => Median-Vorhersage: lambda_pred(s) = F_window^{-1}(log 2 / s),
       Korridor [kappa_min, 1] * lambda_pred.

Gemessen wird: (1) F_window aus N_WIN zufaelligen Fenstern (+ Tail-Fit
beta_w -> alpha_pred = 1/beta_w), (2) absolute Vorhersagekurve gegen die
(g2)-ball_rand-Mediane.
"""

import json
import sys
import time
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 126720
SEED = 20260611
DUP = {38007, 120130, 71782, 123997}
N_WIN = 6000
CAP = 24
G2_BALL_RAND = {16: 0.3022, 32: 0.2164, 64: 0.1547, 128: 0.0963, 256: 0.1105,
                512: 0.0568, 1024: 0.0550, 2048: 0.0371, 4096: 0.0369}
KAPPA_RANGE = (0.26, 1.0)
OUT_JSON = "_results/b2_extreme_value_model_v2_{}.json".format(date.today())
OUT_MD = "_results/b2_extreme_value_model_v2_{}.md".format(date.today())


def main():
    t0 = time.time()
    rows, cols, vals = [], [], []
    n = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n); cols.append(c); vals.append(float(v))
            n += 1
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n, NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    C = (A.T @ A).tocoo()
    off = C.row < C.col
    gi, gj, gv = C.row[off], C.col[off], C.data[off]
    gw = np.abs(gv) / (norms[gi] * norms[gj])
    nz = gw > 1e-15
    gi, gj, gw = gi[nz], gj[nz], gw[nz]
    m2 = gw >= 0.2
    adj = [[] for _ in range(NCOLS)]
    for a, b in zip(gi[m2], gj[m2]):
        if a in DUP or b in DUP:
            continue
        adj[a].append(b); adj[b].append(a)
    rng = np.random.default_rng(SEED)
    cands = np.array([c for c in range(NCOLS) if adj[c] and c not in DUP])
    print("Graph bereit, {} Spalten mit Nachbarn ({:.1f}s)".format(len(cands), time.time() - t0), flush=True)

    def lam_min(S):
        Asub = A[:, S]
        G = (Asub.T @ Asub).toarray()
        ns = norms[S]
        return float(np.linalg.eigvalsh(G / np.outer(ns, ns))[0])

    lams = []
    for c in rng.choice(cands, N_WIN, replace=False):
        T = [int(c)] + adj[int(c)][:CAP - 1]
        lams.append(lam_min(np.array(T)))
    lams = np.array(sorted(lams))
    print("Fenster-Verteilung fertig ({:.1f}s)".format(time.time() - t0), flush=True)

    # Tail-Fit
    ntail = max(40, int(0.10 * N_WIN))
    x = np.log(lams[:ntail])
    y = np.log((np.arange(ntail) + 1) / N_WIN)
    beta_w, _ = np.polyfit(x, y, 1)

    # Absolute Vorhersage: Median des Minimums von s i.i.d.-Draws = F^{-1}(1-2^{-1/s}) ~ F^{-1}(log2/s)
    pred = {}
    for s, meas in G2_BALL_RAND.items():
        qq = min(max(np.log(2) / s, 1.0 / N_WIN), 0.999)
        lam_pred = float(np.quantile(lams, qq))
        pred[s] = {"measured_g2": meas, "predicted": lam_pred,
                   "corridor": [KAPPA_RANGE[0] * lam_pred, lam_pred],
                   "in_corridor": bool(KAPPA_RANGE[0] * lam_pred <= meas <= lam_pred)}

    report = {"date": str(date.today()), "n_windows": N_WIN, "cap": CAP,
              "window_lam_quantiles": {q: float(np.quantile(lams, q))
                                       for q in (0.001, 0.01, 0.05, 0.25, 0.5, 0.9)},
              "tail_beta_window": float(beta_w),
              "alpha_pred_from_window_tail": float(1.0 / beta_w) if beta_w > 0 else None,
              "alpha_measured_g2_ball_rand": 0.392,
              "prediction_vs_g2": {str(s): v for s, v in sorted(pred.items())}}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(n): Extremwert-Modell v2 — Fenster-Tail ({})".format(date.today()), ""]
    lines.append("{} Radius-1-Fenster (cap {}), λ-Quantile: ".format(N_WIN, CAP) + ", ".join(
        "p{:g}: {:.4f}".format(100 * q, float(np.quantile(lams, q)))
        for q in (0.001, 0.01, 0.05, 0.25, 0.5)))
    lines.append("")
    lines.append("**Fenster-Tail β_w = {:.3f} ⟹ α_pred = {:.3f}** (gemessen g2 ball_rand: 0.392).".format(
        beta_w, 1.0 / beta_w))
    lines.append("")
    lines.append("**Absolute Vorhersage** λ_pred(s) = F_window⁻¹(ln2/s), Korridor [κ_min·λ_pred, λ_pred] mit κ_min = 0.26:")
    lines.append("")
    lines.append("| s | gemessen (g2) | λ_pred | Korridor | im Korridor |")
    lines.append("|---|---|---|---|---|")
    for s in sorted(pred):
        d = pred[s]
        lines.append("| {} | {:.4f} | {:.4f} | [{:.4f}, {:.4f}] | {} |".format(
            s, d["measured_g2"], d["predicted"], d["corridor"][0], d["corridor"][1],
            "✓" if d["in_corridor"] else "✗"))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
