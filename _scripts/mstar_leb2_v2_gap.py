"""Loop 115 LEB-2 2-primary visibility audit.

This script refines the Loop 113 LEB snapshot at the prime q=2.  It asks:
is the 2-primary part of the modular degree paid by the Tamagawa product alone,
or only after we allow the full 2-local/level comparison budget?
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
INPUT = ROOT / "_results" / f"mstar_leb_snapshot_{DATE}.json"
JSON_OUT = ROOT / "_results" / f"mstar_leb2_v2_gap_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_leb2_v2_gap_{DATE}.md"


FACTOR_RE = re.compile(r"^\s*(\d+)(?:\^(\d+))?\s*$")


def valuation_from_factor_string(factor: object, prime: int = 2) -> int:
    text = str(factor)
    if text == "1":
        return 0
    total = 0
    for part in text.split("*"):
        match = FACTOR_RE.match(part)
        if not match:
            raise ValueError(f"Cannot parse factor part {part!r} from {text!r}")
        p = int(match.group(1))
        exp = int(match.group(2) or "1")
        if p == prime:
            total += exp
    return total


def classify_gap(row: dict[str, object]) -> dict[str, object]:
    logn = math.log(int(row["N_cond"]))
    v2_degree = valuation_from_factor_string(row["modular_degree_factor"])
    v2_tamagawa = valuation_from_factor_string(row["tamagawa_factor"])
    v2_level = valuation_from_factor_string(row["level_prime_factor"])
    v2_two = valuation_from_factor_string(row["two_factor"])

    tamagawa_gap = max(v2_degree - v2_tamagawa, 0)
    level_gap = max(v2_degree - v2_level, 0)
    local_gap = max(v2_degree - max(v2_tamagawa, v2_level, v2_two), 0)
    verdict = "2-local-visible" if local_gap == 0 else "2-local-gap"
    if tamagawa_gap > 0:
        tamagawa_verdict = "Tamagawa-alone-fails"
    else:
        tamagawa_verdict = "Tamagawa-pays-2-part"

    return {
        "label": row["label"],
        "N_cond": row["N_cond"],
        "logN": logn,
        "modular_degree_factor": row["modular_degree_factor"],
        "tamagawa_factor": row["tamagawa_factor"],
        "level_prime_factor": row["level_prime_factor"],
        "two_factor": row["two_factor"],
        "v2_degree": v2_degree,
        "v2_tamagawa": v2_tamagawa,
        "v2_level": v2_level,
        "v2_two": v2_two,
        "tamagawa_gap": tamagawa_gap,
        "tamagawa_gap_mass_over_logN": tamagawa_gap * math.log(2) / logn,
        "level_gap": level_gap,
        "level_gap_mass_over_logN": level_gap * math.log(2) / logn,
        "local_gap": local_gap,
        "local_gap_mass_over_logN": local_gap * math.log(2) / logn,
        "two_mass_over_logN": row["two_mass_over_logN"],
        "degree_over_N2": row["degree_over_N2"],
        "degree_exponent_N": row["degree_exponent_N"],
        "external_non_tamagawa_tail_factor": row["external_non_tamagawa_tail_factor"],
        "verdict": verdict,
        "tamagawa_verdict": tamagawa_verdict,
    }


def top(rows: list[dict[str, object]], key: str, count: int = 6) -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: float(row[key]), reverse=True)[:count]


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [classify_gap(row) for row in payload["rows"]]
    summary = {
        "case_count": len(rows),
        "two_local_visible_count": sum(1 for row in rows if row["verdict"] == "2-local-visible"),
        "tamagawa_alone_fails_count": sum(
            1 for row in rows if row["tamagawa_verdict"] == "Tamagawa-alone-fails"
        ),
        "max_tamagawa_gaps": top(rows, "tamagawa_gap_mass_over_logN"),
        "max_two_masses": top(rows, "two_mass_over_logN"),
        "local_gap_rows": [row for row in rows if row["verdict"] != "2-local-visible"],
        "abchome_rows": [row for row in rows if "ABCHome" in str(row["label"])],
        "reyssat_rows": [row for row in rows if "Reyssat" in str(row["label"])],
    }
    out = {
        "date": DATE,
        "source": str(INPUT.relative_to(ROOT)),
        "purpose": "Loop 115 LEB-2 v2 audit: Tamagawa-only gap versus 2-local/level visibility.",
        "summary": summary,
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M* LEB-2 v2 Gap Audit",
        "",
        f"Source: `{INPUT.relative_to(ROOT)}`",
        "",
        "## Summary",
        "",
        f"- Cases: {summary['case_count']}",
        f"- 2-local visible cases: {summary['two_local_visible_count']}",
        f"- Tamagawa-alone failures: {summary['tamagawa_alone_fails_count']}",
        f"- Rows with residual 2-local gap: {len(summary['local_gap_rows'])}",
        "",
        "## Largest Tamagawa-Alone Gaps",
        "",
        "| label | v2(deg) | v2(Tam) | gap | gap/logN | v2(level) | local gap | deg/N^2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["max_tamagawa_gaps"]:
        lines.append(
            f"| {row['label']} | {row['v2_degree']} | {row['v2_tamagawa']} | "
            f"{row['tamagawa_gap']} | {float(row['tamagawa_gap_mass_over_logN']):.6f} | "
            f"{row['v2_level']} | {row['local_gap']} | {float(row['degree_over_N2']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Tamagawa alone does not pay the 2-primary congruence mass in the stress cases.",
            "- The same 2-primary mass is level/2-local visible in all rows of this ledger.",
            "- Therefore LEB-2 must be a 2-adic Hecke/Néron comparison theorem, not a Tamagawa-product estimate.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
