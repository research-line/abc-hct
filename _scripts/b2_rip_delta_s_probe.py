#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2: delta_s-RIP-Messung der Hecke-Witness-Matrix (240672/raw, Cremona-Witness).

Kontext (TODO B2, Codex-Audit 2 + BDFKK-Template): CR-2b-No-Escape als
sparse-nullvector-/RIP-Frage. Die SPALTEN der Witness-Matrix (Zeilen =
manin_T + U3 + T5-Relationen, symmetrisch nach Z geliftet, ueber R
normalisiert) werden auf restricted isometry getestet:

    delta(S) = max |Eigenwert(G_S) - 1|,  G_S = A_S^T A_S (normalisiert),
    zusaetzlich lambda_min(G_S) (sparse-nullvector-Relevanz).

BDFKK-Dichotomie als Testdesign: drei Sampling-Modi pro Sparsity s --
  random      : s gleichverteilte Spalten (Pseudozufalls-Horn)
  consecutive : s aufeinanderfolgende Spaltenindizes (Struktur-Proxy)
  arith_prog  : arithmetische Progression mit zufaelliger Differenz
                (additive Struktur im Indexraum, Struktur-Horn)
Frage: Ist delta_s im Random-Horn klein (RIP-artig) und reissen
strukturierte Mengen aus (dann ist CR-2b eine deterministische
RIP-Luecke im BDFKK-Sinn und die Dichotomie-Strategie greift)?

Caveat: Spaltenindex-Nachbarschaft ist ein PROXY fuer additive Struktur
im Manin-/P1-Raum (Quotientenspalten); Befunde sind diagnostisch.
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
SPARSITIES = [8, 16, 32, 64, 128]
NSAMPLES = 400
SEED = 20260610
OUT_JSON = "_results/b2_rip_delta_s_witness_240672_{}.json".format(date.today())
OUT_MD = "_results/b2_rip_delta_s_witness_240672_{}.md".format(date.today())


def load_matrix():
    rows, cols, vals = [], [], []
    n_rows = 0
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            for c, v in r["row"]:
                v = v if v <= Q // 2 else v - Q  # symmetrischer Lift
                rows.append(n_rows)
                cols.append(c)
                vals.append(float(v))
            n_rows += 1
    A = coo_matrix((vals, (rows, cols)), shape=(n_rows, NCOLS))
    return csc_matrix(A)


def main():
    t0 = time.time()
    print("Lade Witness-Matrix ...", flush=True)
    A = load_matrix()
    print("  shape={}, nnz={} ({:.1f}s)".format(A.shape, A.nnz, time.time() - t0), flush=True)

    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    nonzero_cols = np.nonzero(norms > 0)[0]
    print("  Spalten mit nnz>0: {} / {}".format(len(nonzero_cols), NCOLS), flush=True)

    rng = np.random.default_rng(SEED)
    pos = {c: i for i, c in enumerate(nonzero_cols)}

    def delta_of(cols_set):
        cols_set = [c for c in cols_set if norms[c] > 0]
        if len(cols_set) < 2:
            return None, None
        Asub = A[:, cols_set].toarray()
        Asub /= norms[cols_set]
        G = Asub.T @ Asub
        ev = np.linalg.eigvalsh(G)
        return float(max(abs(ev[0] - 1), abs(ev[-1] - 1))), float(ev[0])

    results = {}
    for s in SPARSITIES:
        modes = {"random": [], "consecutive": [], "arith_prog": []}
        lmins = {"random": [], "consecutive": [], "arith_prog": []}
        for _ in range(NSAMPLES):
            # random
            S = rng.choice(nonzero_cols, size=s, replace=False)
            d, lm = delta_of(list(S))
            if d is not None:
                modes["random"].append(d); lmins["random"].append(lm)
            # consecutive (im Raum der nonzero-Spalten)
            start = rng.integers(0, len(nonzero_cols) - s)
            S = nonzero_cols[start:start + s]
            d, lm = delta_of(list(S))
            if d is not None:
                modes["consecutive"].append(d); lmins["consecutive"].append(lm)
            # arithmetische Progression im Spaltenindexraum
            diff_max = min(2048, (NCOLS - 1) // s)
            diff = int(rng.integers(2, diff_max))
            start = int(rng.integers(0, NCOLS - s * diff))
            S = [start + k * diff for k in range(s)]
            d, lm = delta_of(S)
            if d is not None:
                modes["arith_prog"].append(d); lmins["arith_prog"].append(lm)
        results[s] = {}
        for m in modes:
            arr = np.array(modes[m]); lmin = np.array(lmins[m])
            results[s][m] = {
                "n": len(arr),
                "delta_median": float(np.median(arr)),
                "delta_p95": float(np.quantile(arr, 0.95)),
                "delta_max": float(arr.max()),
                "lambda_min_median": float(np.median(lmin)),
                "lambda_min_min": float(lmin.min()),
                "frac_singular": float((lmin < 1e-9).mean()),
            }
        print("s={} fertig ({:.1f}s)".format(s, time.time() - t0), flush=True)

    report = {
        "date": str(date.today()),
        "source": SRC,
        "q": Q,
        "lift": "symmetric",
        "shape": list(A.shape),
        "nnz": int(A.nnz),
        "nonzero_cols": int(len(nonzero_cols)),
        "n_samples_per_mode": NSAMPLES,
        "seed": SEED,
        "results": results,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2: delta_s-RIP-Messung der Witness-Matrix 240672/raw ({})".format(date.today()), ""]
    lines.append("Matrix: {}x{}, nnz={}, Spalten normalisiert (R, symmetrischer Lift mod {}).".format(
        A.shape[0], A.shape[1], A.nnz, Q))
    lines.append("{} Samples je Modus. Modi: random / consecutive / arith_prog (Index-Proxy für additive Struktur).".format(NSAMPLES))
    lines.append("")
    lines.append("| s | Modus | δ Median | δ p95 | δ max | λ_min Median | λ_min min | Anteil singulär |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in SPARSITIES:
        for m in ("random", "consecutive", "arith_prog"):
            r = results[s][m]
            lines.append("| {} | {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.3f} |".format(
                s, m, r["delta_median"], r["delta_p95"], r["delta_max"],
                r["lambda_min_median"], r["lambda_min_min"], r["frac_singular"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
