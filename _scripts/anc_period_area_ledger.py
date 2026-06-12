"""Loop 71 period-area normal form for Frey curves.

Loop 70 isolated the remaining modular-degree factor as the complex period
area.  This script measures that area in the Frey AGM model:

    Vol_model = Omega_a * Omega_b,
    Omega_a = 2*pi / AGM(sqrt(c), sqrt(a)),
    Omega_b = 2*pi / AGM(sqrt(c), sqrt(b)).

By homogeneity,

    Vol_model = S_area(a/c) / c

where

    S_area(x) = 4*pi^2 / (AGM(1,sqrt(x))*AGM(1,sqrt(1-x))).

The unbounded arithmetic term is therefore c/rad(abc); the shape factor is
only logarithmic in skew cases and cannot pay a polynomial abc defect.
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
JSON_OUT = ROOT / "_data" / f"anc_period_area_ledger_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_period_area_normal_form.md"


@dataclass(frozen=True)
class AreaRow:
    source: str
    label: str
    a: int
    b: int
    c: int
    rad_abc: int
    n_cond: int | None
    quality: float
    omega_a: float
    omega_b: float
    volume_model: float
    area_shape: float
    area_times_rad: float
    area_loss_rad: float
    epsilon_needed_area: float
    shape_exponent_rad: float
    c_over_rad: float


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


def radical_from_parts(*parts: int) -> int:
    primes: set[int] = set()
    for part in parts:
        primes.update(factorize(part))
    result = 1
    for prime in primes:
        result *= prime
    return result


def agm(x: float, y: float, tol: float = 1e-15) -> float:
    while abs(x - y) > tol * max(abs(x), 1.0):
        x, y = (x + y) / 2.0, math.sqrt(x * y)
    return x


def frey_periods(a: int, b: int, c: int) -> tuple[float, float]:
    omega_a = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(a))
    omega_b = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(b))
    return omega_a, omega_b


def build_row(source: str, label: str, a: int, b: int, c: int, n_cond: int | None) -> AreaRow:
    rad_abc = radical_from_parts(a, b, c)
    omega_a, omega_b = frey_periods(a, b, c)
    volume_model = omega_a * omega_b
    area_shape = volume_model * c
    area_times_rad = volume_model * rad_abc
    area_loss = -math.log(area_times_rad)
    log_rad = math.log(rad_abc)
    return AreaRow(
        source=source,
        label=label,
        a=a,
        b=b,
        c=c,
        rad_abc=rad_abc,
        n_cond=n_cond,
        quality=math.log(c) / log_rad,
        omega_a=omega_a,
        omega_b=omega_b,
        volume_model=volume_model,
        area_shape=area_shape,
        area_times_rad=area_times_rad,
        area_loss_rad=area_loss,
        epsilon_needed_area=max(0.0, area_loss / log_rad),
        shape_exponent_rad=math.log(area_shape) / log_rad,
        c_over_rad=c / rad_abc,
    )


def load_em1_rows() -> list[AreaRow]:
    rows: list[AreaRow] = []
    for line in EM1_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        a = int(item["a"])
        b = int(item["b"])
        c = int(item["c"])
        rows.append(build_row("em1", str(item["label"]), a, b, c, int(item["N_cond"])))
    return rows


def load_watkins_rows() -> list[AreaRow]:
    rows: list[AreaRow] = []
    with WATKINS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            a = int(item["a"])
            b = int(item["b"])
            c = int(item["c"])
            rows.append(build_row("watkins_a+b80", f"({a},{b},{c})", a, b, c, int(item["N"])))
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


def summarize(rows: list[AreaRow]) -> dict[str, float | int]:
    shapes = [row.area_shape for row in rows]
    norms = [row.area_times_rad for row in rows]
    eps = [row.epsilon_needed_area for row in rows]
    return {
        "row_count": len(rows),
        "area_shape_min": min(shapes),
        "area_shape_median": median(shapes),
        "area_shape_mean": mean(shapes),
        "area_shape_max": max(shapes),
        "area_times_rad_min": min(norms),
        "area_times_rad_median": median(norms),
        "area_times_rad_max": max(norms),
        "epsilon_needed_area_max": max(eps),
        "epsilon_needed_area_median": median(eps),
        "shape_exponent_max": max(row.shape_exponent_rad for row in rows),
        "shape_exponent_median": median(row.shape_exponent_rad for row in rows),
        "shape_q90": quantile(shapes, 0.90),
    }


def top(rows: list[AreaRow], key: str, count: int = 8, reverse: bool = True) -> list[dict[str, object]]:
    return [asdict(row) for row in sorted(rows, key=lambda row: getattr(row, key), reverse=reverse)[:count]]


def build_payload(em1_rows: list[AreaRow], watkins_rows: list[AreaRow]) -> dict[str, object]:
    all_rows = em1_rows + watkins_rows
    return {
        "date": DATE,
        "identity": "Omega_a*Omega_b = S_area(a/c)/c",
        "summaries": {
            "em1": summarize(em1_rows),
            "watkins_a+b80": summarize(watkins_rows),
            "all": summarize(all_rows),
        },
        "em1_rows_by_quality": [asdict(row) for row in sorted(em1_rows, key=lambda row: row.quality, reverse=True)],
        "top_watkins_shape": top(watkins_rows, "area_shape"),
        "top_watkins_area_defect": top(watkins_rows, "epsilon_needed_area"),
        "top_watkins_quality": top(watkins_rows, "quality"),
    }


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def table_row(item: dict[str, object]) -> str:
    return (
        f"| {item['label']} | {fmt(float(item['quality']))} | "
        f"{fmt(float(item['c_over_rad']))} | {fmt(float(item['area_shape']))} | "
        f"{fmt(float(item['area_times_rad']))} | {fmt(float(item['epsilon_needed_area']))} |"
    )


def build_report(payload: dict[str, object]) -> str:
    summaries = payload["summaries"]
    assert isinstance(summaries, dict)
    em1 = summaries["em1"]
    watkins = summaries["watkins_a+b80"]
    assert isinstance(em1, dict) and isinstance(watkins, dict)

    lines: list[str] = []
    lines.append("# ANC+ Periodenflächen-Normalform")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 71 / Volumenfaktor nach dem Modulargrad-Audit.")
    lines.append("")
    lines.append("## Ziel")
    lines.append("")
    lines.append(
        "Loop 70 isolierte in der Modulargradformel den Periodenflächeninhalt "
        "\\(\\operatorname{Vol}(E(\\mathbb C))\\) als verbleibenden harten Faktor. "
        "Diese Notiz prüft, ob dieser Faktor für Frey-Kurven eine neue freie "
        "Richtung ist."
    )
    lines.append("")
    lines.append("## Exakte homogene Form")
    lines.append("")
    lines.append("Für \\(E_{a,b}:y^2=x(x-a)(x+b)\\), \\(c=a+b\\), liefert die AGM-Formel")
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\Omega_a=\\frac{2\\pi}{\\operatorname{AGM}(\\sqrt c,\\sqrt a)},\\qquad "
        "\\Omega_b=\\frac{2\\pi}{\\operatorname{AGM}(\\sqrt c,\\sqrt b)}."
    )
    lines.append("$$")
    lines.append("")
    lines.append("Mit \\(x=a/c\\) folgt durch Homogenität")
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\Omega_a\\Omega_b=\\frac{S_{\\rm area}(x)}{c},\\qquad "
        "S_{\\rm area}(x)=\\frac{4\\pi^2}"
        "{\\operatorname{AGM}(1,\\sqrt x)\\operatorname{AGM}(1,\\sqrt{1-x})}."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Der unbeschränkte arithmetische Term ist damit wieder \\(c/\\operatorname{rad}(abc)\\). "
        "Der Shape-Faktor \\(S_{\\rm area}\\) ist nicht konstant wie bei der Systole, "
        "sondern wächst in extrem schiefen Fällen nur logarithmisch; er kann daher "
        "keinen polynomialen abc-Defekt bezahlen."
    )
    lines.append("")
    lines.append("Die normalisierte Flächenaussage lautet")
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\Omega_a\\Omega_b\\,\\operatorname{rad}(abc)"
        "=\\frac{S_{\\rm area}(a/c)}{c/\\operatorname{rad}(abc)}."
    )
    lines.append("$$")
    lines.append("")
    lines.append("## EM-1-Champions")
    lines.append("")
    lines.append("| Tripel | q | c/rad | S_area | Vol*rad | benötigtes ε_area |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for item in payload["em1_rows_by_quality"]:
        assert isinstance(item, dict)
        lines.append(table_row(item))
    lines.append("")
    lines.append(
        "Im EM-1-Satz liegt der Shape-Faktor zwischen "
        f"{fmt(float(em1['area_shape_min']))} und {fmt(float(em1['area_shape_max']))}; "
        "nur die beiden härtesten Champions haben `Vol*rad < 1`. Der größte "
        "zusätzliche Flächenexponent im Sample ist "
        f"{fmt(float(em1['epsilon_needed_area_max']))}."
    )
    lines.append("")
    lines.append("## Watkins-Sample")
    lines.append("")
    lines.append(
        f"Für `a+b<=80` ({watkins['row_count']} Kurven) liegt "
        f"`S_area` zwischen {fmt(float(watkins['area_shape_min']))} und "
        f"{fmt(float(watkins['area_shape_max']))}; Median "
        f"{fmt(float(watkins['area_shape_median']))}. "
        f"`Vol*rad` liegt zwischen {fmt(float(watkins['area_times_rad_min']))} "
        f"und {fmt(float(watkins['area_times_rad_max']))}."
    )
    lines.append("")
    lines.append("Top Shape im Watkins-Sample:")
    lines.append("")
    lines.append("| Tripel | q | c/rad | S_area | Vol*rad | benötigtes ε_area |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for item in payload["top_watkins_shape"]:
        assert isinstance(item, dict)
        lines.append(table_row(item))
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "Das Periodenflächen-Gate ist keine neue Abkürzung. Es ist die "
        "flächenhafte Normalform derselben abc-Lücke:"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\operatorname{Vol}(E(\\mathbb C))\\gtrsim N^{-1-\\varepsilon}"
        "\\quad\\Longleftrightarrow_{\\varepsilon}\\quad"
        "{}c\\lesssim N^{1+\\varepsilon}."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Die Richtung abc \\(\\Rightarrow\\) Fläche ist direkt. Umgekehrt gibt "
        "\\(\\Omega_a\\Omega_b\\operatorname{rad}\\ge N^{-\\varepsilon}\\) nur "
        "\\(c/\\operatorname{rad}\\le S_{\\rm area}N^\\varepsilon\\); der "
        "logarithmische Shape-Faktor wird in der üblichen "
        "\\(\\varepsilon\\)-Buchhaltung absorbiert. Damit bleibt als nicht-tautologischer "
        "Hebel nur eine arithmetische Erklärung, warum Frey-Kurven diesen "
        "Volumenbound erfüllen müssen."
    )
    lines.append("")
    lines.append("## Geschlossen / offen")
    lines.append("")
    lines.append("- Geschlossen: Periodenfläche als unabhängiger archimedischer Freiheitsgrad.")
    lines.append("- Geschlossen: Modulargrad plus Adjoint-\\(L\\)-Wert als Abkürzung ohne Volumenkontrolle.")
    lines.append("- Offen: ein nicht-tautologischer arithmetischer Mechanismus für den Volumenbound.")
    lines.append("- Offen: Hecke-Kongruenzquotienten oder Frey-spezifische Kohomologie als mögliche Zahler dieser Fläche.")
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_period_area_ledger.py`")
    lines.append(f"- `_data/anc_period_area_ledger_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    em1_rows = load_em1_rows()
    watkins_rows = load_watkins_rows()
    payload = build_payload(em1_rows, watkins_rows)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(payload), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
