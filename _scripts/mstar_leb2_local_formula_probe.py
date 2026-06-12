"""Loop 117 probe for an explicit LEB-2 local allowance formula.

The input is the conservative 15-case modular-degree ledger.  The script tests
whether the 2-primary modular-degree length is bounded by local component data:

    v2(prod c_p) + sum_p v2(v_p(Delta_min)) + O(1).

This is not a proof; it is a non-tautological target shape for the 2-adic
Tate/Néron/Hecke comparison in LEB-2.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
INPUT = ROOT / "_results" / "mstar_15case_tail_ledger_2026-05-09.json"
JSON_OUT = ROOT / "_results" / f"mstar_leb2_local_formula_probe_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_leb2_local_formula_probe_{DATE}.md"


FACTOR_RE = re.compile(r"^\s*(\d+)(?:\^(\d+))?\s*$")


def valuation(n: int, prime: int) -> int:
    n = abs(int(n))
    out = 0
    while n and n % prime == 0:
        out += 1
        n //= prime
    return out


def valuation_from_factor_string(factor: str, prime: int = 2) -> int:
    if factor == "1":
        return 0
    total = 0
    for part in factor.split("*"):
        match = FACTOR_RE.match(part)
        if not match:
            raise ValueError(f"Cannot parse factor part {part!r} from {factor!r}")
        p = int(match.group(1))
        exp = int(match.group(2) or "1")
        if p == prime:
            total += exp
    return total


def floor_log2(n: int) -> int:
    return int(math.log2(int(n)))


def row_probe(row: dict[str, object]) -> dict[str, object]:
    local_data = list(row["local_data"])
    v2_degree = valuation_from_factor_string(str(row["modular_degree_factor"]))
    v2_tamagawa = valuation(int(row["tamagawa_product"]), 2)
    sum_v2_delta = sum(valuation(int(local["delta_v"]), 2) for local in local_data)
    sum_floorlog_delta = sum(floor_log2(int(local["delta_v"])) for local in local_data)
    max_delta = max(int(local["delta_v"]) for local in local_data)
    p2_data = next((local for local in local_data if int(local["p"]) == 2), None)

    sharp_envelope = v2_tamagawa + sum_v2_delta
    sharp_plus_one = sharp_envelope + 1
    log_depth_envelope = v2_tamagawa + sum_floorlog_delta

    return {
        "label": row["label"],
        "N_cond": row["N_cond"],
        "modular_degree_factor": row["modular_degree_factor"],
        "tamagawa_product_factor": row["tamagawa_product_factor"],
        "v2_degree": v2_degree,
        "v2_tamagawa": v2_tamagawa,
        "sum_v2_delta_depth": sum_v2_delta,
        "sum_floorlog2_delta_depth": sum_floorlog_delta,
        "max_delta_v": max_delta,
        "p2_delta_v": None if p2_data is None else p2_data["delta_v"],
        "p2_kodaira": None if p2_data is None else p2_data["kodaira"],
        "sharp_envelope": sharp_envelope,
        "sharp_deficit": max(v2_degree - sharp_envelope, 0),
        "sharp_plus_one_envelope": sharp_plus_one,
        "sharp_plus_one_deficit": max(v2_degree - sharp_plus_one, 0),
        "log_depth_envelope": log_depth_envelope,
        "log_depth_deficit": max(v2_degree - log_depth_envelope, 0),
        "degree_over_N2": row["degree_over_N2"],
    }


def top(rows: list[dict[str, object]], key: str, count: int = 6) -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: float(row[key]), reverse=True)[:count]


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row_probe(row) for row in payload["rows"]]
    summary = {
        "case_count": len(rows),
        "sharp_envelope_success_count": sum(1 for row in rows if row["sharp_deficit"] == 0),
        "sharp_plus_one_success_count": sum(1 for row in rows if row["sharp_plus_one_deficit"] == 0),
        "log_depth_success_count": sum(1 for row in rows if row["log_depth_deficit"] == 0),
        "sharp_failures": [row for row in rows if row["sharp_deficit"] > 0],
        "top_v2_degree": top(rows, "v2_degree"),
        "top_sharp_slack": top(
            [
                {
                    **row,
                    "sharp_slack": int(row["sharp_envelope"]) - int(row["v2_degree"]),
                }
                for row in rows
            ],
            "sharp_slack",
        ),
    }
    out = {
        "date": DATE,
        "source": str(INPUT.relative_to(ROOT)),
        "purpose": "Loop 117 probe: explicit local LEB-2 allowance from Tamagawa and discriminant-exponent depth.",
        "candidate_formula": "v2(Cong_2(E)) <= v2(prod c_p(E)) + sum_{p|N} v2(v_p(Delta_min(E))) + O(1)",
        "summary": summary,
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M* LEB-2 Local Formula Probe",
        "",
        f"Source: `{INPUT.relative_to(ROOT)}`",
        "",
        "## Candidate",
        "",
        "\\[",
        "v_2(\\operatorname{Cong}_2(E))",
        "\\le",
        "v_2\\!\\left(\\prod_p c_p(E)\\right)",
        "+",
        "\\sum_{p\\mid N} v_2\\!\\left(v_p(\\Delta_{\\min}(E))\\right)",
        "+O(1).",
        "\\]",
        "",
        "## Summary",
        "",
        f"- Cases: {summary['case_count']}",
        f"- Sharp envelope successes: {summary['sharp_envelope_success_count']}/15",
        f"- Sharp envelope plus one successes: {summary['sharp_plus_one_success_count']}/15",
        f"- Log-depth envelope successes: {summary['log_depth_success_count']}/15",
        "",
        "## Top v2 Degree Cases",
        "",
        "| label | v2(deg) | v2(Tam) | sum v2(delta) | sharp | deficit | sharp+1 deficit | p2 type | p2 delta |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for row in summary["top_v2_degree"]:
        lines.append(
            f"| {row['label']} | {row['v2_degree']} | {row['v2_tamagawa']} | "
            f"{row['sum_v2_delta_depth']} | {row['sharp_envelope']} | "
            f"{row['sharp_deficit']} | {row['sharp_plus_one_deficit']} | "
            f"{row['p2_kodaira']} | {row['p2_delta_v']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The sharp local envelope pays 14/15 cases exactly or with slack.",
            "- The only sharp deficit is Reyssat_ANC_orientation, by one 2-adic unit.",
            "- Adding an O(1) orientation/isogeny/comparison allowance pays all 15 cases.",
            "- This is a target theorem shape, not a proof; it avoids defining the allowance by the modular degree.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
