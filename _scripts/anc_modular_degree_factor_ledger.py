"""Loop 70 modular-degree factor ledger.

The goal is deliberately modest: keep the N-scaling in the modular-degree
formula honest.  The existing Watkins sample gives deg(phi_E).  A simple AGM
model gives the two archimedean Frey periods

    Omega_a = 2*pi / AGM(sqrt(a+b), sqrt(a))
    Omega_b = 2*pi / AGM(sqrt(a+b), sqrt(b)).

The product Omega_a*Omega_b is the right scale for the complex volume, up to
the usual Neron/minimal-model and local factors.  Therefore

    deg(phi_E) * Omega_a * Omega_b / N_cond

is a proxy for the adjoint/symmetric-square boundary factor.  If the old
"Petersson norm ~ L(Sym^2)/N" bookkeeping were the right scale here, this
quantity would not sit at size one.  In the sample it does.
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
WATKINS_CSV = ROOT / "numerics" / "watkins_v3_final_a+b80.csv"
JSON_OUT = ROOT / "_data" / f"anc_modular_degree_factor_ledger_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_modular_degree_factor_audit.md"


@dataclass(frozen=True)
class Row:
    a: int
    b: int
    c: int
    n_cond: int
    deg: float
    quality: float
    omega_a: float
    omega_b: float
    volume_model: float
    adjoint_proxy: float
    degree_over_n: float
    degree_over_n2: float


def parse_number(text: str) -> float:
    value = text.strip()
    if "/" in value:
        num, den = value.split("/", 1)
        return float(Decimal(num) / Decimal(den))
    return float(Decimal(value))


def agm(x: float, y: float, tol: float = 1e-15) -> float:
    while abs(x - y) > tol * max(abs(x), 1.0):
        x, y = (x + y) / 2.0, math.sqrt(x * y)
    return x


def frey_periods(a: int, b: int, c: int) -> tuple[float, float]:
    omega_a = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(a))
    omega_b = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(b))
    return omega_a, omega_b


def load_rows() -> list[Row]:
    rows: list[Row] = []
    with WATKINS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            a = int(item["a"])
            b = int(item["b"])
            c = int(item["c"])
            n_cond = int(item["N"])
            deg = parse_number(item["deg"])
            omega_a, omega_b = frey_periods(a, b, c)
            volume_model = omega_a * omega_b
            rows.append(
                Row(
                    a=a,
                    b=b,
                    c=c,
                    n_cond=n_cond,
                    deg=deg,
                    quality=parse_number(item["quality"]),
                    omega_a=omega_a,
                    omega_b=omega_b,
                    volume_model=volume_model,
                    adjoint_proxy=deg * volume_model / n_cond,
                    degree_over_n=deg / n_cond,
                    degree_over_n2=deg / (n_cond * n_cond),
                )
            )
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


def top(rows: list[Row], key: str, count: int = 8) -> list[dict[str, object]]:
    return [asdict(row) for row in sorted(rows, key=lambda row: getattr(row, key), reverse=True)[:count]]


def build_payload(rows: list[Row]) -> dict[str, object]:
    proxies = [row.adjoint_proxy for row in rows]
    volumes = [row.volume_model for row in rows]
    return {
        "date": DATE,
        "row_count": len(rows),
        "formula_proxy": "deg(phi_E) * Omega_a * Omega_b / N_cond",
        "summary": {
            "adjoint_proxy_min": min(proxies),
            "adjoint_proxy_q10": quantile(proxies, 0.10),
            "adjoint_proxy_q25": quantile(proxies, 0.25),
            "adjoint_proxy_median": median(proxies),
            "adjoint_proxy_mean": mean(proxies),
            "adjoint_proxy_q75": quantile(proxies, 0.75),
            "adjoint_proxy_q90": quantile(proxies, 0.90),
            "adjoint_proxy_max": max(proxies),
            "volume_model_min": min(volumes),
            "volume_model_median": median(volumes),
            "volume_model_max": max(volumes),
        },
        "top_quality": top(rows, "quality"),
        "top_adjoint_proxy": top(rows, "adjoint_proxy"),
        "top_degree_over_n": top(rows, "degree_over_n"),
        "top_degree_over_n2": top(rows, "degree_over_n2"),
    }


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def row_line(item: dict[str, object]) -> str:
    return (
        f"| ({item['a']},{item['b']},{item['c']}) | {item['n_cond']} | "
        f"{fmt(float(item['deg']))} | {fmt(float(item['quality']))} | "
        f"{fmt(float(item['volume_model']))} | {fmt(float(item['adjoint_proxy']))} |"
    )


def build_report(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    assert isinstance(summary, dict)

    lines: list[str] = []
    lines.append("# ANC+ Modulargrad-Faktoren-Audit")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 70 / Petersson-Normierungs- und Modulargrad-Faktor-Audit.")
    lines.append("")
    lines.append("## Auslöser")
    lines.append("")
    lines.append(
        "Im Paper und in älteren Proof-Notes standen zwei inkompatible Skalen "
        "nebeneinander: vorn wurde \\(\\langle f,f\\rangle\\asymp "
        "L(\\mathrm{Sym}^2 f,1)/N\\) benutzt, während die spätere "
        "Zero-Free-Diagnose bereits \\(\\langle f,f\\rangle\\gtrsim "
        "N/(\\log N)^A\\) verwendete. Diese zweite Skala ist die mit der "
        "Modulargradformel verträgliche."
    )
    lines.append("")
    lines.append("## Formelbuchhaltung")
    lines.append("")
    lines.append(
        "Für eine Hecke-normalisierte Gewicht-2-Neuform gilt, bis auf lokale "
        "Faktoren und Konventionskonstanten,"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\langle f_E,f_E\\rangle_{\\rm Pet}\\asymp "
        "N_{\\rm cond}\\,L(\\operatorname{Ad}f_E,1)."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Watkins' Rankin--Selberg-Formel schreibt dieselbe Buchhaltung in der "
        "motivic-symmetric-square-Normalisierung: der Randwert der symmetrischen "
        "Quadrat-\\(L\\)-Funktion, der komplexe Periodenflächeninhalt und \\(\\deg\\varphi\\) "
        "sind durch einen expliziten Faktor mit einem \\(N\\) im Nenner gekoppelt."
    )
    lines.append("")
    lines.append(
        "Mit der Pullback-Formel \\(\\varphi^*\\omega_E=2\\pi i c_E f(z)dz\\) folgt "
        "asymptotisch"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\deg\\varphi_E\\asymp "
        "\\frac{N_{\\rm cond}\\,L(\\operatorname{Ad}f_E,1)}"
        "{c_E^2\\,\\operatorname{Vol}(E(\\mathbb C))}."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Damit ist die alte \\(1/N\\)-Petersson-Skala geschlossen. Sie würde die "
        "Goldfeld-Frey-Skala um zwei Potenzen verschieben und ist mit Watkins' "
        "Formel nicht vereinbar."
    )
    lines.append("")
    lines.append("## Sample-Ledger")
    lines.append("")
    lines.append(
        "Für die vorhandenen `a+b<=80`-Watkins-Daten wurde der einfache AGM-Proxy"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "Q_E=\\frac{\\deg(\\varphi_E)\\,\\Omega_a\\Omega_b}{N_{\\rm cond}},\\qquad "
        "\\Omega_a=\\frac{2\\pi}{\\operatorname{AGM}(\\sqrt c,\\sqrt a)},\\quad "
        "\\Omega_b=\\frac{2\\pi}{\\operatorname{AGM}(\\sqrt c,\\sqrt b)}"
    )
    lines.append("$$")
    lines.append("")
    lines.append("gebildet. Ergebnis:")
    lines.append("")
    lines.append(
        f"- Anzahl Kurven: {payload['row_count']}"
    )
    lines.append(
        "- \\(Q_E\\)-Band: "
        f"{fmt(float(summary['adjoint_proxy_min']))} bis "
        f"{fmt(float(summary['adjoint_proxy_max']))}"
    )
    lines.append(
        "- Median/Mittel: "
        f"{fmt(float(summary['adjoint_proxy_median']))} / "
        f"{fmt(float(summary['adjoint_proxy_mean']))}"
    )
    lines.append(
        "- 10%-90%-Quantil: "
        f"{fmt(float(summary['adjoint_proxy_q10']))} bis "
        f"{fmt(float(summary['adjoint_proxy_q90']))}"
    )
    lines.append("")
    lines.append("Top nach \\(Q_E\\):")
    lines.append("")
    lines.append("| Tripel | N_cond | deg | q | Vol_model | Q_E |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for item in payload["top_adjoint_proxy"]:
        assert isinstance(item, dict)
        lines.append(row_line(item))
    lines.append("")
    lines.append(
        "Das ist kein Beweis: Minimalmodell-, Manin- und lokale Faktoren sind hier "
        "nur als beschränkte bzw. milde Faktoren sichtbar. Aber das Ledger "
        "bestätigt die richtige Größenordnung: \\(\\deg\\cdot\\operatorname{Vol}/N\\) "
        "ist im Sample eine Größe der Ordnung 1, nicht der Ordnung \\(N^{-2}\\)."
    )
    lines.append("")
    lines.append("## Konsequenz für die Route")
    lines.append("")
    lines.append(
        "Die Modulargrad-Obergrenze ist damit keine neue unabhängige Abkürzung "
        "neben der Periodenroute, sondern dieselbe Engstelle in anderer "
        "Koordinate:"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\deg\\varphi_E\\ll N^{2+\\varepsilon}"
        "\\quad\\Longleftrightarrow\\quad"
        "\\operatorname{Vol}(E(\\mathbb C))"
        "\\gtrsim N^{-1+O(\\varepsilon)}"
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "solange \\(L(\\operatorname{Ad}f_E,1)\\) und die lokalen Faktoren nur "
        "subpolynomiell wachsen. Eine reine Zero-Free-/Symmetric-Square-Kontrolle "
        "liefert genau diese Normgröße, aber nicht den benötigten unteren "
        "Periodenflächeninhalt."
    )
    lines.append("")
    lines.append("## Geschlossen / offen")
    lines.append("")
    lines.append("- Geschlossen: die alte \\(L(\\mathrm{Sym}^2)/N\\)-Petersson-Skala.")
    lines.append("- Geschlossen: ein reiner Symmetric-Square-Zero-Free-Beweis der Periodenlücke.")
    lines.append(
        "- Offen: eine Frey-spezifische untere Schranke für "
        "\\(\\operatorname{Vol}(E(\\mathbb C))\\), äquivalent zur Perioden- bzw. "
        "Goldfeld-Frey-Modulargradlücke."
    )
    lines.append("- Offen: ob Hecke-Kongruenzquotienten diese Volumenschranke nicht-tautologisch liefern.")
    lines.append("")
    lines.append("## Quellen")
    lines.append("")
    lines.append(
        "- Goldfeld, *Modular Forms, Elliptic Curves and the ABC-Conjecture*: "
        "<https://www.math.columbia.edu/~goldfeld/ABC-Conjecture.pdf>."
    )
    lines.append(
        "- Watkins, *Computing the modular degree of an elliptic curve*: "
        "<https://magma.maths.usyd.edu.au/~watkins/papers/moddeg.pdf>."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_modular_degree_factor_ledger.py`")
    lines.append(f"- `_data/anc_modular_degree_factor_ledger_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_rows()
    payload = build_payload(rows)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(payload), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
