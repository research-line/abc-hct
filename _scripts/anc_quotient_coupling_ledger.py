"""Coupling ledger for central anti-concentration and the BSD quotient.

The central identity is

    P_E = Omega_E * sqrt(N)
        = (L(E, 1) * sqrt(N)) / (L(E, 1) / Omega_E)
        = Z_E / A_E.

Thus a lower bound for the central value alone never controls the period
unless the algebraic quotient A_E is controlled on the same exponent scale.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_data" / f"anc_quotient_coupling_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_quotient_coupling_lemma.md"


AUDITED_ROWS = [
    {
        "label": "1+2^3=3^2",
        "a": 1,
        "b": 8,
        "rad_abc": 6,
        "n_cond": 48,
        "omega": 3.371501,
        "l_value": 0.842875,
        "a_quotient": 0.25,
        "torsion_sq": 64,
        "tamagawa": 16,
        "sha": 1,
    },
    {
        "label": "3+5^3=2^7",
        "a": 3,
        "b": 125,
        "rad_abc": 30,
        "n_cond": 240,
        "omega": 1.158392,
        "l_value": 1.158392,
        "a_quotient": 1.0,
        "torsion_sq": 16,
        "tamagawa": 16,
        "sha": 1,
    },
    {
        "label": "1+2*3^7=5^4*7",
        "a": 1,
        "b": 4374,
        "rad_abc": 210,
        "n_cond": 3360,
        "omega": 0.337349,
        "l_value": 1.349397,
        "a_quotient": 4.0,
        "torsion_sq": 16,
        "tamagawa": 64,
        "sha": 1,
    },
    {
        "label": "1+2^5*3*5^2=7^4",
        "a": 1,
        "b": 2400,
        "rad_abc": 210,
        "n_cond": 1680,
        "omega": 0.430903,
        "l_value": 1.723611,
        "a_quotient": 4.0,
        "torsion_sq": 64,
        "tamagawa": 256,
        "sha": 1,
    },
    {
        "label": "Reyssat(E_{b,a})",
        "a": 6436341,
        "b": 2,
        "rad_abc": 15042,
        "n_cond": 240672,
        "omega": 0.002477,
        "l_value": 0.894062,
        "a_quotient": 361.0,
        "torsion_sq": 16,
        "tamagawa": 16,
        "sha": 361,
    },
]


def log_exponent(value: float, base: int) -> float:
    if value <= 0 or base <= 1:
        return float("nan")
    return math.log(value) / math.log(base)


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def enrich(row: dict[str, object]) -> dict[str, object]:
    a = int(row["a"])
    b = int(row["b"])
    c = a + b
    n_cond = int(row["n_cond"])
    rad_abc = int(row["rad_abc"])
    omega = float(row["omega"])
    l_value = float(row["l_value"])
    a_quotient = float(row["a_quotient"])

    p_cond = omega * math.sqrt(n_cond)
    z_cond = l_value * math.sqrt(n_cond)
    p_rad = omega * math.sqrt(rad_abc)
    z_rad = l_value * math.sqrt(rad_abc)

    beta_a_cond = log_exponent(a_quotient, n_cond)
    z_exp_cond = log_exponent(z_cond, n_cond)
    p_exp_cond = log_exponent(p_cond, n_cond)
    beta_a_rad = log_exponent(a_quotient, rad_abc)
    z_exp_rad = log_exponent(z_rad, rad_abc)
    p_exp_rad = log_exponent(p_rad, rad_abc)

    return {
        **row,
        "c": c,
        "quality_rad": log_exponent(c, rad_abc),
        "p_cond": p_cond,
        "z_cond": z_cond,
        "p_rad": p_rad,
        "z_rad": z_rad,
        "beta_a_cond": beta_a_cond,
        "z_exponent_cond": z_exp_cond,
        "p_exponent_cond": p_exp_cond,
        "identity_check_cond": z_exp_cond - beta_a_cond - p_exp_cond,
        "beta_a_rad": beta_a_rad,
        "z_exponent_rad": z_exp_rad,
        "p_exponent_rad": p_exp_rad,
        "identity_check_rad": z_exp_rad - beta_a_rad - p_exp_rad,
    }


def build_payload(rows: list[dict[str, object]]) -> dict[str, object]:
    max_beta = max(rows, key=lambda item: float(item["beta_a_cond"]))
    min_p_rad = min(rows, key=lambda item: float(item["p_exponent_rad"]))
    return {
        "date": DATE,
        "identity": "P_E = Omega_E*sqrt(N) = (L(E,1)*sqrt(N))/(L(E,1)/Omega_E) = Z_E/A_E",
        "split_criterion": (
            "If Z_E >= c_e N^{-alpha(e)} and A_E <= C_e N^{beta(e)}, "
            "then P_E >= (c_e/C_e) N^{-(alpha(e)+beta(e))}. "
            "The abc/period gate requires alpha(e)+beta(e) to be arbitrarily small."
        ),
        "rows": rows,
        "max_beta_a_cond": max_beta,
        "min_period_exponent_rad": min_p_rad,
    }


def build_report(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    max_beta = payload["max_beta_a_cond"]
    min_p_rad = payload["min_period_exponent_rad"]

    lines: list[str] = []
    lines.append("# ANC+ Quotienten-Kopplungslemma")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 69 / zentrale Anti-Konzentration mit algebraischer Quotientenkontrolle.")
    lines.append("")
    lines.append("## Normalform")
    lines.append("")
    lines.append("Setze für eine Rang-0-Frey-Kurve")
    lines.append("")
    lines.append("$$")
    lines.append("Z_E=L(E,1)\\sqrt N,\\qquad A_E=\\frac{L(E,1)}{\\Omega_E},\\qquad P_E=\\Omega_E\\sqrt N.")
    lines.append("$$")
    lines.append("")
    lines.append("Dann gilt identisch")
    lines.append("")
    lines.append("$$")
    lines.append("P_E=\\frac{Z_E}{A_E}.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Dabei kann \\(N\\) als Kurvenkonduktor oder, bis auf den beschränkten 2-Anteil, "
        "als \\(\\operatorname{rad}(abc)\\) gelesen werden. Für die L-Funktion ist "
        "der Konduktor natürlicher; für die abc-Periodenform ist der Radikalmaßstab "
        "die direkte Sprache."
    )
    lines.append("")
    lines.append("## Lemma: Exponenten-Kopplung")
    lines.append("")
    lines.append("Angenommen, für jedes \\(\\varepsilon>0\\) gibt es Schranken")
    lines.append("")
    lines.append("$$")
    lines.append("Z_E\\ge c_\\varepsilon N^{-\\alpha(\\varepsilon)},\\qquad")
    lines.append("A_E\\le C_\\varepsilon N^{\\beta(\\varepsilon)}.")
    lines.append("$$")
    lines.append("")
    lines.append("Dann folgt")
    lines.append("")
    lines.append("$$")
    lines.append("P_E\\ge (c_\\varepsilon/C_\\varepsilon)N^{-(\\alpha(\\varepsilon)+\\beta(\\varepsilon))}.")
    lines.append("$$")
    lines.append("")
    lines.append(
        "Die abc-/Perioden-Schranke \\(P_E\\ge C_\\varepsilon N^{-\\varepsilon}\\) "
        "wird durch eine solche Zweiteilung nur erreicht, wenn die Summe "
        "\\(\\alpha(\\varepsilon)+\\beta(\\varepsilon)\\) beliebig klein gemacht werden kann."
    )
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "Eine reine zentrale Anti-Konzentration \\(L(E,1)\\ge N^{-1/2-\\varepsilon}\\), "
        "also \\(Z_E\\ge N^{-\\varepsilon}\\), reicht nur zusammen mit einer "
        "subpolynomiellen Quotientenschranke \\(A_E\\le N^{\\varepsilon}\\). "
        "Eine Goldfeld-Szpiro-Schranke \\(A_E\\ll N^{1/2+\\varepsilon}\\) wäre hier "
        "zu schwach: sie ergäbe nur \\(P_E\\gg N^{-1/2-2\\varepsilon}\\)."
    )
    lines.append("")
    lines.append(
        "Die gekoppelte Alternative \\(Z_E\\ge A_E N^{-\\varepsilon}\\) ist dagegen "
        "formal genau \\(P_E\\ge N^{-\\varepsilon}\\). Sie ist also keine unabhängige "
        "Abkürzung, sondern die Periodenlücke in zentraler Sprache."
    )
    lines.append("")
    lines.append("## Numerische Ledger-Tabelle")
    lines.append("")
    lines.append("| Tripel | q | A_E | beta_A(cond) | Z_cond | P_rad | exp(P_rad) | Quelle der Kompensation |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for row in rows:
        source = "Sha" if int(row["sha"]) > 1 else "Tamagawa/Torsion"
        lines.append(
            "| {label} | {q} | {a_e} | {beta} | {z} | {p_rad} | {p_exp} | {source} |".format(
                label=row["label"],
                q=fmt(float(row["quality_rad"])),
                a_e=fmt(float(row["a_quotient"])),
                beta=fmt(float(row["beta_a_cond"])),
                z=fmt(float(row["z_cond"])),
                p_rad=fmt(float(row["p_rad"])),
                p_exp=fmt(float(row["p_exponent_rad"])),
                source=source,
            )
        )
    lines.append("")
    lines.append("Maximaler Quotienten-Exponent im Ledger:")
    lines.append("")
    lines.append(
        f"- `{max_beta['label']}` mit \\(A_E={fmt(float(max_beta['a_quotient']))}\\) "
        f"und \\(\\log A_E/\\log N_{{cond}}={fmt(float(max_beta['beta_a_cond']))}\\)."
    )
    lines.append("")
    lines.append("Stärkster Radikal-Periodenverlust im Ledger:")
    lines.append("")
    lines.append(
        f"- `{min_p_rad['label']}` mit \\(P_{{rad}}={fmt(float(min_p_rad['p_rad']))}\\) "
        f"und \\(\\log P_{{rad}}/\\log\\operatorname{{rad}}={fmt(float(min_p_rad['p_exponent_rad']))}\\)."
    )
    lines.append("")
    lines.append("## Routenschluss")
    lines.append("")
    lines.append(
        "Die Route \"zentrale Anti-Konzentration plus algebraischer Quotient\" spaltet "
        "in zwei Fälle:"
    )
    lines.append("")
    lines.append(
        "1. **Unabhängiger Split:** \\(Z_E\\ge N^{-\\varepsilon}\\) und "
        "\\(A_E\\le N^{\\varepsilon}\\). Das wäre stark genug, ist aber mit den "
        "Goldfeld-Szpiro-/De-Weger-Erwartungen und dem Reyssat-Signal nicht plausibel."
    )
    lines.append(
        "2. **Gekoppelte Form:** \\(Z_E\\ge A_E N^{-\\varepsilon}\\). Das ist exakt "
        "die Periodenuntergrenze \\(P_E\\ge N^{-\\varepsilon}\\)."
    )
    lines.append("")
    lines.append(
        "Damit ist eine reine L-Wert-Anti-Konzentration geschlossen. Offen bleibt nur "
        "eine echte gekoppelte Struktur, die \\(Z_E/A_E\\) direkt kontrolliert; das ist "
        "inhaltlich dieselbe harte Tür wie die Perioden- oder Modulargradroute."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append("- `_scripts/anc_quotient_coupling_ledger.py`")
    lines.append(f"- `_data/anc_quotient_coupling_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = [enrich(row) for row in AUDITED_ROWS]
    rows.sort(key=lambda item: float(item["quality_rad"]), reverse=True)
    payload = build_payload(rows)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(payload), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
