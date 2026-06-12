#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Survivor-Census auf Level N=240672 selbst (Plateau-Erklaerung qdim=3).

Anlass (2026-06-10): v3 (q'=5077, Nicht-Kongruenzprim) zeigt nach T_13 dasselbe
Plateau qdim=3 wie v2/v2b (q=3863). Frage: Wie viel des Plateaus ist RATIONAL-
strukturell erklaerbar durch Isogenieklassen auf N=240672 selbst, deren a_p auf
den bisher getesteten Replay-Primzahlen {7,11,13,17,19} mit f_E = 240672.g
uebereinstimmen (ueber Z, also mod jedem q)?

Bekannter Kandidat: 240672.c = chi_{-1}-Twist von g (Job-Note hecke_cremona
2026-06-05): identische a_p fuer p=1 mod 4 und fuer a_p=0; Separatoren nur
T_3 (bad/U_3), T_23, T_31. KEINER der Replay-Laeufe v1/v2 und v3-bisher hat
einen c-Separator getestet.

Output: pro Isogenieklasse a_p-Profil, Agreement, Separator-Liste
(welcher gute Replay-Prime trennt die Klasse von f_E), plus Vorhersagen
fuer T_23/T_29/T_31 in v2b und v3.

Methode wie h1_congruence_form_lmfdb_census.py: LMFDB-API ec_curvedata
(ein Vertreter pro Isogenieklasse, a_p ist Isogenie-Invariante), lokale
Punktzaehlung ueber F_p fuer gute p (coprime zu N = 2^5*3*23*109).
"""

import json
import sys
import time
import urllib.request
import urllib.parse
from datetime import date

N = 240672  # = 2^5 * 3 * 23 * 109
# ACHTUNG (Korrektur 2026-06-10, Codex-Audit): 23 | N ist LEVELPRIME, nicht good.
# a_23 ist der U_23-Eigenwert (multiplikative Reduktion, +-1). Die naive
# Punktzaehlung liefert ihn trotzdem korrekt: beim Knoten zaehlt der singulaere
# Punkt als 1 affine Loesung, also count = (p - a_p - 1) + 1 + 1 = p + 1 - a_p.
# Empirisch validiert (Mac-Sage 2026-06-10): HeilbronnCremona-Hecke-Matrix
# liefert fuer p || N exakt die U_p-Eigenwerte (8/8 Testfaelle N=14,15,21,33).
PROBE_PRIMES = [5, 7, 11, 13, 17, 19, 23, 29, 31]  # alle ausser 23 coprime zu N
GOOD_PRIMES = PROBE_PRIMES  # Alias (historischer Name, siehe Kommentar oben)
FE_TRACES = {5: 2, 7: 0, 11: 0, 13: -6, 17: 6, 19: 0, 23: 1, 29: -2, 31: 4}
# Quelle: LMFDB 240672.g / Zensus 2026-06-06; a_23=U_23-Eigenwert=1 (v2b-Launcher-Log).
TESTED_SO_FAR = [7, 11, 13, 17, 19]  # v1+v2+v2b(bis T_19)+v3(bis T_13), gute p
PENDING = [23, 29, 31]

API = "https://www.lmfdb.org/api/ec_curvedata"


def fetch_iso_classes(conductor):
    results = []
    offset = 0
    while True:
        params = {
            "conductor": "i{}".format(conductor),
            "lmfdb_number": "i1",
            "_format": "json",
            "_fields": "lmfdb_label,lmfdb_iso,ainvs",
            "_offset": str(offset),
        }
        url = API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "abc-hct-survivor-census/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
        data = payload.get("data", [])
        results.extend(data)
        if len(data) < 100:
            break
        offset += len(data)
        time.sleep(0.5)
    return results


def ap_point_count(ainvs, p):
    a1, a2, a3, a4, a6 = [a % p for a in ainvs]
    count = 1
    squares = {}
    for z in range(p):
        squares.setdefault((z * z) % p, []).append(z)
    for x in range(p):
        rhs = (4 * (x * x * x + a2 * x * x + a4 * x + a6)
               + (a1 * x + a3) ** 2) % p
        zs = squares.get(rhs, [])
        count += len(zs)
    return p + 1 - count


def main():
    print("Hole Isogenieklassen auf Conductor N={} ...".format(N))
    classes = fetch_iso_classes(N)
    print("  Isogenieklassen: {}".format(len(classes)))

    report = {
        "date": str(date.today()),
        "purpose": "Survivor census on level N itself (qdim=3 plateau explanation)",
        "frey_class": "240672.g",
        "fe_traces": FE_TRACES,
        "good_primes": GOOD_PRIMES,
        "tested_so_far": TESTED_SO_FAR,
        "pending": PENDING,
        "iso_class_count": len(classes),
        "classes": [],
    }

    plateau_survivors = []  # matchen auf allen TESTED_SO_FAR
    for rec in classes:
        ainvs = rec["ainvs"]
        if isinstance(ainvs, str):
            ainvs = json.loads(ainvs)
        traces = {p: ap_point_count(ainvs, p) for p in GOOD_PRIMES}
        separators = [p for p in GOOD_PRIMES if traces[p] != FE_TRACES[p]]
        survives_tested = all(traces[p] == FE_TRACES[p] for p in TESTED_SO_FAR)
        entry = {
            "iso": rec.get("lmfdb_iso", rec.get("lmfdb_label")),
            "traces": traces,
            "separators_good": separators,
            "survives_tested_so_far": survives_tested,
            "first_pending_separator": next(
                (p for p in PENDING if traces[p] != FE_TRACES[p]), None),
        }
        report["classes"].append(entry)
        if survives_tested:
            plateau_survivors.append(entry)

    report["plateau_survivors_tested_so_far"] = [e["iso"] for e in plateau_survivors]

    print("\nKlassen, die ALLE bisher getesteten Replay-Primes {} ueberleben:".format(TESTED_SO_FAR))
    for e in plateau_survivors:
        print("  {}  traces={}  Separatoren(gut)={}  erster offener Separator: {}".format(
            e["iso"], e["traces"], e["separators_good"], e["first_pending_separator"]))

    out_json = "_results/survivor_census_level_n_240672_2026-06-10.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("\nJSON: {}".format(out_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
