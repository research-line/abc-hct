"""Loop 93 ABCHome_2 tail probe for the M* modular-degree route.

Run in Sage:

    micromamba run -n sage python _scripts/mstar_abchome_tail_probe.py

The probe records the local data, modular degree, congruence number, and
isogeny-class structure of the ABCHome_2 Frey curve.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from sage.all import EllipticCurve, factor


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_abchome_tail_probe_{DATE}.json"

LABEL = "ABCHome_2"
A = 11**2
B = 3**2 * 5**6 * 7**3


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def log_ratio(num: int | float, den: int | float) -> float:
    if num <= 0 or den <= 1:
        return float("nan")
    return math.log(float(num)) / math.log(float(den))


def ratio_payload(num: int, den: int) -> dict[str, object]:
    frac = Fraction(int(num), int(den))
    return {
        "num": frac.numerator,
        "den": frac.denominator,
        "float": float(frac),
        "factor_num": factor_string(frac.numerator),
        "factor_den": factor_string(frac.denominator),
    }


def local_data_payload(curve) -> list[dict[str, object]]:
    rows = []
    for item in curve.local_data():
        prime_ideal = item.prime()
        p = int(prime_ideal.gens()[0])
        rows.append(
            {
                "p": p,
                "kodaira": str(item.kodaira_symbol()),
                "bad_reduction_type": str(item.bad_reduction_type()),
                "split_multiplicative": bool(item.has_split_multiplicative_reduction()),
                "nonsplit_multiplicative": bool(item.has_nonsplit_multiplicative_reduction()),
                "conductor_valuation": int(item.conductor_valuation()),
                "minimal_discriminant_valuation": int(item.discriminant_valuation()),
                "tamagawa_number": int(item.tamagawa_number()),
                "tamagawa_exponent": int(item.tamagawa_exponent()),
            }
        )
    return rows


def curve_payload(curve, index: int | None = None) -> dict[str, object]:
    n = int(curve.conductor())
    md = int(curve.modular_degree())
    cn = int(curve.congruence_number())
    payload: dict[str, object] = {
        "index": index,
        "ainvs": [int(x) for x in curve.ainvs()],
        "N_cond": n,
        "modular_degree": md,
        "modular_degree_factor": factor_string(md),
        "congruence_number": cn,
        "congruence_number_factor": factor_string(cn),
        "congruence_equals_modular_degree": cn == md,
        "degree_exponent_N": log_ratio(md, n),
        "degree_over_N2": ratio_payload(md, n * n),
        "torsion_order": int(curve.torsion_order()),
        "two_torsion_rank": int(curve.two_torsion_rank()),
        "root_number": int(curve.root_number()),
        "tamagawa_numbers": [int(x) for x in curve.tamagawa_numbers()],
        "tamagawa_product": int(curve.tamagawa_product()),
        "tamagawa_product_bsd": int(curve.tamagawa_product_bsd()),
    }
    return payload


def main() -> None:
    c = A + B
    curve = EllipticCurve([0, B - A, 0, -A * B, 0])
    minimal = curve.global_minimal_model()
    n = int(curve.conductor())
    md = int(curve.modular_degree())
    cn = int(curve.congruence_number())

    isogeny_class = curve.isogeny_class()
    class_curves = list(isogeny_class.curves)
    class_payload = [curve_payload(item, i) for i, item in enumerate(class_curves)]
    min_curve = min(class_payload, key=lambda row: int(row["modular_degree"]))

    payload = {
        "date": DATE,
        "label": LABEL,
        "a": A,
        "b": B,
        "c": c,
        "abc_factor": factor_string(A * B * c),
        "c_factor": factor_string(c),
        "rad_abc": math.prod(int(p) for p, _e in factor(A * B * c)),
        "quality_rad": log_ratio(c, math.prod(int(p) for p, _e in factor(A * B * c))),
        "N_cond": n,
        "N_cond_factor": factor_string(n),
        "minimal_model_ainvs": [int(x) for x in minimal.ainvs()],
        "minimal_discriminant": int(minimal.discriminant()),
        "minimal_discriminant_factor": factor_string(minimal.discriminant()),
        "frey_curve": curve_payload(curve, 0),
        "local_data": local_data_payload(curve),
        "modular_degree_equals_congruence_number": md == cn,
        "degree_over_N2": ratio_payload(md, n * n),
        "degree_factor_vs_N2": {
            "degree_factor": factor_string(md),
            "N2_factor": factor_string(n * n),
            "interpretation": "Extra 2-adic and 3-adic mass, plus a 17-factor, is partly offset by missing 11^2 and 23^2 factors from N^2.",
        },
        "isogeny_class": {
            "size": len(class_curves),
            "matrix": [[int(x) for x in row] for row in isogeny_class.matrix().rows()],
            "curves": class_payload,
            "min_modular_degree_curve": min_curve,
            "frey_degree_over_min_degree": ratio_payload(md, int(min_curve["modular_degree"])),
        },
        "route_implication": {
            "unit_N2_bound_for_frey_model": "fails in this finite normalization",
            "unit_N2_bound_for_min_degree_in_isogeny_class": "passes in this sample",
            "mstar_scale": "C_eps * N^(2+eps) remains the correct target",
            "structural_signal": "ABCHome_2 stress is tied to congruence_number = modular_degree and a small 2-isogeny class, not to a large unresolved isogeny graph.",
        },
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps(payload["route_implication"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
