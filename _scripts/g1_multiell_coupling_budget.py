"""Budget the remaining G1 multi-ell coupling route.

The earlier G1 probes show that compatible integral lifts live in a free
rank-2 quotient.  Coupling several residual primes ell can only see common
integral divisibility unless a new arithmetic pairing/filtration is supplied.
This ledger combines:

- active m_ell pairs from the G1 requirements file;
- C3/drop capacity from the EM-4 capacity obstruction;
- the free-content invariant from the integral lattice probe where available.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "_data" / "g1_maxideal_projection_requirements_2026-05-09.json"
C3 = ROOT / "_data" / "em4_c3_capacity_obstruction_2026-05-09.json"
CONTENT = ROOT / "_results" / "g1_free_content_invariant_probe_2026-05-09.json"
OUT = ROOT / "_data" / "g1_multiell_coupling_budget_2026-05-09.json"


def safe_ratio(num: float, den: float) -> float | None:
    if den <= 0:
        return None
    return num / den


def main() -> int:
    req = json.loads(REQ.read_text(encoding="utf-8"))
    c3_rows = {row["label"]: row for row in json.loads(C3.read_text(encoding="utf-8"))}
    content_rows = {}
    if CONTENT.exists():
        content = json.loads(CONTENT.read_text(encoding="utf-8"))
        content_rows = {row["label"]: row for row in content["results"]}

    by_label: dict[str, list[dict]] = {}
    for pair in req["active_pairs"]:
        by_label.setdefault(pair["label"], []).append(pair)

    rows = []
    for label, pairs in sorted(by_label.items(), key=lambda item: max(x["quality"] for x in item[1]), reverse=True):
        c3 = c3_rows.get(label)
        active_ells = sorted(int(x["ell"]) for x in pairs)
        D_product = math.prod(int(x["D_ell"]) for x in pairs)
        sum_log_D = sum(math.log(int(x["D_ell"])) for x in pairs)
        feas = sorted(set(x["feasibility"] for x in pairs))
        content = content_rows.get(label)
        content_summary = None
        if content:
            content_summary = {
                "frey_row_content": content["frey_row_content"],
                "frey_column_content": content["frey_column_content"],
                "row_eq_frey": content["control_row_content_stats"]["count_eq_frey"],
                "column_eq_frey": content["control_column_content_stats"]["count_eq_frey"],
                "controls_tested": content["controls_tested"],
            }
        rows.append(
            {
                "label": label,
                "quality": pairs[0]["quality"],
                "a": pairs[0]["a"],
                "b": pairs[0]["b"],
                "c": pairs[0]["c"],
                "N_cond": pairs[0]["N_cond"],
                "active_pair_count": len(pairs),
                "active_ells": active_ells,
                "D_ell_values": [int(x["D_ell"]) for x in pairs],
                "D_product": D_product,
                "sum_log_D_active_pairs": sum_log_D,
                "feasibility_set": feas,
                "c_defect_log_c_over_rad": c3.get("c_defect_log_c_over_rad") if c3 else None,
                "exponent_excess_log_abc_over_rad": c3.get("exponent_excess_log_abc_over_rad") if c3 else None,
                "c3_squarefree_capacity": c3.get("squarefree_capacity") if c3 else None,
                "active_pair_capacity_over_c_defect": (
                    safe_ratio(sum_log_D, c3["c_defect_log_c_over_rad"])
                    if c3 and c3["c_defect_log_c_over_rad"] > 0
                    else None
                ),
                "active_pair_capacity_over_exponent_excess": (
                    safe_ratio(sum_log_D, c3["exponent_excess_log_abc_over_rad"])
                    if c3
                    else None
                ),
                "content_probe": content_summary,
            }
        )

    multi = [row for row in rows if row["active_pair_count"] >= 2]
    summary = {
        "labels": len(rows),
        "active_pairs": sum(row["active_pair_count"] for row in rows),
        "single_ell_labels": sum(1 for row in rows if row["active_pair_count"] == 1),
        "multi_ell_labels": len(multi),
        "multi_ell_small_labels": sum(1 for row in multi if row["feasibility_set"] == ["small"]),
        "multi_ell_hard_labels": sum(1 for row in multi if "hard" in row["feasibility_set"]),
        "max_active_pair_count": max(row["active_pair_count"] for row in rows),
        "max_active_pair_capacity_over_exponent_excess": max(
            row["active_pair_capacity_over_exponent_excess"] or 0 for row in rows
        ),
        "max_active_pair_capacity_over_c_defect": max(
            row["active_pair_capacity_over_c_defect"] or 0 for row in rows
        ),
        "structural_conclusion": (
            "Multi-ell support is sparse: no label has more than two active ell. "
            "Compatible integral lifts reduce to the same free rank-2 lattice vector; "
            "without a new pairing/filtration, cross-ell coupling only sees content/divisibility, "
            "already tested in Loop 87."
        ),
    }
    OUT.write_text(json.dumps({"status": "ok", "summary": summary, "rows": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
