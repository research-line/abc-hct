#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B6/K2 Kill-Kriterium 1: Sieht die S-arithmetische Kodierung die Qualitaet?

EK-Template (Einsiedler-Kleinbock math/0506514): Punkt x_u = u(a/c)-Translat
des Basispunkts in X_S = SL2(Z[1/S]) \\ SL2(R x prod_p Q_p). Mahler:
x verlaesst K_delta <=> existiert 0 != v in Lambda_x mit ALLEN Stellen-Normen
<= delta. Diagonalfluss alpha(t, (n_p)): R-Komponente diag(e^t, e^-t),
p-Komponente diag(p^{n_p}, p^{-n_p}).

Kodierung: Lambda_x = {(q, q*u - q0) : (q, q0) in Z[1/S]^2}, u = a/c,
diagonal eingebettet in R^2 x prod_p Q_p^2.

TIEFE: depth* = max ueber Kegel (n_p <= 0, t + sum n_p log p >= 0) von
-log( min_v max_nu N_nu(v) ). Diskret: endliche Kandidatenmenge (q, q0)
aus S-Zahlen, n_p ganzzahlig in beschraenktem Fenster, t optimal reell.

KILL-KRITERIUM: Wenn depth* fuer das Reyssat-Tripel (q=1.63) NICHT
deutlich groesser ist als fuer Kontroll-Tripel gleicher Groessenordnung
mit q ~ 1.0-1.2, sieht die Kodierung die Qualitaet nicht -> Kill.
"""

import json
import sys
import time
from datetime import date
from fractions import Fraction
from itertools import product as iproduct
from math import log

TRIPLES = {
    # name: (a, b, c) koprim, a+b=c
    "reyssat_q1.63": (2, 3**10 * 109, 23**5),
    "rang5_q1.57": (1, 2 * 3**7, 5**4 * 7),
    # Kontrollen aehnlicher Groesse, niedrige Qualitaet (generisch gewaehlt):
    "control_q_low1": (3, 6436340, 6436343),       # c = 23^5 + 0? -> pruefen unten
    "control_q_low2": (5, 4369, 4374),             # 4374 = 2*3^7
}
DEPTH_N_WINDOW = 40   # |n_p| <= v_p-Reserve + Fenster
EXP_CAP = 60          # q, q0 = prod p^{e}, |e| <= cap via Bewertungs-Heuristik
OUT_JSON = "_results/b6_k2_encoding_depth_probe_{}.json".format(date.today())
OUT_MD = "_results/b6_k2_encoding_depth_probe_{}.md".format(date.today())


def factorize(n):
    fac = {}
    d = 2
    m = abs(n)
    while d * d <= m:
        while m % d == 0:
            fac[d] = fac.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1:
        fac[m] = fac.get(m, 0) + 1
    return fac


def vp(x, p):
    """p-adische Bewertung einer Fraction."""
    if x == 0:
        return 10**9
    num, den = x.numerator, x.denominator
    v = 0
    while num % p == 0:
        num //= p; v += 1
    while den % p == 0:
        den //= p; v -= 1
    return v


def depth_for_triple(a, b, c, max_candidates=4000):
    """Maximale Spitzentiefe des Punktes u(a/c) unter dem S-Kegel."""
    u = Fraction(a, c)
    S = sorted(set(factorize(a)) | set(factorize(b)) | set(factorize(c)))
    logS = {p: log(p) for p in S}

    # Kandidaten (q, q0): S-Zahlen q (Produkte kleiner Potenzen), q0 = naechste
    # S-Zahl... wir nehmen q aus Teiler-Gitter von c^2 * rad-Potenzen und
    # q0 = round(q*u) als Hauptkandidat (der diophantisch beste Partner).
    cands = set()
    # systematisch: q = prod p^{e_p}, e_p in [0, e_max(p)] mit moderater Kappe
    emax = {p: min(2 * vp(Fraction(c), p) + 3, 12) for p in S}
    ranges = [range(0, emax[p] + 1) for p in S]
    n_enum = 1
    for r in ranges:
        n_enum *= len(r)
    if n_enum > max_candidates:
        # Kappen: groesste Exponenten zuerst beschneiden
        while n_enum > max_candidates:
            pmax = max(emax, key=lambda p: emax[p])
            emax[pmax] -= 1
            n_enum = 1
            for p in S:
                n_enum *= emax[p] + 1
        ranges = [range(0, emax[p] + 1) for p in S]
    for es in iproduct(*ranges):
        q = 1
        for p, e in zip(S, es):
            q *= p ** e
        q0 = round(q * u)
        for q0c in (q0, q0 + 1, q0 - 1):
            cands.add((q, q0c))
        cands.add((q, 0))
    cands.discard((0, 0))

    # Vektor-Normen-Daten: v = (q, q*u - q0)
    vecs = []
    for q, q0 in cands:
        w = Fraction(q) * u - q0
        if q == 0 and w == 0:
            continue
        # archimedisch: |q| (1. Komp.), |w| (2. Komp.)
        # p-adisch: |q|_p, |w|_p
        vecs.append({
            "log_abs_q": log(abs(q)) if q != 0 else -10**9,
            "log_abs_w": log(abs(w)) if w != 0 else -10**9,
            "vq": {p: vp(Fraction(q), p) if q != 0 else 10**9 for p in S},
            "vw": {p: vp(w, p) if w != 0 else 10**9 for p in S},
        })

    # Tiefe: max ueber (t, n) im Kegel: n_p <= 0, t + sum n_p log p >= 0
    # Stellen-Normen unter Fluss: R: max(e^{-t}|q|, e^{t}|w|);
    # p: max(p^{-n_p}|q|_p, p^{n_p}|w|_p)  [Konvention: Fluss kontrahiert
    # 1. Koordinate archimedisch fuer t>0, p-adisch fuer n_p<0 die 2.]
    # Wir suchen max_delta: exists (t,n): alle Komponenten <= delta.
    # Diskretes n-Gitter + optimales t analytisch.
    best = {"depth": -1e9, "n": None, "witness": None}
    nranges = [range(-DEPTH_N_WINDOW, 1) for _ in S]
    # Heuristik: nur n im Bewertungs-relevanten Fenster
    nranges = [range(-min(DEPTH_N_WINDOW, emax[p] + 6), 1) for p in S]
    for ns in iproduct(*nranges):
        budget = -sum(n * logS[p] for n, p in zip(ns, S))  # = max erlaubtes t
        if budget < 0:
            continue
        # fuer festes n: pro Vektor die p-Komponenten fix:
        # log N_p = max(-n_p*log p + (-vq_p*log p)?? Achtung Norm: |x|_p = p^{-v_p(x)}
        # 1. Koord p-Norm unter Fluss: p^{n_p} * q  -> |.|_p = p^{-(n_p + vq_p)};
        # 2. Koord: p^{-n_p} * w -> p^{-(-n_p + vw_p)} = p^{n_p - vw_p}.
        # (Fluss diag(p^{n}, p^{-n}); n<=0 kontrahiert 1. Koordinate p-adisch? Nein:
        # |p^{n} q|_p = p^{-n-vq}: n<0 => Norm waechst. EK-Kegel: n<=0 expandiert
        # p-adisch die 1. Koordinate, t>=0 kontrahiert sie archimedisch.)
        for vec in vecs:
            logNp_max = -1e9
            for p, n in zip(S, ns):
                l1 = -(n + vec["vq"][p]) * logS[p]
                l2 = (n - vec["vw"][p]) * logS[p]
                logNp_max = max(logNp_max, l1, l2)
            # archimedisch: log N_R(t) = max(log|q| - t, log|w| + t), t in [0, budget]
            # gesamt: delta(t) = max(logNp_max, log|q|-t, log|w|+t); minimiere ueber t
            t_star = min(budget, max(0.0, (vec["log_abs_q"] - vec["log_abs_w"]) / 2))
            cand_log = max(logNp_max,
                           vec["log_abs_q"] - t_star,
                           vec["log_abs_w"] + t_star)
            depth = -cand_log
            if depth > best["depth"]:
                best = {"depth": depth, "n": dict(zip(S, ns)),
                        "witness": {"log|q|": vec["log_abs_q"], "log|w|": vec["log_abs_w"]}}
    best["S"] = S
    best["log_c"] = log(c)
    best["q_quality"] = log(c) / sum(log(p) for p in S)
    best["depth_normalized_by_logc"] = best["depth"] / log(c)
    return best


def main():
    t0 = time.time()
    # Kontroll-Tripel sauber konstruieren: gleiche Groessenordnung wie Reyssat,
    # niedrige Qualitaet: nimm (a, c-a, c) mit c ~ 23^5 und generischem a
    fixed = dict(TRIPLES)
    c = 23**5
    a = 1234577  # generisch, gcd-check unten
    fixed["control_q_low1"] = (a, c - a, c)
    c2 = 2 * 3**7
    fixed["control_q_low2"] = (5, c2 - 5, c2)

    results = {}
    for name, (a, b, c) in fixed.items():
        from math import gcd
        assert a + b == c and gcd(a, c) == 1, name
        fac_abc = factorize(a * b * c)
        rad = 1
        for p in fac_abc:
            rad *= p
        q = log(c) / log(rad)
        r = depth_for_triple(a, b, c)
        r["abc_quality"] = q
        r["n_primes_S"] = len(r["S"])
        results[name] = r
        print("{}: q = {:.4f} | depth = {:.3f} | depth/log c = {:.3f} | S = {} ({:.1f}s)".format(
            name, q, r["depth"], r["depth_normalized_by_logc"], r["S"], time.time() - t0), flush=True)

    report = {"date": str(date.today()),
              "results": {k: {kk: vv for kk, vv in v.items() if kk != "witness"} | {"witness": v["witness"]}
                          for k, v in results.items()}}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    lines = ["# B6/K2: Kodierungs-Test — Spitzentiefe vs. abc-Qualität ({})".format(date.today()), ""]
    lines.append("| Tripel | abc-Qualität q | S | depth* | depth*/log c |")
    lines.append("|---|---|---|---|---|")
    for name, r in results.items():
        lines.append("| {} | {:.4f} | {} | {:.3f} | {:.3f} |".format(
            name, r["abc_quality"], r["S"], r["depth"], r["depth_normalized_by_logc"]))
    lines.append("")
    lines.append("Kodierung: x = u(a/c)·Basispunkt in X_S; Tiefe = max über EK-Kegel")
    lines.append("(n_p ≤ 0, t + Σn_p log p ≥ 0) von −log(kürzester Mahler-Vektor).")
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
