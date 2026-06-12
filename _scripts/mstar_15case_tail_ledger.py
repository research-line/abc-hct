"""Loop 94 M*/S* tail ledger across the EM/Champion Frey cases.

The ledger compares modular degree and local Tamagawa/discriminant data across
the sample. Dynamic congruence/isogeny computations are disabled here because
they can hang; ABCHome_2 uses the precomputed Loop 93 congruence/isogeny data.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from sage.all import EllipticCurve, factor


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_15case_tail_ledger_{DATE}.json"

CONGRUENCE_N_MAX = 0
ISOGENY_N_MAX = 0

CASES = [
    ("Reyssat_raw", 2, 3**10 * 109),
    ("Reyssat_ANC_orientation", 3**10 * 109, 2),
    ("ABCHome_2", 11**2, 3**2 * 5**6 * 7**3),
    ("classic_4374", 1, 2 * 3**7),
    ("classic_2401", 1, 2400),
    ("1+8=9", 1, 8),
    ("1+63=64", 1, 63),
    ("1+80=81", 1, 80),
    ("5+27=32", 5, 27),
    ("3+125=128", 3, 125),
    ("13+243=256", 13, 243),
    ("32+49=81", 32, 49),
    ("1+4095=4096", 1, 4095),
    ("625+2048=2673", 625, 2048),
    ("1+1023=1024", 1, 1023),
]


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def rad(n: int) -> int:
    out = 1
    for p, _e in factor(int(n)):
        out *= int(p)
    return out


def log_ratio(num: int | float, den: int | float) -> float:
    if num <= 0 or den <= 1:
        return float("nan")
    return math.log(float(num)) / math.log(float(den))


def ratio_float(num: int, den: int) -> float:
    return float(Fraction(int(num), int(den)))


def local_rows(curve) -> list[dict[str, object]]:
    rows = []
    for item in curve.local_data():
        p = int(item.prime().gens()[0])
        rows.append(
            {
                "p": p,
                "kodaira": str(item.kodaira_symbol()),
                "split": bool(item.has_split_multiplicative_reduction()),
                "nonsplit": bool(item.has_nonsplit_multiplicative_reduction()),
                "f_p": int(item.conductor_valuation()),
                "delta_v": int(item.discriminant_valuation()),
                "tamagawa": int(item.tamagawa_number()),
            }
        )
    return rows


def accessible_congruence(label: str, curve, n: int, md: int) -> dict[str, object]:
    if label == "ABCHome_2":
        return {
            "value": md,
            "factor": factor_string(md),
            "status": "precomputed_loop_93",
            "source": "_results/mstar_abchome_tail_probe_2026-05-09.json",
        }
    if CONGRUENCE_N_MAX <= 0:
        return {
            "value": None,
            "factor": None,
            "status": "skipped_dynamic_disabled",
            "reason": "dynamic congruence_number() calls hung in Loop 94; ABCHome is precomputed only",
        }
    if n > CONGRUENCE_N_MAX:
        return {"value": None, "factor": None, "status": f"skipped_N_gt_{CONGRUENCE_N_MAX}"}
    try:
        value = int(curve.congruence_number())
        return {"value": value, "factor": factor_string(value), "status": "computed"}
    except Exception as exc:
        return {"value": None, "factor": None, "status": f"{type(exc).__name__}: {exc}"}


def accessible_isogeny(label: str, curve, n: int, md: int) -> dict[str, object]:
    if label == "ABCHome_2":
        return {
            "status": "precomputed_loop_93",
            "source": "_results/mstar_abchome_tail_probe_2026-05-09.json",
            "size": 4,
            "modular_degrees": [3158507520, 6317015040, 1579253760, 6317015040],
            "min_modular_degree": 1579253760,
            "frey_degree_over_min": 2.0,
            "matrix": [[1, 2, 2, 2], [2, 1, 4, 4], [2, 4, 1, 4], [2, 4, 4, 1]],
        }
    if ISOGENY_N_MAX <= 0:
        return {
            "status": "skipped_dynamic_disabled",
            "size": None,
            "reason": "dynamic isogeny_class() calls are disabled for this conservative ledger",
        }
    if n > ISOGENY_N_MAX:
        return {"status": f"skipped_N_gt_{ISOGENY_N_MAX}", "size": None}
    try:
        cls = curve.isogeny_class()
        degrees = [int(c.modular_degree()) for c in cls.curves]
        min_degree = min(degrees)
        return {
            "status": "computed",
            "size": len(degrees),
            "modular_degrees": degrees,
            "min_modular_degree": min_degree,
            "frey_degree_over_min": ratio_float(md, min_degree),
            "matrix": [[int(x) for x in row] for row in cls.matrix().rows()],
        }
    except Exception as exc:
        return {"status": f"{type(exc).__name__}: {exc}", "size": None}


def build_row(label: str, a: int, b: int) -> dict[str, object]:
    print(f"BEGIN {label}", flush=True)
    c = a + b
    n_rad = rad(a * b * c)
    curve = EllipticCurve([0, b - a, 0, -a * b, 0])
    minimal = curve.global_minimal_model()
    n = int(curve.conductor())
    md = int(curve.modular_degree())
    local = local_rows(curve)
    tam_prod = int(curve.tamagawa_product())
    cn = accessible_congruence(label, curve, n, md)
    isog = accessible_isogeny(label, curve, n, md)
    return {
        "label": label,
        "a": int(a),
        "b": int(b),
        "c": int(c),
        "rad_abc": n_rad,
        "quality_rad": log_ratio(c, n_rad),
        "N_cond": n,
        "N_cond_factor": factor_string(n),
        "minimal_discriminant_factor": factor_string(minimal.discriminant()),
        "modular_degree": md,
        "modular_degree_factor": factor_string(md),
        "degree_exponent_N": log_ratio(md, n),
        "degree_over_N2": ratio_float(md, n * n),
        "tamagawa_product": tam_prod,
        "tamagawa_product_factor": factor_string(tam_prod),
        "degree_over_tamagawa_product": ratio_float(md, tam_prod) if tam_prod else None,
        "local_data": local,
        "max_delta_v": max(row["delta_v"] for row in local),
        "max_tamagawa": max(row["tamagawa"] for row in local),
        "root_number": int(curve.root_number()),
        "torsion_order": int(curve.torsion_order()),
        "two_torsion_rank": int(curve.two_torsion_rank()),
        "congruence_number": cn,
        "congruence_equals_modular_degree": cn.get("value") == md if cn.get("value") else None,
        "isogeny": isog,
    }


def main() -> None:
    rows = [build_row(*case) for case in CASES]
    computed_congruence = [row for row in rows if row["congruence_number"]["status"] == "computed"]
    payload = {
        "date": DATE,
        "purpose": "M*/S* ledger separating visible local Tamagawa/exponent mass from global projection-tail data.",
        "limits": {
            "congruence_N_max": CONGRUENCE_N_MAX,
            "isogeny_N_max": ISOGENY_N_MAX,
            "reason": "Dynamic congruence_number()/isogeny_class() calls are disabled after Loop 94 timeouts; ABCHome_2 is precomputed from Loop 93.",
        },
        "summary": {
            "case_count": len(rows),
            "computed_congruence_count": len(computed_congruence),
            "congruence_equals_modular_degree_count": sum(
                1 for row in computed_congruence if row["congruence_equals_modular_degree"]
            ),
            "max_degree_over_N2": max(rows, key=lambda row: float(row["degree_over_N2"])),
            "max_degree_exponent_N": max(rows, key=lambda row: float(row["degree_exponent_N"])),
            "max_degree_over_tamagawa": max(rows, key=lambda row: float(row["degree_over_tamagawa_product"] or 0)),
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
