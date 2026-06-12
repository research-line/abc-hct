#!/usr/bin/env python3
"""
M-DET 2 (Forensik, Schnelltest 2): Paarweise Eigenform-Kongruenzen
mod {2, 3, 5, 31} zwischen ALLEN rationalen Isogenieklassen auf den
Teiler-Leveln von 60168.

Hintergrund: |D(W)| = 2^3 * 3^2 * 5 * 31 = 11160 (1b, exakt). Der
Eisenstein-Test war NEGATIV (keine Klasse Eisenstein-kongruent).
Naechster natuerlicher Kandidat: Kongruenzen ZWISCHEN rationalen
Eigenformen im Quellraum S_2(Gamma_0(60168)) (Newforms der Teiler-Level
als Oldform-Kopien enthalten). Das Sturm-Hasse-Argument schliesst nur
q > 4*sqrt(B) ~ 580 aus (B = 21120 fuer Level 60168) — kleine q wie
2, 3, 5, 31 sind moeglich und wuerden Rangabfall mod q erzeugen.

Test: a_p(E1) == a_p(E2) mod q fuer alle p <= P_MAX, p nmid 60168
(T_p-Eigenwerte; U_p der bad primes ausgelassen wg. Oldform-Aufspaltung).
P_MAX = 200 ist INDIKATOR, nicht Sturm-Beweis (Sturm-Bound 21120) —
Treffer sind Kandidaten, die ggf. nachverifiziert werden.

Output: _results/mdet2_interclass_congruence_test_60168_<date>.{json,md}
"""
import json, subprocess, time, urllib.parse
from datetime import date
from itertools import combinations

N = 60168  # 2^3 * 3 * 23 * 109
TEST_Q = [2, 3, 5, 31]
P_MAX = 200
API = "https://www.lmfdb.org/api/ec_curvedata"
OUT_JSON = "_results/mdet2_interclass_congruence_test_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet2_interclass_congruence_test_60168_{}.md".format(date.today())


def divisors(n):
    ds = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            ds.append(d)
            if d != n // d:
                ds.append(n // d)
        d += 1
    return sorted(ds)


CHECKPOINT = "_results/mdet2_icc_checkpoint.json"


def fetch_iso_classes(conductor, cache):
    key = str(conductor)
    if key in cache:
        return cache[key]
    results = []
    offset = 0
    while True:
        params = {"conductor": "i{}".format(conductor), "lmfdb_number": "i1",
                  "_format": "json", "_fields": "lmfdb_iso,ainvs", "_offset": str(offset)}
        url = API + "?" + urllib.parse.urlencode(params)
        payload = None
        for attempt in range(12):
            try:
                out = subprocess.run(
                    ["curl", "-s", "-m", "60", url, "-H", "User-Agent: abc-hct-mdet2-icc/1.0"],
                    capture_output=True, text=True, timeout=90).stdout
                payload = json.loads(out)
                break
            except Exception:
                time.sleep(10 + 15 * attempt)
        if payload is None:
            raise RuntimeError("LMFDB nicht erreichbar: N={}".format(conductor))
        data = payload.get("data", [])
        results.extend(data)
        if len(data) < 100:
            break
        offset += len(data)
        time.sleep(1.0)
    cache[key] = results
    with open(CHECKPOINT, "w") as f:
        json.dump(cache, f)
    return results


def ap_point_count(ainvs, p):
    a1, a2, a3, a4, a6 = [a % p for a in ainvs]
    count = 1
    for x in range(p):
        rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
        b = (a1 * x + a3) % p
        disc = (b * b + 4 * rhs) % p
        if p == 2:
            for y in range(2):
                if (y * y + b * y - rhs) % 2 == 0:
                    count += 1
            continue
        if disc == 0:
            count += 1
        elif pow(disc, (p - 1) // 2, p) == 1:
            count += 2
    return p + 1 - count


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, b in enumerate(sieve) if b]


def main():
    t0 = time.time()
    good_primes = [p for p in primes_upto(P_MAX) if N % p != 0]
    try:
        cache = json.load(open(CHECKPOINT))
    except Exception:
        cache = {}
    all_classes = []
    for d in divisors(N):
        if d < 11:
            continue  # keine elliptischen Kurven mit Conductor < 11
        cls = fetch_iso_classes(d, cache)
        for c in cls:
            all_classes.append({"iso": c["lmfdb_iso"], "level": d, "ainvs": c["ainvs"]})
        if cls:
            print(f"N={d}: {len(cls)} Klassen", flush=True)
        time.sleep(1.5)
    print(f"Gesamt: {len(all_classes)} Isogenieklassen auf {len(divisors(N))} Teiler-Leveln "
          f"({time.time()-t0:.0f}s)")

    for c in all_classes:
        c["aps"] = [ap_point_count(c["ainvs"], p) for p in good_primes]

    hits = []
    lines_pairs = []
    for c1, c2 in combinations(all_classes, 2):
        diffs = [a - b for a, b in zip(c1["aps"], c2["aps"])]
        for q in TEST_Q:
            if all(dv % q == 0 for dv in diffs):
                hits.append({"pair": [c1["iso"], c2["iso"]],
                             "levels": [c1["level"], c2["level"]], "q": q})
                lines_pairs.append("| {} (N={}) | {} (N={}) | {} |".format(
                    c1["iso"], c1["level"], c2["iso"], c2["level"], q))
                print(f"KONGRUENZ-KANDIDAT mod {q}: {c1['iso']} == {c2['iso']} "
                      f"(alle p <= {P_MAX})")

    report = {"date": str(date.today()), "level": N, "p_max": P_MAX, "test_q": TEST_Q,
              "n_classes": len(all_classes),
              "classes": [{"iso": c["iso"], "level": c["level"]} for c in all_classes],
              "congruence_candidates": hits,
              "note": ("Indikator p<=200, kein Sturm-Beweis (Bound 21120). "
                       "Nur T_p, p nmid 60168; rationale Klassen der Teiler-Level.")}
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# M-DET 2: Inter-Klassen-Kongruenzen, Teiler-Level von 60168 ({})".format(date.today()), ""]
    lines.append("{} Klassen, q in {}, p <= {} (p nmid N). |D(W)| = 11160 = 2^3*3^2*5*31.".format(
        len(all_classes), TEST_Q, P_MAX))
    lines.append("")
    if hits:
        lines.append("| Klasse 1 | Klasse 2 | q |")
        lines.append("|---|---|---|")
        lines.extend(lines_pairs)
    else:
        lines.append("**KEINE Kongruenz-Kandidaten** — auch Inter-Klassen-Kongruenzen")
        lines.append("(rational, Teiler-Level) erklaeren die Drop-Primes NICHT;")
        lines.append("nicht-rationale Orbits oder konstruktive Mechanismen bleiben.")
    lines.append("")
    lines.append("Total: {:.0f}s".format(time.time() - t0))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON)


if __name__ == "__main__":
    main()
