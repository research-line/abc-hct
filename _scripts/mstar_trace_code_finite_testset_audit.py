#!/usr/bin/env python3
"""Finite-testset audit for the Frey-Legendre trace-code route.

This script only aggregates already generated local results. It does not query
LMFDB and does not attempt heavy Sage computations.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"
DATE = "2026-05-10"


def load_json(name: str) -> dict:
    with (RESULTS / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    old = load_json("mstar_lmfdb_oldlevel_trace_filter_2026-05-09.json")
    missing = load_json("mstar_lmfdb_missing_orbit_audit_2026-05-09.json")
    scale = load_json("mstar_trace_sieve_scale_2026-05-09.json")
    reyssat = load_json("mstar_reyssat_3863_probe_2026-05-09.json")

    by_level = old["summary"]["by_level"]
    orbit_levels = [row for row in by_level if row.get("coverage") == "orbit-traces"]
    newspace_only = [row for row in by_level if row.get("coverage") == "newspace-only"]

    loaded_orbit_dim = sum(int(row.get("orbit_dim_loaded", 0)) for row in orbit_levels)
    loaded_newdim = sum(int(row.get("newspace_dim", 0)) for row in orbit_levels)
    missing_newdim = sum(int(row.get("newspace_dim", 0)) for row in newspace_only)

    level_240672_new = next(
        row for row in scale["full_level_rows"] if row["name"] == "level_240672_new"
    )

    summary = {
        "date": DATE,
        "purpose": "Finite-testset audit for Frey-Legendre trace-code Minimum Distance.",
        "reyssat_weight_log3863_over_logN": math.log(3863) / math.log(240672),
        "oldlevel_orbit_levels_closed_count": len(orbit_levels),
        "oldlevel_orbit_levels_closed": [row["level"] for row in orbit_levels],
        "oldlevel_orbit_loaded_dimension": loaded_orbit_dim,
        "oldlevel_orbit_newdim_sum": loaded_newdim,
        "oldlevel_orbit_survivor_count": sum(int(row.get("survivor_count", 0)) for row in orbit_levels),
        "oldlevel_missing_orbit_levels": [row["level"] for row in newspace_only],
        "oldlevel_missing_orbit_newdim_sum": missing_newdim,
        "full_newlevel_240672_dimension": int(level_240672_new["dimension"]),
        "newlevel_240672_orbit_data_available": False,
        "trace_sieve_newlevel_bound_over_logN": float(level_240672_new["bound_over_logN"]),
        "trace_sieve_newlevel_bound_over_2logN": float(level_240672_new["bound_over_2logN"]),
        "reyssat_3863_cross_class_hits": int(reyssat["summary"]["cross_class_q_hits_count"]),
        "reyssat_3863_old_level_hits": int(reyssat["summary"]["old_level_15042_q_hits_count"]),
        "interpretation": (
            "Finite trace words close the loaded rational/oldlevel orbit data for q=3863, "
            "but there is no public orbit data for the true newlevel N=240672 or for the "
            "three largest oldlevels. The finite-test route is therefore diagnostic only; "
            "the required theorem remains a Frey-Legendre trace-code Minimum Distance theorem."
        ),
    }

    rows = []
    for row in by_level:
        rows.append(
            {
                "level": row["level"],
                "factor": row["level_factor"],
                "newspace_dim": row["newspace_dim"],
                "orbit_dim_loaded": row["orbit_dim_loaded"],
                "coverage": row["coverage"],
                "test_count": row["test_count"],
                "survivor_count": row["survivor_count"],
            }
        )

    out = {
        "summary": summary,
        "oldlevel_rows": rows,
        "missing_public_lmfdb_rows": missing["rows"],
    }

    json_path = RESULTS / f"mstar_trace_code_finite_testset_audit_{DATE}.json"
    md_path = RESULTS / f"mstar_trace_code_finite_testset_audit_{DATE}.md"
    json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# M*: Trace-Code finite Testmengen-Audit",
        "",
        f"Datum: {DATE}",
        "",
        "## Kurzbefund",
        "",
        "- Geladene Oldlevel-Orbitdaten schließen alle sichtbaren rationalen/oldlevel",
        f"  Kandidaten für \\(q=3863\\): {len(orbit_levels)} Levels,",
        f"  geladene Orbit-Dimension {loaded_orbit_dim}, Survivor {summary['oldlevel_orbit_survivor_count']}.",
        "- Drei große Oldlevels haben nur Newspace-Zeilen, aber keine nutzbaren Orbitdaten:",
        f"  {summary['oldlevel_missing_orbit_levels']} mit Newdim-Summe {missing_newdim}.",
        "- Der echte New-Level \\(N=240672\\) hat Newdim",
        f"  {summary['full_newlevel_240672_dimension']}; öffentliche Orbitdaten fehlen.",
        "- Die naive Trace-Sieve-Schranke für den New-Level liegt bei",
        f"  {summary['trace_sieve_newlevel_bound_over_logN']:.2f} log N,",
        "  also weit über dem \\(o(\\log N)\\)-Ziel.",
        "- Reyssat-\\(3863\\) bleibt externer Spike:",
        f"  \\(\\log 3863/\\log 240672={summary['reyssat_weight_log3863_over_logN']:.6f}\\),",
        f"  Cross-Class-Hits {summary['reyssat_3863_cross_class_hits']},",
        f"  Oldlevel-Hits {summary['reyssat_3863_old_level_hits']}.",
        "",
        "## Level-Tabelle",
        "",
        "| Level | Faktor | Newdim | Orbitdim geladen | Coverage | Tests | Survivor |",
        "|---:|---|---:|---:|---|---:|---:|",
    ]
    for row in rows:
        md_lines.append(
            "| {level} | {factor} | {newspace_dim} | {orbit_dim_loaded} | "
            "{coverage} | {test_count} | {survivor_count} |".format(**row)
        )

    md_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Die vorhandenen Daten geben einen positiven Hinweis nur für den geladenen",
            "Oldlevel-Teil: endliche Trace-Wörter töten dort die \\(3863\\)-Kandidaten.",
            "Für den eigentlichen New-Level \\(240672\\) und die drei großen Rest-Oldlevels",
            "fehlen aber genau die Orbitdaten, die ein Minimum-Distance-Verhalten belegen",
            "oder widerlegen könnten.",
            "",
            "Damit bleibt die finite Testmengenroute kein Beweisweg aus vorhandenen Daten.",
            "Sie muss als theoretischer Satz formuliert werden: Frey-Legendre Trace-Code",
            "Minimum Distance für primitive nichtlokale New-Level-Orbits.",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
