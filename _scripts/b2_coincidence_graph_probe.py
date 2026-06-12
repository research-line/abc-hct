#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt 2: Relations-Koinzidenz-Graph der Witness-Matrix (240672/raw).

Beweisbare Grundlage (macht die delta_s-Messung vom 2026-06-10 erklaerbar):
  <phi_i, phi_j> = sum_r M_ri*M_rj  ist != 0  NUR wenn eine Zeile r beide
  Spalten trifft. Also:
  (L1) Ist S unabhaengig im Koinzidenz-Graphen H, dann G_S = I EXAKT.
  (L2) Gershgorin: delta(S) <= max_{i in S} sum_{j in S, j!=i} w_ij,
       w_ij = |<phi_i,phi_j>| / (||phi_i|| ||phi_j||).
Dieses Script misst H: normierte Gram-Offdiagonalen C = A^T A,
Grad-Verteilung, Gewichts-Verteilung, Dichte rho -> Random-Horn-Formel
P(S unabhaengig) ~ (1-rho)^C(s,2), verglichen mit der delta_s-Empirie.
"""

import json
import sys
import time
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix

SRC = "_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl"
Q = 3863
NCOLS = 126720
OUT_JSON = "_results/b2_coincidence_graph_witness_240672_{}.json".format(date.today())
OUT_MD = "_results/b2_coincidence_graph_witness_240672_{}.md".format(date.today())


def main():
    t0 = time.time()
    rows, cols, vals = [], [], []
    n_rows = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q
                rows.append(n_rows); cols.append(c); vals.append(float(v))
            n_rows += 1
    A = csc_matrix(coo_matrix((vals, (rows, cols)), shape=(n_rows, NCOLS)))
    print("A: {}x{}, nnz={} ({:.1f}s)".format(*A.shape, A.nnz, time.time() - t0), flush=True)

    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0

    # Gram (sparse) und Normierung
    C = (A.T @ A).tocoo()
    print("Gram nnz (inkl. Diagonale): {} ({:.1f}s)".format(C.nnz, time.time() - t0), flush=True)
    off = C.row != C.col
    i, j, v = C.row[off], C.col[off], C.data[off]
    w = np.abs(v) / (norms[i] * norms[j])
    nz = w > 1e-15
    i, j, w = i[nz], j[nz], w[nz]
    n_edges = int(len(w) // 2)  # symmetrisch

    # Grad-Verteilung (Anzahl Koinzidenz-Partner pro Spalte)
    deg = np.bincount(i, minlength=NCOLS)
    # gewichteter Grad (Gershgorin-Radius pro Spalte)
    gersh = np.zeros(NCOLS)
    np.add.at(gersh, i, w)

    rho = n_edges / (NCOLS * (NCOLS - 1) / 2)
    report = {
        "date": str(date.today()),
        "source": SRC,
        "matrix": {"shape": list(A.shape), "nnz": int(A.nnz)},
        "graph": {
            "n_edges": n_edges,
            "density_rho": rho,
            "degree": {
                "max": int(deg.max()),
                "mean": float(deg.mean()),
                "median": float(np.median(deg)),
                "p99": float(np.quantile(deg, 0.99)),
                "isolated_cols": int((deg == 0).sum()),
            },
            "weights": {
                "max": float(w.max()),
                "median": float(np.median(w)),
                "p99": float(np.quantile(w, 0.99)),
            },
            "gershgorin_radius": {
                "max": float(gersh.max()),
                "median": float(np.median(gersh)),
                "p99": float(np.quantile(gersh, 0.99)),
                "frac_cols_radius_lt_1": float((gersh < 1.0).mean()),
            },
        },
    }
    # Random-Horn-Vorhersage: P(s-Set unabhaengig) ~ (1-rho)^{s(s-1)/2}
    report["random_horn_prediction"] = {
        str(s): float((1 - rho) ** (s * (s - 1) / 2)) for s in (8, 16, 32, 64, 128)}

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    g = report["graph"]
    lines = ["# B2: Koinzidenz-Graph der Witness-Matrix 240672/raw ({})".format(date.today()), ""]
    lines.append("Kanten (i~j ⟺ ⟨φ_i,φ_j⟩≠0): {} | Dichte ρ = {:.3e}".format(g["n_edges"], rho))
    lines.append("")
    lines.append("| Größe | max | median | p99 |")
    lines.append("|---|---|---|---|")
    lines.append("| Grad (Partner/Spalte) | {} | {} | {} |".format(
        g["degree"]["max"], g["degree"]["median"], g["degree"]["p99"]))
    lines.append("| Kantengewicht w_ij | {:.4f} | {:.4f} | {:.4f} |".format(
        g["weights"]["max"], g["weights"]["median"], g["weights"]["p99"]))
    lines.append("| Gershgorin-Radius/Spalte | {:.4f} | {:.4f} | {:.4f} |".format(
        g["gershgorin_radius"]["max"], g["gershgorin_radius"]["median"], g["gershgorin_radius"]["p99"]))
    lines.append("")
    lines.append("Isolierte Spalten: {} | Spalten mit Gershgorin-Radius < 1: {:.1%}".format(
        g["degree"]["isolated_cols"], g["gershgorin_radius"]["frac_cols_radius_lt_1"]))
    lines.append("")
    lines.append("Random-Horn-Vorhersage P(s-Set unabhängig) = (1−ρ)^(s(s−1)/2): " +
                 ", ".join("s={}: {:.3f}".format(s, p) for s, p in
                           sorted(((int(k), v) for k, v in report["random_horn_prediction"].items()))))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
