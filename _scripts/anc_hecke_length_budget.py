"""Loop 73: budget test for ordinary Hecke/congruence lengths.

The remaining P7/G1 route asks whether depth-sensitive Hecke ideals can
remember the exponent mass lost in abc -> rad(abc).  Standard local
congruence/Tamagawa factors attached to Frey curves are expected to see
v_p(Delta_min), hence logarithmic length in the exponent e=v_p(abc), not
the prime-weighted mass (e-1)log(p).  This script makes that bookkeeping
explicit on the EM-1 test set and records the asymptotic obstruction.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
EM1_JSONL = ROOT / "_data" / "em1" / "pari_p2_results.jsonl"
JSON_OUT = ROOT / "_data" / f"anc_hecke_length_budget_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_hecke_length_obstruction.md"

TEST_ELLS = (3, 5, 7, 11, 13, 17, 19)


@dataclass(frozen=True)
class LengthRow:
    label: str
    a: int
    b: int
    c: int
    rad_abc: int
    n_cond: int
    quality: float
    c_defect_log: float
    exponent_excess_log: float
    support_pweighted_cap: float
    valuation_pweighted_cap: float
    ordinary_log_length_cap: float
    support_over_excess: float | None
    valuation_pweighted_over_excess: float | None
    ordinary_length_over_excess: float | None
    max_prime: int
    max_exponent: int
    max_single_loss: float
    max_single_ordinary_ratio: float | None
    delta_v: dict[int, int]


def factorize(n: int) -> dict[int, int]:
    value = abs(n)
    factors: dict[int, int] = {}
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


def v_l(n: int, ell: int) -> int:
    count = 0
    value = abs(n)
    while value and value % ell == 0:
        count += 1
        value //= ell
    return count


def ratio(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def load_em1() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in EM1_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def delta_profile(row: dict[str, object], abc_factors: dict[int, int]) -> dict[int, int]:
    """Use the measured p=2 value and the Frey semistable formula at odd p."""
    primes = set(factorize(int(row["N_cond"])))
    profile: dict[int, int] = {}
    for prime in sorted(primes):
        if prime == 2:
            profile[prime] = int(row["v2_Delta_min"])
        else:
            profile[prime] = 2 * abc_factors.get(prime, 0)
    return profile


def analyze(row: dict[str, object]) -> LengthRow:
    a = int(row["a"])
    b = int(row["b"])
    c = int(row["c"])
    abc_factors = merge_factors(a, b, c)
    rad_abc = radical(abc_factors)
    delta_v = delta_profile(row, abc_factors)

    exponent_excess = math.log(abs(a * b * c) / rad_abc)
    c_defect = math.log(c / rad_abc)
    quality = math.log(c) / math.log(rad_abc)

    support_pweighted = 0.0
    valuation_pweighted = 0.0
    for ell in TEST_ELLS:
        for prime, delta_exp in delta_v.items():
            depth = v_l(delta_exp, ell)
            if depth:
                support_pweighted += math.log(prime)
                valuation_pweighted += depth * math.log(prime)

    ordinary_log_length = sum(math.log(max(2, delta_exp)) for delta_exp in delta_v.values())

    max_prime = 1
    max_exponent = 1
    max_single_loss = 0.0
    max_single_ratio: float | None = None
    for prime, exponent in abc_factors.items():
        loss = (exponent - 1) * math.log(prime)
        if loss > max_single_loss:
            max_prime = prime
            max_exponent = exponent
            max_single_loss = loss
            delta_exp = delta_v.get(prime, 2 * exponent)
            max_single_ratio = ratio(math.log(max(2, delta_exp)), loss)

    return LengthRow(
        label=str(row["label"]),
        a=a,
        b=b,
        c=c,
        rad_abc=rad_abc,
        n_cond=int(row["N_cond"]),
        quality=quality,
        c_defect_log=c_defect,
        exponent_excess_log=exponent_excess,
        support_pweighted_cap=support_pweighted,
        valuation_pweighted_cap=valuation_pweighted,
        ordinary_log_length_cap=ordinary_log_length,
        support_over_excess=ratio(support_pweighted, exponent_excess),
        valuation_pweighted_over_excess=ratio(valuation_pweighted, exponent_excess),
        ordinary_length_over_excess=ratio(ordinary_log_length, exponent_excess),
        max_prime=max_prime,
        max_exponent=max_exponent,
        max_single_loss=max_single_loss,
        max_single_ordinary_ratio=max_single_ratio,
        delta_v=delta_v,
    )


def summarize(rows: list[LengthRow]) -> dict[str, float | int]:
    ordinary_ratios = [
        row.ordinary_length_over_excess
        for row in rows
        if row.ordinary_length_over_excess is not None
    ]
    valuation_ratios = [
        row.valuation_pweighted_over_excess
        for row in rows
        if row.valuation_pweighted_over_excess is not None
    ]
    support_ratios = [
        row.support_over_excess for row in rows if row.support_over_excess is not None
    ]
    return {
        "row_count": len(rows),
        "quality_max": max(row.quality for row in rows),
        "exponent_excess_max": max(row.exponent_excess_log for row in rows),
        "ordinary_length_ratio_median": median(ordinary_ratios),
        "ordinary_length_ratio_mean": mean(ordinary_ratios),
        "ordinary_length_ratio_max": max(ordinary_ratios),
        "valuation_pweighted_ratio_median": median(valuation_ratios),
        "valuation_pweighted_ratio_max": max(valuation_ratios),
        "support_ratio_median": median(support_ratios),
        "support_ratio_max": max(support_ratios),
    }


def local_stress_table() -> list[dict[str, float | int]]:
    """Synthetic one-prime comparison: local channel size versus p^e memory."""
    out: list[dict[str, float | int]] = []
    for prime, exponent in [(3, 10), (3, 100), (3, 1000), (23, 10), (23, 100)]:
        loss = (exponent - 1) * math.log(prime)
        ordinary = math.log(2 * exponent)
        valuation = sum(v_l(2 * exponent, ell) * math.log(prime) for ell in TEST_ELLS)
        support = sum(
            math.log(prime) for ell in TEST_ELLS if (2 * exponent) % ell == 0
        )
        out.append(
            {
                "p": prime,
                "e": exponent,
                "loss": loss,
                "support_ratio": support / loss,
                "valuation_pweighted_ratio": valuation / loss,
                "ordinary_ratio": ordinary / loss,
            }
        )
    return out


def fmt(value: object, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def build_report(payload: dict[str, object]) -> str:
    rows = payload["em1_by_quality"]
    summary = payload["summary"]
    stress = payload["local_stress_table"]
    assert isinstance(rows, list)
    assert isinstance(summary, dict)
    assert isinstance(stress, list)

    lines: list[str] = []
    lines.append("# ANC+ Hecke-Längen-Obstruktion")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 73 / G1-P7-Normalform nach C3 und Tamagawa-Sha.")
    lines.append("")
    lines.append("## Frage")
    lines.append("")
    lines.append(
        "Nach dem EM-4-Befund kann P7 nicht über bloße squarefree "
        "Führer-Drops laufen. Offen blieb die stärkere Variante: echte "
        "Hecke-Maximalideale, Kongruenzquotienten oder lokale Kongruenzideale "
        "mit Längen. Diese Notiz prüft, wie viel ein gewöhnlicher lokaler "
        "Hecke-/Kongruenzlängenkanal maximal bezahlen kann."
    )
    lines.append("")
    lines.append("## Normalform")
    lines.append("")
    lines.append(
        "Für ungerades \\(p^e\\Vert abc\\) gilt bei der Frey-Kurve "
        "\\(v_p(\\Delta_{\\min})=2e\\). Standard-Lokalgrößen wie "
        "Tamagawa-Faktoren oder lokale Adjoint-Kongruenzideale können daher "
        "höchstens die Größe \\(2e\\) beziehungsweise deren \\(\\ell\\)-adische "
        "Längen sehen. Der verlorene abc-Inhalt an derselben Stelle ist aber"
    )
    lines.append("")
    lines.append("$$")
    lines.append("(e-1)\\log p.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Damit gibt es drei natürliche Budgets, vom schwachen zum sehr "
        "großzügigen Modell:"
    )
    lines.append("")
    lines.append("1. squarefree C3: \\(\\sum_{\\ell,p:\\ell\\mid 2e_p}\\log p\\);")
    lines.append("2. p-gewichtete Länge: \\(\\sum_{\\ell,p}v_\\ell(2e_p)\\log p\\);")
    lines.append("3. gewöhnliche lokale Log-Länge: \\(\\sum_p\\log(2e_p)\\).")
    lines.append("")
    lines.append(
        "Modell 2 ist absichtlich zu freundlich: Es bezahlt jede "
        "\\(\\ell\\)-adische Länge noch einmal mit \\(\\log p\\), obwohl ein "
        "gewöhnliches lokales Ideal der Größe \\(O(e)\\) nur \\(\\log e\\) trägt. "
        "Wenn selbst dieses Modell nur logarithmisch in \\(e\\) wächst, kann "
        "keine Standard-Faktorisierung allein den prime-gewichteten abc-Defekt "
        "liefern."
    )
    lines.append("")
    lines.append("## EM-1-Ledger")
    lines.append("")
    lines.append(
        f"EM-1 enthält {int(summary['row_count'])} Tripel. Maximale Qualität: "
        f"{fmt(summary['quality_max'])}; maximaler Exponent-Exzess "
        f"{fmt(summary['exponent_excess_max'])}. Median der gewöhnlichen "
        f"Log-Länge relativ zum Exzess: "
        f"{fmt(summary['ordinary_length_ratio_median'])}; Maximum "
        f"{fmt(summary['ordinary_length_ratio_max'])}."
    )
    lines.append("")
    lines.append(
        "| Tripel | q | Exp-excess | C3/Excess | val-p/Excess | "
        "log-len/Excess | stärkster p^e | Einzel-log/Verlust |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---|---:|")
    for item in rows:
        assert isinstance(item, dict)
        lines.append(
            f"| {item['label']} | {fmt(item['quality'])} | "
            f"{fmt(item['exponent_excess_log'])} | "
            f"{fmt(item['support_over_excess'])} | "
            f"{fmt(item['valuation_pweighted_over_excess'])} | "
            f"{fmt(item['ordinary_length_over_excess'])} | "
            f"{item['max_prime']}^{item['max_exponent']} | "
            f"{fmt(item['max_single_ordinary_ratio'])} |"
        )
    lines.append("")
    lines.append("## Lokaler Stresstest")
    lines.append("")
    lines.append(
        "Der folgende synthetische Ein-Primstellen-Vergleich ist kein "
        "abc-Datensatz, sondern die lokale Asymptotik, die jeder G1-Satz "
        "überleben müsste."
    )
    lines.append("")
    lines.append("| p | e | support/loss | val-p/loss | log-len/loss |")
    lines.append("|---:|---:|---:|---:|---:|")
    for item in stress:
        assert isinstance(item, dict)
        lines.append(
            f"| {item['p']} | {item['e']} | {fmt(item['support_ratio'])} | "
            f"{fmt(item['valuation_pweighted_ratio'])} | "
            f"{fmt(item['ordinary_ratio'])} |"
        )
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "**Lemma (gewöhnliche Hecke-Längen sind unterlinear).** Sei "
        "\\(p^e\\Vert abc\\) und sei ein lokaler Kongruenzkanal durch eine "
        "Größe \\(O(e^A)\\) oder durch endlich viele \\(\\ell\\)-adische Längen "
        "\\(v_\\ell(2e)\\) kontrolliert. Dann ist sein Log-Beitrag "
        "\\(O_A(\\log e)\\) beziehungsweise \\(O(\\omega(2e)\\log p)\\). Gegen den "
        "benötigten Beitrag \\((e-1)\\log p\\) geht das Verhältnis für "
        "\\(\\log e=o(e\\log p)\\) gegen null."
    )
    lines.append("")
    lines.append(
        "Damit ist die Standardform der Hecke-/Kongruenzidealroute geschlossen: "
        "IKM-artige lokale Faktorisierung plus Tamagawa-/Adjoint-Längen reicht "
        "nicht, solange die lokalen Faktoren nur polynomial in "
        "\\(v_p(\\Delta_{\\min})\\) sind. Offen bleibt nur eine stärkere, nicht "
        "standardmäßige G1-Aussage: ein Frey-spezifischer globaler "
        "Kongruenzschnitt, der lokale Log-Längen in lineare Exponententiefe "
        "verstärkt, oder ein neuer Hecke-Kohomologiekanal mit direkt "
        "\\(p^{e}\\)-sensitiver Größe."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_hecke_length_budget.py`")
    lines.append(f"- `_data/anc_hecke_length_budget_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = [analyze(row) for row in load_em1()]
    payload: dict[str, object] = {
        "date": DATE,
        "purpose": "Test whether ordinary Hecke/congruence lengths can pay prime-weighted exponent memory.",
        "test_ells": TEST_ELLS,
        "summary": summarize(rows),
        "em1_by_quality": [
            asdict(row) for row in sorted(rows, key=lambda item: item.quality, reverse=True)
        ],
        "local_stress_table": local_stress_table(),
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    MD_OUT.write_text(build_report(payload), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
