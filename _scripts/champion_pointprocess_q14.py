#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3-Erweiterung: Punktprozess-Analyse der q>=1.4-Champions (de-Smit-Liste).

Quelle: pub.math.leidenuniv.nl/~smitbde/abc/?set=2 (Stand 2019-03-02,
lokal: _sources/abc_smitbde_set2_goodtriples_2019.html). 241 bekannte
Tripel mit q > 1.4. VOLLSTAENDIGKEIT: bis c < 10^20 (size <= 20) per
ABC@Home + Demeyer-2007-Lauf garantiert; darueber nur bekannte Funde
(zensiert) -> Analyse trennt die Bereiche.

Fragen (Extremwert-Seite der B3-Self-Averaging-Diagnostik):
 1. Waechst die Champion-Zahl pro c-Dekade noch, oder klingt sie ab?
    (abc impliziert: insgesamt endlich viele mit q >= 1.4.)
 2. Wie schwer ist der Exzess-Tail X = q - 1.4? Hill-Tail-Index;
    Top-1-Dominanz der Dekaden-Masse (non-self-averaging-Signatur).
 3. max-q-Trend ueber 20 Dekaden (vgl. B3: trendlos 1.27-1.57 bis c~1.3e5).
"""

import json
import re
import sys
import math
from datetime import date

SRC = "_sources/abc_smitbde_set2_goodtriples_2019.html"
OUT_JSON = "_results/champion_pointprocess_q14_2026-06-10.json"
OUT_MD = "_results/champion_pointprocess_q14_2026-06-10.md"
COMPLETE_SIZE = 20.0  # Vollstaendigkeit bis 20 Stellen (Demeyer 2007 / ABC@Home)
THETA = 1.4


def parse(html):
    # Zeilen: <tr><td>  1<td>1.6299<td>6.81<td>8.64<td ... (by/on-Felder variieren)
    pat = re.compile(r"<tr><td>\s*(\d+)<td>([\d.]+)<td>([\d.]+)<td>([\d.]+)<td")
    rows = []
    for m in pat.finditer(html):
        rows.append({
            "rank": int(m.group(1)),
            "q": float(m.group(2)),
            "size": float(m.group(3)),   # log10(c)
            "merit": float(m.group(4)),
        })
    return rows


def hill_index(excesses, k):
    """Hill-Schaetzer des Tail-Index alpha ueber die k groessten Exzesse."""
    xs = sorted(excesses, reverse=True)[: k + 1]
    if len(xs) < k + 1 or xs[k] <= 0:
        return None
    logs = [math.log(xs[i] / xs[k]) for i in range(k)]
    return k / sum(logs)


def main():
    html = open(SRC, encoding="utf-8", errors="replace").read()
    rows = parse(html)
    n_all = len(rows)
    complete = [r for r in rows if r["size"] <= COMPLETE_SIZE]
    censored = [r for r in rows if r["size"] > COMPLETE_SIZE]
    print("geparst: {} Tripel; vollstaendiger Bereich size<=20: {}; zensiert: {}".format(
        n_all, len(complete), len(censored)))

    # Dekaden-Statistik im vollstaendigen Bereich
    decades = {}
    for r in complete:
        d = int(math.floor(r["size"]))  # c hat d+1 Stellen; size in [d, d+1)
        e = r["q"] - THETA
        decades.setdefault(d, []).append((r["q"], e))
    dec_stats = []
    for d in sorted(decades):
        qs = [q for q, _ in decades[d]]
        es = [e for _, e in decades[d]]
        m = sum(es)
        dec_stats.append({
            "decade_log10c": [d, d + 1],
            "n": len(qs),
            "max_q": max(qs),
            "excess_mass": m,
            "top1_share": (max(es) / m) if m > 0 else None,
        })

    # Hill-Tail-Index der Exzesse (vollstaendiger Bereich)
    excesses = [r["q"] - THETA for r in complete]
    hill = {str(k): hill_index(excesses, k) for k in (20, 50, 100, 150)}

    # Kumulative Zaehlung N(<=size) zur Wachstumsfrage
    sizes = sorted(r["size"] for r in complete)
    cum = [(s, i + 1) for i, s in enumerate(sizes)]

    report = {
        "date": str(date.today()),
        "source": "de Smit set=2 (2019-03-02), " + SRC,
        "theta": THETA,
        "complete_up_to_size": COMPLETE_SIZE,
        "n_total_listed": n_all,
        "n_complete_region": len(complete),
        "n_censored_region": len(censored),
        "decade_stats_complete": dec_stats,
        "hill_tail_index_excess": hill,
        "max_q_overall": max(r["q"] for r in rows),
        "cumulative_count_complete": cum[::20] + [cum[-1]],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = ["# Champion-Punktprozess q>=1.4 (de-Smit-Liste, 2026-06-10)", ""]
    lines.append("Quelle: `{}` (Stand 2019-03-02). {} Tripel gelistet, davon {} im".format(
        SRC, n_all, len(complete)))
    lines.append("VOLLSTAENDIGEN Bereich c < 10^20 (ABC@Home + Demeyer 2007); {} zensiert (>20 Stellen).".format(
        len(censored)))
    lines.append("")
    lines.append("| Dekade (log10 c) | N | max q | Exzessmasse Σ(q−1.4) | Top-1-Anteil |")
    lines.append("|---|---:|---|---|---|")
    for s in dec_stats:
        lines.append("| [{}, {}) | {} | {:.4f} | {:.4f} | {} |".format(
            s["decade_log10c"][0], s["decade_log10c"][1], s["n"], s["max_q"],
            s["excess_mass"],
            "{:.2f}".format(s["top1_share"]) if s["top1_share"] is not None else "—"))
    lines.append("")
    lines.append("Hill-Tail-Index des Exzesses X=q−1.4 (vollst. Bereich): " +
                 ", ".join("k={}: {}".format(k, "{:.2f}".format(v) if v else "—")
                           for k, v in hill.items()))
    lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
