"""Loop 92 Sage probe for the M* modular-degree gate.

Run inside the Sage micromamba environment, for example:

    micromamba run -n sage python _scripts/mstar_sage_modular_degree_probe.py

The script computes exact modular degrees for the EM/Champion Frey curves
that are still small enough for Sage's elliptic-curve machinery.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from sage.all import EllipticCurve, factor


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_sage_modular_degree_probe_{DATE}.json"


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


def rad(n: int) -> int:
    out = 1
    for p, _e in factor(int(n)):
        out *= int(p)
    return out


def log_ratio(num: float, den: float) -> float:
    if num <= 0 or den <= 1:
        return float("nan")
    return math.log(num) / math.log(den)


def safe_label(curve) -> tuple[str | None, str | None]:
    try:
        return str(curve.label()), None
    except Exception as exc:  # Sage may compute degree beyond its label table.
        return None, f"{type(exc).__name__}: {exc}"


def build_row(label: str, a: int, b: int) -> dict[str, object]:
    c = a + b
    n_rad = rad(a * b * c)
    curve = EllipticCurve([0, b - a, 0, -a * b, 0])
    n_cond = int(curve.conductor())
    sage_label, label_error = safe_label(curve)
    degree = int(curve.modular_degree())
    return {
        "label": label,
        "a": int(a),
        "b": int(b),
        "c": int(c),
        "rad_abc": int(n_rad),
        "quality_rad": log_ratio(c, n_rad),
        "N_cond": n_cond,
        "sage_label": sage_label,
        "sage_label_error": label_error,
        "modular_degree": degree,
        "degree_exponent_N": log_ratio(degree, n_cond),
        "degree_over_N": degree / n_cond,
        "degree_over_N2": degree / (n_cond**2),
        "ratio_N_2p01": degree / (n_cond**2.01),
        "ratio_N_2p10": degree / (n_cond**2.10),
    }


def main() -> None:
    rows = [build_row(label, a, b) for label, a, b in CASES]
    max_exp = max(rows, key=lambda row: float(row["degree_exponent_N"]))
    max_n2 = max(rows, key=lambda row: float(row["degree_over_N2"]))
    payload = {
        "date": DATE,
        "purpose": "Exact Sage modular-degree probe for the M* Frey degree gate.",
        "bound_language": {
            "goldfeld_frey_scale": "deg(phi_E) <= C_eps * N_cond^(2+eps)",
            "watkins_strong_diagnostic": "deg(phi_E) <= C_eps * N_cond^(1+eps)",
            "warning": "Finite constants are not counterexamples to the asymptotic M* gate.",
        },
        "summary": {
            "case_count": len(rows),
            "max_degree_exponent_N": max_exp,
            "max_degree_over_N2": max_n2,
            "label_lookup_failures": sum(1 for row in rows if row["sage_label"] is None),
        },
        "rows": rows,
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
