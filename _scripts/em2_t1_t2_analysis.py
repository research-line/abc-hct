"""EM-2 root-number analysis after the Reyssat orientation audit.

Run from the project root:
    python _scripts/em2_t1_t2_analysis.py

Outputs a compact Markdown report with:
- T1: preregistered Fisher exact test on EM-1 Frey triples
- T2: descriptive N=240672 isogeny-class baseline
"""

from __future__ import annotations

import json
import math
from datetime import date
from fractions import Fraction
from math import comb
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
EM1 = PROJECT / "_data" / "em1" / "pari_p2_results.jsonl"
OUT = PROJECT / "_results" / f"em2_t1_t2_results_{date.today().isoformat()}.md"


def q_value(row: dict) -> float:
    n_rad = radical(abs(row["a"] * row["b"] * row["c"]))
    return math.log(row["c"]) / math.log(n_rad)


def radical(n: int) -> int:
    out = 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            out *= d
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out *= n
    return out


def load_em1() -> list[dict]:
    rows = []
    for line in EM1.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["q"] = q_value(row)
        rows.append(row)
    return rows


def dedup_triples(rows: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        key = (row["a"], row["b"], row["c"], row["N_cond"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def fisher_one_sided_greater(a: int, b: int, c: int, d: int) -> Fraction:
    """P(X >= a) for table [[a,b],[c,d]] under fixed margins."""
    row1 = a + b
    row2 = c + d
    col1 = a + c
    total = row1 + row2
    max_x = min(row1, col1)
    denom = comb(total, row1)
    num = 0
    for x in range(a, max_x + 1):
        num += comb(col1, x) * comb(total - col1, row1 - x)
    return Fraction(num, denom)


def t1(rows: list[dict]) -> dict:
    champion = [r for r in rows if r["q"] >= 1.5]
    controls = [r for r in rows if r["q"] < 1.3]
    champ_neg = sum(1 for r in champion if int(r["root_number"]) == -1)
    champ_pos = sum(1 for r in champion if int(r["root_number"]) == 1)
    ctrl_neg = sum(1 for r in controls if int(r["root_number"]) == -1)
    ctrl_pos = sum(1 for r in controls if int(r["root_number"]) == 1)
    p = fisher_one_sided_greater(champ_neg, champ_pos, ctrl_neg, ctrl_pos)
    return {
        "champion": champion,
        "controls": controls,
        "table": (champ_neg, champ_pos, ctrl_neg, ctrl_pos),
        "p": p,
    }


def t2() -> dict:
    # From _proof-notes/EM-2_root_number_audit.md and LMFDB single-label checks.
    signs = {
        "240672.a": +1,
        "240672.b": -1,
        "240672.c": +1,
        "240672.d": +1,
        "240672.e": -1,
        "240672.f": -1,
        "240672.g": -1,  # original Reyssat class, represented by 240672.g3
        "240672.h": +1,
    }
    excluded = "240672.g"
    controls = {k: v for k, v in signs.items() if k != excluded}
    return {"signs": signs, "excluded": excluded, "controls": controls}


def write_report(rows: list[dict], t1_result: dict, t2_result: dict) -> None:
    a, b, c, d = t1_result["table"]
    p = t1_result["p"]
    lines = [
        "# EM-2 T1/T2 Results",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Audit status: root-number convention cleared. Original Reyssat orientation "
        "`E_{2,6436341}` is `240672.g3` with global `w(E)=-1`; swapped orientation "
        "`E_{6436341,2}` is `240672.c3` with global `w(E)=+1`, rank 0, Sha 361.",
        "",
        "## T1: Preregistered Frey-Sample Test",
        "",
        "Table: `Champion(q>=1.5)` x `w(E)=-1` against `Non-champion(q<1.3)`.",
        "",
        "| Group | w=-1 | w=+1 | n |",
        "|---|---:|---:|---:|",
        f"| Champions | {a} | {b} | {a + b} |",
        f"| Non-champions | {c} | {d} | {c + d} |",
        "",
        f"One-sided Fisher exact p-value: `{float(p):.4f}` (`{p.numerator}/{p.denominator}`).",
        "",
        "Conclusion: no significant EM-2 signal in this small preregistered sample.",
        "",
        "Champion rows:",
        "",
        "| Label | a | b | c | q | N_cond | w(E) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in t1_result["champion"]:
        lines.append(
            f"| {row['label']} | {row['a']} | {row['b']} | {row['c']} | "
            f"{row['q']:.3f} | {row['N_cond']} | {row['root_number']:+d} |"
        )
    lines.extend(
        [
            "",
            "## T2: Exact-Conductor Baseline at N=240672",
            "",
            "Effective unit: LMFDB isogeny class. The original Reyssat class `240672.g` "
            "is excluded from the control denominator.",
            "",
            "| Class set | w=-1 | w=+1 | total |",
            "|---|---:|---:|---:|",
        ]
    )
    all_signs = t2_result["signs"]
    controls = t2_result["controls"]
    all_neg = sum(1 for value in all_signs.values() if value == -1)
    all_pos = sum(1 for value in all_signs.values() if value == +1)
    ctrl_neg = sum(1 for value in controls.values() if value == -1)
    ctrl_pos = sum(1 for value in controls.values() if value == +1)
    lines.append(f"| All N=240672 classes | {all_neg} | {all_pos} | {len(all_signs)} |")
    lines.append(f"| Excluding Reyssat class `240672.g` | {ctrl_neg} | {ctrl_pos} | {len(controls)} |")
    lines.extend(
        [
            "",
            "Class signs:",
            "",
            "| Isogeny class | global w(E) |",
            "|---|---:|",
        ]
    )
    for label, sign in sorted(all_signs.items()):
        mark = " (Reyssat original)" if label == "240672.g" else ""
        lines.append(f"| {label}{mark} | {sign:+d} |")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = dedup_triples(load_em1())
    result_t1 = t1(rows)
    result_t2 = t2()
    write_report(rows, result_t1, result_t2)
    a, b, c, d = result_t1["table"]
    print(f"T1 table: champions [-,+]=[{a},{b}], controls [-,+]=[{c},{d}]")
    print(f"T1 one-sided Fisher p={float(result_t1['p']):.4f}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
