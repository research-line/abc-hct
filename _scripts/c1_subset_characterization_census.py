#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 Subset-Charakterisierung: Eigenform-Zerlegung der 48-dim Gate-2-Baseline.

Q_W-Baseline qdim = 48 = Dimension des simultanen (T3-1, T5-2)-Eigenraums
im witness-erzeugten +1-Quotienten mod 3863. Dieses Script rechnet den
RATIONALEN Anteil exakt: alle elliptischen Isogenieklassen mit Conductor
d | 240672, a3 = 1 UND a5 = 2 (fuer |a_p| <= 2 sqrt p ist = dasselbe wie
== mod 3863); jede traegt sigma_0(240672/d) Oldform-Kopien bei.

Zusaetzlich: a13/a17/a19/a23-Profile aller Treffer -> Validierung des
beobachteten qdim-Verlaufs (48 -> 3 nach T13(-6); 3 -> 2 -> 1 unter U23(+1)).
Der nicht durch rationale Kurven erklaerte Rest = nicht-rationale Orbits
und/oder Eisenstein-Anteil (Ribet-Form-Frage).
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from math import isqrt

N = 240672  # 2^5 * 3 * 23 * 109
AP_FE = {13: -6, 17: 6, 19: 0, 23: 1}
API = "https://www.lmfdb.org/api/ec_curvedata"
OUT_JSON = "_results/c1_subset_characterization_census_{}.json".format(date.today())
OUT_MD = "_results/c1_subset_characterization_census_{}.md".format(date.today())


def divisors(n):
    ds = [1]
    for p, e in [(2, 5), (3, 1), (23, 1), (109, 1)]:
        ds = [d * p ** k for d in ds for k in range(e + 1)]
    return sorted(ds)


def sigma0(n):
    c = 0
    for d in range(1, n + 1):
        if n % d == 0:
            c += 1
    return c


def fetch_iso_classes(conductor):
    import subprocess
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
        payload = None
        for attempt in range(8):
            try:
                out = subprocess.run(
                    ["curl", "-s", "-m", "60", url, "-H", "User-Agent: abc-hct-c1-census/1.0"],
                    capture_output=True, text=True, timeout=90).stdout
                payload = json.loads(out)
                break
            except Exception:
                time.sleep(5 + 10 * attempt)
        if payload is None:
            raise RuntimeError("LMFDB nach 5 Versuchen nicht erreichbar: d={}".format(conductor))
        data = payload.get("data", [])
        results.extend(data)
        if len(data) < 100:
            break
        offset += len(data)
        time.sleep(0.4)
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
    t0 = time.time()
    hits = []
    per_level = {}
    import os
    CKPT = "_results/c1_census_checkpoint.json"
    cache = json.load(open(CKPT, encoding="utf-8")) if os.path.exists(CKPT) else {}
    for d in divisors(N):
        if d < 11:
            continue
        if str(d) in cache:
            classes = cache[str(d)]
        else:
            try:
                classes = fetch_iso_classes(d)
            except Exception as e:
                print("  d={}: API-Fehler {} — retry nach 30s".format(d, e), flush=True)
                time.sleep(30)
                classes = fetch_iso_classes(d)
            cache[str(d)] = classes
            with open(CKPT, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        n_match = 0
        for c in classes:
            ainvs = c["ainvs"]
            # a3, a5 nur fuer gute Reduktion sinnvoll: p | d => U_p-Eigenwert,
            # Punktzaehlung liefert dann a_p der singulaeren Faser — wir
            # markieren bad primes explizit.
            rec = {"label": c["lmfdb_iso"], "level": d, "mult_sigma0": sigma0(N // d)}
            ok = True
            for p, target in ((3, 1), (5, 2)):
                if d % p == 0:
                    ap = ap_point_count(ainvs, p)  # = U_p-Eigenwert bei mult. Reduktion
                else:
                    ap = ap_point_count(ainvs, p)
                rec["a{}".format(p)] = ap
                if ap != target:
                    ok = False
                    break
            if not ok:
                continue
            for p in (13, 17, 19, 23):
                rec["a{}".format(p)] = ap_point_count(ainvs, p)
            rec["bad_primes_in_d"] = [p for p in (2, 3, 23, 109) if d % p == 0]
            hits.append(rec)
            n_match += 1
        per_level[d] = {"n_classes": len(classes), "n_match_a3_1_a5_2": n_match}
        print("d={}: {} Klassen, {} mit (a3,a5)=(1,2) ({:.0f}s)".format(
            d, len(classes), n_match, time.time() - t0), flush=True)
        time.sleep(1.5)

    total_rational = sum(h["mult_sigma0"] for h in hits)
    # Verlaufs-Validierung: welche Treffer ueberleben T13 - (-6)?
    survive_t13 = [h for h in hits if h["a13"] == AP_FE[13]]
    survive_t13_17_19 = [h for h in survive_t13
                         if h["a17"] == AP_FE[17] and h["a19"] == AP_FE[19]]
    survive_all = [h for h in survive_t13_17_19 if h["a23"] == AP_FE[23]]

    report = {
        "date": str(date.today()),
        "baseline_qdim": 48,
        "per_level": per_level,
        "hits": hits,
        "total_rational_dimension": total_rational,
        "unexplained_dimension": 48 - total_rational,
        "survive_T13": [{"label": h["label"], "mult": h["mult_sigma0"],
                         "a13": h["a13"], "a17": h["a17"], "a19": h["a19"], "a23": h["a23"]}
                        for h in survive_t13],
        "survive_T13_T17_T19_dim": sum(h["mult_sigma0"] for h in survive_t13_17_19),
        "survive_all_incl_U23": [h["label"] for h in survive_all],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# C1: Eigenform-Zerlegung der 48-dim Gate-2-Baseline (rationaler Anteil) ({})".format(date.today()), ""]
    lines.append("LMFDB-Census: alle Isogenieklassen mit Conductor d | 240672, (a₃, a₅) = (1, 2); Oldform-Multiplizität σ₀(240672/d).")
    lines.append("")
    lines.append("| Klasse | Level d | σ₀(N/d) | a₁₃ | a₁₇ | a₁₉ | a₂₃ |")
    lines.append("|---|---|---|---|---|---|---|")
    for h in sorted(hits, key=lambda x: (x["level"], x["label"])):
        lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            h["label"], h["level"], h["mult_sigma0"], h["a13"], h["a17"], h["a19"], h["a23"]))
    lines.append("")
    lines.append("**Rational erklärte Dimension: {} von 48 — unerklärt: {}** (= nicht-rationale Orbits / Eisenstein / Witness-Effekte).".format(
        total_rational, 48 - total_rational))
    lines.append("")
    lines.append("**Verlaufs-Validierung:** T₁₃-Überlebende (a₁₃ = −6): Gesamtdim {} | nach T₁₇/T₁₉: {} | nach U₂₃ (alle f_E-Eigenwerte): {}".format(
        sum(h["mult_sigma0"] for h in survive_t13),
        report["survive_T13_T17_T19_dim"], report["survive_all_incl_U23"]))
    lines.append("")
    lines.append("Laufzeit: {:.0f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
