#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CX2+CX3 (Codex-Audit 2026-06-11): zwei billige Kill-or-Go-Tests an den
240 de-Smit-Champions.

CX2 — SUBTORUS-NAEHE: Tripel als Punkt (x, y) = (a/c, b/c) auf x+y=1 in
(Q*)^2; Bewertungsvektoren vx, vy in Z^S. Frage: Liegen hohe q-Tripel
nahe an echten Subtori x^m y^n = const (kleine |m|+|n|)? Score:
  T(r) = min_{0<|m|+|n|<=M} ||m vx + n vy||_2 / (||(m,n)||_2 * ||vx||+||vy||-Skala)
plus exakte Subtorus-Treffer (m vx + n vy = 0). Korrelation mit q.

CX3 — ADDITIVE EXPANSION: Fuer den Support S eines Champions die Menge
M(S, X) der S-glatten Zahlen <= X (X so gewaehlt, dass |M| ~ TARGET).
Additive Geschlossenheit:
  closure(S) = #{(u,v): u <= v, u+v in M} / |M|^2.
Baseline: NREP Zufalls-Traeger (jeder Prime p durch Zufallsprime in
[p/2, 2p] ersetzt, gleiche Anzahl). z-Score pro Champion; Korrelation z
vs. q. Codex-These: hohe Qualitaet ~ anomal NIEDRIGE Expansion (= hohe
Geschlossenheit).
"""

import json
import re
import sys
import time
from datetime import date
from math import log

import numpy as np
from sympy import isprime, nextprime, prevprime

SRC = "_sources/abc_smitbde_set2_goodtriples_2019.html"
SEED = 20260611
M_RANGE = 6
TARGET = 600
NREP = 3
OUT_JSON = "_results/cx2_cx3_codex_tests_{}.json".format(date.today())
OUT_MD = "_results/cx2_cx3_codex_tests_{}.md".format(date.today())


def parse_triples():
    html = open(SRC, encoding="iso-8859-1").read()
    body = html[html.find("known triples with q"):]

    def pf(cell):
        cell = cell.replace("&#x200B;", " ")
        fac = {}
        for m in re.finditer(r"(\d+)(?:<sup>(\d+)</sup>)?", cell):
            p, e = int(m.group(1)), int(m.group(2) or 1)
            fac[p] = fac.get(p, 0) + e
        return fac

    def val(fac):
        v = 1
        for p, e in fac.items():
            v *= p ** e
        return v

    out = []
    for row in re.finditer(
            r"<tr><td>\s*(\d+)<td>([\d.]+)<td>[\d.]+<td>[\d.]+<td class=\"abcnum\">[^<]*<td>[^<]*"
            r"<td class=\"abcnum\">(.*?)<td class=\"abcnum\">(.*?)<td class=\"abcnum\">(.*?)(?=<tr>|</table>|\Z)",
            body, re.S):
        if "BIG" in row.group(0):
            continue
        fa, fb, fc = pf(row.group(3)), pf(row.group(4)), pf(row.group(5))
        if val(fa) + val(fb) != val(fc):
            continue
        out.append({"rank": int(row.group(1)), "q": float(row.group(2)),
                    "fa": fa, "fb": fb, "fc": fc})
    return out


def smooth_set(primes, target):
    """S-glatte Zahlen, adaptives X fuer |M| ~ target; Cap INNERHALB der
    Erzeugung (sonst MemoryError bei kleinem p und grossem X)."""
    X = 10 ** 6
    cap = 30 * target
    out = [1]
    for _ in range(30):
        out = [1]
        overflow = False
        for p in primes:
            new = []
            for m in out:
                v = m
                while v <= X:
                    new.append(v)
                    if len(new) > cap:
                        overflow = True
                        break
                    v *= p
                if overflow:
                    break
            if overflow:
                break
            out = new
        if overflow or len(out) > target:
            X = int(X / 1.8)
            continue
        if len(out) < max(20, target // 3) and X < 10 ** 11:
            X = int(X * 2.2)
            continue
        return np.array(sorted(out)), X
    return np.array(sorted(out)), X


def closure_score(arr):
    if len(arr) < 10:
        return None
    s = np.add.outer(arr, arr)
    iu = np.triu_indices(len(arr))
    hits = np.isin(s[iu], arr).sum()
    return float(hits) / (len(arr) ** 2)


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    triples = parse_triples()
    print("{} Tripel geparst ({:.1f}s)".format(len(triples), time.time() - t0), flush=True)

    # --- CX2 ---
    cx2 = []
    for t in triples:
        S = sorted(set(t["fa"]) | set(t["fb"]) | set(t["fc"]))
        vx = np.array([t["fa"].get(p, 0) - t["fc"].get(p, 0) for p in S], dtype=float)
        vy = np.array([t["fb"].get(p, 0) - t["fc"].get(p, 0) for p in S], dtype=float)
        scale = np.sqrt((vx ** 2 + vy ** 2).sum())
        best, exact = 1e9, 0
        for m in range(-M_RANGE, M_RANGE + 1):
            for n in range(-M_RANGE, M_RANGE + 1):
                if m == 0 and n == 0:
                    continue
                w = m * vx + n * vy
                nw = np.sqrt((w ** 2).sum())
                if nw < 1e-12:
                    exact += 1
                sc = nw / (np.sqrt(m * m + n * n) * max(scale, 1e-9))
                best = min(best, sc)
        cx2.append({"rank": t["rank"], "q": t["q"], "score": best, "exact_subtorus": exact})
    qs = np.array([c["q"] for c in cx2])
    sc = np.array([c["score"] for c in cx2])
    # Spearman-artig: Rang-Korrelation
    def rankcorr(a, b):
        ra = np.argsort(np.argsort(a)).astype(float)
        rb = np.argsort(np.argsort(b)).astype(float)
        return float(np.corrcoef(ra, rb)[0, 1])
    rho_cx2 = rankcorr(qs, sc)
    hi = qs >= np.median(qs)
    cx2_summary = {
        "rank_corr_q_vs_subtorus_score": rho_cx2,
        "score_median_high_q": float(np.median(sc[hi])),
        "score_median_low_q": float(np.median(sc[~hi])),
        "n_exact_subtorus_points": int(sum(1 for c in cx2 if c["exact_subtorus"] > 0)),
        "top5_closest": sorted(({"rank": c["rank"], "q": c["q"], "score": round(c["score"], 4)}
                                for c in cx2), key=lambda d: d["score"])[:5],
    }
    print("CX2: rank-corr(q, score) = {:.3f} | exakte Subtorus-Punkte: {} ({:.1f}s)".format(
        rho_cx2, cx2_summary["n_exact_subtorus_points"], time.time() - t0), flush=True)

    # --- CX3 ---
    cx3 = []
    for ti, t in enumerate(triples):
        S = sorted(set(t["fa"]) | set(t["fb"]) | set(t["fc"]))
        arr, X = smooth_set(S, TARGET)
        c0 = closure_score(arr)
        if c0 is None:
            continue
        base = []
        for _ in range(NREP):
            Sr = []
            for p in S:
                lo, hi_ = max(2, p // 2), 2 * p + 1
                cand = rng.integers(lo, hi_)
                pr = int(nextprime(cand))
                if pr > hi_:
                    pr = int(prevprime(max(cand, 3)))
                while pr in Sr:
                    pr = int(nextprime(pr))
                Sr.append(pr)
            arr_r, _ = smooth_set(sorted(Sr), TARGET)
            cb = closure_score(arr_r)
            if cb is not None:
                base.append(cb)
        if len(base) < 2:
            continue
        mu, sd = float(np.mean(base)), float(np.std(base))
        z = (c0 - mu) / max(sd, 1e-12)
        cx3.append({"rank": t["rank"], "q": t["q"], "closure": c0,
                    "base_mu": mu, "base_sd": sd, "z": z, "n_smooth": int(len(arr))})
        if (ti + 1) % 40 == 0:
            print("  CX3: {}/{} ({:.1f}s)".format(ti + 1, len(triples), time.time() - t0), flush=True)
    qz = np.array([c["q"] for c in cx3])
    zz = np.array([c["z"] for c in cx3])
    rho_cx3 = rankcorr(qz, zz)
    cx3_summary = {
        "n_evaluated": len(cx3),
        "z_median": float(np.median(zz)),
        "z_mean": float(np.mean(zz)),
        "frac_z_gt_2": float((zz > 2).mean()),
        "rank_corr_q_vs_z": rho_cx3,
        "z_median_high_q": float(np.median(zz[qz >= np.median(qz)])),
        "z_median_low_q": float(np.median(zz[qz < np.median(qz)])),
    }
    print("CX3: z-median = {:.2f} | rank-corr(q, z) = {:.3f} ({:.1f}s)".format(
        cx3_summary["z_median"], rho_cx3, time.time() - t0), flush=True)

    report = {"date": str(date.today()), "cx2_summary": cx2_summary, "cx2": cx2,
              "cx3_summary": cx3_summary, "cx3": cx3}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# CX2+CX3: Codex-Audit-Tests an den de-Smit-Champions ({})".format(date.today()), ""]
    lines.append("**CX2 (Subtorus-Nähe):** rank-corr(q, score) = {:.3f}; Score-Median hohe q: {:.4f}, niedrige q: {:.4f}; exakte Subtorus-Punkte: {}.".format(
        rho_cx2, cx2_summary["score_median_high_q"], cx2_summary["score_median_low_q"],
        cx2_summary["n_exact_subtorus_points"]))
    lines.append("")
    lines.append("Top-5 subtorus-nächste: {}".format(cx2_summary["top5_closest"]))
    lines.append("")
    lines.append("**CX3 (additive Geschlossenheit vs. Zufalls-Träger):** n = {}; z-Median = {:.2f} (Mittel {:.2f}); Anteil z > 2: {:.1%}; rank-corr(q, z) = {:.3f}; z-Median hohe/niedrige q: {:.2f} / {:.2f}.".format(
        cx3_summary["n_evaluated"], cx3_summary["z_median"], cx3_summary["z_mean"],
        cx3_summary["frac_z_gt_2"], rho_cx3, cx3_summary["z_median_high_q"], cx3_summary["z_median_low_q"]))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`".format(time.time() - t0, OUT_JSON))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
