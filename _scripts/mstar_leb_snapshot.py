"""Loop 113 local exception budget snapshot.

This reuses the Loop 103 defect-budget split and asks a narrower LEB question:
which modular-degree factors are already visible in level primes, 2-adic mass,
or Tamagawa/component factors, and which remain external non-local tails?
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
INPUT = ROOT / "_results" / "mstar_defect_budget_snapshot_2026-05-09.json"
JSON_OUT = ROOT / "_results" / f"mstar_leb_snapshot_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_leb_snapshot_{DATE}.md"


def classify(row: dict[str, object]) -> dict[str, object]:
    nonlocal_mass = float(row["external_non_tamagawa_tail_mass_over_logN"])
    if nonlocal_mass == 0:
        verdict = "LEB-visible"
    elif nonlocal_mass < 0.25:
        verdict = "small-nonlocal-tail"
    else:
        verdict = "nonlocal-tail"
    return {
        "label": row["label"],
        "N_cond": row["N_cond"],
        "modular_degree_factor": row["modular_degree_factor"],
        "tamagawa_factor": row["tamagawa_factor"],
        "level_prime_factor": row["level_prime_factor"],
        "two_factor": row["two_factor"],
        "external_factor": row["external_factor"],
        "external_non_tamagawa_tail_factor": row["external_non_tamagawa_tail_factor"],
        "external_non_tamagawa_tail_mass_over_logN": nonlocal_mass,
        "tamagawa_visible_mass_over_logN": row["tamagawa_visible_mass_over_logN"],
        "level_prime_mass_over_logN": row["level_prime_mass_over_logN"],
        "two_mass_over_logN": row["two_mass_over_logN"],
        "degree_over_N2": row["degree_over_N2"],
        "degree_exponent_N": row["degree_exponent_N"],
        "verdict": verdict,
    }


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [classify(row) for row in payload["rows"]]
    rows_sorted = sorted(rows, key=lambda row: float(row["external_non_tamagawa_tail_mass_over_logN"]), reverse=True)
    summary = {
        "case_count": len(rows),
        "leb_visible_count": sum(1 for row in rows if row["verdict"] == "LEB-visible"),
        "nonlocal_tail_count": sum(1 for row in rows if row["verdict"] == "nonlocal-tail"),
        "top_nonlocal_tails": rows_sorted[:5],
        "abchome_rows": [row for row in rows if "ABCHome" in str(row["label"])],
        "reyssat_rows": [row for row in rows if "Reyssat" in str(row["label"])],
    }
    out = {
        "date": DATE,
        "source": str(INPUT.relative_to(ROOT)),
        "purpose": "Loop 113 LEB snapshot: local-visible mass versus external non-Tamagawa tails.",
        "summary": summary,
        "rows": rows_sorted,
    }
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M* LEB Snapshot",
        "",
        f"Source: `{INPUT.relative_to(ROOT)}`",
        "",
        "## Summary",
        "",
        f"- Cases: {summary['case_count']}",
        f"- LEB-visible cases: {summary['leb_visible_count']}",
        f"- Nonlocal-tail cases: {summary['nonlocal_tail_count']}",
        "",
        "## Top External Non-Tamagawa Tails",
        "",
        "| label | tail | tail/logN | two/logN | Tamagawa/logN | level/logN | verdict |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary["top_nonlocal_tails"]:
        lines.append(
            f"| {row['label']} | `{row['external_non_tamagawa_tail_factor']}` | "
            f"{float(row['external_non_tamagawa_tail_mass_over_logN']):.6f} | "
            f"{float(row['two_mass_over_logN']):.6f} | "
            f"{float(row['tamagawa_visible_mass_over_logN']):.6f} | "
            f"{float(row['level_prime_mass_over_logN']):.6f} | {row['verdict']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- ABCHome_2 is LEB-visible: its stress is 2-adic/level/Tamagawa-visible, not an external nonlocal tail.",
            "- Reyssat remains the nonlocal test: the factor 3863 is not paid by the local Tamagawa/component ledger.",
            "- LEB therefore helps with local stress cases, but it does not prove NL-DualSmall.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
