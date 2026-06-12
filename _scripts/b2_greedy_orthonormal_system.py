#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (d): Konstruktives orthonormales Teilsystem + Cancellation-Messung.

(1) GREEDY-INDEPENDENT-SET auf dem Koinzidenz-Graphen H (min-degree greedy):
    Nach Lemma L1 ist jede in H unabhaengige Spaltenmenge EXAKT orthonormal
    (G_S = I). Turan-Untergrenze: |IS| >= n/(1+mittlerer Grad) ~ 5700.
    Gemessen wird die tatsaechliche Greedy-Groesse + Verifikation an
    Zufallsstichproben (gram == I).
(2) CANCELLATION-MESSUNG (Vorbereitung analytisches Horn / weak flat RIP):
    Fuer zufaellige disjunkte I, J (|I|=|J|=K) das Verhaeltnis
        r(I,J) = |<sum_I phi, sum_J phi>| / K
    (die weak-flat-RIP-Groesse theta') und die Vorzeichen-Ausloeschung
        c(I,J) = |sum_r a_r b_r| / sum_r |a_r b_r|   (1 = keine Ausloeschung).
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
OUT_JSON = "_results/b2_orthonormal_system_witness_240672_{}.json".format(date.today())
OUT_MD = "_results/b2_orthonormal_system_witness_240672_{}.md".format(date.today())


def main():
    t0 = time.time()
    rows, cols, vals = [], [], []
    row_entries = []  # Spaltenlisten pro Zeile (fuer Cliquen/Adjazenz)
    n_rows = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ent = []
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n_rows); cols.append(c); vals.append(float(v))
                ent.append(c)
            row_entries.append(ent)
            n_rows += 1
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n_rows, NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    print("A geladen ({:.1f}s)".format(time.time() - t0), flush=True)

    # Adjazenzlisten von H (Cliquen pro Zeile)
    adj = [set() for _ in range(NCOLS)]
    clique_sizes = {}
    for ent in row_entries:
        k = len(ent)
        clique_sizes[k] = clique_sizes.get(k, 0) + 1
        for a in range(k):
            for b in range(a + 1, k):
                i, j = ent[a], ent[b]
                if i != j:
                    adj[i].add(j); adj[j].add(i)
    deg = np.array([len(a) for a in adj])
    print("H gebaut: mittl. Grad {:.1f} ({:.1f}s)".format(deg.mean(), time.time() - t0), flush=True)

    # Greedy-Independent-Set (aufsteigender Grad)
    order = np.argsort(deg, kind="stable")
    blocked = np.zeros(NCOLS, dtype=bool)
    indep = []
    for v in order:
        if not blocked[v]:
            indep.append(int(v))
            for u in adj[v]:
                blocked[u] = True
    indep = np.array(indep)
    print("Greedy-IS: {} Spalten ({:.1f}s)".format(len(indep), time.time() - t0), flush=True)

    # Verifikation: G_S = I auf Zufallsstichproben aus dem IS
    rng = np.random.default_rng(SEED)
    ver_ok = True
    for _ in range(20):
        S = rng.choice(indep, size=min(256, len(indep)), replace=False)
        Asub = A[:, S].toarray() / norms[S]
        G = Asub.T @ Asub
        if not np.allclose(G, np.eye(len(S)), atol=1e-12):
            ver_ok = False
            break

    # Cancellation-Messung
    canc = {}
    all_cols = np.arange(NCOLS)
    for K in (64, 128, 256, 512):
        ratios, cancs = [], []
        for _ in range(120):
            pick = rng.choice(all_cols, size=2 * K, replace=False)
            I, J = pick[:K], pick[K:]
            uI = np.zeros(NCOLS); uI[I] = 1.0 / norms[I]
            uJ = np.zeros(NCOLS); uJ[J] = 1.0 / norms[J]
            a = A @ uI  # Zeilenvektor-Summen
            b = A @ uJ
            num = float(abs(a @ b))
            den = float(np.abs(a * b).sum())
            ratios.append(num / K)
            cancs.append(num / den if den > 0 else None)
        cancs = [c for c in cancs if c is not None]
        canc[K] = {
            "theta_prime_median": float(np.median(ratios)),
            "theta_prime_p95": float(np.quantile(ratios, 0.95)),
            "theta_prime_max": float(max(ratios)),
            "cancellation_median": float(np.median(cancs)),
            "cancellation_p95": float(np.quantile(cancs, 0.95)),
        }
        print("K={} fertig ({:.1f}s)".format(K, time.time() - t0), flush=True)

    report = {
        "date": str(date.today()),
        "clique_size_distribution_rows": clique_sizes,
        "graph_mean_degree": float(deg.mean()),
        "turan_lower_bound": float(NCOLS / (1 + deg.mean())),
        "greedy_independent_set_size": int(len(indep)),
        "greedy_is_fraction_of_cols": float(len(indep) / NCOLS),
        "verification_G_eq_I": bool(ver_ok),
        "cancellation": canc,
        "seed": SEED,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(d): Konstruktives orthonormales Teilsystem + Cancellation ({})".format(date.today()), ""]
    lines.append("Cliquengrößen (Zeilen-nnz): {}".format(
        {k: clique_sizes[k] for k in sorted(clique_sizes)}))
    lines.append("")
    lines.append("**Greedy-Independent-Set: {} Spalten ({:.1%} aller Spalten)** — Turán-Garantie wäre {:.0f}.".format(
        len(indep), len(indep) / NCOLS, NCOLS / (1 + deg.mean())))
    lines.append("Verifikation G_S = I (20 × 256er-Stichproben, atol 1e-12): {}.".format(
        "BESTANDEN" if ver_ok else "FEHLGESCHLAGEN"))
    lines.append("")
    lines.append("| K | θ′ Median | θ′ p95 | θ′ max | Cancellation-Faktor Median | p95 |")
    lines.append("|---|---|---|---|---|---|")
    for K in sorted(canc):
        c = canc[K]
        lines.append("| {} | {:.4f} | {:.4f} | {:.4f} | {:.3f} | {:.3f} |".format(
            K, c["theta_prime_median"], c["theta_prime_p95"], c["theta_prime_max"],
            c["cancellation_median"], c["cancellation_p95"]))
    lines.append("")
    lines.append("θ′(I,J) = |⟨Σ_I φ, Σ_J φ⟩|/K (weak-flat-RIP-Größe); Cancellation = |Σ a_r b_r|/Σ|a_r b_r|.")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
