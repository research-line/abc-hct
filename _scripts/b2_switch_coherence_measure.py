#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 Switch-Kohaerenz: Messung am konkreten Z/4-Lift vtilde.

Lemma-Kandidat L-SWITCH: Fuer jede rein-+-1-Zeile r mit Support-Schnitt
genau {i, j} (auf ungeraden Eintraegen) gilt s_r = +1, d.h. die Restsumme
sum_{c != i,j} M_rc * vtilde_c == 0 mod 4. Daraus folgt (G3) auf
+-1-Zeilen sofort: sigma_i*sigma_j = -eps_r ist durch das Paar fixiert,
zwei Zeilen mit eps_1 != eps_2 koennen nicht beide Spalten im Support haben.

Gemessen wird:
(1) s_r-Verteilung nach (Schicht, rein-+-1?, Support-Schnitt m=2).
(2) Wo sitzen die vtilde==2-Spalten: Eintragsparitaet ihrer Inzidenzen
    (gerade Eintraege sind mod-4-harmlos: +-2*2=+-4==0).
(3) Falls s_r != +1 vorkommt: alle 4 Lifts (w + ker, ker = {0, v}) pruefen
    — Lift-Eichfreiheit (2-dim Kern: nur v verfuegbar; v' unbekannt,
    wird dokumentiert).
"""

import json
import sys
import time
from collections import Counter
from datetime import date

import numpy as np

SRC = "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl"
VT = "_results/b2_z4_lift_vtilde_60168.npy"
Q = 3863
NCOLS = 31680
OUT_JSON = "_results/b2_switch_coherence_measure_{}.json".format(date.today())
OUT_MD = "_results/b2_switch_coherence_measure_{}.md".format(date.today())


def main():
    t0 = time.time()
    vt = np.load(VT).astype(np.int64)
    supp = (vt % 2 == 1)
    sigma = np.where(vt == 1, 1, np.where(vt == 3, -1, 0))
    print("vtilde geladen: counts", {k: int((vt == k).sum()) for k in range(4)}, flush=True)

    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ent = [(c, (val if val <= Q // 2 else val - Q)) for c, val in r["row"]]
            rows.append((r["stage"].split("_batch")[0], ent))

    stats = Counter()
    s_neg_examples = []
    col_2_odd_incidence = Counter()  # vtilde==2-Spalten: Paritaet der Eintraege ihrer Zeilen
    for stage, ent in rows:
        lay = "maninT" if stage.startswith("manin") else "T5"
        pure1 = all(abs(val) == 1 for _, val in ent)
        odd = [(c, val) for c, val in ent if val % 2 != 0]
        on_supp = [(c, val) for c, val in odd if supp[c]]
        # vtilde==2-Inzidenz-Statistik
        for c, val in ent:
            if vt[c] == 2:
                col_2_odd_incidence[("odd" if val % 2 else "even", lay)] += 1
        if len(on_supp) != 2:
            continue
        (i, vi), (j, vj) = on_supp
        eps = 1 if vi * vj > 0 else -1
        rest = sum(val * vt[c] for c, val in ent if c != i and c != j) % 4
        # Zeile gesamt == 0 mod 4 (Kern!), also: vi*sigma_i + vj*sigma_j + rest == 0
        # s_r aus sigma_i*sigma_j = -eps*s_r:
        s_r = -eps * sigma[i] * sigma[j]
        assert rest in (0, 2)
        assert (s_r == 1) == (rest == 0), "Switch-Formel inkonsistent"
        stats[(lay, "pure1" if pure1 else "has2", "s=+1" if s_r == 1 else "s=-1")] += 1
        if s_r == -1 and pure1 and len(s_neg_examples) < 8:
            s_neg_examples.append({"layer": lay, "pair": [int(i), int(j)],
                                   "row_len": len(ent),
                                   "rest_cols_vt2_odd": [int(c) for c, val in ent
                                                         if c != i and c != j and vt[c] == 2 and val % 2]})

    report = {"date": str(date.today()),
              "s_r_distribution": {"{}|{}|{}".format(*k): v for k, v in sorted(stats.items())},
              "vt2_incidence_by_entry_parity": {"{}|{}".format(*k): v
                                                for k, v in sorted(col_2_odd_incidence.items())},
              "s_neg_pure1_examples": s_neg_examples}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B2: Switch-Kohärenz-Messung am ℤ/4-Lift ({})".format(date.today()), ""]
    lines.append("| Schicht | Zeilentyp | s_r | n |")
    lines.append("|---|---|---|---|")
    for k, v in sorted(stats.items()):
        lines.append("| {} | {} | {} | {} |".format(k[0], k[1], k[2], v))
    lines.append("")
    lines.append("ṽ=2-Spalten-Inzidenzen nach Eintragsparität: {}".format(
        dict(sorted(col_2_odd_incidence.items()))))
    lines.append("")
    if s_neg_examples:
        lines.append("s = −1 auf rein-±1-Zeilen (Beispiele): {}".format(s_neg_examples[:4]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    for k, v in sorted(stats.items()):
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
