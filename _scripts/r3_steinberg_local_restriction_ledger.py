#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R3/D1 — Steinberg-lokaler Restriktions-Ledger fuer die adjungierte Selmer-Bilanz.

Hintergrund (MG_r3_cr2b_two_ledger_theory_2026-06-14.md):
Fuer absolut irreduzibles rho_bar_{E,q} entfaellt in der Greenberg-Wiles/Poitou-Tate-Formel
der globale Kongruenz-Term (H^0(Q,Ad^0)=H^0(Q,Ad^0*)=0); es bleibt eine REINE lokale Bilanz
  dim Sel_L(Ad^0) - dim Sel_{L*}(Ad^0*) = sum_v ( dim L_v - dim H^0(Q_v,Ad^0) ).
An einer Steinberg-Stelle p|N (Frey ist an jedem p|abc Steinberg) ist der lokale Term genau
dann >0 ("q-exzeptionell"/vexing), wenn q | p^2-1 (p == ±1 mod q) -- die Stellen, an denen die
adjungierte lokale Deformation eine Extra-Dimension traegt. Die Zahl solcher Stellen ist der
nicht-zirkulaere lokale Handle fuer K1.

NICHT-ZIRKULAR: Inputs = Primtraeger S=primes(abc) (aus der Faktorform) + die elementare
Bedingung q|p^2-1. KEINE deg-phi-/L-Wert-/Kongruenzzahl-Eingabe.

GO/KILL:
  - GO (K1 lebt potenziell): #exzeptionelle Steinberg-Primes bleibt KONTROLLIERT/sublogarithmisch
    relativ zu |S|=omega(rad) -- d.h. die lokalen Bedingungen "expandieren" nicht trivial mit jeder
    Primstelle, der Selmer-Defekt-Support ist duenn.
  - KILL: #exzeptionell waechst ~ omega(rad) (jede Stelle exzeptionell -> kein lokaler Gewinn) ODER
    der exzeptionelle Support reproduziert genau die bekannte Kongruenzmasse (zirkulaer).

Datenquelle: de Smit, 241 gute Tripel (q_abc>=1.4), Faktorform -> Primtraeger.
Aufruf (Mac): cd ~/compute/abc_r1 && python3 _scripts/r3_steinberg_local_restriction_ledger.py
"""
import json, re, math
from pathlib import Path
from datetime import date

ROOT = Path.cwd()
(ROOT / "_results").mkdir(exist_ok=True)
HTML = ROOT / "_sources" / "abc_smitbde_set2_goodtriples_2019.html"
OUT_JSON = ROOT / "_results" / "r3_steinberg_local_restriction_ledger_{}.json".format(date.today())
OUT_MD = ROOT / "_results" / "r3_steinberg_local_restriction_ledger_{}.md".format(date.today())

SEP_RE = re.compile(r"(?:&middot;|&#x200B;|&#8203;|​|&nbsp;)+")
TAGSTRIP_RE = re.compile(r"<[^>]*>")
ENT_RE = re.compile(r"&[#0-9a-zA-Z]+;")

def parse_factored(cell_html):
    s = cell_html.replace("<sup>", "^").replace("</sup>", "")
    primes = set()
    for tok in SEP_RE.split(s):
        tok = ENT_RE.sub("", TAGSTRIP_RE.sub("", tok)).strip()
        if not tok:
            continue
        base = tok.split("^", 1)[0]
        try:
            primes.add(int(base))
        except ValueError:
            pass
    return primes

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
            S = parse_factored(cells[6]) | parse_factored(cells[7]) | parse_factored(cells[8])
        except (ValueError, IndexError):
            continue
        S_odd = {p for p in S if p > 2}   # Steinberg-Stellen (ungerade p|abc)
        out.append({"rank": int(rank_s), "q_abc": q_listed, "S_odd": sorted(S_odd), "omega": len(S_odd)})
    return out

def exceptional_count(S_odd, q):
    """#{p in S_odd : q | p^2-1, p != q}  (q-exzeptionelle Steinberg-Primes)."""
    return sum(1 for p in S_odd if p != q and (p * p - 1) % q == 0)

def main():
    triples = load_triples()
    # Auxiliary-Primes q: feste Vergleichswerte + der Reyssat-Marker 3863.
    QSET = [101, 251, 1009, 3863, 5077]
    rows = []
    for t in triples:
        rec = {"rank": t["rank"], "q_abc": round(t["q_abc"], 4), "omega": t["omega"], "exc": {}}
        for q in QSET:
            rec["exc"][q] = exceptional_count(t["S_odd"], q)
        rows.append(rec)
    # Aggregierte Skalierung: mittlere #exzeptionell / omega, und max.
    agg = {}
    for q in QSET:
        excs = [r["exc"][q] for r in rows]
        omegas = [r["omega"] for r in rows]
        ratios = [e / o for e, o in zip(excs, omegas) if o]
        agg[q] = {
            "mean_exc": round(sum(excs) / len(excs), 4),
            "max_exc": max(excs),
            "mean_exc_over_omega": round(sum(ratios) / len(ratios), 5),
            "frac_triples_with_exc>0": round(sum(1 for e in excs if e > 0) / len(excs), 4),
            "expected_random_per_omega": round(2.0 / (q - 1), 6),
        }
    result = {"n_triples": len(rows), "qset": QSET, "aggregate": agg,
              "note": "exc[q] = #{p in S_odd: q|p^2-1}; vergleiche mean_exc_over_omega mit expected_random 2/(q-1)",
              "rows_head": rows[:15]}
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = ["# R3/D1 Steinberg-lokaler Restriktions-Ledger ({})".format(date.today()), "",
             "exc[q] = #q-exzeptionelle Steinberg-Primes (q|p^2-1) im Primtraeger S_odd=primes(abc)_>2.",
             "Frage: waechst exc ~ omega (KILL) oder bleibt es kontrolliert/random-duenn (GO-Signal)?", "",
             "| q | mean exc | max exc | mean exc/omega | random 2/(q-1) | frac mit exc>0 |",
             "|---|---:|---:|---:|---:|---:|"]
    for q in QSET:
        a = agg[q]
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            q, a["mean_exc"], a["max_exc"], a["mean_exc_over_omega"],
            a["expected_random_per_omega"], a["frac_triples_with_exc>0"]))
    lines += ["", "Lesart: liegt mean_exc/omega nahe am Random-Erwartungswert 2/(q-1) und << 1, dann sind",
              "die exzeptionellen (Selmer-Defekt tragenden) Stellen DUENN -> der lokale Steinberg-Term",
              "expandiert NICHT mit jeder Primstelle; der adjungierte Selmer-Defekt-Support ist sublinear",
              "in omega (GO-Signal fuer K1, nicht-zirkulaer). Liegt exc ~ omega -> KILL.", "",
              "ACHTUNG: rein lokaler Handle; die volle Sel_{L*}-Dimension braucht zusaetzlich den",
              "globalen H^1(Q_S,Ad^0)-Schnitt (naechste, schwerere Stufe)."]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("WROTE", OUT_JSON)
    print("n_triples", len(rows))
    for q in QSET:
        print(q, "->", agg[q])

main()
