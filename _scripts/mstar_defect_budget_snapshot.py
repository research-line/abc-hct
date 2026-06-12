"""Loop 103 defect-budget snapshot from the Loop 94 M* ledger.

This script does not call Sage. It reuses the conservative 15-case modular
degree ledger and splits modular-degree prime mass into level-prime,
external, Tamagawa-visible, and non-Tamagawa tail pieces.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
INPUT = ROOT / "_results" / f"mstar_15case_tail_ledger_{DATE}.json"
JSON_OUT = ROOT / "_results" / f"mstar_defect_budget_snapshot_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_defect_budget_snapshot_{DATE}.md"


def factorint(n: int) -> dict[int, int]:
    n = abs(int(n))
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


def multiply_factor(factors: dict[int, int]) -> int:
    out = 1
    for p, e in factors.items():
        out *= p**e
    return out


def factor_string(factors: dict[int, int]) -> str:
    if not factors:
        return "1"
    parts = []
    for p in sorted(factors):
        e = factors[p]
        parts.append(str(p) if e == 1 else f"{p}^{e}")
    return " * ".join(parts)


def intersect_factor(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
    return {p: min(e, b[p]) for p, e in a.items() if p in b}


def subtract_factor(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
    out = {}
    for p, e in a.items():
        rem = e - b.get(p, 0)
        if rem > 0:
            out[p] = rem
    return out


def log_mass(factors: dict[int, int]) -> float:
    return sum(e * math.log(p) for p, e in factors.items())


def split_row(row: dict[str, object]) -> dict[str, object]:
    label = str(row["label"])
    n = int(row["N_cond"])
    md = int(row["modular_degree"])
    tam = int(row["tamagawa_product"])
    logn = math.log(n)

    nfac = factorint(n)
    mdfac = factorint(md)
    tamfac = factorint(tam)

    level = {p: e for p, e in mdfac.items() if p in nfac}
    external = {p: e for p, e in mdfac.items() if p not in nfac}
    tam_visible = intersect_factor(mdfac, tamfac)
    non_tam = subtract_factor(mdfac, tam_visible)
    external_non_tam = {p: e for p, e in non_tam.items() if p not in nfac}
    two_part = {2: mdfac[2]} if 2 in mdfac else {}

    return {
        "label": label,
        "N_cond": n,
        "logN": logn,
        "modular_degree": md,
        "modular_degree_factor": factor_string(mdfac),
        "tamagawa_product": tam,
        "tamagawa_factor": factor_string(tamfac),
        "degree_over_N2": row["degree_over_N2"],
        "degree_exponent_N": row["degree_exponent_N"],
        "level_prime_part": multiply_factor(level),
        "level_prime_factor": factor_string(level),
        "level_prime_mass_over_logN": log_mass(level) / logn,
        "external_part": multiply_factor(external),
        "external_factor": factor_string(external),
        "external_mass_over_logN": log_mass(external) / logn,
        "tamagawa_visible_part": multiply_factor(tam_visible),
        "tamagawa_visible_factor": factor_string(tam_visible),
        "tamagawa_visible_mass_over_logN": log_mass(tam_visible) / logn,
        "non_tamagawa_tail_part": multiply_factor(non_tam),
        "non_tamagawa_tail_factor": factor_string(non_tam),
        "non_tamagawa_tail_mass_over_logN": log_mass(non_tam) / logn,
        "external_non_tamagawa_tail_part": multiply_factor(external_non_tam),
        "external_non_tamagawa_tail_factor": factor_string(external_non_tam),
        "external_non_tamagawa_tail_mass_over_logN": log_mass(external_non_tam) / logn,
        "two_part": multiply_factor(two_part),
        "two_factor": factor_string(two_part),
        "two_mass_over_logN": log_mass(two_part) / logn,
    }


def top(rows: list[dict[str, object]], key: str, count: int = 5) -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: float(row[key]), reverse=True)[:count]


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [split_row(row) for row in payload["rows"]]
    summary = {
        "case_count": len(rows),
        "max_external_mass": top(rows, "external_mass_over_logN", 3),
        "max_external_non_tamagawa_tail": top(rows, "external_non_tamagawa_tail_mass_over_logN", 5),
        "max_two_mass": top(rows, "two_mass_over_logN", 5),
        "max_non_tamagawa_tail": top(rows, "non_tamagawa_tail_mass_over_logN", 5),
    }
    out = {
        "date": DATE,
        "source": str(INPUT.relative_to(ROOT)),
        "purpose": "Loop 103 defect-budget split for L2/FPE diagnostics.",
        "summary": summary,
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M* Defect-Budget Snapshot",
        "",
        f"Source: `{INPUT.relative_to(ROOT)}`",
        "",
        "## Top External Non-Tamagawa Tail",
        "",
        "| label | factor | mass/logN | deg/N^2 |",
        "|---|---:|---:|---:|",
    ]
    for row in summary["max_external_non_tamagawa_tail"]:
        lines.append(
            f"| {row['label']} | `{row['external_non_tamagawa_tail_factor']}` | "
            f"{float(row['external_non_tamagawa_tail_mass_over_logN']):.6f} | "
            f"{float(row['degree_over_N2']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Top 2-Adic Degree Mass",
            "",
            "| label | factor | mass/logN | deg/N^2 |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in summary["max_two_mass"]:
        lines.append(
            f"| {row['label']} | `{row['two_factor']}` | "
            f"{float(row['two_mass_over_logN']):.6f} | "
            f"{float(row['degree_over_N2']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `external_non_tamagawa_tail` is the part of the modular degree whose primes neither divide the conductor nor the Tamagawa product.",
            "- This is only a diagnostic split; it is not a proof of local/global origin.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
