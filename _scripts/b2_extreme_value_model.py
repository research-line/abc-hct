#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (k): Extremwert-Modell fuer das lambda_min-Power-Law.

Modell: Ein Ball der Groesse s enthaelt ~nu*s lokale Konfigurationen mit
i.i.d.-artigen lokalen lambda-Werten aus einer Verteilung F mit unterem
Tail F(lam) ~ C*lam^beta. Dann ist lambda_min(s) ~ (C*nu*s)^(-1/beta),
also Power-Law mit alpha = 1/beta.

Tests:
(1) TAIL-FIT: empirische lambda_min-Verteilung kleiner Baelle (s=16),
    log-log-Fit des unteren Tails -> beta. Vorhersage alpha = 1/beta
    gegen die (g2)-Fits (ball_rand 0.39, ball_heavy 0.53).
(2) LOKALITAETS-REDUKTION (beweisrelevant): kappa(S) =
    lambda_min(G_S) / min ueber lokale Fenster T (Radius-1-Nachbarschaften
    in S, capped). Cauchy-Interlacing: kappa <= 1 EXAKT (T Teilmenge S).
    Empirie: kappa >= konst > 0?  Dann gilt lambda_min global ~ lokales
    Minimum -> v3(iii) reduziert auf ENDLICHE lokale Konfigurationen.
"""

import json
import sys
import time
from collections import deque
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 126720
SEED = 20260611
DUP = {38007, 120130, 71782, 123997}
N_SMALL = 400
S_SMALL = 16
LOC_PLAN = [(128, 12), (256, 12), (512, 8)]
CAP_WINDOW = 24
OUT_JSON = "_results/b2_extreme_value_model_{}.json".format(date.today())
OUT_MD = "_results/b2_extreme_value_model_{}.md".format(date.today())


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
    nondup = np.array([c for c in range(NCOLS) if c not in DUP])
    print("Graph bereit ({:.1f}s)".format(time.time() - t0), flush=True)

    def bfs_ball(center, size):
        seen = {center}; q = deque([center]); out = [center]
        while q and len(out) < size:
            u = q.popleft()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w); out.append(w); q.append(w)
                    if len(out) >= size:
                        break
        S = out[:size]
        if len(S) < size:
            extra = rng.choice(np.setdiff1d(nondup, S), size - len(S), replace=False)
            S = S + extra.tolist()
        return np.array(S)

    def lam_min(S):
        Asub = A[:, S]
        G = (Asub.T @ Asub).toarray()
        ns = norms[S]
        return float(np.linalg.eigvalsh(G / np.outer(ns, ns))[0])

    # --- (1) Tail-Fit kleiner Baelle ---
    lams = np.array(sorted(lam_min(bfs_ball(int(rng.choice(nondup)), S_SMALL))
                           for _ in range(N_SMALL)))
    # empirische CDF am unteren Ende (unterste 15%)
    ntail = max(20, int(0.15 * N_SMALL))
    x = np.log(lams[:ntail])
    y = np.log((np.arange(ntail) + 1) / N_SMALL)
    beta, logC = np.polyfit(x, y, 1)
    alpha_pred = 1.0 / beta if beta > 0 else None
    print("Tail-Fit: beta = {:.3f} -> alpha_pred = {:.3f} ({:.1f}s)".format(
        beta, alpha_pred or -1, time.time() - t0), flush=True)

    # --- (2) Lokalitaets-Reduktion ---
    loc_results = {}
    for s, ntrial in LOC_PLAN:
        kappas, lmins, locmins = [], [], []
        for _ in range(ntrial):
            S = bfs_ball(int(rng.choice(nondup)), s)
            lS = lam_min(S)
            Sset = set(S.tolist())
            # lokale Fenster: Radius-1-Nachbarschaft jeder Spalte, geschnitten mit S
            best = 1e9
            for c in S:
                T = [c] + [w for w in adj[c] if w in Sset][:CAP_WINDOW - 1]
                if len(T) < 2:
                    continue
                lT = lam_min(np.array(T))
                best = min(best, lT)
            kappas.append(lS / best if best < 1e8 and best > 0 else None)
            lmins.append(lS); locmins.append(best)
        kk = [k for k in kappas if k is not None]
        loc_results[s] = {
            "kappa_median": float(np.median(kk)),
            "kappa_min": float(np.min(kk)),
            "kappa_max": float(np.max(kk)),
            "lambda_min_median": float(np.median(lmins)),
            "local_min_median": float(np.median(locmins)),
            "n": len(kk),
        }
        print("s={}: kappa median {:.3f} [{:.3f}, {:.3f}] ({:.1f}s)".format(
            s, loc_results[s]["kappa_median"], loc_results[s]["kappa_min"],
            loc_results[s]["kappa_max"], time.time() - t0), flush=True)

    report = {"date": str(date.today()),
              "tail_fit_small_balls": {
                  "n_balls": N_SMALL, "s": S_SMALL,
                  "beta": float(beta), "alpha_predicted": float(alpha_pred) if alpha_pred else None,
                  "alpha_measured_g2": {"ball_heavy": 0.532, "ball_rand": 0.392},
                  "lam_quantiles": {q: float(np.quantile(lams, q)) for q in (0.01, 0.05, 0.25, 0.5)}},
              "locality_reduction": {str(s): v for s, v in loc_results.items()},
              "cap_window": CAP_WINDOW}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(k): Extremwert-Modell für das λ_min-Power-Law ({})".format(date.today()), ""]
    lines.append("**(1) Tail-Fit** ({} Bälle, s={}): unterer Tail F(λ) ~ λ^β mit **β = {:.3f}** ⟹ Vorhersage α = 1/β = **{:.3f}** — gemessen (g2): ball_rand 0.392, ball_heavy 0.532.".format(
        N_SMALL, S_SMALL, beta, alpha_pred))
    lines.append("")
    lines.append("λ_min-Quantile der kleinen Bälle: " + ", ".join(
        "p{:.0f}: {:.4f}".format(100 * q, float(np.quantile(lams, q))) for q in (0.01, 0.05, 0.25, 0.5)))
    lines.append("")
    lines.append("**(2) Lokalitäts-Reduktion** (κ = λ_min(S)/min lokale Fenster ≤ {}; Cauchy-Interlacing ⟹ κ ≤ 1 exakt):".format(CAP_WINDOW))
    lines.append("")
    lines.append("| s | κ median | κ min | κ max | λ_min med | lokales min med |")
    lines.append("|---|---|---|---|---|---|")
    for s, _ in LOC_PLAN:
        r = loc_results[s]
        lines.append("| {} | {:.3f} | {:.3f} | {:.3f} | {:.4f} | {:.4f} |".format(
            s, r["kappa_median"], r["kappa_min"], r["kappa_max"],
            r["lambda_min_median"], r["local_min_median"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
