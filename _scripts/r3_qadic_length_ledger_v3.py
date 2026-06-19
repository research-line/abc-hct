#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R3 v3 — q-adische LAENGENebene des Steinberg/BK-Ledgers (Codex-Gluecke L2).

MOTIVATION (Codex-Glied-2b-Audit, 2026-06-14):
Glied 2b der R5.2-Kette traegt formal noch nicht. Codex' haertester Punkt (L2): die beweisrelevante
Groesse ist nicht die Indikator-/Paar-Zaehlung (n_qall, mult_all aus v2), sondern die q-adische
LAENGENsumme. Auf q^oo-Niveau (Cor 1.5 gibt eine Z_q-Laenge ord_q(deg phi)) zaehlen nicht Indikatoren
[q|r^2-1], sondern q-adische Vielfachheiten v_q(r-1), v_q(r+1), v_q(2 e_r). Eine einzelne Stelle kann
auf Laengenebene > 1 beitragen. v2 hat das NICHT gemessen.

Dieses Script misst die LAENGENebene: fuer jedes kurvenspezifische exzeptionelle Paar (r,q) die Tiefe
  character-Kanal:  d_char(r,q) = v_q(r^2-1) = v_q(r-1)+v_q(r+1)
  Tate-Kanal:       d_tate(r,q) = v_q(2 e_r)   (q ungerade => = v_q(e_r))
und aggregiert die gewichtete Laengensumme je Champion:
  L_total(E) = sum_{r in S_odd} [ sum_{q good | r^2-1} d_char(r,q) + sum_{q good | 2 e_r} d_tate(r,q) ].

FRAGE (entscheidet die Substanz von Glied 2b auf Laengenebene):
  - Sind die Tiefen d ueberwiegend 1 (q teilt genau einmal), oder kommen grosse Tiefen vor?
  - Skaliert L_total mit der Qualitaet q_abc? (corr) -- wenn NICHT, ist die Laengenebene ebenso
    qualitaets-flach wie die Dimensionsebene => Substanz von 2b auf der beweisrelevanten Ebene erhaertet.
  - Wenn L_total mit q_abc waechst => der lebende Faden lebt (Laengen-Hebel moeglich).

WICHTIG (Nicht-Zirkularitaet + ehrliche Grenze): die "guten" q sind q ∤ 2 rad(abc). Die Laengensumme
ueber ALLE guten q ist ~ Omega(prod (r^2-1)) ~ O(log N) global -- das ist KEIN Widerspruch: die
Greenberg-Wiles-Korrektur fuer Sel[q^oo] laeuft pro FIXEM Koeffizienten-q, nicht summiert ueber q.
Wir messen daher ZWEI Sichten:
  (B) per-fixem-q (wie v2, jetzt mit Tiefe): bestaetigt Blindheit fuer grosses festes q.
  (C) kurvenspezifisch, aber AUFGESCHLUESSELT nach Tiefenverteilung: zeigt, ob einzelne (r,q) tiefe
      Laengen tragen und ob die qualitaets-flache Eigenschaft auf Laengenebene haelt.
Die beweisrelevante Aussage ist: fuer JEDES feste q bleibt die per-q-Laengensumme thin (->(B)); die
kurvenspezifische Tiefenverteilung (->(C)) zeigt, dass auch wo exz. Paare existieren, die Tiefen klein
und qualitaets-unkorreliert sind.

Aufruf (Mac): cd ~/compute/abc_r1 && python3 _scripts/r3_qadic_length_ledger_v3.py
"""
import json, re, math
from pathlib import Path
from datetime import date

ROOT = Path.cwd()
(ROOT / "_results").mkdir(exist_ok=True)
HTML = ROOT / "_sources" / "abc_smitbde_set2_goodtriples_2019.html"
OUT_JSON = ROOT / "_results" / "r3_qadic_length_ledger_v3_{}.json".format(date.today())
OUT_MD = ROOT / "_results" / "r3_qadic_length_ledger_v3_{}.md".format(date.today())

SEP_RE = re.compile(r"(?:&middot;|&#x200B;|&#8203;|​|&nbsp;)+")
TAGSTRIP_RE = re.compile(r"<[^>]*>")
ENT_RE = re.compile(r"&[#0-9a-zA-Z]+;")


def parse_factored(cell_html):
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
            out[int(base_s)] = out.get(int(base_s), 0) + int(exp_s)
        except ValueError:
            pass
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
        exps = {}
        for f in (parse_factored(cells[6]), parse_factored(cells[7]), parse_factored(cells[8])):
            for p, e in f.items():
                exps[p] = exps.get(p, 0) + e
        S_odd = sorted(p for p in exps if p > 2)
        if not S_odd:
            continue
        out.append({"rank": int(rank_s), "q_abc": q_listed, "S_odd": S_odd,
                    "omega": len(S_odd), "exps": {p: exps[p] for p in S_odd}})
    return out


def vq(n, q):
    """q-adische Bewertung v_q(n)."""
    n = abs(int(n))
    if n == 0:
        return 0
    v = 0
    while n % q == 0:
        n //= q
        v += 1
    return v


def prime_factors(n):
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


def main():
    triples = load_triples()
    QSET = [101, 251, 1009, 3863, 5077]

    # (B) per-fixem-q LAENGENsumme (mit Tiefe) -- Blindheit fuer grosses festes q
    agg_fixed = {}
    for q in QSET:
        Lc, Lt = [], []
        for t in triples:
            lc = sum(vq(r * r - 1, q) for r in t["S_odd"] if r != q)
            lt = sum(vq(2 * e, q) for e in t["exps"].values())
            Lc.append(lc)
            Lt.append(lt)
        agg_fixed[q] = {
            "char_len_mean": round(sum(Lc) / len(Lc), 5), "char_len_max": max(Lc),
            "tate_len_mean": round(sum(Lt) / len(Lt), 5), "tate_len_max": max(Lt),
        }

    # (C) kurvenspezifisch, Tiefenverteilung + gewichtete Laengensumme je Champion
    rows = []
    all_depths_char, all_depths_tate = [], []
    for t in triples:
        rad = set(t["S_odd"]) | {2}
        L_char, L_tate = 0, 0
        max_d_char, max_d_tate = 0, 0
        n_pairs_char, n_pairs_tate = 0, 0
        for r in t["S_odd"]:
            for q in prime_factors(r * r - 1):
                if q > 2 and q not in rad:
                    d = vq(r * r - 1, q)
                    L_char += d
                    n_pairs_char += 1
                    max_d_char = max(max_d_char, d)
                    all_depths_char.append(d)
        for r, e in t["exps"].items():
            for q in prime_factors(2 * e):
                if q > 2 and q not in rad:
                    d = vq(2 * e, q)
                    L_tate += d
                    n_pairs_tate += 1
                    max_d_tate = max(max_d_tate, d)
                    all_depths_tate.append(d)
        rows.append({
            "rank": t["rank"], "q_abc": round(t["q_abc"], 4), "omega": t["omega"],
            "L_char": L_char, "L_tate": L_tate, "L_total": L_char + L_tate,
            "n_pairs": n_pairs_char + n_pairs_tate,
            "max_depth_char": max_d_char, "max_depth_tate": max_d_tate,
        })

    def corr(xs, ys):
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        sy = math.sqrt(sum((y - my) ** 2 for y in ys))
        return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy), 4) if sx and sy else 0.0

    quals = [r["q_abc"] for r in rows]
    omegas = [r["omega"] for r in rows]
    Ltot = [r["L_total"] for r in rows]

    def depth_hist(ds):
        h = {}
        for d in ds:
            h[d] = h.get(d, 0) + 1
        return {str(k): h[k] for k in sorted(h)}

    scan = {
        "n_triples": len(rows),
        "mean_L_total": round(sum(Ltot) / len(Ltot), 3),
        "max_L_total": max(Ltot),
        "mean_L_char": round(sum(r["L_char"] for r in rows) / len(rows), 3),
        "mean_L_tate": round(sum(r["L_tate"] for r in rows) / len(rows), 3),
        "global_max_depth_char": max((r["max_depth_char"] for r in rows), default=0),
        "global_max_depth_tate": max((r["max_depth_tate"] for r in rows), default=0),
        "depth_hist_char": depth_hist(all_depths_char),
        "depth_hist_tate": depth_hist(all_depths_tate),
        "corr(L_total, q_abc)": corr(Ltot, quals),
        "corr(L_total, omega)": corr(Ltot, omegas),
        "frac_pairs_depth1_char": round(sum(1 for d in all_depths_char if d == 1) / max(1, len(all_depths_char)), 4),
        "frac_pairs_depth1_tate": round(sum(1 for d in all_depths_tate if d == 1) / max(1, len(all_depths_tate)), 4),
    }

    result = {
        "n_triples": len(triples), "qset_fixed": QSET,
        "B_fixed_q_length": agg_fixed,
        "C_curve_specific_length": scan,
        "rows_head": sorted(rows, key=lambda r: -r["q_abc"])[:15],
        "note": ("Laengenebene (Codex L2): Tiefen v_q(r^2-1), v_q(2e_r) je exz. Paar. "
                 "B: fixed grosses q blind. C: Tiefenverteilung + gewichtete Laengensumme L_total; "
                 "qualitaets-flach? => Substanz von Glied 2b auf Laengenebene erhaertet."),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    L = ["# R3 v3 — q-adische Laengenebene ({})".format(date.today()), "",
         "## (B) per-fixem-q Laengensumme (mit Tiefe) — erwartet blind fuer grosses q", "",
         "| q | char_len_mean | char_len_max | tate_len_mean | tate_len_max |",
         "|---|---:|---:|---:|---:|"]
    for q in QSET:
        a = agg_fixed[q]
        L.append("| {} | {} | {} | {} | {} |".format(
            q, a["char_len_mean"], a["char_len_max"], a["tate_len_mean"], a["tate_len_max"]))
    L += ["", "## (C) kurvenspezifische Tiefenverteilung + gewichtete Laengensumme", ""]
    for k, v in scan.items():
        L.append("- **{}**: {}".format(k, v))
    L += ["",
          "Lesart: ist die Tiefenverteilung dominiert von d=1 (frac_pairs_depth1 ~ 1) und max_depth klein,",
          "UND corr(L_total, q_abc) schwach/negativ, dann haelt die qualitaets-flache Eigenschaft auf der",
          "q-adischen LAENGENebene (nicht nur Indikatorebene) => Substanz von Glied 2b (R5.2) auf der",
          "beweisrelevanten Ebene erhaertet. Starke Tiefen oder corr(L_total,q_abc)>0 => lebender Faden."]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")

    print("WROTE", OUT_JSON.name)
    print("n_triples", len(triples))
    print("B fixed-q char_len_mean / tate_len_mean:")
    for q in QSET:
        print("  ", q, agg_fixed[q]["char_len_mean"], agg_fixed[q]["tate_len_mean"])
    print("C scan:", json.dumps(scan, indent=2, default=str))


main()
