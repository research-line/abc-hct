#!/usr/bin/env python3
"""Loop 138: staged charpoly/Hecke-field data path.

This is a planning/audit script, not a heavy Sage job.  It aggregates existing
dimension and LMFDB-gap diagnostics into a concrete computational route that
avoids materializing the full level 240672 modular-symbol space first.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"
DATE = "2026-05-10"

FEASIBILITY = RESULTS / "mstar_level240672_feasibility_2026-05-09.json"
MISSING = RESULTS / "mstar_lmfdb_missing_orbit_audit_2026-05-09.json"
OLD_T5 = RESULTS / "mstar_oldlevel_t5_charpoly_scan_2026-05-09.json"

N = 240_672
Q = 3863
TEST_PRIMES = [5, 7, 11, 13]


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def oldlevel_row_by_level(feasibility: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for row in feasibility["old_levels_top_by_new_dimension"]:
        out[int(row["level"])] = row
    return out


def main() -> None:
    feasibility = load(FEASIBILITY)
    missing = load(MISSING)
    old_t5 = load(OLD_T5)

    old_by_level = oldlevel_row_by_level(feasibility)
    missing_levels = [int(level) for level in missing["summary"]["levels_with_newspace_rows"]]

    targets = []
    for row in missing["rows"]:
        level = int(row["level"])
        dim_row = old_by_level.get(level, {})
        newspace = row["newspaces"][0] if row.get("newspaces") else {}
        targets.append(
            {
                "level": level,
                "factor": row["level_factor"],
                "new_dimension": int(newspace.get("mf_new_dim") or dim_row.get("dimension_new_cusp_forms")),
                "total_cusp_dimension": int(dim_row.get("dimension_cusp_forms", 0) or 0),
                "sturm_bound": int(dim_row.get("sturm_bound_weight2", 0) or 0),
                "oldspace_contribution_at_N": int(dim_row.get("oldspace_contribution_at_N", 0) or 0),
                "lmfdb_total_trace_display": newspace.get("trace_display"),
                "lmfdb_has_orbit_data": bool(row.get("usable_orbit_data")),
                "lmfdb_has_charpoly_data": bool(row.get("usable_charpoly_data")),
                "priority": "R1" if level == 60168 else "R2",
                "recommended_first_test": "det(T_5-a_5(E)) mod 3863 on S2(Gamma0(M))^new",
            }
        )
    targets.sort(key=lambda item: (item["new_dimension"], item["level"]))

    main = feasibility["main_level"]
    newlevel_target = {
        "level": N,
        "factor": main["factor"],
        "new_dimension": int(main["dimension_new_cusp_forms"]),
        "total_cusp_dimension": int(main["dimension_cusp_forms"]),
        "sturm_bound": int(main["sturm_bound_weight2"]),
        "old_dimension": int(main["dimension_old_cusp_forms"]),
        "recommended_first_test": "after oldlevel cleanup: det(T_5-a_5(E)) mod 3863 on the true new_subspace",
        "risk": "high; split by Atkin-Lehner signs before a full determinant if possible",
    }

    old_t5_summary = old_t5.get("summary", {})
    stages = [
        {
            "id": "R0",
            "name": "Do not use LMFDB total traces as orbit evidence",
            "reason": (
                "The missing levels have only mf_newspaces rows. Total traces do not "
                "exclude individual orbit factors unless a one-orbit decomposition is known."
            ),
            "status": "guardrail",
        },
        {
            "id": "R1",
            "name": "Restlevel determinant filter",
            "targets": [item["level"] for item in targets],
            "test": "Compute det(T_p-a_p(E)) mod 3863 on the newspace, starting with p=5.",
            "success_condition": "nonzero determinant kills the level for that Reyssat orientation",
            "continuation": "only if determinant is zero, compute the kernel and add p=7,11,13",
            "status": "next executable data step",
        },
        {
            "id": "R2",
            "name": "Kernel cascade",
            "test": "Intersect kernels of T_p-a_p(E) modulo 3863 for p=5,7,11,13.",
            "success_condition": "zero kernel kills the level; nonzero kernel is a real residual candidate",
            "status": "conditional",
        },
        {
            "id": "R3",
            "name": "Orbit/field recovery only after a kernel survivor",
            "test": "Compute factor data, minimal polynomials, or q-adic field primes only on surviving subspace.",
            "reason": "Full charpoly/order data are too expensive before the determinant/kernelfilter.",
            "status": "conditional",
        },
        {
            "id": "N1",
            "name": "True newlevel after restlevels",
            "target": N,
            "test": "Run the same determinant/kernelfilter on the 4752-dimensional new_subspace.",
            "guardrail": "Avoid full S2 dimension 42209; use new_subspace and Atkin-Lehner splitting if Sage exposes it.",
            "status": "high-risk later step",
        },
        {
            "id": "F1",
            "name": "FOG-FC evidence, not proof",
            "test": "If q=3863 is killed or localized, repeat for several external primes and small T to estimate index support.",
            "guardrail": "This remains data support for FOG-FC, not a proof of the asymptotic theorem.",
            "status": "later evidence step",
        },
    ]

    payload = {
        "date": DATE,
        "purpose": "Staged computational data path for missing oldlevel/newlevel Hecke data.",
        "q": Q,
        "frey_level": N,
        "test_primes": TEST_PRIMES,
        "input_files": [str(FEASIBILITY), str(MISSING), str(OLD_T5)],
        "existing_t5_scan_summary": old_t5_summary,
        "missing_oldlevel_targets": targets,
        "true_newlevel_target": newlevel_target,
        "stages": stages,
        "interpretation": (
            "The next computational investment should be a mod-q determinant/kernel cascade "
            "on the three missing oldlevels, not a full level-240672 modular-symbol build. "
            "Only surviving kernels justify expensive orbit/Hecke-field recovery."
        ),
    }

    json_path = RESULTS / f"mstar_charpoly_data_path_{DATE}.json"
    md_path = RESULTS / f"mstar_charpoly_data_path_{DATE}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M*: Charpoly-/Hecke-Feld-Datenpfad",
        "",
        f"Datum: {DATE}",
        "",
        "## Kurzbefund",
        "",
        "Der nächste rechnerische Schritt sollte kein voller ModularSymbols-Lauf auf",
        "\\(N=240672\\) sein. Sinnvoller ist eine gestufte Mod-\\(3863\\)-",
        "Determinant-/Kern-Kaskade auf den drei Rest-Oldlevels.",
        "",
        "## Ziellevels",
        "",
        "| Level | Faktor | Newdim | Gesamtdim | Sturm | Beitrag in N | Erste Probe |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in targets:
        lines.append(
            f"| {row['level']} | {row['factor']} | {row['new_dimension']} | "
            f"{row['total_cusp_dimension']} | {row['sturm_bound']} | "
            f"{row['oldspace_contribution_at_N']} | {row['recommended_first_test']} |"
        )

    lines.extend(
        [
            "",
            "## Echter New-Level",
            "",
            f"- Level: {newlevel_target['level']} = {newlevel_target['factor']}.",
            f"- Newdim: {newlevel_target['new_dimension']}.",
            f"- Gesamtdimension: {newlevel_target['total_cusp_dimension']}.",
            f"- Sturm-Bound: {newlevel_target['sturm_bound']}.",
            f"- Risiko: {newlevel_target['risk']}.",
            "",
            "## Gestufter Plan",
            "",
        ]
    )
    for stage in stages:
        lines.extend(
            [
                f"### {stage['id']} -- {stage['name']}",
                "",
                stage.get("test") or stage.get("reason") or "",
                "",
                f"Status: {stage['status']}.",
                "",
            ]
        )

    lines.extend(
        [
            "## Entscheidung",
            "",
            "Rechnerisch lohnt zuerst R1/R2 auf \\(60168,80224,120336\\).",
            "Wenn diese drei Levels sterben, bleibt der echte New-Level als einziger",
            "Datenkern. Wenn ein Restlevel überlebt, muss nur dieser Survivor",
            "teuer in Orbit-/Hecke-Feld-Daten zerlegt werden.",
            "",
            "Dieser Pfad ist Dateninfrastruktur für FOG-FC/NL-DualSmall; er ersetzt",
            "keinen asymptotischen Beweis.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(payload["interpretation"], ensure_ascii=False))


if __name__ == "__main__":
    main()
