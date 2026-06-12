#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3 Self-Averaging-Diagnostik der abc-Qualitaet (IDEENSPEICHER Iter 4, TODO 2026-06-10).

Frage (Spin-Glas-Analogie): Ist die abc-Qualitaet q = log c / log rad(abc)
ueber die Tripel-Familie self-averaging? Gemessen wird der
non-self-averaging-Parameter R = Var(X)/<X>^2 fuer
  (a) die Bulk-Qualitaet q (Tripel-Ebene und Block-Ebene),
  (b) die Tail-Exzess-Masse E_theta = max(q - theta, 0) (Block-Ebene),
in dyadischen c-Fenstern W_k = [2^k, 2^(k+1)).

Block-Ebene = Spin-Glas-Lesart: "Probe" = c-Teilblock des Fensters
(NBLOCKS gleichbreite Teilbloecke), Observable = Blockmittel. R_block -> 0
mit wachsendem k bedeutet self-averaging (eine grosse "Probe" repraesentiert
das Ensemble); R_block ≳ const bedeutet non-self-averaging (jede Probe hat
individuellen Charakter -> Statistik erzwingt das Individuum nicht).

Enumeration: alle Tripel a + b = c, 1 <= a < b, gcd(a,b)=1, c <= CMAX.
rad via Numpy-Sieb; gcd(a,c) via np.gcd (gcd(a,b)=gcd(a,c) wegen b=c-a).

Aufruf:
  PYTHONIOENCODING=utf-8 python _scripts/abc_quality_self_averaging_probe.py \
      [--cmax 65535] [--kmin 6] [--nblocks 16] \
      [--out-json PATH] [--out-md PATH]
"""

import argparse
import json
import math
import sys
import time
from datetime import date

import numpy as np

THETAS = [0.8, 0.9, 1.0]


def rad_sieve(n):
    """rad[m] fuer 0..n via Primsieb (rad[0]=rad[1]=1)."""
    rad = np.ones(n + 1, dtype=np.int64)
    is_comp = np.zeros(n + 1, dtype=bool)
    for p in range(2, n + 1):
        if not is_comp[p]:
            rad[p::p] *= p
            is_comp[p * p::p] = True
    return rad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmax", type=int, default=65535)
    ap.add_argument("--kmin", type=int, default=6)
    ap.add_argument("--nblocks", type=int, default=16)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    args = ap.parse_args()

    cmax = args.cmax
    kmax = cmax.bit_length() - 1  # groesstes k mit 2^k <= cmax
    today = str(date.today())
    out_json = args.out_json or "_results/abc_quality_self_averaging_probe_{}.json".format(today)
    out_md = args.out_md or "_results/abc_quality_self_averaging_probe_{}.md".format(today)

    t0 = time.time()
    print("rad-Sieb bis {} ...".format(cmax), flush=True)
    rad = rad_sieve(cmax)
    lograd = np.log(rad.astype(np.float64))
    print("  Sieb fertig ({:.1f}s)".format(time.time() - t0), flush=True)

    # Akkumulatoren: pro Fenster k und Sub-Block j
    NB = args.nblocks
    windows = {}
    for k in range(args.kmin, kmax + 1):
        windows[k] = {
            "n": np.zeros(NB, dtype=np.int64),
            "sum_q": np.zeros(NB),
            "sum_q2": np.zeros(NB),
            "max_q": np.zeros(NB),
            "tail_n": {th: np.zeros(NB, dtype=np.int64) for th in THETAS},
            "tail_mass": {th: np.zeros(NB) for th in THETAS},
            "champions": [],  # (q, a, b, c) mit q > 1.0
        }

    print("Tripel-Scan c in [2^{}, {}] ...".format(args.kmin, cmax), flush=True)
    t1 = time.time()
    for c in range(2 ** args.kmin, cmax + 1):
        k = c.bit_length() - 1
        lo = 2 ** k
        width = 2 ** k  # Fensterbreite
        j = min(NB - 1, (c - lo) * NB // width)
        W = windows[k]

        a = np.arange(1, (c - 1) // 2 + 1, dtype=np.int64)
        cop = np.gcd(a, c) == 1
        if c % 2 == 0:
            pass  # a=c/2 ausgeschlossen via (c-1)//2; gerade c: gcd-Filter regelt Rest
        a = a[cop]
        if a.size == 0:
            continue
        b = c - a
        logr = lograd[a] + lograd[b] + lograd[c]
        q = math.log(c) / logr

        W["n"][j] += q.size
        W["sum_q"][j] += float(q.sum())
        W["sum_q2"][j] += float((q * q).sum())
        mq = float(q.max())
        if mq > W["max_q"][j]:
            W["max_q"][j] = mq
        for th in THETAS:
            exc = q - th
            mask = exc > 0
            nm = int(mask.sum())
            if nm:
                W["tail_n"][th][j] += nm
                W["tail_mass"][th][j] += float(exc[mask].sum())
                if th == 1.0:
                    for idx in np.nonzero(mask)[0]:
                        W["champions"].append(
                            (round(float(q[idx]), 5), int(a[idx]), int(b[idx]), int(c)))
        if c % 8192 == 0:
            print("  c={} ({:.1f}s)".format(c, time.time() - t1), flush=True)

    # Auswertung
    def r_param(vals):
        vals = np.asarray(vals, dtype=np.float64)
        m = vals.mean()
        if m == 0:
            return None
        return float(vals.var(ddof=1) / (m * m)) if vals.size > 1 else None

    report = {
        "date": today,
        "purpose": "B3 self-averaging diagnostic of abc quality (spin-glass analogy)",
        "cmax": cmax,
        "kmin": args.kmin,
        "kmax": kmax,
        "nblocks": NB,
        "thetas": THETAS,
        "windows": [],
    }
    for k in range(args.kmin, kmax + 1):
        W = windows[k]
        n_tot = int(W["n"].sum())
        if n_tot == 0:
            continue
        sum_q = float(W["sum_q"].sum())
        sum_q2 = float(W["sum_q2"].sum())
        mean_q = sum_q / n_tot
        var_q = max(sum_q2 / n_tot - mean_q ** 2, 0.0)
        # Block-Observablen
        valid = W["n"] > 0
        block_mean_q = W["sum_q"][valid] / W["n"][valid]
        entry = {
            "k": k,
            "c_range": [2 ** k, min(2 ** (k + 1) - 1, cmax)],
            "n_triples": n_tot,
            "mean_q": mean_q,
            "var_q": var_q,
            "R_q_triple": var_q / mean_q ** 2,
            "max_q": float(W["max_q"].max()),
            "R_q_block": r_param(block_mean_q),
            "tails": {},
        }
        for th in THETAS:
            tn = int(W["tail_n"][th].sum())
            tm = float(W["tail_mass"][th].sum())
            block_tailmass = W["tail_mass"][th][valid] / W["n"][valid]
            entry["tails"][str(th)] = {
                "tail_n": tn,
                "tail_fraction": tn / n_tot,
                "tail_mass_per_triple": tm / n_tot,
                "R_tailmass_block": r_param(block_tailmass),
            }
        entry["champions_q_gt_1"] = sorted(W["champions"], reverse=True)[:10]
        report["windows"].append(entry)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown-Tabelle
    lines = []
    lines.append("# B3 Self-Averaging-Diagnostik der abc-Qualität ({})".format(today))
    lines.append("")
    lines.append("Alle Tripel a+b=c, gcd(a,b)=1, c ≤ {}. q = log c / log rad(abc).".format(cmax))
    lines.append("Blöcke pro Dyade: {}. Script: `_scripts/abc_quality_self_averaging_probe.py`.".format(NB))
    lines.append("")
    lines.append("| k | c-Fenster | n | ⟨q⟩ | R_q (Tripel) | R_q (Block) | max q | p(q>0.9) | M₀.₈/n | R_M0.8 (Block) | R_M0.9 (Block) |")
    lines.append("|---|---|---:|---|---|---|---|---|---|---|---|")
    for e in report["windows"]:
        t08 = e["tails"]["0.8"]
        t09 = e["tails"]["0.9"]
        fmt = lambda x: ("{:.3g}".format(x) if x is not None else "—")
        lines.append("| {} | [{}, {}] | {} | {:.4f} | {:.3g} | {} | {:.3f} | {:.2e} | {:.2e} | {} | {} |".format(
            e["k"], e["c_range"][0], e["c_range"][1], e["n_triples"],
            e["mean_q"], e["R_q_triple"], fmt(e["R_q_block"]), e["max_q"],
            t09["tail_fraction"], t08["tail_mass_per_triple"],
            fmt(t08["R_tailmass_block"]), fmt(t09["R_tailmass_block"])))
    lines.append("")
    lines.append("Laufzeit: {:.1f}s. JSON: `{}`.".format(time.time() - t0, out_json))
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\nFertig ({:.1f}s). JSON: {}  MD: {}".format(time.time() - t0, out_json, out_md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
