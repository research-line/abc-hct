"""Budget check for global Hecke eigenvalue separators in M-G*.

The point is not to compute actual modular-form eigenvalues.  The script
quantifies the scale mismatch of a standard interpolation proof:

    e_f = prod_{g != f} (T - a_g(T)) / (a_f(T) - a_g(T)).

Even after the maximal local type filter from Loop 77, the number of remaining
components is typically far larger than O(log N).  Any proof that isolates f by
generic eigenvalue separation therefore produces denominator bounds on an
exponential-in-dimension scale, not on the target N^(2+o(1)) scale.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "_data" / "mg_local_type_filter_budget_2026-05-09.json"
OUTPUT = ROOT / "_data" / "mg_eigen_separator_budget_2026-05-09.json"


def separator_row(row: dict) -> dict:
    n = int(row.get("n_cond") or row.get("n_primorial"))
    log_n = math.log(n)
    dim = float(row["filtered_dimension_heuristic"])
    effective_dim = max(dim, 1.0)
    # Murty/Sturm-style distinguishing uses small Hecke operators.  Taking a
    # polylogarithmic index is generous for the separator but still harmless.
    b = max(3.0, log_n * log_n)
    log_eigenvalue_window = math.log(4.0 * math.sqrt(b))
    single_operator_log_scale = max(effective_dim - 1.0, 0.0) * log_eigenvalue_window
    discriminant_log_scale = effective_dim * max(effective_dim - 1.0, 0.0) * log_eigenvalue_window
    target_log_scale = 2.0 * log_n
    return {
        "label": row.get("label", f"primorial_omega_{row.get('omega_n')}"),
        "n": n,
        "omega_n": row["omega_n"],
        "filtered_dimension_heuristic": dim,
        "separator_index_polylog": b,
        "log_eigenvalue_window": log_eigenvalue_window,
        "single_operator_interpolation_log_scale": single_operator_log_scale,
        "full_discriminant_log_scale": discriminant_log_scale,
        "target_log_N2": target_log_scale,
        "single_operator_over_target": (
            single_operator_log_scale / target_log_scale if target_log_scale else 0.0
        ),
        "discriminant_over_target": (
            discriminant_log_scale / target_log_scale if target_log_scale else 0.0
        ),
    }


def summarize(rows: list[dict]) -> dict:
    active = [r for r in rows if r["filtered_dimension_heuristic"] > 1.0]
    ratios = [r["single_operator_over_target"] for r in active]
    disc_ratios = [r["discriminant_over_target"] for r in active]
    return {
        "active_rows": len(active),
        "min_single_operator_over_target": min(ratios),
        "median_single_operator_over_target": sorted(ratios)[len(ratios) // 2],
        "max_single_operator_over_target": max(ratios),
        "min_discriminant_over_target": min(disc_ratios),
        "median_discriminant_over_target": sorted(disc_ratios)[len(disc_ratios) // 2],
        "conclusion": (
            "Distinguishing by global Hecke eigenvalues is not enough: generic "
            "interpolation costs scale with the remaining dimension, whereas "
            "M-G* needs only O(log N) denominator growth."
        ),
    }


def main() -> None:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [separator_row(row) for row in source["em1_by_quality"]]
    synthetic = [separator_row(row) for row in source["synthetic_primorial_stress"]]
    result = {
        "date": "2026-05-09",
        "purpose": "Compare standard global Hecke eigenvalue separation with the M-G* projector denominator target.",
        "target": "log den(pi_f) <= (2+o(1)) log N",
        "interpretation": {
            "distinguishing_vs_denominator": "A finite set of Hecke eigenvalues can distinguish forms without giving a small inverse/eigenprojector denominator.",
            "single_operator_scale": "Product interpolation over the remaining components costs roughly D log(polylog N).",
            "discriminant_scale": "Full Hecke discriminant bounds cost roughly D^2 log(polylog N).",
        },
        "summary_em1": summarize(rows),
        "em1_by_quality": rows,
        "synthetic_primorial_stress": synthetic,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
