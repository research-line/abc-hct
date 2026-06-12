"""EM-4: capacity obstruction for squarefree residual conductor drops.

The C3 data D_ell records whether ell divides v_p(Delta_min).  This script
compares that squarefree/divisor-memory capacity with the exponent mass
lost in abc -> rad(abc).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "_proof-notes" / "C3_capacity_obstruction.md"
OUT_JSON = ROOT / "_data" / "em4_c3_capacity_obstruction_2026-05-09.json"

TEST_ELLS = [3, 5, 7, 11, 13, 17, 19]


@dataclass(frozen=True)
class Triple:
    a: int
    b: int
    label: str

    @property
    def c(self) -> int:
        return self.a + self.b


TRIPLES = [
    Triple(2, 3**10 * 109, "Reyssat"),
    Triple(11**2, 3**2 * 5**6 * 7**3, "ABCHome_2"),
    Triple(1, 2 * 3**7, "classic_4374"),
    Triple(1, 2400, "classic_2401"),
    Triple(1, 8, "1+8=9"),
    Triple(1, 63, "1+63=64"),
    Triple(1, 80, "1+80=81"),
    Triple(5, 27, "5+27=32"),
    Triple(3, 125, "3+125=128"),
    Triple(13, 243, "13+243=256"),
    Triple(32, 49, "32+49=81"),
    Triple(1, 4374, "1+4374=4375_dup"),
    Triple(1, 2**12 - 1, "1+4095=4096"),
    Triple(625, 2048, "625+2048=2673"),
    Triple(1, 1023, "1+1023=1024"),
]


def factorize(n: int) -> dict[int, int]:
    n = abs(n)
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def rad_from_factors(factors: dict[int, int]) -> int:
    out = 1
    for p in factors:
        out *= p
    return out


def merge_factors(*items: dict[int, int]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for item in items:
        for p, e in item.items():
            merged[p] = merged.get(p, 0) + e
    return merged


def load_p2() -> dict[str, dict[str, int | str]]:
    path = ROOT / "_data" / "em1" / "pari_p2_results.jsonl"
    out: dict[str, dict[str, int | str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[row["label"]] = row
    return out


def v_l(n: int, ell: int) -> int:
    n = abs(n)
    count = 0
    while n and n % ell == 0:
        count += 1
        n //= ell
    return count


def analyze(t: Triple, p2_rows: dict[str, dict[str, int | str]]) -> dict[str, object]:
    fa, fb, fc = factorize(t.a), factorize(t.b), factorize(t.c)
    fabc = merge_factors(fa, fb, fc)
    rad_abc = rad_from_factors(fabc)
    abc = abs(t.a * t.b * t.c)
    quality = math.log(t.c) / math.log(rad_abc)
    c_defect = math.log(t.c / rad_abc)
    exponent_excess = math.log(abc / rad_abc)

    p2 = p2_rows.get(t.label)
    if p2 is None and t.label == "1+4374=4375_dup":
        p2 = p2_rows.get("1+4374=4375_dup")
    if p2 is None:
        raise KeyError(f"missing p2 row for {t.label}")

    n_cond = int(p2["N_cond"])
    ncond_primes = set(factorize(n_cond))

    delta_v: dict[int, int] = {}
    for p in ncond_primes:
        if p == 2:
            delta_v[p] = int(p2["v2_Delta_min"])
        else:
            delta_v[p] = 2 * fabc.get(p, 0)

    drop_by_ell: dict[int, list[int]] = {}
    squarefree_capacity = 0.0
    valuation_weighted_capacity = 0.0
    union: set[int] = set()
    for ell in TEST_ELLS:
        primes = sorted(p for p, v in delta_v.items() if v > 0 and v % ell == 0)
        drop_by_ell[ell] = primes
        union.update(primes)
        d_ell = math.prod(primes) if primes else 1
        squarefree_capacity += math.log(d_ell)
        for p in primes:
            valuation_weighted_capacity += v_l(delta_v[p], ell) * math.log(p)

    union_capacity = math.log(math.prod(union)) if union else 0.0

    return {
        "label": t.label,
        "a": t.a,
        "b": t.b,
        "c": t.c,
        "quality": quality,
        "rad_abc": rad_abc,
        "N_cond": n_cond,
        "c_defect_log_c_over_rad": c_defect,
        "exponent_excess_log_abc_over_rad": exponent_excess,
        "delta_v": delta_v,
        "drop_by_ell": drop_by_ell,
        "drop_union": sorted(union),
        "union_capacity": union_capacity,
        "squarefree_capacity": squarefree_capacity,
        "valuation_weighted_capacity": valuation_weighted_capacity,
        "squarefree_over_c_defect": (
            squarefree_capacity / c_defect if c_defect > 0 else None
        ),
        "squarefree_over_exponent_excess": (
            squarefree_capacity / exponent_excess if exponent_excess > 0 else None
        ),
        "weighted_over_exponent_excess": (
            valuation_weighted_capacity / exponent_excess
            if exponent_excess > 0
            else None
        ),
    }


def fmt(x: object, digits: int = 3) -> str:
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    return str(x)


def write_report(rows: list[dict[str, object]]) -> None:
    champions = [r for r in rows if float(r["quality"]) >= 1.45]
    lines: list[str] = []
    lines.append("# C3-Kapazitätsobstruktion")
    lines.append("")
    lines.append("**Datum:** 2026-05-09")
    lines.append("**Status:** EM-4 / G1-Präzisierung nach EM-3a-Nullbefund.")
    lines.append("")
    lines.append("## Aussage")
    lines.append("")
    lines.append(
        "Die residualen Führer-Drops `D_ell` speichern für eine Primstelle `p` "
        "nur, ob `ell | v_p(Delta_min)` gilt. Für Frey-Kurven an ungeraden "
        "Primstellen gilt `v_p(Delta_min)=2e_p`. Damit ist der C3-Kanal ein "
        "Divisor-/Paritätsgedächtnis der Exponenten, nicht das Exponentengedächtnis "
        "`e_p log p` selbst."
    )
    lines.append("")
    lines.append("Formal:")
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\sum_{\\ell\\in S}\\log D_\\ell="
        "\\sum_{p\\mid N}\\#\\{\\ell\\in S:\\ell\\mid v_p(\\Delta_{\\min})\\}\\log p."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Für einen einzelnen hohen Exponenten `e` wächst der rechte Faktor nur "
        "wie die Anzahl verschiedener Primteiler von `2e`, also divisorisch, "
        "während der verlorene abc-Exponent linear wie `(e-1)log p` wächst."
    )
    lines.append("")
    lines.append("## Datencheck")
    lines.append("")
    lines.append(
        "`C3 cap` ist hier `sum_{ell in {3,5,7,11,13,17,19}} log D_ell`; "
        "`C-defect` ist `log(c/rad(abc))`; `Exp-excess` ist `log(abc/rad(abc))`."
    )
    lines.append(
        "Die p=2-Beiträge werden dabei bewusst großzügig als "
        "`ell | v_2(Delta_min)` mitgezählt. Bei additiver Reduktion ist das kein "
        "voller Ribet-Level-Lowering-Satz; als Kapazitätsabschätzung ist es also "
        "eher eine obere Schranke zugunsten von C3."
    )
    lines.append("")
    lines.append(
        "| Tripel | q | Ncond | C-defect | Exp-excess | C3 cap | "
        "C3/C-defect | C3/Exp-excess | Drop-Union |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for r in sorted(rows, key=lambda item: -float(item["quality"])):
        lines.append(
            f"| {r['label']} | {fmt(r['quality'])} | {r['N_cond']} | "
            f"{fmt(r['c_defect_log_c_over_rad'])} | "
            f"{fmt(r['exponent_excess_log_abc_over_rad'])} | "
            f"{fmt(r['squarefree_capacity'])} | "
            f"{fmt(r['squarefree_over_c_defect'])} | "
            f"{fmt(r['squarefree_over_exponent_excess'])} | "
            f"{','.join(str(p) for p in r['drop_union']) or '-'} |"
        )
    lines.append("")
    lines.append("## Champion-Befund")
    lines.append("")
    for r in champions:
        lines.append(
            f"- `{r['label']}`: C3 cap/C-defect = "
            f"{fmt(r['squarefree_over_c_defect'])}, C3 cap/Exp-excess = "
            f"{fmt(r['squarefree_over_exponent_excess'])}."
        )
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "**Proposition (C3-Unterkapazität).** Für eine Familie mit einer Primstelle "
        "`p^e || abc` und `e -> infinity`, aber `omega(2e)=o(e)`, gilt"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\frac{\\sum_{\\ell\\in S}\\log D_\\ell}"
        "{(e-1)\\log p}\\leq \\frac{\\omega_S(2e)}{e-1}\\to 0"
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "für jedes feste oder langsam wachsende Set kleiner Primzahlen `S`. "
        "Squarefree C3 sieht also höchstens die Divisorentropie von `e`, nicht die "
        "lineare Exponententiefe."
    )
    lines.append("")
    lines.append(
        "C3 in der squarefree Level-Lowering-Form kann den verlorenen Exponenteninhalt "
        "nicht tragen. Das schließt nicht G1, aber es schließt die schwache Route "
        "`viele D_ell-Loci allein erzwingen abc`."
    )
    lines.append("")
    lines.append(
        "Ein verbleibender G1-Satz muss daher mindestens eines der folgenden Dinge tun:"
    )
    lines.append("")
    lines.append("- echte Hecke-Maximalideale/Kongruenzquotienten mit Längen statt bloßer Unterstützung kontrollieren;")
    lines.append("- eine depth-sensitive lokale Größe verwenden, die mehr als `rad(v_p(Delta))` sieht;")
    lines.append("- oder eine neue Anti-Konzentrationsaussage beweisen, die nicht aus C3 allein folgt.")
    lines.append("")
    lines.append("**Kurzurteil:** C3 ist ein Wegweiser, kein Bezahlkanal für den abc-Defekt.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p2 = load_p2()
    rows = [analyze(t, p2) for t in TRIPLES]
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(rows)
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
