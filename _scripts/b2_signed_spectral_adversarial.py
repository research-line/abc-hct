#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (g): Signierte Spektralanalyse auf adversarialen Traegern.

Hauptlemma v3(iii): Im perkolierten Mittelbereich entscheidet die
SIGNIERTE Groesse lambda_min(G_S), nicht theta'. Dieses Script testet
lambda_min auf den boeswilligsten Traeger-Familien, die die (f)-
Klassifikation benennt:

  A) cluster:    Vereinigung von Mikro-Cluster-Komponenten (w >= 0.5) —
                 die klassifizierten Struktur-Richtungen en bloc.
  B) ball:       BFS-Baelle im 0.2-Graphen um die schwersten Kanten —
                 perkolierte Nachbarschaften (Mittelbereich pur).
  C) topdeg:     Spalten mit hoechstem gewichtetem Grad (Gershgorin-
                 Worst-Case-Spalten).
  D) consecutive: Index-konsekutiv (bekannter delta_s-Ausreisser).
  E) random:     Baseline.

Pro Traeger S: lambda_min(G_S), delta(S) = max|lambda-1|. Fuer die
schlimmsten Faelle: Eigenvektor-Analyse (Traeger-Konzentration,
Beteiligung der Mikro-Cluster) — falls Fast-Kerne existieren, werden
sie hier EXPLIZIT.
"""

import json
import sys
import time
from collections import deque
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix
from scipy.sparse.csgraph import connected_components

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 126720
SEED = 20260611
SIZES = (16, 32, 64, 128, 256, 512)
N_TRIALS = 24
OUT_JSON = "_results/b2_signed_spectral_adversarial_{}.json".format(date.today())
OUT_MD = "_results/b2_signed_spectral_adversarial_{}.md".format(date.today())


def spectrum_stats(A, norms, S):
    Asub = A[:, S].toarray() / norms[S]
    G = Asub.T @ Asub
    ev = np.linalg.eigvalsh(G)
    return float(ev[0]), float(np.abs(ev - 1).max())


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
    print("A geladen ({:.1f}s)".format(time.time() - t0), flush=True)

    C = (A.T @ A).tocoo()
    off = C.row < C.col
    gi, gj, gv = C.row[off], C.col[off], C.data[off]
    gw = np.abs(gv) / (norms[gi] * norms[gj])
    nz = gw > 1e-15
    gi, gj, gw = gi[nz], gj[nz], gw[nz]

    # Mikro-Cluster (w >= 0.5)
    mh = gw >= 0.5
    sub = coo_matrix((np.ones(mh.sum()), (gi[mh], gj[mh])), shape=(NCOLS, NCOLS))
    ncomp, labels = connected_components(sub.tocsr(), directed=False)
    counts = np.bincount(labels)
    comp_ids = np.where(counts >= 2)[0]
    comp_cols = {cid: np.where(labels == cid)[0] for cid in comp_ids}
    print("Mikro-Cluster: {} Komponenten ({:.1f}s)".format(len(comp_ids), time.time() - t0), flush=True)

    # 0.2-Graph als Adjazenzliste (fuer BFS-Baelle)
    m2 = gw >= 0.2
    adj = [[] for _ in range(NCOLS)]
    for a, b in zip(gi[m2], gj[m2]):
        adj[a].append(b); adj[b].append(a)

    # gewichteter Grad (Gershgorin-Radius, volle Kanten)
    rad = np.zeros(NCOLS)
    np.add.at(rad, gi, gw)
    np.add.at(rad, gj, gw)
    topdeg_order = np.argsort(-rad)

    # schwerste Kanten als Ball-Zentren
    heavy_order = np.argsort(-gw)

    rng = np.random.default_rng(SEED)
    results = {}

    def bfs_ball(center, size):
        seen = {center}
        q = deque([center])
        out = [center]
        while q and len(out) < size:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); out.append(v); q.append(v)
                    if len(out) >= size:
                        break
        return np.array(out[:size])

    for s in SIZES:
        fam = {}
        # A) cluster: zufaellige Vereinigung von Komponenten bis Groesse s
        lam, del_ = [], []
        for _ in range(N_TRIALS):
            pick = []
            for cid in rng.permutation(comp_ids):
                cc = comp_cols[cid]
                if len(pick) + len(cc) > s:
                    continue
                pick.extend(cc.tolist())
                if len(pick) >= s - 1:
                    break
            if len(pick) < s:
                rest = rng.choice(np.setdiff1d(np.arange(NCOLS), pick), s - len(pick), replace=False)
                pick.extend(rest.tolist())
            l, d = spectrum_stats(A, norms, np.array(pick))
            lam.append(l); del_.append(d)
        fam["cluster"] = (lam, del_)

        # B) ball: BFS im 0.2-Graphen um Endpunkte der schwersten Kanten
        lam, del_ = [], []
        for k in range(N_TRIALS):
            center = int(gi[heavy_order[k]])
            S = bfs_ball(center, s)
            if len(S) < s:  # Komponente kleiner als s: auffuellen random
                rest = rng.choice(np.setdiff1d(np.arange(NCOLS), S), s - len(S), replace=False)
                S = np.concatenate([S, rest])
            l, d = spectrum_stats(A, norms, S)
            lam.append(l); del_.append(d)
        fam["ball"] = (lam, del_)

        # C) topdeg
        lam, del_ = [], []
        for k in range(N_TRIALS):
            S = topdeg_order[k * s:(k + 1) * s]
            l, d = spectrum_stats(A, norms, S)
            lam.append(l); del_.append(d)
        fam["topdeg"] = (lam, del_)

        # D) consecutive
        lam, del_ = [], []
        for _ in range(N_TRIALS):
            start = int(rng.integers(0, NCOLS - s))
            S = np.arange(start, start + s)
            l, d = spectrum_stats(A, norms, S)
            lam.append(l); del_.append(d)
        fam["consecutive"] = (lam, del_)

        # E) random
        lam, del_ = [], []
        for _ in range(N_TRIALS):
            S = rng.choice(NCOLS, s, replace=False)
            l, d = spectrum_stats(A, norms, S)
            lam.append(l); del_.append(d)
        fam["random"] = (lam, del_)

        results[s] = {k: {
            "lambda_min_median": float(np.median(v[0])),
            "lambda_min_min": float(np.min(v[0])),
            "delta_median": float(np.median(v[1])),
            "delta_max": float(np.max(v[1])),
            "n_singular": int(sum(1 for x in v[0] if x < 1e-10)),
        } for k, v in fam.items()}
        print("s={} fertig ({:.1f}s)".format(s, time.time() - t0), flush=True)

    # Worst-Case-Analyse: schlimmster Ball-Traeger bei s=512 -> Eigenvektor
    worst = {"family": None, "s": None, "lambda_min": 1e9}
    for famname, builder in (("ball", None),):
        pass
    # gezielt: groesster Ball s=512 um die allerschwerste Kante
    S = bfs_ball(int(gi[heavy_order[0]]), 512)
    if len(S) >= 16:
        Asub = A[:, S].toarray() / norms[S]
        G = Asub.T @ Asub
        ev, evec = np.linalg.eigh(G)
        x = evec[:, 0]
        absx = np.abs(x)
        order = np.argsort(-absx)
        mass_top10 = float((absx[order[:10]] ** 2).sum())
        in_cluster = np.isin(S, np.concatenate([comp_cols[c] for c in comp_ids]))
        mass_cluster = float((absx[in_cluster] ** 2).sum())
        worst = {
            "ball_size": int(len(S)),
            "lambda_min": float(ev[0]),
            "eigvec_mass_top10": mass_top10,
            "eigvec_mass_on_microclusters": mass_cluster,
            "top5_weights": [float(absx[order[k]]) for k in range(5)],
        }

    report = {"date": str(date.today()), "n_trials": N_TRIALS,
              "results": {str(s): results[s] for s in SIZES},
              "worst_ball_512_eigvec": worst}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(g): Signierte Spektralanalyse — λ_min auf adversarialen Trägern ({})".format(date.today()), ""]
    lines.append("Träger-Familien: cluster (Mikro-Cluster-Vereinigungen), ball (BFS im 0.2-Graphen um schwerste Kanten), topdeg (höchster gewichteter Grad), consecutive, random. {} Trials/Zelle.".format(N_TRIALS))
    lines.append("")
    lines.append("| s | Familie | λ_min median | λ_min min | δ median | δ max | singulär |")
    lines.append("|---|---|---|---|---|---|---|")
    for s in SIZES:
        for famname in ("cluster", "ball", "topdeg", "consecutive", "random"):
            r = results[s][famname]
            lines.append("| {} | {} | {:.4f} | {:.4f} | {:.3f} | {:.3f} | {}/{} |".format(
                s, famname, r["lambda_min_median"], r["lambda_min_min"],
                r["delta_median"], r["delta_max"], r["n_singular"], N_TRIALS))
    lines.append("")
    lines.append("**Worst-Ball-512-Eigenvektor:** λ_min = {:.4f}, Masse Top-10-Spalten {:.1%}, Masse auf Mikro-Clustern {:.1%}".format(
        worst["lambda_min"], worst["eigvec_mass_top10"], worst["eigvec_mass_on_microclusters"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
