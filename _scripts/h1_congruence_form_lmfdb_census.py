#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1-Test der Kongruenzprim-Obstruktion (MG_congruence_prime_3863_obstruction_2026-06-10.md).

Frage: Existiert eine RATIONALE Newform g (= Isogenieklasse elliptischer Kurven)
auf einem Level M | 240672 mit sigma_0(240672/M) = 2 (d.h. N/M prim), deren
a_p fuer die guten Primzahlen p in {5,7,11,13,17,19,29,31} mit f_E = 240672.g
uebereinstimmen?

Hintergrund: 3863 | deg phi(240672.g1) => Kongruenzform g == f_E mod lambda
existiert (Ribet). H1 favorisiert g als Newform auf M=120336 (2 Oldform-Kopien
erklaeren qdim=3 = 1 + 2). Fuer kleine gute p gilt |a_p| <= 2*sqrt(p) << 3863,
also Kongruenz mod 3863 <=> exakte Gleichheit.

Kandidaten-Level (N/M prim): 120336 (N/2), 80224 (N/3), 10464 (N/23), 2208 (N/109).

Methode: LMFDB-API ec_curvedata (ein Vertreter pro Isogenieklasse, a_p ist
Isogenie-Invariante), lokale Punktzaehlung ueber F_p (p good fuer alle M | N,
da p coprime zu N).

Negativ-Ergebnis schliesst H1 NICHT aus (g kann nicht-rational oder
Eisenstein sein), widerlegt aber die staerkste/einfachste Form.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
from datetime import date

N = 240672  # = 2^5 * 3 * 23 * 109
CANDIDATE_LEVELS = [120336, 80224, 10464, 2208]  # N/M prim: 2, 3, 23, 109
GOOD_PRIMES = [5, 7, 11, 13, 17, 19, 29, 31]  # coprime zu N
FE_TRACES = {5: 2, 7: 0, 11: 0, 13: -6, 17: 6, 19: 0, 29: -2, 31: 4}
# Quelle f_E-Eigenwerte: LMFDB 240672.g / Zensus 2026-06-06 + v3-Launcher
# (t7_replay_fingerprint v3: {13:-6, 7:0, 11:0, 17:6, 19:0, 23:1, 29:-2, 31:4}, a_5=2)

API = "https://www.lmfdb.org/api/ec_curvedata"


def fetch_iso_classes(conductor):
    """Alle Isogenieklassen-Vertreter (lmfdb_number=1) mit ainvs holen, paged."""
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
        req = urllib.request.Request(url, headers={"User-Agent": "abc-hct-h1-census/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
        data = payload.get("data", [])
        results.extend(data)
        if len(data) < 100:  # LMFDB default page size
            break
        offset += len(data)
        time.sleep(0.5)
    return results


def ap_point_count(ainvs, p):
    """a_p = p + 1 - #E(F_p) via naive Punktzaehlung (p good, p klein)."""
    a1, a2, a3, a4, a6 = [a % p for a in ainvs]
    count = 1  # Punkt im Unendlichen
    # Quadrat-Lookup: y^2 + (a1*x + a3)*y - (x^3 + a2*x^2 + a4*x + a6) = 0
    # Substitution: z = 2y + a1*x + a3 (p ungerade) => z^2 = rhs
    inv2 = pow(2, -1, p)
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
    report = {
        "date": str(date.today()),
        "purpose": "H1 rational congruence form census (3863-obstruction)",
        "frey_class": "240672.g",
        "fe_traces": FE_TRACES,
        "good_primes": GOOD_PRIMES,
        "levels": {},
    }
    any_match = False
    for M in CANDIDATE_LEVELS:
        print("Level M={} (N/M={}):".format(M, N // M))
        classes = fetch_iso_classes(M)
        print("  Isogenieklassen: {}".format(len(classes)))
        level_entry = {"iso_class_count": len(classes), "classes": [], "matches": []}
        for rec in classes:
            ainvs = rec["ainvs"]
            if isinstance(ainvs, str):
                ainvs = json.loads(ainvs)
            traces = {p: ap_point_count(ainvs, p) for p in GOOD_PRIMES}
            match = all(traces[p] == FE_TRACES[p] for p in GOOD_PRIMES)
            agree = sum(1 for p in GOOD_PRIMES if traces[p] == FE_TRACES[p])
            level_entry["classes"].append({
                "iso": rec.get("lmfdb_iso", rec.get("lmfdb_label")),
                "traces": traces,
                "agreement": "{}/{}".format(agree, len(GOOD_PRIMES)),
                "full_match": match,
            })
            if match:
                any_match = True
                level_entry["matches"].append(rec.get("lmfdb_iso"))
                print("  MATCH: {} traces={}".format(rec.get("lmfdb_iso"), traces))
        if not level_entry["matches"]:
            best = max(level_entry["classes"],
                       key=lambda c: c["agreement"], default=None)
            print("  kein Voll-Match; bestes Agreement: {}".format(
                best["agreement"] if best else "n/a"))
        report["levels"][str(M)] = level_entry

    report["any_rational_match"] = any_match
    out_json = "_results/h1_congruence_form_lmfdb_census_2026-06-10.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("\nGesamtergebnis: any_rational_match = {}".format(any_match))
    print("JSON: {}".format(out_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
