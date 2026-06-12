#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (f): Struktur-Kern-Klassifikation + Gershgorin auf generischem Teil.

Hauptlemma v2 verlangt: (a) RIP auf dem generischen Teil, (b) endliche
Klassifikation des Struktur-Kerns. Dieses Script liefert die Grundlage:

(1) GEWICHTS-PROFIL aller Gram-Kanten w_ij = |<phi_i,phi_j>|/(|phi_i||phi_j|).
(2) KERN-EXTRAKTION pro Schwelle theta_c: Kanten mit w >= theta_c,
    Kern-Spalten, Zusammenhangskomponenten (Anzahl, Groessenverteilung).
(3) KERN-KLASSIFIKATION (theta_c = TH_MAIN): Koinzidenz-Multiplizitaet
    (# gemeinsame Zeilen), Spalten-nnz-Paare, Schicht-Attribution
    (maninT/U3/T5-Anteile der gemeinsamen Zeilen), exakt parallele Paare.
    Hypothese: schwere Kanten ~ kleine Spalten-nnz + Einzelschicht-Koinzidenz.
(4) GENERISCHER TEIL = Spalten ohne inzidente Kante >= theta_c:
    (4a) Gershgorin-Radius eingeschraenkt auf generische Kanten.
         max < 1  =>  G_S invertierbar fuer ALLE S im generischen Teil
         (BEWEISBAR via Lemma L2) — der Satz hinter Hauptlemma v2(a).
    (4b) Adversariales Matching-theta' nur im generischen Teil.
"""

import json
import sys
import time
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix
from scipy.sparse.csgraph import connected_components

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 126720
THETAS = [0.5, 0.3, 0.2, 0.1, 0.05]
TH_MAIN = 0.3
MAX_CLASSIFY = 400_000  # Sicherheitsgrenze fuer die Kanten-Klassifikation
OUT_JSON = "_results/b2_structure_kernel_classification_{}.json".format(date.today())
OUT_MD = "_results/b2_structure_kernel_classification_{}.md".format(date.today())

LAYER_OF = {
    "manin_T_relations_after_SI": "maninT",
    "T_3_minus_1": "U3",
    "T_5_minus_2": "T5",
}
LAYERS = ("maninT", "U3", "T5")


def main():
    t0 = time.time()
    rows, cols, vals = [], [], []
    row_layer = []
    n = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            lay = LAYER_OF.get(r["stage"].split("_batch")[0], r["stage"].split("_batch")[0])
            row_layer.append(lay)
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n); cols.append(c); vals.append(float(v))
            n += 1
    row_layer = np.array(row_layer)
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n, NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    col_nnz = np.diff(A.indptr)
    print("A geladen: {}x{}, nnz={} ({:.1f}s)".format(n, NCOLS, A.nnz, time.time() - t0), flush=True)

    # --- Gram-Kanten (i<j) ---
    C = (A.T @ A).tocoo()
    off = C.row < C.col
    gi, gj, gv = C.row[off], C.col[off], C.data[off]
    gw = np.abs(gv) / (norms[gi] * norms[gj])
    nz = gw > 1e-15
    gi, gj, gw = gi[nz], gj[nz], gw[nz]
    print("Gram-Kanten (i<j, nichttrivial): {} ({:.1f}s)".format(len(gw), time.time() - t0), flush=True)

    report = {"date": str(date.today()), "n_edges": int(len(gw))}
    report["weight_profile"] = {
        "quantiles": {q: float(np.quantile(gw, q)) for q in (0.5, 0.9, 0.99, 0.999)},
        "max": float(gw.max()),
        "counts_ge": {str(t): int((gw >= t).sum()) for t in THETAS},
        "n_exact_parallel": int((gw > 1 - 1e-9).sum()),
    }

    # --- Kern pro Schwelle: Spalten + Komponenten ---
    report["kernel_by_threshold"] = {}
    for t in THETAS:
        m = gw >= t
        hi, hj = gi[m], gj[m]
        kern_cols = np.unique(np.concatenate([hi, hj]))
        sub = coo_matrix((np.ones(len(hi)), (hi, hj)), shape=(NCOLS, NCOLS))
        ncomp, labels = connected_components(sub.tocsr(), directed=False)
        counts = np.bincount(labels)
        comp_sizes = counts[counts >= 2]
        report["kernel_by_threshold"][str(t)] = {
            "n_heavy_edges": int(m.sum()),
            "n_kernel_cols": int(len(kern_cols)),
            "frac_kernel_cols": float(len(kern_cols) / NCOLS),
            "n_components_ge2": int(len(comp_sizes)),
            "comp_size_max": int(comp_sizes.max()) if len(comp_sizes) else 0,
            "comp_size_median": float(np.median(comp_sizes)) if len(comp_sizes) else 0,
            "comp_size_hist_top": {str(k): int(v) for k, v in
                                   sorted(np.c_[np.unique(comp_sizes, return_counts=True)].tolist(),
                                          key=lambda x: -x[1])[:8]} if len(comp_sizes) else {},
        }
        print("theta_c={}: {} Kanten, {} Kern-Spalten, {} Komponenten ({:.1f}s)".format(
            t, int(m.sum()), len(kern_cols), int(len(comp_sizes)), time.time() - t0), flush=True)

    # --- Klassifikation der schweren Kanten bei TH_MAIN ---
    m = gw >= TH_MAIN
    hi, hj, hw = gi[m], gj[m], gw[m]
    if len(hi) > MAX_CLASSIFY:
        sel = np.random.default_rng(20260611).choice(len(hi), MAX_CLASSIFY, replace=False)
        hi, hj, hw = hi[sel], hj[sel], hw[sel]
        report["classification_sampled"] = True
    else:
        report["classification_sampled"] = False

    P = A.copy(); P.data = np.ones_like(P.data)  # Inzidenz-Pattern
    Pr = P.tocsr()
    mult_layers = {}
    for lay in LAYERS + ("ALL",):
        Pl = Pr if lay == "ALL" else Pr[row_layer == lay]
        Ml = (Pl.T @ Pl).tocsr()
        mult_layers[lay] = np.asarray(Ml[hi, hj]).ravel()
        print("Multiplizitaet {} fertig ({:.1f}s)".format(lay, time.time() - t0), flush=True)

    mult = mult_layers["ALL"]
    nnz_lo = np.minimum(col_nnz[hi], col_nnz[hj])
    nnz_hi = np.maximum(col_nnz[hi], col_nnz[hj])
    # Schicht-Signaturen: (m_maninT, m_U3, m_T5) der gemeinsamen Zeilen
    sig = np.stack([mult_layers[l] for l in LAYERS], axis=1).astype(int)
    sig_keys, sig_counts = np.unique(sig, axis=0, return_counts=True)
    top_sig = sorted(zip(sig_keys.tolist(), sig_counts.tolist()), key=lambda x: -x[1])[:10]
    pair_keys, pair_counts = np.unique(np.stack([nnz_lo, nnz_hi], axis=1), axis=0, return_counts=True)
    top_pairs = sorted(zip(pair_keys.tolist(), pair_counts.tolist()), key=lambda x: -x[1])[:10]

    report["heavy_edge_classification"] = {
        "threshold": TH_MAIN,
        "n_edges": int(len(hi)),
        "mult_hist": {str(k): int(v) for k, v in zip(*np.unique(mult, return_counts=True))},
        "layer_signature_top10": [{"maninT_U3_T5": k, "count": c} for k, c in top_sig],
        "colnnz_pair_top10": [{"nnz_lo_hi": k, "count": c} for k, c in top_pairs],
        "frac_both_nnz_le2": float(((col_nnz[hi] <= 2) & (col_nnz[hj] <= 2)).mean()),
        "frac_both_nnz_le4": float(((col_nnz[hi] <= 4) & (col_nnz[hj] <= 4)).mean()),
        "w_median": float(np.median(hw)),
    }

    # --- Generischer Teil ---
    report["generic_part"] = {}
    for t in (0.5, TH_MAIN):
        mh = gw >= t
        kern_mask = np.zeros(NCOLS, dtype=bool)
        kern_mask[gi[mh]] = True
        kern_mask[gj[mh]] = True
        gen_mask = ~kern_mask
        # Kanten innerhalb des generischen Teils
        eg = gen_mask[gi] & gen_mask[gj]
        egi, egj, egw = gi[eg], gj[eg], gw[eg]
        rad = np.zeros(NCOLS)
        np.add.at(rad, egi, egw)
        np.add.at(rad, egj, egw)
        rad_gen = rad[gen_mask]
        if not len(rad_gen):
            report["generic_part"][str(t)] = {"n_generic_cols": 0}
            continue
        # Adversariales Matching nur generisch
        order = np.argsort(-egw)
        used = np.zeros(NCOLS, dtype=bool)
        acc, K = 0.0, 0
        targets = {64: None, 128: None, 256: None, 512: None, 1024: None}
        for idx in order:
            a, b = int(egi[idx]), int(egj[idx])
            if used[a] or used[b]:
                continue
            used[a] = used[b] = True
            acc += float(egw[idx]); K += 1
            if K in targets:
                targets[K] = acc / K
            if K >= 1024:
                break
        report["generic_part"][str(t)] = {
            "n_generic_cols": int(gen_mask.sum()),
            "frac_generic_cols": float(gen_mask.mean()),
            "gershgorin_on_generic": {
                "max": float(rad_gen.max()),
                "p99": float(np.quantile(rad_gen, 0.99)),
                "median": float(np.median(rad_gen)),
                "frac_lt_0.5": float((rad_gen < 0.5).mean()),
                "frac_lt_1": float((rad_gen < 1.0).mean()),
            },
            "adversarial_theta_prime_matching": {str(k): v for k, v in targets.items() if v},
        }
        print("Generisch theta_c={}: {} Spalten, Gershgorin max {:.3f} ({:.1f}s)".format(
            t, int(gen_mask.sum()), float(rad_gen.max()), time.time() - t0), flush=True)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # --- Markdown ---
    lines = ["# B2(f): Struktur-Kern-Klassifikation + generischer Teil ({})".format(date.today()), ""]
    wp = report["weight_profile"]
    lines.append("Kanten gesamt: {} | Gewichts-Quantile: median {:.4f}, p99 {:.4f}, p99.9 {:.4f}, max {:.4f} | exakt parallel: {}".format(
        report["n_edges"], wp["quantiles"][0.5], wp["quantiles"][0.99], wp["quantiles"][0.999],
        wp["max"], wp["n_exact_parallel"]))
    lines.append("")
    lines.append("| θ_c | schwere Kanten | Kern-Spalten | Anteil | Komponenten | max Komp. |")
    lines.append("|---|---|---|---|---|---|")
    for t in THETAS:
        k = report["kernel_by_threshold"][str(t)]
        lines.append("| {} | {} | {} | {:.2%} | {} | {} |".format(
            t, k["n_heavy_edges"], k["n_kernel_cols"], k["frac_kernel_cols"],
            k["n_components_ge2"], k["comp_size_max"]))
    lines.append("")
    hc = report["heavy_edge_classification"]
    lines.append("**Klassifikation (θ_c = {}, {} Kanten):** beide Spalten-nnz ≤2: {:.1%}, ≤4: {:.1%}".format(
        TH_MAIN, hc["n_edges"], hc["frac_both_nnz_le2"], hc["frac_both_nnz_le4"]))
    lines.append("")
    lines.append("Multiplizität gemeinsamer Zeilen: {}".format(hc["mult_hist"]))
    lines.append("")
    lines.append("Top Schicht-Signaturen (maninT, U₃, T₅): {}".format(
        ", ".join("{}×{}".format(tuple(s["maninT_U3_T5"]), s["count"]) for s in hc["layer_signature_top10"][:6])))
    lines.append("")
    lines.append("Top Spalten-nnz-Paare (lo, hi): {}".format(
        ", ".join("{}×{}".format(tuple(p["nnz_lo_hi"]), p["count"]) for p in hc["colnnz_pair_top10"][:6])))
    lines.append("")
    for t in (0.5, TH_MAIN):
        g = report["generic_part"][str(t)]
        if g["n_generic_cols"] == 0:
            lines.append("**Generischer Teil (θ_c = {}): LEER** — jede Spalte hat eine Kante ≥ θ_c.".format(t))
            lines.append("")
            continue
        gg = g["gershgorin_on_generic"]
        lines.append("**Generischer Teil (θ_c = {}):** {} Spalten ({:.1%}). Gershgorin: max {:.3f}, p99 {:.3f}, median {:.3f}; <0.5: {:.1%}, <1: {:.1%}. Adversarial θ′: {}".format(
            t, g["n_generic_cols"], g["frac_generic_cols"], gg["max"], gg["p99"], gg["median"],
            gg["frac_lt_0.5"], gg["frac_lt_1"],
            ", ".join("K={}: {:.3f}".format(k, v) for k, v in sorted(
                ((int(k), v) for k, v in g["adversarial_theta_prime_matching"].items())))))
        lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
