"""Loop 72 Tamagawa/Sha exponent budget for Frey quotient control.

For a Frey curve E_{a,b}: y^2=x(x-a)(x+b), odd bad primes are semistable.
If p|abc is odd and e=v_p(abc), then v_p(Delta_min)=2e and the local
Tamagawa number is at most 2e (split multiplicative gives equality, nonsplit
is <=2).  The 2-adic place is absorbed by a coarse logarithmic envelope.

This script compares the radical defect c/rad(abc) with a divisor-type
Tamagawa envelope.  The point is not to compute exact Tamagawa numbers, but to
make the exponent bookkeeping visible: Tamagawa is local/divisor-like, while
the abc defect is prime-weighted.  Therefore Goldfeld-Szpiro/Sha is the real
algebraic quotient route once the central L-value is separated.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
EM1_JSONL = ROOT / "_data" / "em1" / "pari_p2_results.jsonl"
WATKINS_CSV = ROOT / "numerics" / "watkins_v3_final_a+b80.csv"
JSON_OUT = ROOT / "_data" / f"anc_tamagawa_sha_budget_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_tamagawa_sha_budget.md"


@dataclass(frozen=True)
class BudgetRow:
    source: str
    label: str
    a: int
    b: int
    c: int
    rad_abc: int
    n_cond: int | None
    quality: float
    factor_count: int
    max_exponent: int
    exponent_product: int
    divisor_count_abc: int
    tamagawa_envelope: int
    c_over_rad: float
    defect_exp_rad: float
    tamagawa_exp_rad: float
    tau_exp_rad: float
    tamagawa_to_defect_ratio: float | None


def parse_number(text: str) -> float:
    value = text.strip()
    if "/" in value:
        num, den = value.split("/", 1)
        return float(Decimal(num) / Decimal(den))
    return float(Decimal(value))


def factorize(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    value = abs(n)
    d = 2
    while d * d <= value:
        while value % d == 0:
            factors[d] = factors.get(d, 0) + 1
            value //= d
        d += 1 if d == 2 else 2
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def merge_factors(*parts: int) -> dict[int, int]:
    merged: dict[int, int] = {}
    for part in parts:
        for prime, exponent in factorize(part).items():
            merged[prime] = merged.get(prime, 0) + exponent
    return merged


def radical(factors: dict[int, int]) -> int:
    result = 1
    for prime in factors:
        result *= prime
    return result


def divisor_count(factors: dict[int, int]) -> int:
    result = 1
    for exponent in factors.values():
        result *= exponent + 1
    return result


def tamagawa_envelope(factors: dict[int, int]) -> int:
    result = 1
    for prime, exponent in factors.items():
        if prime == 2:
            result *= max(16, 2 * exponent)
        else:
            result *= max(2, 2 * exponent)
    return result


def exponent_product(factors: dict[int, int]) -> int:
    result = 1
    for exponent in factors.values():
        result *= max(1, exponent)
    return result


def safe_log_exponent(value: float, base: int) -> float:
    if value <= 0 or base <= 1:
        return float("nan")
    return math.log(value) / math.log(base)


def build_row(source: str, label: str, a: int, b: int, c: int, n_cond: int | None) -> BudgetRow:
    factors = merge_factors(a, b, c)
    rad_abc = radical(factors)
    log_rad = math.log(rad_abc)
    c_over_rad = c / rad_abc
    defect_exp = max(0.0, math.log(c_over_rad) / log_rad)
    envelope = tamagawa_envelope(factors)
    tam_exp = safe_log_exponent(envelope, rad_abc)
    tau = divisor_count(factors)
    tau_exp = safe_log_exponent(tau, rad_abc)
    ratio = tam_exp / defect_exp if defect_exp > 0 else None
    return BudgetRow(
        source=source,
        label=label,
        a=a,
        b=b,
        c=c,
        rad_abc=rad_abc,
        n_cond=n_cond,
        quality=math.log(c) / log_rad,
        factor_count=len(factors),
        max_exponent=max(factors.values()),
        exponent_product=exponent_product(factors),
        divisor_count_abc=tau,
        tamagawa_envelope=envelope,
        c_over_rad=c_over_rad,
        defect_exp_rad=defect_exp,
        tamagawa_exp_rad=tam_exp,
        tau_exp_rad=tau_exp,
        tamagawa_to_defect_ratio=ratio,
    )


def load_em1_rows() -> list[BudgetRow]:
    rows: list[BudgetRow] = []
    for line in EM1_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        a = int(item["a"])
        b = int(item["b"])
        c = int(item["c"])
        rows.append(build_row("em1", str(item["label"]), a, b, c, int(item["N_cond"])))
    return rows


def load_watkins_rows() -> list[BudgetRow]:
    rows: list[BudgetRow] = []
    with WATKINS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            a = int(item["a"])
            b = int(item["b"])
            c = int(item["c"])
            rows.append(build_row("watkins_a+b80", f"({a},{b},{c})", a, b, c, int(item["N"])))
    return rows


def summarize(rows: list[BudgetRow]) -> dict[str, float | int]:
    defect_rows = [row for row in rows if row.defect_exp_rad > 0]
    ratios = [row.tamagawa_to_defect_ratio for row in defect_rows if row.tamagawa_to_defect_ratio is not None]
    return {
        "row_count": len(rows),
        "rows_with_c_over_rad_gt_1": len(defect_rows),
        "quality_max": max(row.quality for row in rows),
        "defect_exp_max": max(row.defect_exp_rad for row in rows),
        "tamagawa_exp_median": median(row.tamagawa_exp_rad for row in rows),
        "tamagawa_exp_mean": mean(row.tamagawa_exp_rad for row in rows),
        "tamagawa_exp_max": max(row.tamagawa_exp_rad for row in rows),
        "tau_exp_max": max(row.tau_exp_rad for row in rows),
        "ratio_median": median(ratios) if ratios else 0.0,
        "ratio_max": max(ratios) if ratios else 0.0,
    }


def top(rows: list[BudgetRow], key: str, count: int = 10, reverse: bool = True) -> list[dict[str, object]]:
    return [asdict(row) for row in sorted(rows, key=lambda row: getattr(row, key), reverse=reverse)[:count]]


def build_payload(em1_rows: list[BudgetRow], watkins_rows: list[BudgetRow]) -> dict[str, object]:
    all_rows = em1_rows + watkins_rows
    return {
        "date": DATE,
        "purpose": "Separate divisor-type Tamagawa growth from Sha/central-value quotient control.",
        "local_envelope": "odd p: c_p <= 2*v_p(abc); p=2: coarse max(16,2*v_2(abc)) envelope",
        "summaries": {
            "em1": summarize(em1_rows),
            "watkins_a+b80": summarize(watkins_rows),
            "all": summarize(all_rows),
        },
        "em1_by_quality": [asdict(row) for row in sorted(em1_rows, key=lambda row: row.quality, reverse=True)],
        "top_defect": top(all_rows, "defect_exp_rad"),
        "top_tamagawa_envelope": top(all_rows, "tamagawa_exp_rad"),
        "top_ratio": [
            asdict(row)
            for row in sorted(
                [row for row in all_rows if row.tamagawa_to_defect_ratio is not None],
                key=lambda row: row.tamagawa_to_defect_ratio or 0.0,
                reverse=True,
            )[:10]
        ],
    }


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def fmt_ratio(value: object) -> str:
    if value is None:
        return "-"
    return fmt(float(value))


def table_row(item: dict[str, object]) -> str:
    return (
        f"| {item['label']} | {fmt(float(item['quality']))} | "
        f"{fmt(float(item['c_over_rad']))} | {fmt(float(item['defect_exp_rad']))} | "
        f"{int(item['tamagawa_envelope'])} | {fmt(float(item['tamagawa_exp_rad']))} | "
        f"{fmt_ratio(item['tamagawa_to_defect_ratio'])} |"
    )


def build_report(payload: dict[str, object]) -> str:
    summaries = payload["summaries"]
    assert isinstance(summaries, dict)
    em1 = summaries["em1"]
    all_summary = summaries["all"]
    assert isinstance(em1, dict) and isinstance(all_summary, dict)

    lines: list[str] = []
    lines.append("# ANC+ Tamagawa-Sha-Budget")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 72 / Goldfeld-Szpiro/Sha-Route nach Modulargrad und Periodenfläche.")
    lines.append("")
    lines.append("## Ziel")
    lines.append("")
    lines.append(
        "Diese Notiz trennt den algebraischen BSD-Quotienten "
        "\\(A_E=L(E,1)/\\Omega_E\\) in Tamagawa-, Torsions- und Sha-Anteile. "
        "Der Anlass ist eine Präzisierung der Goldfeld-Szpiro/Sha-Route: "
        "Tamagawa-Faktoren sind bei Frey-Kurven nur divisor-artig und tragen "
        "nicht den prime-gewichteten abc-Defekt. Der harte algebraische Anteil "
        "ist daher Sha, gekoppelt mit einer zentralen Nichtverschwindens- oder "
        "Anti-Konzentrationsaussage."
    )
    lines.append("")
    lines.append("## Lokale Hülle")
    lines.append("")
    lines.append(
        "Für \\(E_{a,b}:y^2=x(x-a)(x+b)\\) und ungerades \\(p\\mid abc\\) ist die "
        "Reduktion semistabil. Schreibt man \\(e=v_p(abc)\\), dann gilt "
        "\\(v_p(\\Delta_{\\min})=2e\\) und der Tamagawa-Faktor erfüllt grob"
    )
    lines.append("")
    lines.append("$$")
    lines.append("c_p\\le 2e.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Split-multiplikativ erreicht diese Hülle, nonsplit-multiplikativ ist "
        "kleiner. Die 2-adische Stelle wird im Ledger konservativ durch "
        "\\(\\max(16,2v_2(abc))\\) absorbiert; eine einzelne solche Stelle kann "
        "keinen festen abc-Exponenten tragen."
    )
    lines.append("")
    lines.append("Damit ist")
    lines.append("")
    lines.append("$$")
    lines.append("\\prod_p c_p \\le C_2\\prod_{p\\mid abc}(2v_p(abc)+O(1)),")
    lines.append("$$")
    lines.append("")
    lines.append(
        "also ein Divisor-/Exponentenprodukt, nicht der Radikaldefekt "
        "\\(abc/\\operatorname{rad}(abc)\\) und auch nicht \\(c/\\operatorname{rad}(abc)\\). "
        "Für jede feste Qualitäts-Skala \\(c\\le N^Q\\) ist dieser Faktor "
        "\\(N^{o(1)}\\)."
    )
    lines.append("")
    lines.append("## Ledger-Befund")
    lines.append("")
    lines.append(
        f"EM-1: maximale Qualität {fmt(float(em1['quality_max']))}, maximaler "
        f"Radikaldefekt-Exponent {fmt(float(em1['defect_exp_max']))}, maximale "
        f"Tamagawa-Hüllen-Exponent {fmt(float(em1['tamagawa_exp_max']))}."
    )
    lines.append("")
    lines.append(
        f"Gesamtledger: {int(all_summary['row_count'])} Zeilen; maximale "
        f"Tamagawa-Hüllen-Exponent {fmt(float(all_summary['tamagawa_exp_max']))}, "
        f"maximaler Divisorfunktions-Exponent {fmt(float(all_summary['tau_exp_max']))}. "
        "Diese Maxima liegen in kleinen, sehr glatten Beispielen und werden von "
        "der bewusst groben Hülle verstärkt; sie sind kein Signal für eine "
        "prime-gewichtete Defektzahlung."
    )
    lines.append("")
    lines.append(
        "Wichtig: Das Ledger soll nicht zeigen, dass Tamagawa in jedem kleinen "
        "Beispiel numerisch klein ist. Split-multiplikative kleine Primzahlen "
        "können sichtbare Faktoren erzeugen. Der Punkt ist strukturell: "
        "\\(\\prod e_p\\) ist exponenten-/divisorartig, während der Frey-Defekt "
        "\\(\\prod p^{e_p-1}\\) prime-gewichtet ist. In der für ANC+ relevanten "
        "Orientierung kann Tamagawa zusätzlich deutlich kleiner sein, wie die "
        "Reyssat-Orientierungsdiagnose zeigt."
    )
    lines.append("")
    lines.append("EM-1 nach Qualität:")
    lines.append("")
    lines.append("| Tripel | q | c/rad | Defekt-Exp. | Tam-Hülle | Tam-Exp. | Tam/Defekt |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    em1_rows = payload["em1_by_quality"]
    assert isinstance(em1_rows, list)
    for item in em1_rows:
        assert isinstance(item, dict)
        lines.append(table_row(item))
    lines.append("")
    lines.append("## Exponentenbudget")
    lines.append("")
    lines.append(
        "Unter BSD im Rang-0-Fall gilt"
    )
    lines.append("")
    lines.append("$$")
    lines.append("A_E=\\frac{L(E,1)}{\\Omega_E}=\\frac{|\\Sha(E)|\\prod_p c_p}{|E(\\mathbb Q)_{\\rm tors}|^2}.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Mazurs Torsionssatz macht den Nenner konstant beschränkt; die obige "
        "Tamagawa-Hülle ist für feste Qualitäts-Skala \\(N^{o(1)}\\). Also ist "
        "Quotientenkontrolle im exponentiellen Sinn, bis auf diesen "
        "divisorartigen Faktor, gleichbedeutend mit Sha-Kontrolle:"
    )
    lines.append("")
    lines.append("$$")
    lines.append("A_E\\le N^{\\sigma+o(1)}\\quad\\Longleftrightarrow\\quad |\\Sha(E)|\\le N^{\\sigma+o(1)}.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Wenn zusätzlich eine zentrale Untergrenze \\(L(E,1)\\ge N^{-\\alpha-o(1)}\\) "
        "vorliegt, folgt"
    )
    lines.append("")
    lines.append("$$")
    lines.append("\\Omega_E=\\frac{L(E,1)}{A_E}\\ge N^{-(\\alpha+\\sigma)-o(1)}.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Die Perioden-/abc-Schwelle verlangt \\(\\alpha+\\sigma\\le 1/2\\). "
        "Daraus ergeben sich zwei saubere Lesarten:"
    )
    lines.append("")
    lines.append("1. Goldfeld-Szpiro \\(\\sigma=1/2\\) reicht nur mit subpolynomieller zentraler Untergrenze \\(\\alpha=0\\).")
    lines.append("2. Die schwächere zentrale ANC-Skala \\(L(E,1)\\ge N^{-1/2-o(1)}\\) reicht nur mit subpolynomieller Sha-/Quotientenkontrolle \\(\\sigma=0\\).")
    lines.append("")
    lines.append("## Schluss")
    lines.append("")
    lines.append(
        "Die Goldfeld-Szpiro/Sha-Route ist keine Tamagawa-Route. Tamagawa ist "
        "diagnostisch wichtig, aber asymptotisch zu dünn, um den prime-gewichteten "
        "Frey-Defekt allein zu bezahlen. Offen bleibt genau eine gekoppelte Aussage: "
        "entweder Goldfeld-Szpiro plus eine sehr starke zentrale "
        "Nichtverschwindensschranke, oder zentrale Anti-Konzentration plus "
        "subpolynomielle Sha-Kontrolle. "
        "Ohne diese Kopplung ist der algebraische Quotient nur eine Umbenennung "
        "der Periodenlücke."
    )
    lines.append("")
    lines.append("## Quellenanker")
    lines.append("")
    lines.append(
        "- Goldfeld-Szpiro (1995), "
        "https://numdam.org/item/CM_1995__97_1-2_71_0/ : formulieren die "
        "\\(|\\Sha|\\ll N^{1/2+\\varepsilon}\\)-Schranke und zeigen die "
        "BSD-bedingte Verbindung zur Szpiro-Diskriminantenschranke."
    )
    lines.append(
        "- De Weger (1998), "
        "https://math.deweger.net/papers/%5B25%5DdW-ABCSha-QuJMathOxf%5B1998%5D.pdf : "
        "zeigt bedingt Beispiele mit \\(|\\Sha|\\) im Wesentlichen von der "
        "Größe \\(N^{1/2}\\), darunter Frey-/abc-nahe Beispiele; die "
        "Goldfeld-Szpiro-Skala ist daher scharf."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_tamagawa_sha_budget.py`")
    lines.append(f"- `_data/anc_tamagawa_sha_budget_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    em1_rows = load_em1_rows()
    watkins_rows = load_watkins_rows()
    payload = build_payload(em1_rows, watkins_rows)
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    MD_OUT.write_text(build_report(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
