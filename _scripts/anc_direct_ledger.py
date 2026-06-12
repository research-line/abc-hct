"""Direct ANC+ period ledger for the EM-1 Frey triples.

This script deliberately avoids C3/level-lowering data.  It measures the
archimedean period target itself:

    lambda_model * sqrt(rad(abc))

For Frey curves, the model shortest lattice vector has the form

    lambda_model = 2 K(min(a/c,b/c)) / sqrt(c),

where K is the complete elliptic integral in the parameter convention.
Thus

    -log(lambda_model * sqrt(rad(abc)))
      = 0.5 * log(c / rad(abc)) - log(2K(min(a/c,b/c))).

The report records this identity numerically and keeps the conclusion honest:
the direct ANC+ route is exactly the period/radical defect problem.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P2_DATA = ROOT / "_data" / "em1" / "pari_p2_results.jsonl"
DATE = "2026-05-09"
JSON_OUT = ROOT / "_data" / f"anc_direct_ledger_{DATE}.json"
MD_OUT = ROOT / "_proof-notes" / "ANC_plus_direct_attack.md"


def factorize(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    d = 2
    value = abs(n)
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


def elliptic_k_parameter(m: float) -> float:
    # K(m) = pi / (2 AGM(1, sqrt(1-m))) for parameter m.
    return math.pi / (2.0 * agm(1.0, math.sqrt(max(0.0, 1.0 - m))))


def lambda_shape(a: int, b: int, c: int) -> float:
    m = min(a / c, b / c)
    return 2.0 * elliptic_k_parameter(m)


def load_triples() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in P2_DATA.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def compute_rows() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in load_triples():
        a = int(row["a"])
        b = int(row["b"])
        c = int(row["c"])
        rad_abc = radical_from_parts(a, b, c)
        n_cond = int(row["N_cond"])
        shape = lambda_shape(a, b, c)
        lambda_model = shape / math.sqrt(c)
        lambda_sqrt_rad = lambda_model * math.sqrt(rad_abc)
        lambda_sqrt_cond = lambda_model * math.sqrt(n_cond)
        c_defect = math.log(c / rad_abc)
        quality = math.log(c) / math.log(rad_abc)
        period_loss = -math.log(lambda_sqrt_rad)
        identity_loss = 0.5 * c_defect - math.log(shape)
        eps_needed = max(0.0, period_loss / math.log(rad_abc))
        output.append(
            {
                "label": row["label"],
                "a": a,
                "b": b,
                "c": c,
                "rad_abc": rad_abc,
                "N_cond": n_cond,
                "quality": quality,
                "c_defect": c_defect,
                "shape_2K": shape,
                "lambda_model": lambda_model,
                "lambda_sqrt_rad": lambda_sqrt_rad,
                "lambda_sqrt_cond": lambda_sqrt_cond,
                "period_loss_rad": period_loss,
                "identity_loss_check": identity_loss,
                "epsilon_needed_rad": eps_needed,
                "root_number_original": int(row["root_number"]),
            }
        )
    output.sort(key=lambda item: float(item["quality"]), reverse=True)
    return output


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def build_report(rows: list[dict[str, object]]) -> str:
    champion_rows = [r for r in rows if float(r["quality"]) >= 1.4]
    all_shapes = [float(r["shape_2K"]) for r in rows]

    lines: list[str] = []
    lines.append("# ANC+ direkt: Perioden-Ledger")
    lines.append("")
    lines.append(f"**Datum:** {DATE}")
    lines.append("**Status:** Loop 66 / direkte ANC+-Normalisierung nach EM-4.")
    lines.append("")
    lines.append("## Kernidentität")
    lines.append("")
    lines.append(
        "Für Frey-Kurven ist die archimedische Modell-Lattice-Größe bereits "
        "vollständig auf den abc-Defekt normalisiert:"
    )
    lines.append("")
    lines.append("$$")
    lines.append(
        "\\lambda_{\\rm model}=\\frac{2K(\\min(a/c,b/c))}{\\sqrt c},\\qquad"
    )
    lines.append(
        "-\\log(\\lambda_{\\rm model}\\sqrt{\\operatorname{rad}(abc)})"
        "=\\frac12\\log\\frac{c}{\\operatorname{rad}(abc)}"
        "-\\log(2K(\\min(a/c,b/c)))."
    )
    lines.append("$$")
    lines.append("")
    lines.append(
        "Der Formfaktor `2K(min(a/c,b/c))` liegt im EM-1-Sample im engen Band "
        f"{fmt(min(all_shapes))} bis {fmt(max(all_shapes))}; der unbeschränkte "
        "Teil ist genau `0.5 log(c/rad(abc))`."
    )
    lines.append("")
    lines.append(
        "Néron-Minimalisierung kann diese Modellgröße durch einen zusätzlichen "
        "Skalierungsfaktor verändern. Für die direkte ANC+-Frage ist das kein "
        "neuer freier Kanal: Der unbeschränkte Defektterm bleibt "
        "`0.5 log(c/rad(abc))`; alle geometrischen Formfaktoren sind bereits "
        "durch Shape-Elimination kontrolliert."
    )
    lines.append("")
    lines.append("## Champion-Tabelle")
    lines.append("")
    lines.append(
        "| Tripel | q | C-defect | 2K-shape | λ√rad | benötigtes ε | root(original) |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in champion_rows:
        lines.append(
            "| {label} | {q} | {defect} | {shape} | {lsr} | {eps} | {root} |".format(
                label=row["label"],
                q=fmt(float(row["quality"])),
                defect=fmt(float(row["c_defect"])),
                shape=fmt(float(row["shape_2K"])),
                lsr=fmt(float(row["lambda_sqrt_rad"])),
                eps=fmt(float(row["epsilon_needed_rad"])),
                root=row["root_number_original"],
            )
        )
    lines.append("")
    lines.append("## Direktes ANC+-Urteil")
    lines.append("")
    lines.append(
        "Die direkte Periodenroute hat keinen versteckten geometrischen Spielraum "
        "mehr. Nach Shape-Elimination ist die Aussage"
    )
    lines.append("")
    lines.append("$$\\lambda_{\\rm model}\\ge c_\\varepsilon\\,N^{-1/2-\\varepsilon}$$")
    lines.append("")
    lines.append(
        "äquivalent dazu, den Defekt `log(c/rad(abc))` logarithmisch zu "
        "kontrollieren. Der Formfaktor ist beschränkt; er kann keine wachsende "
        "abc-Qualität bezahlen."
    )
    lines.append("")
    lines.append(
        "Damit ist `ANC+ direkt` als rein archimedischer/AGM-Beweis kein neuer "
        "Hebel, sondern die schärfste Normalform der Kernlücke. Ein echter "
        "direkter Angriff muss außerhalb dieser Identität ansetzen:"
    )
    lines.append("")
    lines.append("- Modulargrad-Obergrenze `deg(phi_E) <= N^{2+epsilon}`;")
    lines.append("- Goldfeld-Szpiro-/Sha-Kontrolle für den BSD-Quotienten;")
    lines.append("- oder eine echte zentrale Anti-Konzentration mit Kontrolle des algebraischen Quotienten.")
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "Der nächste direkte ANC+-Schritt sollte nicht weitere Periodenformeln "
        "suchen. Diese sind ausgeschöpft. Sinnvoll ist nur eine der drei "
        "äquivalent schweren Formen: Modulargrad, Sha/Goldfeld-Szpiro oder "
        "Hecke-/Modularsymbol-Anti-Konzentration mit algebraischer Quotientenkontrolle."
    )
    lines.append("")
    lines.append("## Artefakte")
    lines.append("")
    lines.append(f"- `_scripts/anc_direct_ledger.py`")
    lines.append(f"- `_data/anc_direct_ledger_{DATE}.json`")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = compute_rows()
    JSON_OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(rows), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
