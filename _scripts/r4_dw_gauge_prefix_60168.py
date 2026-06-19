#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R4 (D(W)-Gauge): Drop-Prime-Set als Funktion des kumulativen Row-Praefixes, 60168/raw.

Frage (R4 / Codex D2 / extern Ansatz 4): Ist D(W) eine saturierungs-/operator-bestimmte
Gauge-Groesse oder ein kanonisches Invariant? M-DET 3 zeigte: Manin-Block voller Rang, Drops
nur in der Hecke-Schicht; 240672 (6 Operatoren) hat Drop {2}, 60168 (1 Operator) {2,3,5,31}.

Dieser Test rankt KUMULATIVE Row-Praefixe der bestehenden 60168-Witness (Manin zuerst, dann
Hecke-Saturierung) ueber GF(p) und berichtet das Drop-Set je Praefix. Wenn das Drop-Set mit
hinzugefuegten Hecke-Zeilen WAECHST/WECHSELT, ist D(W) operator-bestimmt (Gauge) -> R4-KILL
fuer "D(W) als uniforme Groessenkontrolle"; bleibt es ab einem festen Operator-Set stabil,
existiert eine kanonische Stabilisierung. Reine Re-Rangberechnung (keine neue Hecke-Rechnung).

Aufruf (Mac, abc_hct): PATH-Sage; nohup python3 _scripts/r4_dw_gauge_prefix_60168.py &
"""
import json, sys, time
from pathlib import Path
from datetime import date
from collections import Counter

WITNESS = Path("_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl")
WQ = 3863
NCOLS = 31680
PRIMES = [2, 3, 5, 7, 19, 23, 31, 109]          # fokussierter Satz (bekannte Drop-Kandidaten + Kontrolle)
PREFIXES = [21104, 24000, 27000, 30000, 31680]  # Manin(~21104) -> voll(31680)
OUT_JSON = Path("_results/r4_dw_gauge_prefix_60168_{}.json".format(date.today()))
OUT_MD = Path("_results/r4_dw_gauge_prefix_60168_{}.md".format(date.today()))

def main():
    from sage.all import GF, matrix
    t0 = time.time()
    half = WQ // 2
    # alle Rows einlesen (sign-Lift), als Liste von dicts
    rows = []
    with open(WITNESS) as f:
        for line in f:
            rec = json.loads(line)
            d = {}
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WQ
                if v:
                    d[int(c)] = v
            rows.append(d)
    nrows = len(rows)
    print(f"[{time.strftime('%H:%M:%S')}] Witness geladen: {nrows} Zeilen ({time.time()-t0:.0f}s)", flush=True)

    result = {"witness_rows": nrows, "ncols": NCOLS, "primes": PRIMES,
              "prefixes": [p for p in PREFIXES if p <= nrows], "by_prefix": {}}
    for pre in PREFIXES:
        if pre > nrows:
            continue
        sub = rows[:pre]
        entries = {}
        for i, d in enumerate(sub):
            for c, v in d.items():
                entries[(i, c)] = v
        ranks = {}
        for p in PRIMES:
            t1 = time.time()
            Fp = GF(p)
            M = matrix(Fp, pre, NCOLS, {k: Fp(v) for k, v in entries.items()}, sparse=True)
            r = int(M.rank())
            ranks[p] = r
            print(f"[{time.strftime('%H:%M:%S')}] prefix={pre} p={p}: rank={r} ({time.time()-t1:.0f}s)", flush=True)
        rank_q = Counter(ranks.values()).most_common(1)[0][0]
        drops = {p: rank_q - r for p, r in ranks.items() if r < rank_q}
        result["by_prefix"][str(pre)] = {"rank_modal": rank_q,
                                         "ranks": {str(p): r for p, r in ranks.items()},
                                         "drop_set": sorted(drops.keys()),
                                         "drops": {str(p): d for p, d in sorted(drops.items())}}
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")  # inkrementell sichern
        print(f"[{time.strftime('%H:%M:%S')}] prefix={pre}: rank_Q={rank_q} drop_set={sorted(drops.keys())}", flush=True)

    lines = ["# R4 D(W)-Gauge: Drop-Set ueber kumulative Row-Praefixe (60168/raw, {})".format(date.today()), "",
             "Frage: ist das Drop-Set operator-/saturierungsbestimmt (Gauge) oder kanonisch?", "",
             "| Praefix (Rows) | rank_Q | Drop-Set |", "|---|---:|---|"]
    for pre, e in result["by_prefix"].items():
        lines.append("| {} | {} | {} |".format(pre, e["rank_modal"], e["drop_set"]))
    lines += ["", "Lesart: waechst/wechselt das Drop-Set mit Hecke-Zeilen -> D(W) ist Gauge (R4-KILL fuer",
              "uniforme Groessenkontrolle); stabilisiert es ab festem Operator-Set -> kanonische Regel moeglich."]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[{time.strftime('%H:%M:%S')}] FERTIG ({time.time()-t0:.0f}s). {OUT_JSON}", flush=True)

# Kein __name__-Guard: `sage file.py` setzt __name__ nicht auf "__main__".
main()
