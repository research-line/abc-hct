#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Hauptlemma-Vorbereitung: Schicht-Vorzeichen + adversariales theta'.

Reduktions-Lemma (exakt, trivial): <sum_I phi, sum_J phi> =
sum ueber Kanten (i,j) in I x J von G_ij. Die weak-flat-RIP-Frage ist
also reine gewichtete Bipartit-Kantensummen-Frage ueber H.

Gemessen wird:
(1) SCHICHT-ZERLEGUNG der Gram-Eintraege: G = G_maninT + G_U3 + G_T5
    (Zeilenfamilien getrennt) — Vorzeichenverteilung und |G_ij|-Statistik
    pro Schicht. Balancierte Vorzeichen => algebraisches Horn kann
    Cancellation nutzen; systematische Vorzeichen => nicht.
(2) ADVERSARIALES theta': Greedy-Auswahl der schwersten Bipartit-Kanten
    (Matching-artig: jede Spalte nur einmal) => untere Schranke fuer
    worst-case theta'(K) = (max gewichtete Kantensumme)/K.
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
OUT_JSON = "_results/b2_layer_signs_adversarial_{}.json".format(date.today())
OUT_MD = "_results/b2_layer_signs_adversarial_{}.md".format(date.today())

LAYER_OF = {
    "manin_T_relations_after_SI": "maninT",
    "T_3_minus_1": "U3",
    "T_5_minus_2": "T5",
}


def load_layer(layer_name):
    rows, cols, vals = [], [], []
    n = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            lay = LAYER_OF.get(r["stage"].split("_batch")[0], r["stage"].split("_batch")[0])
            if lay != layer_name:
                continue
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n); cols.append(c); vals.append(float(v))
            n += 1
    return csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n, NCOLS))) if n else None


def main():
    t0 = time.time()
    # Gesamtnormen (fuer einheitliche Normierung wie bisher)
    rows, cols, vals = [], [], []
    n_all = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n_all); cols.append(c); vals.append(float(v))
            n_all += 1
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n_all, NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0

    report = {"date": str(date.today()), "layers": {}}
    lines = ["# B2: Schicht-Vorzeichen + adversariales θ′ ({})".format(date.today()), ""]
    lines.append("Reduktions-Lemma: ⟨Σ_I φ, Σ_J φ⟩ = Σ_{Kanten(I×J)} G_ij (exakt).")
    lines.append("")
    lines.append("| Schicht | Kanten | G>0 | G<0 | Anteil + | |G| median | |G| max (norm.) |")
    lines.append("|---|---|---|---|---|---|---|")

    total_C = None
    for lay in ("maninT", "U3", "T5"):
        Al = load_layer(lay)
        C = (Al.T @ Al).tocoo()
        off = (C.row < C.col)
        i, j, v = C.row[off], C.col[off], C.data[off]
        nz = np.abs(v) > 1e-15
        i, j, v = i[nz], j[nz], v[nz]
        w = np.abs(v) / (norms[i] * norms[j])
        pos = int((v > 0).sum()); neg = int((v < 0).sum())
        report["layers"][lay] = {
            "n_edges": int(len(v)),
            "pos": pos, "neg": neg,
            "frac_pos": pos / max(len(v), 1),
            "w_median": float(np.median(w)) if len(w) else None,
            "w_max": float(w.max()) if len(w) else None,
        }
        lines.append("| {} | {} | {} | {} | {:.3f} | {:.4f} | {:.4f} |".format(
            lay, len(v), pos, neg, pos / max(len(v), 1),
            float(np.median(w)), float(w.max())))
        print(lay, "fertig ({:.1f}s)".format(time.time() - t0), flush=True)

    # Adversariales theta': schwerste Kanten, Matching-greedy (jede Spalte 1x)
    C = (A.T @ A).tocoo()
    off = (C.row < C.col)
    i, j, v = C.row[off], C.col[off], C.data[off]
    w = np.abs(v) / (norms[i] * norms[j])
    nz = w > 1e-15
    i, j, w = i[nz], j[nz], w[nz]
    order = np.argsort(-w)
    used = np.zeros(NCOLS, dtype=bool)
    adv = {}
    acc, K = 0.0, 0
    targets = {64: None, 128: None, 256: None, 512: None, 1024: None}
    for idx in order:
        a, b = int(i[idx]), int(j[idx])
        if used[a] or used[b]:
            continue
        used[a] = used[b] = True
        acc += float(w[idx]); K += 1
        if K in targets:
            targets[K] = acc / K
        if K >= 1024:
            break
    report["adversarial_theta_prime_matching"] = {str(k): v for k, v in targets.items() if v}
    lines.append("")
    lines.append("**Adversariales θ′ (Matching der schwersten Kanten, I×J disjunkt):** " +
                 ", ".join("K={}: {:.3f}".format(k, v) for k, v in sorted(
                     ((int(k), v) for k, v in report["adversarial_theta_prime_matching"].items()))))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
