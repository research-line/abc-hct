#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2: v'-Identifikation + Kasteleyn-Messung am 60168-Zeugen.

(1) KERN-BASIS mod 2 des rc3c-Systems (Gauss ueber F2 mit Python-Int-
    Bitmasken, Rang 31.678 -> Kern-Dim 2). Identifiziere v' (zweiter
    Kernvektor neben dem bekannten p2-Kern v).
(2) v'-CHARAKTERISIERUNG: Support-Groesse; manin-m-Verteilung (trifft
    jedes Dreieck gerade — m in {0,2}? 2/3-Gesetz? Dimer-Komplement?);
    Ueberlapp mit v; dasselbe fuer v+v'.
(3) KASTELEYN-MESSUNG: sigma-Eichung tau (sigma auf Supp(v), +1 sonst).
    Nach Eichung hat jedes manin-Dreieck auf seinem Support-Paar Produkt
    -1 (Satz). Gemessen: Verteilung des vollen Dreieck-Produkts
    prod_{c in r} sign(M'_rc) — haengt nur vom Dimer-Kanten-Vorzeichen ab
    (eichfrei auf Dimer-Kanten: Verteilung dokumentiert die verbleibende
    Freiheit/Struktur fuer eine Kasteleyn-Orientierungsregel).
"""

import json
import sys
import time
from collections import Counter
from datetime import date

import numpy as np

SRC = "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl"
CK = "_results/mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json"
VT = "_results/b2_z4_lift_vtilde_60168.npy"
Q = 3863
N = 31680
OUT_JSON = "_results/b2_kernel_basis_vprime_kasteleyn_{}.json".format(date.today())
OUT_MD = "_results/b2_kernel_basis_vprime_kasteleyn_{}.md".format(date.today())


def main():
    t0 = time.time()
    rows_ent = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ent = [(c, (val if val <= Q // 2 else val - Q)) for c, val in r["row"]]
            rows_ent.append((r["stage"].split("_batch")[0], ent))

    # --- (1) Gauss ueber F2 (Python-Int-Bitmasken, Zeilen als Spalten-Sets) ---
    basis = {}  # pivot_col -> row_bitmask
    for stage, ent in rows_ent:
        row = 0
        for c, val in ent:
            if val % 2 != 0:
                row |= (1 << c)
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                break
    rank = len(basis)
    free_cols = [c for c in range(N) if c not in basis]
    print("Rang mod 2: {} | freie Spalten: {} ({:.1f}s)".format(
        rank, free_cols, time.time() - t0), flush=True)

    # Kernvektoren: aufsteigende Substitution (Pivot = hoechstes Bit der Zeile,
    # alle anderen Bits sind kleiner und bei aufsteigender Abarbeitung bestimmt)
    kernel_vecs = []
    for fcol in free_cols:
        xbits = 1 << fcol
        for p in sorted(basis):
            row = basis[p] & ~(1 << p)
            if (row & xbits).bit_count() & 1:
                xbits |= 1 << p
        x = np.zeros(N, dtype=np.int64)
        for c in range(N):
            if (xbits >> c) & 1:
                x[c] = 1
        kernel_vecs.append(x)
    print("Kernbasis extrahiert ({:.1f}s)".format(time.time() - t0), flush=True)

    # Verifikation + Identifikation von v
    v = np.zeros(N, dtype=np.int64)
    v[np.array(json.load(open(CK, encoding="utf-8"))["kernel_support"])] = 1

    def is_kernel(x):
        for stage, ent in rows_ent:
            s = sum(x[c] for c, val in ent if val % 2 != 0) % 2
            if s:
                return False
        return True

    span = {}
    k0, k1 = kernel_vecs
    for name, x in (("k0", k0), ("k1", k1), ("k0+k1", (k0 + k1) % 2)):
        span[name] = x
    v_match = None
    for name, x in span.items():
        if (x == v).all():
            v_match = name
    print("v im Spann als:", v_match, flush=True)
    # v' = der Basisvektor (oder Kombination), der nicht v ist:
    candidates = {n: x for n, x in span.items() if not (x == v).all()}

    # --- (2) Charakterisierung aller Nicht-v-Kernvektoren ---
    tri = [ent for stage, ent in rows_ent if stage.startswith("manin")]
    char = {}
    for name, x in candidates.items():
        supp_size = int(x.sum())
        mdist = Counter()
        for ent in tri:
            odd = [c for c, val in ent if val % 2 != 0]
            mdist[sum(1 for c in odd if x[c])] += 1
        # Dimer-Test: Komplement von x trifft jedes Dreieck genau 1?
        is_dimer_compl = all(
            sum(1 for c in [cc for cc, vv in ent if vv % 2 != 0] if not x[c]) == 1
            for ent in tri) if supp_size > 0 else False
        char[name] = {"support_size": supp_size,
                      "frac": supp_size / N,
                      "manin_m_dist": {str(k): c for k, c in sorted(mdist.items())},
                      "complement_is_dimer": bool(is_dimer_compl),
                      "overlap_with_v": int(((x == 1) & (v == 1)).sum()),
                      "verified_kernel": bool(is_kernel(x))}
        print(name, char[name], flush=True)

    # --- (3) Kasteleyn-Messung: Dreieck-Produkte in sigma-Eichung ---
    vt = np.load(VT).astype(np.int64)
    tau = np.where(vt == 3, -1, 1)  # sigma auf Supp, +1 auf Komplement
    prod_dist = Counter()
    dimer_sign_dist = Counter()
    for ent in tri:
        odd = [(c, val) for c, val in ent if val % 2 != 0]
        if len(odd) != 3:
            continue
        signs = [(1 if val * tau[c] > 0 else -1) for c, val in odd]
        prod_dist[np.prod(signs)] += 1
        # Vorzeichen der Dimer-Kante (Komplement-Spalte) in der Eichung
        for c, val in odd:
            if vt[c] % 2 == 0:
                dimer_sign_dist[1 if val * tau[c] > 0 else -1] += 1

    report = {"date": str(date.today()), "rank_mod2": rank, "free_cols": free_cols,
              "v_in_span_as": v_match,
              "nonv_kernel_vectors": {n: {k: vv for k, vv in d.items()} for n, d in char.items()},
              "kasteleyn_triangle_product_dist": {str(k): c for k, c in sorted(prod_dist.items())},
              "kasteleyn_dimer_edge_sign_dist": {str(k): c for k, c in sorted(dimer_sign_dist.items())}}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2: v′-Identifikation + Kasteleyn-Messung ({})".format(date.today()), ""]
    lines.append("Rang mod 2: {} | freie Spalten: {} | v im Spann als: {}".format(rank, free_cols, v_match))
    lines.append("")
    for n, d in char.items():
        lines.append("**{}**: Support {} ({:.1%}), manin-m-Verteilung {}, Komplement-Dimer: {}, Überlapp mit v: {}, Kern verifiziert: {}".format(
            n, d["support_size"], d["frac"], d["manin_m_dist"], d["complement_is_dimer"],
            d["overlap_with_v"], d["verified_kernel"]))
    lines.append("")
    lines.append("**Kasteleyn (σ-Eichung):** Dreieck-Produkte {} | Dimer-Kanten-Vorzeichen {}".format(
        dict(sorted(prod_dist.items())), dict(sorted(dimer_sign_dist.items()))))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
