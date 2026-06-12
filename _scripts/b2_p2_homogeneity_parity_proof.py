#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Schritt (j): p2-Kern-Homogenitaet — Paritaets-Mechanismus exakt testen.

Satz-Kandidaten (Beweiskette):
(S1) SYSTEM-TRANSFER: Der p2-Kernvektor v (aus dem Repair-Witness,
     Support 21.128) ist auch Kernvektor des rc3c-Witness-Systems mod 2.
     Test: jede rc3c-Zeile trifft Supp(v) auf ihren UNGERADEN Eintraegen
     in gerader Anzahl. (Mod 2: Eintrag +-1 -> 1, +-2 -> 0.)
(S2) EXAKTE HOMOGENITAET fuer kurze Zeilen: Zeile mit genau 2 ungeraden
     Eintraegen {i,j} + (S1) => v_i = v_j EXAKT.
(S3) QUANTITATIVE ANREICHERUNG: Paritaets-Konditionierung pro Zeile der
     ungeraden Laenge k erzeugt Paar-Korrelation; Vorhersage
     P(homogen | k) aus Binomial(k, p) konditioniert auf gerade Paritaet,
     verglichen mit der gemessenen Homogenitaetsrate pro k.
MECHANISMUS-TEST: mod 2 ist vorzeichenblind => auch INKOHAERENTE
     Multikanten (Vorzeichenprodukte entgegengesetzt, kleines |G|)
     muessen dieselbe Homogenitaet zeigen wie kohaerente.
"""

import json
import sys
import time
from collections import Counter, defaultdict
from datetime import date

import numpy as np
from scipy.sparse import coo_matrix, csc_matrix

SRC = "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl"
CK = "_results/mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json"
Q = 3863
NCOLS = 31680
OUT_JSON = "_results/b2_p2_homogeneity_parity_proof_{}.json".format(date.today())
OUT_MD = "_results/b2_p2_homogeneity_parity_proof_{}.md".format(date.today())


def main():
    t0 = time.time()
    v = np.zeros(NCOLS, dtype=bool)
    v[np.array(json.load(open(CK, encoding="utf-8"))["kernel_support"])] = True
    p = float(v.mean())

    rows_data = []  # (stage, [(col, val_signed)])
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ent = [(c, (val if val <= Q // 2 else val - Q)) for c, val in r["row"]]
            rows_data.append((r["stage"].split("_batch")[0], ent))
    print("{} Zeilen geladen ({:.1f}s)".format(len(rows_data), time.time() - t0), flush=True)

    # --- (S1) Paritaets-Test aller Zeilen ---
    fails = {"maninT": 0, "T5": 0}
    tot = {"maninT": 0, "T5": 0}
    odd_len_hist = Counter()
    len2_rows = []
    for stage, ent in rows_data:
        lay = "maninT" if stage.startswith("manin") else "T5"
        odd_cols = [c for c, val in ent if val % 2 != 0]
        odd_len_hist[len(odd_cols)] += 1
        tot[lay] += 1
        if sum(1 for c in odd_cols if v[c]) % 2 != 0:
            fails[lay] += 1
        if len(odd_cols) == 2:
            len2_rows.append(odd_cols)
    s1_ok = (fails["maninT"] + fails["T5"] == 0)
    print("(S1) Paritaets-Fails: maninT {}/{}, T5 {}/{} ({:.1f}s)".format(
        fails["maninT"], tot["maninT"], fails["T5"], tot["T5"], time.time() - t0), flush=True)

    # --- (S2) Laenge-2-Zeilen: exakte Homogenitaet ---
    s2_total = len(len2_rows)
    s2_homog = sum(1 for (i, j) in len2_rows if v[i] == v[j])

    # --- Gram + schwere Kanten + Multiplizitaet/Kohaerenz ---
    rows_i, cols_i, vals_i = [], [], []
    for n, (stage, ent) in enumerate(rows_data):
        for c, val in ent:
            rows_i.append(n); cols_i.append(c); vals_i.append(float(val))
    A = csc_matrix(coo_matrix((vals_i, (rows_i, cols_i)), shape=(len(rows_data), NCOLS)))
    norms = np.sqrt(np.asarray(A.multiply(A).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    C = (A.T @ A).tocoo()
    off = C.row < C.col
    gi, gj, gv = C.row[off], C.col[off], C.data[off]
    gw = np.abs(gv) / (norms[gi] * norms[gj])

    P = A.copy(); P.data = np.ones_like(P.data)
    M = (P.T @ P).tocoo()
    moff = M.row < M.col
    mi, mj, mult_all = M.row[moff], M.col[moff], M.data[moff].astype(int)
    # Gram-Wert an denselben Paaren nachschlagen (gleiche Sortierung herstellen)
    key_g = gi.astype(np.int64) * NCOLS + gj
    key_m = mi.astype(np.int64) * NCOLS + mj
    gmap = dict(zip(key_g.tolist(), gv.tolist()))
    gv_at_m = np.array([gmap.get(k, 0.0) for k in key_m.tolist()])
    print("Koinzidenz-Paare: {} ({:.1f}s)".format(len(mi), time.time() - t0), flush=True)

    homog = (v[mi] == v[mj])
    baseline = p * p + (1 - p) * (1 - p)

    def rate(mask):
        return float(homog[mask].mean()) if mask.sum() else None, int(mask.sum())

    w_at_m = np.abs(gv_at_m) / (norms[mi] * norms[mj])
    report_rates = {}
    # nach Multiplizitaet
    for m_ in (1, 2, 3, 4):
        r_, n_ = rate(mult_all == m_)
        report_rates["mult_{}".format(m_)] = {"rate": r_, "n": n_}
    # schwere vs. leichte
    r_, n_ = rate(w_at_m >= 0.5)
    report_rates["heavy_w_ge_0.5"] = {"rate": r_, "n": n_}
    r_, n_ = rate((mult_all >= 2) & (w_at_m >= 0.5))
    report_rates["mult_ge2_coherent_heavy"] = {"rate": r_, "n": n_}
    # MECHANISMUS-TEST: mult>=2 aber INKOHAERENT (Cancellation: |G| klein trotz 2 Zeilen)
    r_, n_ = rate((mult_all >= 2) & (np.abs(gv_at_m) < 1e-9))
    report_rates["mult_ge2_fully_cancelled_G_eq_0"] = {"rate": r_, "n": n_}
    r_, n_ = rate((mult_all >= 2) & (np.abs(gv_at_m) > 1e-9) & (w_at_m < 0.5))
    report_rates["mult_ge2_partial_light"] = {"rate": r_, "n": n_}

    # --- (S3) Vorhersage aus Paritaets-Konditionierung pro Zeilenlaenge k ---
    # P(homogen | Paar in Zeile ungerader Laenge k, Paritaet gerade), v-Eintraege ~ Bernoulli(p)
    def s3_pred(k, p):
        # Verteilung m ~ Bin(k,p) konditioniert auf m gerade; Paar homogen:
        # [C(m,2)+C(k-m,2)] / C(k,2)
        from math import comb
        num, den = 0.0, 0.0
        for m_ in range(0, k + 1, 2):
            w_ = comb(k, m_) * (p ** m_) * ((1 - p) ** (k - m_))
            den += w_
            num += w_ * (comb(m_, 2) + comb(k - m_, 2)) / comb(k, 2)
        return num / den

    # gemessene Homogenitaet pro gemeinsamer Zeile (Paare AUS einer Zeile)
    per_k_meas = defaultdict(lambda: [0, 0])
    for stage, ent in rows_data:
        odd_cols = [c for c, val in ent if val % 2 != 0]
        k = len(odd_cols)
        if k < 2 or k > 14:
            continue
        for a in range(k):
            for b in range(a + 1, k):
                per_k_meas[k][1] += 1
                if v[odd_cols[a]] == v[odd_cols[b]]:
                    per_k_meas[k][0] += 1
    s3_table = []
    for k in sorted(per_k_meas):
        hom, n_ = per_k_meas[k]
        s3_table.append({"k": k, "measured": hom / n_, "predicted": s3_pred(k, p), "n_pairs": n_})

    report = {
        "date": str(date.today()), "level": 60168,
        "p_support_density": p, "baseline_homog": baseline,
        "S1_parity_transfer": {"fails_maninT": fails["maninT"], "fails_T5": fails["T5"],
                               "total_rows": len(rows_data), "holds": bool(s1_ok),
                               "odd_len_hist": {str(k): c for k, c in sorted(odd_len_hist.items())}},
        "S2_len2_rows": {"n_rows": s2_total, "n_homog": s2_homog,
                         "exact": bool(s2_total == s2_homog)},
        "homogeneity_rates": report_rates,
        "S3_parity_prediction_vs_measured": s3_table,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2(j): p2-Kern-Homogenität — Paritäts-Mechanismus ({})".format(date.today()), ""]
    lines.append("Support-Dichte p = {:.4f}, Baseline-Homogenität p²+(1−p)² = {:.4f}".format(p, baseline))
    lines.append("")
    lines.append("**(S1) System-Transfer:** Paritäts-Fails maninT {}/{} | T₅ {}/{} → {}".format(
        fails["maninT"], tot["maninT"], fails["T5"], tot["T5"],
        "**BESTANDEN (exakt)**" if s1_ok else "VERLETZT"))
    lines.append("")
    lines.append("Ungerade Zeilenlängen (Histogramm): {}".format(dict(sorted(odd_len_hist.items()))))
    lines.append("")
    lines.append("**(S2) Länge-2-Zeilen:** {} Zeilen, davon homogen {} → {}".format(
        s2_total, s2_homog, "**EXAKT (Satz)**" if s2_total == s2_homog else "nicht exakt"))
    lines.append("")
    lines.append("**Homogenitätsraten (Baseline {:.3f}):**".format(baseline))
    lines.append("")
    lines.append("| Klasse | Rate | n |")
    lines.append("|---|---|---|")
    for k, d in report_rates.items():
        lines.append("| {} | {} | {} |".format(
            k, "{:.4f}".format(d["rate"]) if d["rate"] is not None else "—", d["n"]))
    lines.append("")
    lines.append("**(S3) Paritäts-Vorhersage vs. Messung (Paare pro Zeile ungerader Länge k):**")
    lines.append("")
    lines.append("| k | gemessen | vorhergesagt (Parität) | n Paare |")
    lines.append("|---|---|---|---|")
    for row in s3_table:
        lines.append("| {} | {:.4f} | {:.4f} | {} |".format(
            row["k"], row["measured"], row["predicted"], row["n_pairs"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
