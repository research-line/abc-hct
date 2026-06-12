"""Loop 67 ledger for the three remaining direct ANC+ gates.

The script keeps the bookkeeping deliberately local:

1. Modular-degree gate:
   read the existing PARI/GP Watkins sample for Frey curves with a+b <= 80
   and summarize the sharp abc-scale test deg(phi_E) <= N_cond^(1+eps).

2. Goldfeld-Szpiro/Sha gate:
   reuse the BSD decomposition rows from ze_decomposition.py as audited
   sample data and expose where the algebraic quotient A_E = L/Omega grows.

3. Central anti-concentration with quotient control:
   record the exact split Z_E = L(E,1)*sqrt(N_cond) = A_E*P_E and show
   that lower bounds for L(E,1) alone do not imply period lower bounds unless
   A_E is controlled from above.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
WATKINS_CSV = ROOT / "numerics" / "watkins_v3_final_a+b80.csv"
JSON_OUT = ROOT / "_data" / f"anc_three_gate_ledger_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_three_gate_attack.md"


@dataclass(frozen=True)
class WatkinsRow:
    a: int
    b: int
    c: int
    n_cond: int
    deg: float
    quality: float
    ratio_eps001: float
    ratio_eps01: float
    ratio_degree_conjecture_eps001: float
    ratio_degree_conjecture_eps01: float
    degree_exponent: float


@dataclass(frozen=True)
class BsdRow:
    label: str
    n_cond: int
    quality: float
    omega: float
    l_value: float
    a_e: float
    tors_sq: int
    tamagawa_product: int
    sha: int
    p_e: float
    z_e: float
    a_exponent: float


def parse_number(text: str) -> float:
    """Parse PARI-ish rationals or decimal strings from the CSV."""
    value = text.strip()
    if "/" in value:
        num, den = value.split("/", 1)
        return float(Decimal(num) / Decimal(den))
    return float(Decimal(value))


def load_watkins_rows() -> list[WatkinsRow]:
    rows: list[WatkinsRow] = []
    with WATKINS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            n_cond = int(item["N"])
            deg = parse_number(item["deg"])
            degree_exponent = math.log(deg) / math.log(n_cond) if deg > 0 and n_cond > 1 else float("nan")
            rows.append(
                WatkinsRow(
                    a=int(item["a"]),
                    b=int(item["b"]),
                    c=int(item["c"]),
                    n_cond=n_cond,
                    deg=deg,
                    quality=parse_number(item["quality"]),
                    ratio_eps001=parse_number(item["ratio_eps0.01"]),
                    ratio_eps01=parse_number(item["ratio_eps0.1"]),
                    ratio_degree_conjecture_eps001=deg / (n_cond ** 2.01),
                    ratio_degree_conjecture_eps01=deg / (n_cond ** 2.1),
                    degree_exponent=degree_exponent,
                )
            )
    return rows


def known_bsd_rows() -> list[BsdRow]:
    """Audited rank-0 BSD rows from _scripts/ze_decomposition.py output.

    For Reyssat the row is explicitly the swapped ANC+ orientation
    E_{6436341,2}; the original E_{2,6436341} has w=-1 and rank 1.
    """
    raw = [
        ("1+2^3=3^2", 48, 1.23, 3.371501, 0.842875, 0.25, 64, 16, 1, 23.358, 5.840),
        ("3+5^3=2^7", 240, 1.43, 1.158392, 1.158392, 1.0, 16, 16, 1, 17.946, 17.946),
        ("1+2*3^7=5^4*7", 3360, 1.57, 0.337349, 1.349397, 4.0, 16, 64, 1, 19.555, 78.218),
        ("1+2^5*3*5^2=7^4", 1680, 1.46, 0.430903, 1.723611, 4.0, 64, 256, 1, 17.662, 70.647),
        ("Reyssat(E_{6436341,2})", 240672, 1.63, 0.002477, 0.894062, 361.0, 16, 16, 361, 1.215, 438.612),
    ]
    rows: list[BsdRow] = []
    for label, n_cond, quality, omega, l_value, a_e, tors_sq, tam, sha, p_e, z_e in raw:
        rows.append(
            BsdRow(
                label=label,
                n_cond=n_cond,
                quality=quality,
                omega=omega,
                l_value=l_value,
                a_e=a_e,
                tors_sq=tors_sq,
                tamagawa_product=tam,
                sha=sha,
                p_e=p_e,
                z_e=z_e,
                a_exponent=math.log(a_e) / math.log(n_cond) if a_e > 0 else float("nan"),
            )
        )
    return rows


def max_by(rows: list[WatkinsRow], attr: str) -> WatkinsRow:
    return max(rows, key=lambda row: getattr(row, attr))


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def watkins_summary(rows: list[WatkinsRow]) -> dict[str, object]:
    max_ratio_001 = max_by(rows, "ratio_eps001")
    max_ratio_01 = max_by(rows, "ratio_eps01")
    max_degree_conj_001 = max_by(rows, "ratio_degree_conjecture_eps001")
    max_degree_conj_01 = max_by(rows, "ratio_degree_conjecture_eps01")
    max_exponent = max_by(rows, "degree_exponent")
    top_quality = sorted(rows, key=lambda row: row.quality, reverse=True)[:10]
    top_ratio = sorted(rows, key=lambda row: row.ratio_eps001, reverse=True)[:10]
    quality_subsets: dict[str, dict[str, object]] = {}
    for threshold in [1.0, 1.2, 1.4]:
        subset = [row for row in rows if row.quality >= threshold]
        key = f"q_ge_{threshold:.1f}"
        if not subset:
            quality_subsets[key] = {
                "threshold": threshold,
                "row_count": 0,
                "unit_exceedances_eps_0_01": 0,
                "unit_exceedances_eps_0_1": 0,
                "max_ratio_eps_0_01": None,
                "max_ratio_eps_0_1": None,
            }
            continue
        quality_subsets[key] = {
            "threshold": threshold,
            "row_count": len(subset),
            "unit_exceedances_eps_0_01": sum(1 for row in subset if row.ratio_eps001 > 1),
            "unit_exceedances_eps_0_1": sum(1 for row in subset if row.ratio_eps01 > 1),
            "max_ratio_eps_0_01": asdict(max(subset, key=lambda row: row.ratio_eps001)),
            "max_ratio_eps_0_1": asdict(max(subset, key=lambda row: row.ratio_eps01)),
        }
    return {
        "source_csv": str(WATKINS_CSV.relative_to(ROOT)),
        "row_count": len(rows),
        "bound_tested": "deg(phi_E) <= N_cond^(1+epsilon)",
        "degree_conjecture_bound": "deg(phi_E) <= N_cond^(2+epsilon)",
        "unit_exceedances_eps_0_01": sum(1 for row in rows if row.ratio_eps001 > 1),
        "unit_exceedances_eps_0_1": sum(1 for row in rows if row.ratio_eps01 > 1),
        "degree_conjecture_unit_exceedances_eps_0_01": sum(
            1 for row in rows if row.ratio_degree_conjecture_eps001 > 1
        ),
        "degree_conjecture_unit_exceedances_eps_0_1": sum(
            1 for row in rows if row.ratio_degree_conjecture_eps01 > 1
        ),
        "max_ratio_eps_0_01": asdict(max_ratio_001),
        "max_ratio_eps_0_1": asdict(max_ratio_01),
        "max_degree_conjecture_ratio_eps_0_01": asdict(max_degree_conj_001),
        "max_degree_conjecture_ratio_eps_0_1": asdict(max_degree_conj_01),
        "max_degree_exponent": asdict(max_exponent),
        "quality_subsets": quality_subsets,
        "top_quality_rows": [asdict(row) for row in top_quality],
        "top_ratio_eps_0_01_rows": [asdict(row) for row in top_ratio],
    }


def bsd_summary(rows: list[BsdRow]) -> dict[str, object]:
    max_a = max(rows, key=lambda row: row.a_e)
    min_p = min(rows, key=lambda row: row.p_e)
    max_z = max(rows, key=lambda row: row.z_e)
    return {
        "source": "_scripts/ze_decomposition.py audited output",
        "identity": "Z_E = L(E,1)*sqrt(N_cond) = A_E * P_E",
        "rows": [asdict(row) for row in rows],
        "max_A_E": asdict(max_a),
        "min_P_E": asdict(min_p),
        "max_Z_E": asdict(max_z),
        "A_E_range": [min(row.a_e for row in rows), max(row.a_e for row in rows)],
        "P_E_range": [min(row.p_e for row in rows), max(row.p_e for row in rows)],
        "Z_E_range": [min(row.z_e for row in rows), max(row.z_e for row in rows)],
    }


def build_report(w_summary: dict[str, object], b_summary: dict[str, object]) -> str:
    max_r001 = w_summary["max_ratio_eps_0_01"]
    max_r01 = w_summary["max_ratio_eps_0_1"]
    max_dc001 = w_summary["max_degree_conjecture_ratio_eps_0_01"]
    max_dc01 = w_summary["max_degree_conjecture_ratio_eps_0_1"]
    max_exp = w_summary["max_degree_exponent"]
    b_rows = b_summary["rows"]

    lines: list[str] = []
    lines.append("# ANC+ Drei-Gate-Angriff")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 67 / direkter Angriff auf die drei nach Loop 66 verbleibenden ANC+-Türen.")
    lines.append("")
    lines.append("## Ergebnis in einem Satz")
    lines.append("")
    lines.append(
        "Von den drei Türen ist die Modulargrad-Obergrenze die sauberste harte "
        "Zielhypothese; Goldfeld-Szpiro/Sha und zentrale Anti-Konzentration "
        "kollabieren beide auf dieselbe fehlende Kontrolle des algebraischen "
        "Quotienten \\(A_E=L(E,1)/\\Omega_E\\)."
    )
    lines.append("")
    lines.append("## Gate M: Modulargrad-Obergrenze")
    lines.append("")
    lines.append(
        "Hier müssen zwei Skalen getrennt werden. Goldfelds Degree Conjecture "
        "für Frey-Kurven hat die abc-äquivalente Form"
    )
    lines.append("")
    lines.append("$$\\deg(\\varphi_E) \\le C_\\varepsilon N_{\\rm cond}^{2+\\varepsilon}.$$ ")
    lines.append("")
    lines.append(
        "Das vorhandene PARI/GP-Watkins-Sample `a+b <= 80` testet daneben die "
        "stärkere Watkins-Diagnostik"
    )
    lines.append("")
    lines.append("$$\\deg(\\varphi_E) \\le C_\\varepsilon N_{\\rm cond}^{1+\\varepsilon},$$")
    lines.append("")
    lines.append(
        "die numerisch interessant ist, aber nicht der minimale abc-äquivalente "
        "Maßstab aus Goldfelds Degree Conjecture."
    )
    lines.append("")
    lines.append(
        f"Ausgewertet wurden {w_summary['row_count']} Frey-Kurven. Mit der "
        "willkürlichen Normierungskonstante 1 gibt es auf der starken Watkins-Skala "
        f"{w_summary['unit_exceedances_eps_0_01']} Überschreitungen für "
        f"\\(\\varepsilon=0.01\\) und {w_summary['unit_exceedances_eps_0_1']} "
        "Überschreitungen für \\(\\varepsilon=0.1\\). Das ist keine "
        "asymptotische Falsifikation, weil die Schranke eine freie Konstante "
        "\\(C_\\varepsilon\\) hat."
    )
    lines.append("")
    lines.append("| Test | maximales Verhältnis | Tripel | N_cond | deg | q |")
    lines.append("|---|---:|---|---:|---:|---:|")
    for label, row, ratio_key in [
        ("Watkins: deg/N^1.01", max_r001, "ratio_eps001"),
        ("Watkins: deg/N^1.10", max_r01, "ratio_eps01"),
        ("Degree: deg/N^2.01", max_dc001, "ratio_degree_conjecture_eps001"),
        ("Degree: deg/N^2.10", max_dc01, "ratio_degree_conjecture_eps01"),
    ]:
        lines.append(
            "| {label} | {ratio} | ({a},{b},{c}) | {n} | {deg} | {q} |".format(
                label=label,
                ratio=fmt(float(row[ratio_key]), 6 if "2." in label else 4),
                a=row["a"],
                b=row["b"],
                c=row["c"],
                n=row["n_cond"],
                deg=fmt(float(row["deg"]), 0),
                q=fmt(float(row["quality"]), 4),
            )
        )
    lines.append("")
    lines.append(
        "Der größte beobachtete Grad-Exponent ist "
        f"`log(deg)/log(N_cond) = {fmt(float(max_exp['degree_exponent']), 3)}` "
        f"bei `({max_exp['a']},{max_exp['b']},{max_exp['c']})`."
    )
    lines.append("")
    lines.append("Für die abc-relevanteren höheren Qualitätsbereiche verschwindet diese Unit-Konstanten-Spitze:")
    lines.append("")
    lines.append("| Qualitätsbereich | Anzahl | Unit-Überschreitungen eps=0.01 | max deg/N^1.01 |")
    lines.append("|---|---:|---:|---:|")
    for key in ["q_ge_1.0", "q_ge_1.2", "q_ge_1.4"]:
        subset = w_summary["quality_subsets"][key]
        max_row = subset["max_ratio_eps_0_01"]
        max_value = float(max_row["ratio_eps001"]) if max_row else 0.0
        lines.append(
            "| q >= {threshold} | {count} | {exceed} | {max_value} |".format(
                threshold=fmt(float(subset["threshold"]), 1),
                count=subset["row_count"],
                exceed=subset["unit_exceedances_eps_0_01"],
                max_value=fmt(max_value, 4),
            )
        )
    lines.append("")
    lines.append(
        "**Urteil M:** numerisch kein Gegenbeispiel, aber auch kein Beweis. "
        "Die Goldfeld-Frey-Degree-Skala `N^(2+epsilon)` wird im Sample mit "
        "riesiger Reserve erfüllt. Die stärkere Watkins-Skala `N^(1+epsilon)` "
        "ist als Diagnostik nützlich, darf aber nicht als abc-scharfer Maßstab "
        "etikettiert werden. Was fehlt, ist ein uniformer Frey-spezifischer "
        "Mechanismus für alle Leiter."
    )
    lines.append("")
    lines.append("## Gate GS: Goldfeld-Szpiro/Sha")
    lines.append("")
    lines.append(
        "BSD zerlegt im Rang-0-Fall"
    )
    lines.append("")
    lines.append("$$L(E,1)=\\Omega_E\\,A_E,\\qquad A_E=\\frac{|\\Sha(E)|\\prod c_p}{|E(\\mathbb Q)_{\\rm tors}|^2}.$$ ")
    lines.append("")
    lines.append(
        "Die geprüften Rang-0-Zeilen zeigen, dass \\(A_E\\) kein kleiner "
        "Nebenfaktor ist, sondern genau der harte Quotient."
    )
    lines.append("")
    lines.append("| Tripel | N_cond | q | A_E | Sha | P_E=Omega*sqrt(N) | Z_E=L*sqrt(N) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in b_rows:
        lines.append(
            "| {label} | {n} | {q} | {a_e} | {sha} | {p_e} | {z_e} |".format(
                label=row["label"],
                n=row["n_cond"],
                q=fmt(float(row["quality"]), 2),
                a_e=fmt(float(row["a_e"]), 3),
                sha=row["sha"],
                p_e=fmt(float(row["p_e"]), 3),
                z_e=fmt(float(row["z_e"]), 3),
            )
        )
    lines.append("")
    lines.append(
        "Bei der vertauschten Reyssat-ANC+-Orientierung `E_{6436341,2}` "
        "liegt `A_E=361`, getrieben durch `Sha=19^2`; zugleich ist "
        "`P_E=Omega*sqrt(N_cond)=1.215` der kleinste Periodenkern der Tabelle. "
        "Die ursprüngliche Orientierung `E_{2,6436341}` ist die w=-1/Rang-1-Kurve "
        "und gehört nicht in diese Rang-0-BSD-Zeile."
    )
    lines.append("")
    lines.append(
        "**Urteil GS:** Goldfeld-Szpiro/Sha ist keine unabhängige Abkürzung. "
        "Eine individuelle Schranke \\(A_E\\le N^{1/2+\\varepsilon}\\) wäre genau "
        "die benötigte Quotientenkontrolle; ohne sie dreht BSD nur die Periodenlücke "
        "in eine Sha-Lücke."
    )
    lines.append("")
    lines.append("## Gate CAQ: zentrale Anti-Konzentration mit Quotientenkontrolle")
    lines.append("")
    lines.append(
        "Die zentrale Größe \\(Z_E=L(E,1)\\sqrt{N_{\\rm cond}}\\) ist im Sample "
        "nicht klein. Gerade beim hochqualitativen Reyssat-Fall ist sie groß. "
        "Das beweist aber keine Periodenuntergrenze, denn"
    )
    lines.append("")
    lines.append("$$P_E=\\Omega_E\\sqrt{N_{\\rm cond}}=\\frac{Z_E}{A_E}.$$ ")
    lines.append("")
    lines.append(
        "Eine reine Untergrenze für \\(L(E,1)\\) reicht also nicht. Benötigt wird "
        "die gekoppelte Aussage"
    )
    lines.append("")
    lines.append("$$L(E,1) \\ge c_\\varepsilon\\,N^{-1/2-\\varepsilon}\\,A_E,$$")
    lines.append("")
    lines.append(
        "oder getrennt: eine zentrale Untergrenze plus eine obere Schranke für "
        "den algebraischen Quotienten \\(A_E\\), deren Exponenten zusammen die "
        "Periodenschranke ergeben."
    )
    lines.append("")
    lines.append(
        "**Urteil CAQ:** zentrale Anti-Konzentration bleibt nur dann ein echter "
        "ANC+-Angriff, wenn sie den algebraischen Quotienten mitführt. Ohne "
        "Quotientenkontrolle misst sie den falschen Zähler."
    )
    lines.append("")
    lines.append("## Beweisstand nach Loop 67")
    lines.append("")
    lines.append("| Route | Stand | Entscheidung |")
    lines.append("|---|---|---|")
    lines.append("| Modulargrad | Offen, sauberstes Ziel | weiter offen; braucht uniformen Frey-Mechanismus |")
    lines.append("| Goldfeld-Szpiro/Sha | Offen als bekannte harte Sha-Form | keine Abkürzung; Quotientenkontrolle nötig |")
    lines.append("| Zentrale Anti-Konzentration | Offen nur gekoppelt mit A_E | L-Untergrenze allein reicht nicht |")
    lines.append("")
    lines.append(
        "Damit ist keine Tür bewiesen und keine Tür vollständig geschlossen. "
        "Geschlossen ist nur die Hoffnung, dass eine isolierte L-Wert-Untergrenze "
        "oder ein isolierter Sha-Verweis die Periodenlücke ersetzt. Der nächste "
        "harte Arbeitspunkt ist eine der beiden äquivalenten Formen: "
        "Modulargrad `deg(phi_E) <= N_cond^(2+epsilon)` oder direkte "
        "`A_E`-Kontrolle in der Frey-Familie."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_three_gate_ledger.py`")
    lines.append(f"- `_data/anc_three_gate_ledger_{DATE}.json`")
    lines.append("- `_proof-notes/ANC_three_gate_attack.md`")
    return "\n".join(lines) + "\n"


def main() -> None:
    watkins_rows = load_watkins_rows()
    bsd_rows = known_bsd_rows()
    payload = {
        "date": DATE,
        "watkins": watkins_summary(watkins_rows),
        "bsd": bsd_summary(bsd_rows),
        "verdict": {
            "modular_degree": "open; numerically consistent on a+b<=80 sample",
            "goldfeld_szpiro_sha": "not a shortcut; equivalent quotient-control gate",
            "central_anti_concentration": "insufficient without A_E upper control",
        },
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(payload["watkins"], payload["bsd"]), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
