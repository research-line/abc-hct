#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (g2): Skalierungs-Fit lambda_min(s) + Lokalisierung der flachsten Richtungen.

Offene Flanke aus (g): Ball-lambda_min faellt monoton 0.25 -> 0.06
(s = 16 -> 512) ohne Plateau. Existieren Fast-Kerne mittlerer
Traegergroesse (10^3-10^4)? Dieses Script:

(1) BEREINIGT: die 2 bekannten antiparallelen Duplikat-Paare werden
    ausgeschlossen (DUP) — der Fit misst den nicht-trivialen Anteil.
(2) SKALIERUNG: lambda_min(G_S) fuer Ball-Traeger (BFS im 0.2-Graphen)
    um (a) Endpunkte schwerster Kanten, (b) zufaellige Zentren; dazu
    random-Baseline. s = 16 ... 4096. Log-log-Fit lambda_min ~ s^-alpha.
(3) LOKALISIERUNG: fuer den flachsten Trial pro s die 3 untersten
    Eigenvektoren: IPR (effektive Traegergroesse 1/IPR), Masse auf
    Mikro-Cluster-Spalten, Masse auf Top-10/Top-1%-Spalten.
    Lokalisiert => klassifizierbar (v3(ii)-artig);
    delokalisiert => echtes Mittelbereichs-Phaenomen (v3(iii)-Gegner).
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
DUP = {38007, 120130, 71782, 123997}  # antiparallele Paare (g3) — trivial, exkludiert
PLAN = [(16, 12), (32, 12), (64, 12), (128, 12), (256, 8), (512, 8), (1024, 6), (2048, 4), (4096, 3)]
OUT_JSON = "_results/b2_lambda_min_scaling_fit_{}.json".format(date.today())
OUT_MD = "_results/b2_lambda_min_scaling_fit_{}.md".format(date.today())


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

    # Mikro-Cluster-Spalten (w >= 0.5) fuer Lokalisierungs-Attribution
    mh = gw >= 0.5
    sub = coo_matrix((np.ones(int(mh.sum())), (gi[mh], gj[mh])), shape=(NCOLS, NCOLS))
    _, labels = connected_components(sub.tocsr(), directed=False)
    counts = np.bincount(labels)
    micro_mask = np.zeros(NCOLS, dtype=bool)
    micro_mask[np.isin(labels, np.where(counts >= 2)[0])] = True

    # 0.2-Graph Adjazenz (DUP-Spalten raus)
    m2 = gw >= 0.2
    adj = [[] for _ in range(NCOLS)]
    for a, b in zip(gi[m2], gj[m2]):
        if a in DUP or b in DUP:
            continue
        adj[a].append(b); adj[b].append(a)
    heavy_order = [k for k in np.argsort(-gw)
                   if gi[k] not in DUP and gj[k] not in DUP][:64]
    rng = np.random.default_rng(SEED)
    nondup = np.array([c for c in range(NCOLS) if c not in DUP])
    print("Graph vorbereitet ({:.1f}s)".format(time.time() - t0), flush=True)

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
        S = out[:size]
        if len(S) < size:
            extra = rng.choice(np.setdiff1d(nondup, S), size - len(S), replace=False)
            S = S + extra.tolist()
        return np.array(S)

    def gram(S):
        Asub = A[:, S]
        G = (Asub.T @ Asub).toarray()
        ns = norms[S]
        return G / np.outer(ns, ns)

    results = {}
    flat_analysis = {}
    for s, ntrial in PLAN:
        fams = {"ball_heavy": [], "ball_rand": [], "random": []}
        flattest = {"lam": 1e9, "S": None, "fam": None}
        for k in range(ntrial):
            trio = {
                "ball_heavy": bfs_ball(int(gi[heavy_order[k % len(heavy_order)]]), s),
                "ball_rand": bfs_ball(int(rng.choice(nondup)), s),
                "random": rng.choice(nondup, s, replace=False),
            }
            for fam, S in trio.items():
                G = gram(S)
                ev = np.linalg.eigvalsh(G)
                fams[fam].append(float(ev[0]))
                if fam.startswith("ball") and ev[0] < flattest["lam"]:
                    flattest = {"lam": float(ev[0]), "S": S.copy(), "fam": fam}
        results[s] = {fam: {
            "lambda_min_median": float(np.median(v)),
            "lambda_min_min": float(np.min(v)),
            "n_singular": int(sum(1 for x in v if x < 1e-10)),
        } for fam, v in fams.items()}

        # Lokalisierung am flachsten Ball-Trial
        S = flattest["S"]
        G = gram(S)
        ev, evec = np.linalg.eigh(G)
        loc = []
        for j in range(3):
            x = evec[:, j]
            ipr = float((x ** 4).sum())
            absx2 = x ** 2
            order = np.argsort(-absx2)
            loc.append({
                "lambda": float(ev[j]),
                "ipr_inv_effsupport": float(1.0 / ipr),
                "mass_top10": float(absx2[order[:10]].sum()),
                "mass_top1pct": float(absx2[order[:max(1, len(S) // 100)]].sum()),
                "mass_on_microclusters": float(absx2[micro_mask[S]].sum()),
            })
        flat_analysis[s] = {"family": flattest["fam"], "modes": loc}
        print("s={} fertig: ball_heavy med {:.4f}, ball_rand med {:.4f}, random med {:.4f} ({:.1f}s)".format(
            s, results[s]["ball_heavy"]["lambda_min_median"],
            results[s]["ball_rand"]["lambda_min_median"],
            results[s]["random"]["lambda_min_median"], time.time() - t0), flush=True)

    # Log-log-Fit ueber Mediane
    fits = {}
    for fam in ("ball_heavy", "ball_rand", "random"):
        xs = np.log([s for s, _ in PLAN])
        ys = np.log([max(results[s][fam]["lambda_min_median"], 1e-12) for s, _ in PLAN])
        alpha, c = np.polyfit(xs, ys, 1)
        fits[fam] = {"alpha": float(-alpha), "prefactor": float(np.exp(c))}

    report = {"date": str(date.today()), "dup_excluded": sorted(DUP),
              "plan": PLAN, "results": {str(s): results[s] for s, _ in PLAN},
              "fits_lambda_min_vs_s_powerlaw": fits,
              "flattest_mode_localization": {str(s): flat_analysis[s] for s, _ in PLAN}}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(g2): λ_min-Skalierung + Lokalisierung (bereinigt um Duplikat-Paare) ({})".format(date.today()), ""]
    lines.append("| s | ball_heavy med | ball_rand med | random med | min (ball) | singulär |")
    lines.append("|---|---|---|---|---|---|")
    for s, ntrial in PLAN:
        r = results[s]
        lines.append("| {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {}+{}/{} |".format(
            s, r["ball_heavy"]["lambda_min_median"], r["ball_rand"]["lambda_min_median"],
            r["random"]["lambda_min_median"],
            min(r["ball_heavy"]["lambda_min_min"], r["ball_rand"]["lambda_min_min"]),
            r["ball_heavy"]["n_singular"], r["ball_rand"]["n_singular"], ntrial))
    lines.append("")
    lines.append("**Power-Law-Fits λ_min ~ c·s^(−α):** " + ", ".join(
        "{}: α={:.3f} (c={:.2f})".format(f, v["alpha"], v["prefactor"]) for f, v in fits.items()))
    lines.append("")
    lines.append("## Lokalisierung der flachsten Moden (flachster Ball-Trial pro s)")
    lines.append("")
    lines.append("| s | λ₀ | 1/IPR (eff. Träger) | Masse Top-10 | Masse Mikro-Cluster |")
    lines.append("|---|---|---|---|---|")
    for s, _ in PLAN:
        m = flat_analysis[s]["modes"][0]
        lines.append("| {} | {:.4f} | {:.1f} | {:.1%} | {:.1%} |".format(
            s, m["lambda"], m["ipr_inv_effsupport"], m["mass_top10"], m["mass_on_microclusters"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
