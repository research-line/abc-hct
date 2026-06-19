#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 Spreading Kill-or-Keep-Test (IDEENSPEICHER Iter 4 B1 / Codex-Ajtai-Punkt 2).

Frage (Ajtai-Reverse): Kann ein hypothetischer abc-Verletzer ISOLIERT bleiben?
Spreading lebt nur, wenn es eine qualitaetserhaltende Operation auf Tripeln mit
EXPANSION gibt (ein Tripel -> positive Dichte Fast-Verletzer). Kill-Kriterium
(IDEENSPEICHER): "Keine Operation mit kleinem |Delta q| UND Expansion => B1 verwerfen."

Dieser Test ist die BILLIGE erste Stufe: er prueft eine NOTWENDIGE Bedingung fuer
Spreading, naemlich ob die bekannten guten Tripel im Radikal-Raum CLUSTERN (ueber
einem Glattheits-Nullmodell) -- ohne Clustering kann keine kleine-Delta-q-Operation
mit Expansion existieren. Zusaetzlich werden die konkreten deterministischen
Tripel-Operationen (Skalierung; additive Stoerung) auf Gueltigkeit + Expansion
enumeriert.

Datenquelle: Bart de Smit, "ABC triples by quality" (241 gute Tripel q>=1.4),
   _sources/abc_smitbde_set2_goodtriples_2019.html (Faktorform -> Primtraeger direkt).
de Weger: separate Datei nicht im Projekt vorhanden -> de Smit als Referenzset.

Gemessen:
 (1) Parser-Selbsttest a+b=c und q_listed ~ q_computed (Vertrauen in die Eingabe).
 (2) Radikal-Overlap-Graph (Overlap-Koeffizient |Pi cap Pj| / min(|Pi|,|Pj|)) ueber
     mehrere Schwellen: Komponentenstruktur, Grad, Delta q entlang Kanten.
 (3) Glattheits-Nullmodell (grad-/groessen-erhaltende Primtraeger-Permutation):
     EXZESS (beobachtet - Null) ist das Signal; reines small-prime-Cooccurrence
     wird so herausgerechnet.
 (4) Operations-Enumeration: Skalierung+Primitivierung (Orbit 1, keine Expansion);
     additive Stoerung (verletzt a+b=c -> ungueltig). -> deterministische
     Tripel-Operationen sind nicht-expandierend (Rigiditaet von a+b=c).

Verdikt:
 KILL  wenn kein signifikanter Overlap-Exzess ueber dem Nullmodell ODER der Exzess
       nicht mit kleinem Delta q einhergeht  -> Verletzer kann isoliert bleiben.
 KEEP  wenn signifikanter Exzess-Cluster mit kleinem Delta q  -> Spreading hat
       empirisches Leben; naechste (harte) Stufe: Operation explizit ausweisen.

Aufruf:
  PYTHONIOENCODING=utf-8 python _scripts/b1_spreading_kill_or_keep.py \
      [--html PATH] [--nshuffle 500] [--seed 12345] \
      [--out-json PATH] [--out-md PATH]
"""

import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import date


# ---------------------------------------------------------------------------
# 1. Parser der de-Smit-Faktorform
# ---------------------------------------------------------------------------

SEP_RE = re.compile(r"(?:&middot;|&#x200B;|&#8203;|​|&nbsp;)+")
TAGSTRIP_RE = re.compile(r"<[^>]*>")
ENT_RE = re.compile(r"&[#0-9a-zA-Z]+;")


def parse_factored(cell_html):
    """'2<sup>21</sup>&#x200B;23' -> (value, {primes}, {prime:exp})."""
    s = cell_html
    s = s.replace("<sup>", "^").replace("</sup>", "")
    tokens = SEP_RE.split(s)
    value = 1
    exps = {}
    for tok in tokens:
        tok = TAGSTRIP_RE.sub("", tok)
        tok = ENT_RE.sub("", tok).strip()
        if not tok:
            continue
        if "^" in tok:
            base_s, exp_s = tok.split("^", 1)
            base, exp = int(base_s), int(exp_s)
        else:
            base, exp = int(tok), 1
        value *= base ** exp
        exps[base] = exps.get(base, 0) + exp
    return value, set(exps.keys()), exps


def strip_cell(cell):
    """Nimm den Text nach dem ersten '>' (entfernt 'class="abcnum"' etc.)."""
    idx = cell.find(">")
    return cell[idx + 1:] if idx >= 0 else cell


def load_triples(html_path):
    with open(html_path, "r", encoding="iso-8859-1") as f:
        html = f.read()
    triples = []
    bad = []
    # Datenzeilen beginnen mit '<tr><td>' und haben numerischen Rang.
    for rowmatch in re.finditer(r"<tr>(<td.*?)(?=<tr>|</table>|$)", html, re.S):
        row = rowmatch.group(1)
        cells = row.split("<td")
        # cells[0] == '' (vor erstem <td); echte Zellen ab cells[1]
        cells = [strip_cell(c) for c in cells[1:]]
        if len(cells) < 9:
            continue
        rank_s = TAGSTRIP_RE.sub("", cells[0]).strip()
        if not re.match(r"^\d+$", rank_s):
            continue
        try:
            q_listed = float(TAGSTRIP_RE.sub("", cells[1]).strip())
            va, pa, ea = parse_factored(cells[6])
            vb, pb, eb = parse_factored(cells[7])
            vc, pc, ec = parse_factored(cells[8])
        except (ValueError, IndexError):
            bad.append(rank_s)
            continue
        support = pa | pb | pc
        rad = 1
        for p in support:
            rad *= p
        ok = (va + vb == vc)
        q_comp = math.log(vc) / math.log(rad) if rad > 1 else 0.0
        triples.append({
            "rank": int(rank_s),
            "a": va, "b": vb, "c": vc,
            "q_listed": q_listed,
            "q_comp": q_comp,
            "support": sorted(support),
            "k": len(support),
            "rad": rad,
            "ab_ok": ok,
        })
    return triples, bad


# ---------------------------------------------------------------------------
# 2./3. Overlap-Graph + Nullmodell
# ---------------------------------------------------------------------------

def overlap_coeff(s1, s2):
    inter = len(s1 & s2)
    m = min(len(s1), len(s2))
    return inter / m if m else 0.0


def components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
    comp = defaultdict(list)
    for i in range(n):
        comp[find(i)].append(i)
    return sorted((len(v) for v in comp.values()), reverse=True)


def graph_stats(supports, qual, thr):
    """Kanten bei Overlap-Koeffizient >= thr. Liefert Grad-/Komponenten-/Delta-q-Stats."""
    n = len(supports)
    edges = []
    dq = []
    for i in range(n):
        for j in range(i + 1, n):
            oc = overlap_coeff(supports[i], supports[j])
            if oc >= thr:
                edges.append((i, j))
                dq.append(abs(qual[i] - qual[j]))
    comps = components(n, edges)
    deg = [0] * n
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    return {
        "threshold": thr,
        "n_edges": len(edges),
        "mean_degree": sum(deg) / n if n else 0.0,
        "max_component": comps[0] if comps else 0,
        "n_components": len(comps),
        "largest_comp_frac": (comps[0] / n) if comps else 0.0,
        "mean_dq_edge": (sum(dq) / len(dq)) if dq else None,
    }


def null_ensemble(triples, thr, nshuffle, rng):
    """Grad-/groessen-erhaltende Primtraeger-Permutation: jedem Tripel werden k_i
    Primes aus dem globalen Pool gezogen, Ziehgewicht = globale Nutzungshaeufigkeit
    (so bleibt 'kleine Primes sind haeufig' erhalten). Exzess ueber dieses Modell
    ist das echte Cluster-Signal."""
    usage = defaultdict(int)
    for t in triples:
        for p in t["support"]:
            usage[p] += 1
    pool = sorted(usage.keys())
    weights = [usage[p] for p in pool]
    qual = [t["q_listed"] for t in triples]
    ks = [t["k"] for t in triples]

    stats = {"n_edges": [], "max_component": [], "largest_comp_frac": [],
             "mean_degree": [], "mean_dq_edge": []}
    for _ in range(nshuffle):
        supports = []
        for k in ks:
            # gewichtetes Ziehen ohne Zuruecklegen
            chosen = _weighted_sample_without_replacement(pool, weights, k, rng)
            supports.append(set(chosen))
        gs = graph_stats(supports, qual, thr)
        for key in stats:
            v = gs[key]
            if v is not None:
                stats[key].append(v)
    return {k: _msd(v) for k, v in stats.items()}


def _weighted_sample_without_replacement(pool, weights, k, rng):
    # Efraimidis-Spirakis: key = u^(1/w)
    if k >= len(pool):
        return list(pool)
    keys = []
    for p, w in zip(pool, weights):
        u = rng.random()
        keys.append((u ** (1.0 / w), p))
    keys.sort(reverse=True)
    return [p for _, p in keys[:k]]


def _msd(vals):
    if not vals:
        return {"mean": None, "sd": None, "n": 0}
    m = sum(vals) / len(vals)
    var = sum((x - m) ** 2 for x in vals) / len(vals)
    return {"mean": m, "sd": math.sqrt(var), "n": len(vals)}


def zscore(obs, null):
    if null["mean"] is None or null["sd"] in (None, 0.0):
        return None
    return (obs - null["mean"]) / null["sd"]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    # Script-relativ auflösen (portabel: Windows-Laptop UND Mac Studio).
    # Frueherer Bug: hartkodierter Git-Bash-Pfad zum lokalen Arbeitsbaum -> FileNotFoundError
    # unter Windows-Python und auf dem Mac (2026-06-14 Crash-Session).
    base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--html", default=base + "/_sources/abc_smitbde_set2_goodtriples_2019.html")
    ap.add_argument("--nshuffle", type=int, default=500)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    args = ap.parse_args()

    import random
    rng = random.Random(args.seed)

    today = str(date.today())
    out_json = args.out_json or (base + "/_results/b1_spreading_kill_or_keep_{}.json".format(today))
    out_md = args.out_md or (base + "/_results/b1_spreading_kill_or_keep_{}.md".format(today))

    triples, bad = load_triples(args.html)
    n = len(triples)
    n_ok = sum(1 for t in triples if t["ab_ok"])
    q_err = [abs(t["q_listed"] - t["q_comp"]) for t in triples if t["rad"] > 1]
    max_qerr = max(q_err) if q_err else None

    print("Geparste Tripel: {} (a+b=c verifiziert: {}/{}, Parsefehler: {})".format(
        n, n_ok, n, len(bad)), flush=True)
    print("max |q_listed - q_comp| = {}".format(max_qerr), flush=True)

    supports = [set(t["support"]) for t in triples]
    qual = [t["q_listed"] for t in triples]

    thresholds = [0.5, 0.667, 0.75, 1.0]
    rows = []
    for thr in thresholds:
        obs = graph_stats(supports, qual, thr)
        null = null_ensemble(triples, thr, args.nshuffle, rng)
        z_edges = zscore(obs["n_edges"], null["n_edges"])
        z_comp = zscore(obs["max_component"], null["max_component"])
        rows.append({"obs": obs, "null": null, "z_edges": z_edges, "z_comp": z_comp})
        print("thr={:.3f}: edges obs={} null~{:.1f}+/-{:.1f} (z={}); "
              "maxcomp obs={} null~{:.1f} (z={}); mean_dq_edge={}".format(
                  thr, obs["n_edges"],
                  null["n_edges"]["mean"] or 0.0, null["n_edges"]["sd"] or 0.0,
                  None if z_edges is None else round(z_edges, 2),
                  obs["max_component"], null["max_component"]["mean"] or 0.0,
                  None if z_comp is None else round(z_comp, 2),
                  None if obs["mean_dq_edge"] is None else round(obs["mean_dq_edge"], 4)),
              flush=True)

    # Delta-q-Baseline: mittlerer |q_i - q_j| ueber ALLE Paare (Referenz fuer "klein")
    allpairs_dq = []
    for i in range(n):
        for j in range(i + 1, n):
            allpairs_dq.append(abs(qual[i] - qual[j]))
    mean_dq_all = sum(allpairs_dq) / len(allpairs_dq) if allpairs_dq else None

    # ---- Operations-Enumeration (deterministische Tripel-Operationen) ----
    # Skalierung+Primitivierung: (da,db,dc) -> primitiv = (a,b,c). Orbit 1.
    ops = [
        {"name": "Skalierung+Primitivierung", "valid": True, "delta_q": 0.0,
         "expansion": "Orbit=1 (primitiv invariant) -> KEINE Expansion"},
        {"name": "additive Stoerung (a+e, b, c)", "valid": False, "delta_q": None,
         "expansion": "verletzt a+b=c -> ungueltig (Rigiditaet)"},
        {"name": "Primexponent-Bump im Radikal", "valid": False, "delta_q": None,
         "expansion": "veraendert c, a+b=c neu zu loesen -> keine lokale Operation"},
    ]

    # ---- Verdikt ----
    # KEEP nur wenn an einer Schwelle ein klar signifikanter Exzess (z>=3) UND
    # die Kanten-Delta-q deutlich unter der All-Paar-Baseline liegt.
    keep_signals = []
    for thr, r in zip(thresholds, rows):
        z = r["z_comp"] if r["z_comp"] is not None else (r["z_edges"] or 0.0)
        dqe = r["obs"]["mean_dq_edge"]
        small_dq = (dqe is not None and mean_dq_all is not None and dqe < 0.6 * mean_dq_all)
        if z is not None and z >= 3.0 and small_dq:
            keep_signals.append({"thr": thr, "z": z, "mean_dq_edge": dqe})
    verdict = "KEEP" if keep_signals else "KILL"

    report = {
        "date": today,
        "purpose": "B1 spreading kill-or-keep test (Ajtai-reverse necessary condition)",
        "data_source": "de Smit 241 good ABC triples (q>=1.4), 2019",
        "n_triples": n,
        "ab_verified": n_ok,
        "parse_errors": bad,
        "max_q_error": max_qerr,
        "mean_dq_allpairs": mean_dq_all,
        "thresholds": rows,
        "operations": ops,
        "keep_signals": keep_signals,
        "verdict": verdict,
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown
    L = []
    L.append("# B1 Spreading Kill-or-Keep-Test ({})".format(today))
    L.append("")
    L.append("**Frage (Ajtai-Reverse):** Kann ein abc-Verletzer isoliert bleiben? "
             "Spreading lebt nur bei qualitaetserhaltender Operation MIT Expansion.")
    L.append("**Daten:** de Smit, 241 gute Tripel (q≥1.4). a+b=c verifiziert: "
             "{}/{} (Parsefehler {}); max |q_listed−q_comp| = {}.".format(
                 n_ok, n, len(bad), None if max_qerr is None else round(max_qerr, 4)))
    L.append("**Notwendige Bedingung getestet:** Radikal-Cluster ÜBER Glattheits-Nullmodell "
             "({} Permutationen, grad-/größen-erhaltend).".format(args.nshuffle))
    L.append("")
    L.append("Mittleres |q_i−q_j| über alle Paare (Baseline „klein\"): {:.4f}.".format(mean_dq_all))
    L.append("")
    L.append("| Overlap-Schwelle | Kanten (obs) | Kanten (Null μ±σ) | z | max Komp. (obs) | max Komp. (Null μ) | z | ⟨Δq⟩ Kante |")
    L.append("|---|---:|---|---:|---:|---:|---:|---:|")
    for thr, r in zip(thresholds, rows):
        o, nu = r["obs"], r["null"]
        L.append("| {:.3f} | {} | {:.1f}±{:.1f} | {} | {} | {:.1f} | {} | {} |".format(
            thr, o["n_edges"],
            nu["n_edges"]["mean"] or 0.0, nu["n_edges"]["sd"] or 0.0,
            "—" if r["z_edges"] is None else "{:.2f}".format(r["z_edges"]),
            o["max_component"], nu["max_component"]["mean"] or 0.0,
            "—" if r["z_comp"] is None else "{:.2f}".format(r["z_comp"]),
            "—" if o["mean_dq_edge"] is None else "{:.4f}".format(o["mean_dq_edge"])))
    L.append("")
    L.append("## Operations-Enumeration (deterministische Tripel-Operationen)")
    L.append("")
    L.append("| Operation | gültig? | Δq | Expansion |")
    L.append("|---|---|---|---|")
    for op in ops:
        L.append("| {} | {} | {} | {} |".format(
            op["name"], "ja" if op["valid"] else "nein",
            "—" if op["delta_q"] is None else op["delta_q"], op["expansion"]))
    L.append("")
    L.append("## Verdikt: **{}**".format(verdict))
    L.append("")
    if verdict == "KILL":
        L.append("Kein Overlap-Exzess (z≥3) mit gleichzeitig kleinem Kanten-Δq über dem "
                 "Glattheits-Nullmodell; die deterministischen Tripel-Operationen sind "
                 "nicht-expandierend (a+b=c-Rigidität). ⟹ Die NOTWENDIGE Bedingung für "
                 "Spreading ist nicht erfüllt: ein Verletzer kann im Radikal-Raum isoliert "
                 "bleiben. Triple-Ebene-B1 verworfen; falls Spreading existiert, lebt es in "
                 "der Kurven-/Twist-Familie (Zertifikatsraum), nicht in der Tripel-Familie.")
    else:
        L.append("Signifikanter Radikal-Cluster-Exzess mit kleinem Δq vorhanden ⟹ die "
                 "notwendige Bedingung für Spreading hält. Nächste (harte) Stufe: die "
                 "qualitätserhaltende Operation explizit ausweisen und ihre Dichte beweisen "
                 "(Granville–Stark-Architektur).")
    L.append("")
    L.append("Caveat: Dies ist die billige erste Stufe (notwendige Bedingung). KILL ist "
             "belastbar (kein Cluster ⟹ keine Operation); KEEP ist nur ein Weiterleben, "
             "kein Spreading-Beweis. de Weger-Set nicht im Projekt — de Smit als Referenz.")
    L.append("")
    L.append("JSON: `{}`. Script: `_scripts/b1_spreading_kill_or_keep.py`.".format(out_json))
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print("\nVerdikt: {}".format(verdict))
    print("JSON: {}\nMD:   {}".format(out_json, out_md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
