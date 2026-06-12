#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 Kill-Test Teil 2 / C8: Radikal-Cluster-Analyse der de-Smit-Champions.

B1-Restfrage: Existiert eine qualitaetserhaltende, informations-expandierende
Operation im Tripelraum? Empirische Spur waere: Champions mit VERWANDTEN
Radikal-Strukturen (gemeinsame grosse Primes, Potenz-Bilder, Kompositions-
Muster). Dieses Script prueft an den 241 guten Tripeln (q >= 1.4):

(1) PARSE der Faktorisierungen (a, b, c als Primpotenz-Produkte direkt im
    de-Smit-HTML), q-Nachrechnung als Kontrolle.
(2) POTENZ-BILD-SUCHE: Paare (T, T') mit a' = a^k / b' = b^k / c' = c^k
    (k = 2, 3) — Verdopplungs-Spur. Analytische Vorhersage: LEER, denn die
    Kompositions-Kontraktion q -> 2q/(1+q) drueckt Champions unter 1.4.
(3) PRIME-SHARING-GRAPH fuer Schwellen P0 in {7, 13, 50}: Kanten zwischen
    Tripeln mit >= 1 bzw. >= 2 gemeinsamen Primes > P0; Komponenten.
(4) KONFIGURATIONSMODELL-NULLTEST: Stub-Matching mit identischen Tripel-
    und Prime-Graden (200 Shuffles) — ist die beobachtete Zahl der
    >=1- bzw. >=2-Sharing-Paare auffaellig?
"""

import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from math import log

import numpy as np

SRC = "_sources/abc_smitbde_set2_goodtriples_2019.html"
SEED = 20260611
N_SHUFFLE = 200
OUT_JSON = "_results/b1_c8_radical_cluster_analysis_{}.json".format(date.today())
OUT_MD = "_results/b1_c8_radical_cluster_analysis_{}.md".format(date.today())


def parse_factorization(cell):
    """'2<sup>21</sup>&#x200B;23' -> {2: 21, 23: 1}"""
    cell = cell.replace("&#x200B;", " ").replace("​", " ")
    fac = {}
    for m in re.finditer(r"(\d+)(?:<sup>(\d+)</sup>)?", cell):
        p, e = int(m.group(1)), int(m.group(2) or 1)
        fac[p] = fac.get(p, 0) + e
    return fac


def value(fac):
    v = 1
    for p, e in fac.items():
        v *= p ** e
    return v


def main():
    t0 = time.time()
    html = open(SRC, encoding="iso-8859-1").read()
    body = html[html.find("known triples with q"):]
    triples = []
    n_skipped_big = 0
    for row in re.finditer(
            r"<tr><td>\s*(\d+)<td>([\d.]+)<td>[\d.]+<td>[\d.]+<td class=\"abcnum\">[^<]*<td>[^<]*"
            r"<td class=\"abcnum\">(.*?)<td class=\"abcnum\">(.*?)<td class=\"abcnum\">(.*?)(?=<tr>|</table>|\Z)",
            body, re.S):
        if "BIG" in row.group(0):
            n_skipped_big += 1
            continue
        rank, q_listed = int(row.group(1)), float(row.group(2))
        fa, fb, fc = (parse_factorization(row.group(k)) for k in (3, 4, 5))
        a, b, c = value(fa), value(fb), value(fc)
        if a + b != c:
            continue  # Parse-Fehler aussortieren (wird gezaehlt)
        rad = 1
        for p in set(fa) | set(fb) | set(fc):
            rad *= p
        q = log(c) / log(rad)
        triples.append({"rank": rank, "q_listed": q_listed, "q": q,
                        "a": a, "b": b, "c": c,
                        "fa": fa, "fb": fb, "fc": fc,
                        "support": sorted(set(fa) | set(fb) | set(fc))})
    n = len(triples)
    q_ok = sum(1 for t in triples if abs(t["q"] - t["q_listed"]) < 0.005)
    print("geparst: {} Tripel (a+b=c exakt), {} BIG-Zeilen exkludiert, q-Kontrolle: {}/{} ({:.1f}s)".format(
        n, n_skipped_big, q_ok, n, time.time() - t0), flush=True)

    report = {"date": str(date.today()), "n_triples": n, "q_check_passed": q_ok,
              "n_skipped_big": n_skipped_big}

    # --- (2) Potenz-Bild-Suche ---
    vals = {}
    for t in triples:
        for key in ("a", "b", "c"):
            vals.setdefault(t[key], []).append((t["rank"], key))
    power_hits = []
    for t in triples:
        for key in ("a", "b", "c"):
            x = t[key]
            if x < 100:
                continue  # Kleinwert-Koinzidenzen (a=2 vs a'=4 etc.) ausschliessen
            for k in (2, 3):
                if x ** k in vals:
                    power_hits.append({"src_rank": t["rank"], "src_slot": key, "k": k,
                                       "img": vals[x ** k]})
    # volles Verdopplungs-Bild: (a^2, b(a+c), c^2) als komplettes Tripel vorhanden?
    cset = {t["c"]: t["rank"] for t in triples}
    full_doubling = [{"src_rank": t["rank"], "img_rank": cset[t["c"] ** 2]}
                     for t in triples if t["c"] ** 2 in cset]
    report["power_image_pairs_xge100"] = power_hits
    report["full_doubling_images"] = full_doubling
    print("Potenz-Bilder (x>=100, k=2,3): {} | volle Verdopplungs-Bilder: {}".format(
        len(power_hits), len(full_doubling)), flush=True)

    # --- (3)+(4) Prime-Sharing ---
    report["sharing"] = {}
    rng = np.random.default_rng(SEED)
    for P0 in (7, 13, 50):
        sup = [set(p for p in t["support"] if p > P0) for t in triples]
        # beobachtete Paar-Statistik
        prime_owners = defaultdict(list)
        for i, s in enumerate(sup):
            for p in s:
                prime_owners[p].append(i)
        pair_common = Counter()
        for p, owners in prime_owners.items():
            for x in range(len(owners)):
                for y in range(x + 1, len(owners)):
                    pair_common[(owners[x], owners[y])] += 1
        obs_ge1 = len(pair_common)
        obs_ge2 = sum(1 for v in pair_common.values() if v >= 2)
        # Komponenten des >=1-Graphen
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for (i, j) in pair_common:
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
        comp = Counter(find(i) for i in range(n))
        comp_sizes = sorted((v for v in comp.values() if v >= 2), reverse=True)

        # Nullmodell: degree-erhaltende Edge-Swaps (MCMC, keine Multi-Edges)
        edge_list = [(i, p) for i, s in enumerate(sup) for p in s]
        edge_set = set(edge_list)
        nE = len(edge_list)
        null_ge1, null_ge2 = [], []
        if nE >= 4:
            for k in range(20 * nE):  # Burn-in
                e1, e2 = rng.integers(0, nE, 2)
                (i, p), (j, q) = edge_list[e1], edge_list[e2]
                if i == j or p == q or (i, q) in edge_set or (j, p) in edge_set:
                    continue
                edge_set.discard((i, p)); edge_set.discard((j, q))
                edge_set.add((i, q)); edge_set.add((j, p))
                edge_list[e1], edge_list[e2] = (i, q), (j, p)
            for snap in range(N_SHUFFLE):
                for k in range(2 * nE):  # Dekorrelation zwischen Snapshots
                    e1, e2 = rng.integers(0, nE, 2)
                    (i, p), (j, q) = edge_list[e1], edge_list[e2]
                    if i == j or p == q or (i, q) in edge_set or (j, p) in edge_set:
                        continue
                    edge_set.discard((i, p)); edge_set.discard((j, q))
                    edge_set.add((i, q)); edge_set.add((j, p))
                    edge_list[e1], edge_list[e2] = (i, q), (j, p)
                owners_null = defaultdict(list)
                for i, p in edge_list:
                    owners_null[p].append(i)
                pc = Counter()
                for p, ow in owners_null.items():
                    for x in range(len(ow)):
                        for y in range(x + 1, len(ow)):
                            a_, b_ = (ow[x], ow[y]) if ow[x] < ow[y] else (ow[y], ow[x])
                            pc[(a_, b_)] += 1
                null_ge1.append(len(pc))
                null_ge2.append(sum(1 for v in pc.values() if v >= 2))
        null_ge1, null_ge2 = np.array(null_ge1), np.array(null_ge2)

        # groesste Mehrfach-Sharing-Paare dokumentieren
        top_pairs = sorted(pair_common.items(), key=lambda x: -x[1])[:6]
        top_doc = [{"ranks": [triples[i]["rank"], triples[j]["rank"]],
                    "n_common": v,
                    "common_primes": sorted(set(p for p in triples[i]["support"] if p > P0)
                                            & set(p for p in triples[j]["support"] if p > P0))}
                   for (i, j), v in top_pairs]

        report["sharing"][str(P0)] = {
            "n_primes_gt_P0": len(prime_owners),
            "pairs_ge1": obs_ge1, "pairs_ge2": obs_ge2,
            "null_ge1_mean": float(null_ge1.mean()), "null_ge1_sd": float(null_ge1.std()),
            "null_ge2_mean": float(null_ge2.mean()), "null_ge2_sd": float(null_ge2.std()),
            "z_ge1": float((obs_ge1 - null_ge1.mean()) / max(null_ge1.std(), 1e-9)),
            "z_ge2": float((obs_ge2 - null_ge2.mean()) / max(null_ge2.std(), 1e-9)),
            "components_ge2_sizes_top": comp_sizes[:8],
            "n_isolated": int(n - sum(comp_sizes)),
            "top_multi_sharing_pairs": top_doc,
        }
        print("P0={}: Paare >=1: {} (null {:.0f}±{:.0f}), >=2: {} (null {:.1f}±{:.1f}) ({:.1f}s)".format(
            P0, obs_ge1, null_ge1.mean(), null_ge1.std(), obs_ge2,
            null_ge2.mean(), null_ge2.std(), time.time() - t0), flush=True)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# B1/C8: Radikal-Cluster-Analyse der de-Smit-Champions ({})".format(date.today()), ""]
    lines.append("{} Tripel geparst (a+b=c exakt), q-Nachrechnung: {}/{} innerhalb 0.005.".format(n, q_ok, n))
    lines.append("")
    lines.append("**(2) Potenz-Bilder (x ≥ 100, k=2,3, alle Slots):** {} Treffer; volle Verdopplungs-Bilder (c′=c²): {} — Vorhersage der Kompositions-Kontraktion q→2q/(1+q): leer.".format(
        len(power_hits), len(full_doubling)))
    lines.append("")
    lines.append("| P₀ | Primes>P₀ | Paare ≥1 gem. | Null (μ±σ) | z | Paare ≥2 gem. | Null | z | Komp.-Größen |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for P0 in (7, 13, 50):
        s = report["sharing"][str(P0)]
        lines.append("| {} | {} | {} | {:.0f}±{:.0f} | {:+.1f} | {} | {:.1f}±{:.1f} | {:+.1f} | {} |".format(
            P0, s["n_primes_gt_P0"], s["pairs_ge1"], s["null_ge1_mean"], s["null_ge1_sd"], s["z_ge1"],
            s["pairs_ge2"], s["null_ge2_mean"], s["null_ge2_sd"], s["z_ge2"],
            s["components_ge2_sizes_top"]))
    lines.append("")
    lines.append("**Top-Mehrfach-Sharing-Paare (P₀=13):**")
    for d in report["sharing"]["13"]["top_multi_sharing_pairs"]:
        lines.append("- Ranks {} | {} gemeinsame Primes > 13: {}".format(
            d["ranks"], d["n_common"], d["common_primes"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
