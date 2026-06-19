#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R3/D1 v2 — Steinberg-lokaler Ledger MIT Tate-Parameter-Kanal + kurvenspezifischem All-q-Scan.

KORREKTUR-MOTIVATION (advisor + Codex-Audit #2, 2026-06-14):
v1 (`r3_steinberg_local_restriction_ledger.py`) fixierte EIN q ueber alle 241 Tripel und mass nur
`exc_char[q]=#{p: q|p^2-1}`. Das war DOPPELT unvollstaendig:
  (advisor) Fixed-q-Artefakt: q|p^2-1 verlangt p>=q; de-Smit-Champions haben KLEINE Primtraeger
            => exc≈0 ist Messblindheit, kein arithmetischer Befund. Falscher Messpunkt.
  (Codex)   Fehlender Kanal: der lokale adjungierte Steinberg-Term hat NEBEN dem character-exceptional
            Teil (q|p^2-1) einen Tate-Parameter-Kanal q|v_p(q_E). Fuer die Frey-Kurve
            E_{a,b}: y^2=x(x-a)(x+b) gilt an ungeradem p|abc: v_p(Delta_min)=2 v_p(abc)=2 e_p
            (genau ein Faktor a,b,c traegt p), und v_p(q_E)=-v_p(j)=v_p(Delta_min)=2 e_p.
            => q | v_p(q_E)  <=>  q | 2 e_p  <=> (q ungerade) q | e_p.

Dieses Script misst BEIDE Kanaele in ZWEI Modi:
  (A) FIXED-Q DIAGNOSE (wie v1, jetzt mit Tate-Spalte): bestaetigt, dass fixed grosses q fuer BEIDE
      Kanaele blind ist (exc_char≈exc_tate≈0) => der fixed-q-Ansatz ist tot, nicht "free conditions".
  (B) KURVENSPEZIFISCHER ALL-Q-SCAN (die informative, nicht-zirkulaere Version): fuer jeden Champion
      die TATSAECHLICHEN lokal-exzeptionellen Primes (kleine, kurvenspezifische q):
        Qchar(E) = U_{p in S_odd} primfaktoren(p^2-1)
        Qtate(E) = U_{p in S_odd} primfaktoren(e_p)
      gefiltert auf gute q (q>2, q ∤ 2 rad). Gemessen: |Qchar|, |Qtate|, Gesamt-Multiplizitaet,
      und die Skalierung gegen Qualitaet q_abc und omega(rad). Frage CR-2b-a (Support): waechst die
      lokal-exzeptionelle MASSE sub-/ueberlogarithmisch mit der Qualitaet?

NICHT-ZIRKULAR: Inputs = Primtraeger + Exponenten aus der Faktorform + elementare Teilbarkeit.
KEINE deg-phi-/L-Wert-/Kongruenzzahl-Eingabe. Der All-q-Scan nutzt KEIN curve-spezifisches
Kongruenzprim (das waere abc-stark) -- nur elementare Faktorisierung von p^2-1 und e_p.

GRENZE (ehrlich): Auch der All-q-Scan ist NUR ein lokaler Support-Indikator (CR-2b-a). Die
Groessenfrage CR-2b-b (dim Sel_{L*} sublog) braucht den globalen H^1(Q_S,Ad^0)-Schnitt (R5.2,
ungestartet). Dieses Script ENTSCHEIDET R3 NICHT -- es liefert das praezise lokale Support-Bild.

Aufruf (Mac): cd ~/compute/abc_r1 && python3 _scripts/r3_steinberg_tate_ledger_v2.py
"""
import json, re, math
from pathlib import Path
from datetime import date

ROOT = Path.cwd()
(ROOT / "_results").mkdir(exist_ok=True)
HTML = ROOT / "_sources" / "abc_smitbde_set2_goodtriples_2019.html"
OUT_JSON = ROOT / "_results" / "r3_steinberg_tate_ledger_v2_{}.json".format(date.today())
OUT_MD = ROOT / "_results" / "r3_steinberg_tate_ledger_v2_{}.md".format(date.today())

SEP_RE = re.compile(r"(?:&middot;|&#x200B;|&#8203;|​|&nbsp;)+")
TAGSTRIP_RE = re.compile(r"<[^>]*>")
ENT_RE = re.compile(r"&[#0-9a-zA-Z]+;")


def parse_factored(cell_html):
    """-> dict {prime: exponent} aus einer faktorisierten Zelle (z.B. '2^3 . 5 . 109^2')."""
    s = cell_html.replace("<sup>", "^").replace("</sup>", "")
    out = {}
    for tok in SEP_RE.split(s):
        tok = ENT_RE.sub("", TAGSTRIP_RE.sub("", tok)).strip()
        if not tok:
            continue
        if "^" in tok:
            base_s, exp_s = tok.split("^", 1)
        else:
            base_s, exp_s = tok, "1"
        try:
            base = int(base_s)
            exp = int(exp_s)
        except ValueError:
            continue
        out[base] = out.get(base, 0) + exp
    return out


def strip_cell(cell):
    idx = cell.find(">")
    return cell[idx + 1:] if idx >= 0 else cell


def load_triples():
    html = HTML.read_text(encoding="iso-8859-1")
    out = []
    for rm in re.finditer(r"<tr>(<td.*?)(?=<tr>|</table>|$)", html, re.S):
        cells = [strip_cell(c) for c in rm.group(1).split("<td")[1:]]
        if len(cells) < 9:
            continue
        rank_s = TAGSTRIP_RE.sub("", cells[0]).strip()
        if not re.match(r"^\d+$", rank_s):
            continue
        try:
            q_listed = float(TAGSTRIP_RE.sub("", cells[1]).strip())
        except (ValueError, IndexError):
            continue
        # a, b, c faktorisiert in cells[6], cells[7], cells[8]
        fa = parse_factored(cells[6])
        fb = parse_factored(cells[7])
        fc = parse_factored(cells[8])
        # Exponent e_p je Prim: in einem abc-Tripel teilt p genau eines von a,b,c.
        exps = {}
        for f in (fa, fb, fc):
            for p, e in f.items():
                exps[p] = exps.get(p, 0) + e
        S_odd = sorted(p for p in exps if p > 2)
        if not S_odd:
            continue
        out.append({
            "rank": int(rank_s), "q_abc": q_listed,
            "S_odd": S_odd, "omega": len(S_odd),
            "exps": {p: exps[p] for p in S_odd},
        })
    return out


def prime_factors(n):
    """Menge der Primfaktoren von n (n>=1)."""
    n = abs(int(n))
    fs = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            fs.add(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        fs.add(n)
    return fs


# ---------- (A) FIXED-Q DIAGNOSE ----------
def exc_char_fixed(S_odd, q):
    return sum(1 for p in S_odd if p != q and (p * p - 1) % q == 0)


def exc_tate_fixed(exps, q):
    # q | v_p(q_E) <=> q | 2 e_p <=> (q ungerade) q | e_p
    return sum(1 for p, e in exps.items() if (2 * e) % q == 0)


# ---------- (B) KURVENSPEZIFISCHER ALL-Q-SCAN ----------
def curve_exceptional(t, rad_primes):
    """Kurvenspezifische lokal-exzeptionelle gute Primes (q>2, q nicht in rad)."""
    Qchar, Qtate = set(), set()
    mult_char, mult_tate = 0, 0
    for p in t["S_odd"]:
        for q in prime_factors(p * p - 1):
            if q > 2 and q not in rad_primes:
                Qchar.add(q)
                mult_char += 1
    for p, e in t["exps"].items():
        for q in prime_factors(2 * e):
            if q > 2 and q not in rad_primes:
                Qtate.add(q)
                mult_tate += 1
    return Qchar, Qtate, mult_char, mult_tate


def main():
    triples = load_triples()
    QSET = [101, 251, 1009, 3863, 5077]

    # (A) Fixed-q Diagnose, beide Kanaele
    agg_fixed = {}
    for q in QSET:
        ch = [exc_char_fixed(t["S_odd"], q) for t in triples]
        ta = [exc_tate_fixed(t["exps"], q) for t in triples]
        omw = [t["omega"] for t in triples]
        agg_fixed[q] = {
            "char_mean": round(sum(ch) / len(ch), 5), "char_max": max(ch),
            "tate_mean": round(sum(ta) / len(ta), 5), "tate_max": max(ta),
            "char_frac>0": round(sum(1 for x in ch if x) / len(ch), 4),
            "tate_frac>0": round(sum(1 for x in ta if x) / len(ta), 4),
            "expected_random_char_per_omega": round(2.0 / (q - 1), 6),
        }

    # (B) Kurvenspezifischer All-q-Scan
    rows_scan = []
    for t in triples:
        rad_primes = set(t["S_odd"]) | {2}
        Qchar, Qtate, mc, mt = curve_exceptional(t, rad_primes)
        Qall = Qchar | Qtate
        rows_scan.append({
            "rank": t["rank"], "q_abc": round(t["q_abc"], 4), "omega": t["omega"],
            "n_qchar": len(Qchar), "n_qtate": len(Qtate), "n_qall": len(Qall),
            "mult_char": mc, "mult_tate": mt,
            "max_exp": max(t["exps"].values()),
            "qtate_primes": sorted(Qtate)[:12],
        })

    # Skalierung gegen Qualitaet & omega
    def corr(xs, ys):
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        sy = math.sqrt(sum((y - my) ** 2 for y in ys))
        if sx == 0 or sy == 0:
            return 0.0
        return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy), 4)

    omegas = [r["omega"] for r in rows_scan]
    quals = [r["q_abc"] for r in rows_scan]
    n_qall = [r["n_qall"] for r in rows_scan]
    n_qtate = [r["n_qtate"] for r in rows_scan]
    mult_tate = [r["mult_tate"] for r in rows_scan]
    logN_proxy = [math.log(max(2, r["omega"])) for r in rows_scan]  # grober log-N-Proxy

    scan_agg = {
        "n_triples": len(rows_scan),
        "mean_n_qall": round(sum(n_qall) / len(n_qall), 3),
        "mean_n_qtate": round(sum(n_qtate) / len(n_qtate), 3),
        "mean_mult_tate": round(sum(mult_tate) / len(mult_tate), 3),
        "max_n_qall": max(n_qall),
        "corr(n_qall, omega)": corr(n_qall, omegas),
        "corr(n_qall, q_abc)": corr(n_qall, quals),
        "corr(n_qtate, q_abc)": corr(n_qtate, quals),
        "corr(mult_tate, omega)": corr(mult_tate, omegas),
        "frac_triples_with_qtate>0": round(sum(1 for x in n_qtate if x) / len(n_qtate), 4),
    }

    result = {
        "n_triples": len(triples), "qset_fixed": QSET,
        "A_fixed_q_diagnose": agg_fixed,
        "B_curve_specific_scan": scan_agg,
        "scan_rows_head": sorted(rows_scan, key=lambda r: -r["q_abc"])[:15],
        "note": ("A: fixed grosses q ist fuer BEIDE Kanaele blind (Artefakt). "
                 "B: kurvenspezifische lokal-exzeptionelle Masse; tate-Kanal q|e_p. "
                 "Lokaler Support-Indikator (CR-2b-a), ENTSCHEIDET CR-2b-b NICHT (-> R5.2 global)."),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    L = ["# R3/D1 v2 — Steinberg + Tate-Kanal Ledger ({})".format(date.today()), "",
         "## (A) Fixed-q Diagnose (beide Kanaele) — erwartet: blind fuer grosses q", "",
         "| q | char_mean | char_max | tate_mean | tate_max | char_frac>0 | tate_frac>0 |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    for q in QSET:
        a = agg_fixed[q]
        L.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            q, a["char_mean"], a["char_max"], a["tate_mean"], a["tate_max"],
            a["char_frac>0"], a["tate_frac>0"]))
    L += ["", "Lesart A: char UND tate ≈0 fuer grosses festes q => der fixed-q-Ledger ist BLIND",
          "(Messartefakt: q|p^2-1 braucht p>=q, q|e_p braucht e_p>=q; beide klein in Champions).",
          "Das ist KEIN 'free conditions', sondern der falsche Messpunkt (advisor-Catch bestaetigt).", "",
          "## (B) Kurvenspezifischer All-q-Scan (die informative Version)", "",
          "n_qchar/qtate = #verschiedene kurvenspezifische exzeptionelle gute Primes je Kanal.", ""]
    for k, v in scan_agg.items():
        L.append("- **{}**: {}".format(k, v))
    L += ["",
          "Lesart B: waechst die lokal-exzeptionelle Masse (n_qall / mult_tate) mit Qualitaet q_abc",
          "oder omega? Schwache/keine Korrelation => der lokale Support ist duenn und qualitaets-",
          "robust (stuetzt CR-2b-a No-hidden-basin). Starke Korrelation mit omega aber NICHT mit",
          "q_abc => Masse skaliert mit Stellenzahl, nicht mit Qualitaet (kein Qualitaets-Hebel).", "",
          "ENTSCHEIDET NICHT die Groesse (CR-2b-b): dafuer globaler H^1(Q_S,Ad^0)-Schnitt (R5.2)."]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")

    print("WROTE", OUT_JSON.name, OUT_MD.name)
    print("n_triples", len(triples))
    print("A fixed-q (q, char_mean, tate_mean):")
    for q in QSET:
        print("  ", q, agg_fixed[q]["char_mean"], agg_fixed[q]["tate_mean"])
    print("B scan:", json.dumps(scan_agg, indent=2))


main()
