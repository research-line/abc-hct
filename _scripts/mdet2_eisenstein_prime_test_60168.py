#!/usr/bin/env python3
"""
M-DET 2 (Forensik, Schnelltest): Sind die Drop-Primes {3, 5, 31} des
60168-Witness-Systems Eisenstein-Kongruenz-Primes einer 60168-Kurve?

Hintergrund (Satz-Note Par. 8, M-DET 1a/1b): Drop-Primes des Systems sind
EXAKT {2, 3, 5, 31}; v_3(D(W)) = 2 (1b, log-belegt). Die Konstante ist
T_p-Eigenvektor mit Eigenwert 1+p (Eisenstein). Wenn fuer eine Kurve E
mit Conductor 60168 gilt  a_p(E) == 1+p mod q  fuer alle p (Eisenstein-
Kongruenz mod q), dann annihiliert (T_p - a_p) die Konstante mod q nicht
-- ein struktureller Kandidat dafuer, warum das Witness-System mod q
Rang verliert. Dieser Test prueft die Kongruenz direkt:

  Fuer jede Isogenieklasse mit Conductor 60168 (LMFDB, Vertreter .1)
  und jedes Test-q: gilt a_p(E) == 1+p mod q fuer ALLE p nmid N,
  p <= P_MAX? (a_p lokal via Punktzaehlung; P_MAX=200 => |a_p - (1+p)|
  <= 1+p+2*sqrt(p) < 230 << moegliche q-Produkte; ein Bestehen ist bei
  q <= 31 ein echtes Kongruenz-Signal, kein Groessenartefakt.)
  Zusatz p | N (p in {2, 3, 23, 109}): U_p-Kompatibilitaet
  a_p in {1 mod q, p mod q} (Eisenstein-U_p-Eigenwerte sind 1 und p).

Interpretation:
  - Klasse mit Eisenstein-q-Menge ⊇ {3, 5, 31}: starke ARITHMETISCHE
    Erklaerung der Drop-Primes (und Rueckwaerts-Identifikation der
    Quellkurve des Witness).
  - Keine Klasse: konstruktive Erklaerung (Relationen-Kombinatorik,
    z. B. Dreiecks-Nilpotenz (1-T)^2 mod 3) wird fuehrend; Kernvektor-
    Forensik (Mac-Job) entscheidet.

Output: _results/mdet2_eisenstein_prime_test_60168_<date>.{json,md}
"""
import json, subprocess, time, urllib.parse
from datetime import date

CONDUCTOR = 60168  # = 2^3 * 3 * 23 * 109
BAD_PRIMES = [2, 3, 23, 109]
P_MAX = 200
TEST_Q = [3, 5, 31, 7, 11, 13, 19]  # Drop-Primes zuerst, Rest Kontrollen
API = "https://www.lmfdb.org/api/ec_curvedata"
OUT_JSON = "_results/mdet2_eisenstein_prime_test_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet2_eisenstein_prime_test_60168_{}.md".format(date.today())


def fetch_iso_classes(conductor):
    results = []
    offset = 0
    while True:
        params = {
            "conductor": "i{}".format(conductor),
            "lmfdb_number": "i1",
            "_format": "json",
            "_fields": "lmfdb_label,lmfdb_iso,ainvs,torsion,isogeny_degrees",
            "_offset": str(offset),
        }
        url = API + "?" + urllib.parse.urlencode(params)
        payload = None
        for attempt in range(8):
            try:
                out = subprocess.run(
                    ["curl", "-s", "-m", "60", url, "-H", "User-Agent: abc-hct-mdet2-eis/1.0"],
                    capture_output=True, text=True, timeout=90).stdout
                payload = json.loads(out)
                break
            except Exception:
                time.sleep(5 + 10 * attempt)
        if payload is None:
            raise RuntimeError("LMFDB nicht erreichbar")
        data = payload.get("data", [])
        results.extend(data)
        if len(data) < 100:
            break
        offset += len(data)
        time.sleep(0.4)
    return results


def ap_point_count(ainvs, p):
    """a_p = p + 1 - #E(F_p) via direkte Punktzaehlung (p klein)."""
    a1, a2, a3, a4, a6 = [a % p for a in ainvs]
    count = 1  # Punkt im Unendlichen
    for x in range(p):
        # y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6
        rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
        b = (a1 * x + a3) % p
        # y^2 + b*y - rhs == 0  =>  Diskriminante b^2 + 4*rhs
        disc = (b * b + 4 * rhs) % p
        if p == 2:
            for y in range(2):
                if (y * y + b * y - rhs) % 2 == 0:
                    count += 1
            continue
        ls = pow(disc, (p - 1) // 2, p) if disc else 0
        if disc == 0:
            count += 1
        elif ls == 1:
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
    classes = fetch_iso_classes(CONDUCTOR)
    print(f"LMFDB: {len(classes)} Isogenieklassen mit Conductor {CONDUCTOR}")
    good_primes = [p for p in primes_upto(P_MAX) if CONDUCTOR % p != 0]

    report = {"date": str(date.today()), "conductor": CONDUCTOR, "p_max": P_MAX,
              "test_q": TEST_Q, "classes": []}
    lines = ["# M-DET 2: Eisenstein-Prime-Test, Conductor 60168 ({})".format(date.today()), ""]
    lines.append("Drop-Primes des Witness-Systems: {2: v=?, 3: v=2, 5: v=?, 31: v=?} (1a/1b)")
    lines.append("")
    lines.append("| Klasse | Torsion | Isogenie-Grade | Eisenstein-q (alle p<=200 bestanden) | erste Gegenbeispiele |")
    lines.append("|---|---|---|---|---|")

    for cls in classes:
        ainvs = cls["ainvs"]
        label = cls["lmfdb_iso"]
        aps = {p: ap_point_count(ainvs, p) for p in good_primes}
        bad_aps = {p: ap_point_count(ainvs, p) for p in BAD_PRIMES}
        eis_q = []
        counterex = {}
        for q in TEST_Q:
            ok = True
            for p in good_primes:
                if (aps[p] - (1 + p)) % q != 0:
                    ok = False
                    counterex[q] = "p={}: a_p={} vs 1+p={}".format(p, aps[p], 1 + p)
                    break
            if ok:
                # U_p-Kompatibilitaet (informativ, kein Veto: Eisenstein-U_p in {1, p})
                upinfo = all((bad_aps[p] - 1) % q == 0 or (bad_aps[p] - p) % q == 0
                             for p in BAD_PRIMES)
                eis_q.append({"q": q, "u_p_compatible": upinfo})
        report["classes"].append({
            "iso": label, "torsion": cls.get("torsion"),
            "isogeny_degrees": cls.get("isogeny_degrees"),
            "ap_small": {str(p): aps[p] for p in good_primes[:10]},
            "u_p": {str(p): bad_aps[p] for p in BAD_PRIMES},
            "eisenstein_q": eis_q,
            "first_counterexamples": counterex})
        eis_str = ", ".join("{}{}".format(e["q"], "" if e["u_p_compatible"] else "*") for e in eis_q) or "—"
        cex_str = "; ".join("q={}: {}".format(q, c) for q, c in sorted(counterex.items())[:2]) or "—"
        print(f"{label}: torsion={cls.get('torsion')}, Eisenstein-q = [{eis_str}]")
        lines.append("| {} | {} | {} | {} | {} |".format(
            label, cls.get("torsion"), cls.get("isogeny_degrees"), eis_str, cex_str))

    lines.append("")
    lines.append("(* = U_p-Werte nicht {1,p}-kompatibel mod q — Kongruenz nur in den T_p, p nmid N)")
    lines.append("")
    lines.append("Total: {:.0f}s".format(time.time() - t0))
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)


if __name__ == "__main__":
    main()
