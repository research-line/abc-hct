"""Loop 95 Reyssat 3863 congruence probe.

This script avoids global congruence_number()/isogeny_class() calls.  It uses
local LMFDB control ainvs at conductor 240672 and compares Frobenius traces.
The goal is to see whether the modular-degree factor 3863 is visible as a
same-level Hecke congruence with another known class.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from sage.all import EllipticCurve, factor, gcd, kronecker_symbol, prime_range


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
CONTROLS = ROOT / "_data" / "em1" / "lmfdb_controls_N240672.json"
OLD_CONTROLS = ROOT / "_data" / "em1" / "lmfdb_controls_N15042.json"
JSON_OUT = ROOT / "_results" / f"mstar_reyssat_3863_probe_{DATE}.json"

Q = 3863
TRACE_BOUND = 20_000


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def ratio_float(num: int, den: int) -> float:
    return float(Fraction(int(num), int(den)))


def log_ratio(num: int | float, den: int | float) -> float:
    if num <= 0 or den <= 1:
        return float("nan")
    return math.log(float(num)) / math.log(float(den))


def curve_from_frey(a: int, b: int):
    return EllipticCurve([0, b - a, 0, -a * b, 0])


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


def basic_curve_record(label: str, curve) -> dict[str, object]:
    conductor = int(curve.conductor())
    md = int(curve.modular_degree())
    tam = int(curve.tamagawa_product())
    return {
        "label": label,
        "ainvs": [int(x) for x in curve.ainvs()],
        "conductor": conductor,
        "conductor_factor": factor_string(conductor),
        "minimal_discriminant_factor": factor_string(curve.global_minimal_model().discriminant()),
        "j_invariant": str(curve.j_invariant()),
        "modular_degree": md,
        "modular_degree_factor": factor_string(md),
        "degree_over_N2": ratio_float(md, conductor * conductor),
        "degree_exponent_N": log_ratio(md, conductor),
        "tamagawa_product": tam,
        "tamagawa_product_factor": factor_string(tam),
        "root_number": int(curve.root_number()),
        "torsion_order": int(curve.torsion_order()),
        "two_torsion_rank": int(curve.two_torsion_rank()),
        "local_data": local_rows(curve),
    }


def trace_gcd(source, target, primes: list[int], mode: str = "diff") -> dict[str, object]:
    """Compare ap(source) with ap(target), optionally with a sign/twist."""
    g = 0
    q_zero = 0
    q_nonzero = 0
    first_nonzero: list[dict[str, int]] = []
    first_q_violations: list[dict[str, int]] = []
    max_abs_delta = 0

    for p in primes:
        a_source = int(source.ap(p))
        a_target = int(target.ap(p))
        if mode == "diff":
            delta = a_source - a_target
        elif mode == "sum":
            delta = a_source + a_target
        else:
            d = int(mode)
            chi = int(kronecker_symbol(d, p))
            delta = a_source - chi * a_target

        abs_delta = abs(delta)
        max_abs_delta = max(max_abs_delta, abs_delta)
        if abs_delta:
            g = abs_delta if g == 0 else int(gcd(g, abs_delta))
            if len(first_nonzero) < 12:
                first_nonzero.append({"p": p, "delta": delta})

        if delta % Q == 0:
            q_zero += 1
        else:
            q_nonzero += 1
            if len(first_q_violations) < 12:
                first_q_violations.append({"p": p, "delta_mod_q": int(delta % Q), "delta": delta})

    return {
        "mode": mode,
        "prime_count": len(primes),
        "gcd_delta": int(g),
        "gcd_delta_factor": factor_string(g) if g else "0",
        "q": Q,
        "q_divides_all_sampled_deltas": q_nonzero == 0,
        "q_zero_count": q_zero,
        "q_nonzero_count": q_nonzero,
        "max_abs_delta": max_abs_delta,
        "first_nonzero_deltas": first_nonzero,
        "first_q_violations": first_q_violations,
    }


def compare_to_controls(source_label: str, source, controls: list[dict[str, object]], primes: list[int]):
    expected_class = "g" if "raw" in source_label.lower() else "c"
    rows = []
    for item in controls:
        target = EllipticCurve(item["ainvs"])
        target_class = item["label"].split(".")[1][0]
        diff = trace_gcd(source, target, primes, "diff")
        summ = trace_gcd(source, target, primes, "sum")
        rows.append(
            {
                "source": source_label,
                "source_expected_lmfdb_class": expected_class,
                "target_label": item["label"],
                "target_class": target_class,
                "same_expected_isogeny_class": target_class == expected_class,
                "target_rank": item.get("rank"),
                "target_torsion": item.get("torsion"),
                "same_j": str(source.j_invariant()) == str(target.j_invariant()),
                "target_root_number": int(target.root_number()),
                "diff": diff,
                "sum": summ,
            }
        )
    return rows


def compare_to_old_controls(source_label: str, source, controls: list[dict[str, object]], primes: list[int]):
    rows = []
    for item in controls:
        target = EllipticCurve(item["ainvs"])
        diff = trace_gcd(source, target, primes, "diff")
        summ = trace_gcd(source, target, primes, "sum")
        rows.append(
            {
                "source": source_label,
                "target_label": item["label"],
                "target_rank": item.get("rank"),
                "target_conductor": int(target.conductor()),
                "target_root_number": int(target.root_number()),
                "diff": diff,
                "sum": summ,
            }
        )
    return rows


def same_class_modular_degree_records(controls: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in controls:
        target_class = item["label"].split(".")[1][0]
        if target_class not in {"c", "g"}:
            continue
        target = EllipticCurve(item["ainvs"])
        md = int(target.modular_degree())
        n = int(target.conductor())
        tam = int(target.tamagawa_product())
        rows.append(
            {
                "label": item["label"],
                "class": target_class,
                "rank": item.get("rank"),
                "torsion": item.get("torsion"),
                "root_number": int(target.root_number()),
                "tamagawa_product": tam,
                "tamagawa_product_factor": factor_string(tam),
                "modular_degree": md,
                "modular_degree_factor": factor_string(md),
                "degree_over_N2": ratio_float(md, n * n),
                "frey_degree_ratio_raw": ratio_float(md, 4450176000),
            }
        )
    return rows


def twist_scan(source, target, primes: list[int], candidates: list[int]) -> list[dict[str, object]]:
    return [trace_gcd(source, target, primes, str(d)) for d in candidates]


def main() -> None:
    raw_a = 2
    raw_b = 3**10 * 109
    anc_a = raw_b
    anc_b = raw_a

    raw = curve_from_frey(raw_a, raw_b)
    anc = curve_from_frey(anc_a, anc_b)
    conductor = int(raw.conductor())
    primes = [int(p) for p in prime_range(2, TRACE_BOUND) if conductor % int(p) != 0]

    controls_payload = json.loads(CONTROLS.read_text(encoding="utf-8"))
    controls = controls_payload["curves"]
    old_controls_payload = json.loads(OLD_CONTROLS.read_text(encoding="utf-8"))
    old_controls = old_controls_payload["curves"]

    raw_vs_anc = {
        "diff": trace_gcd(raw, anc, primes, "diff"),
        "sum": trace_gcd(raw, anc, primes, "sum"),
        "twist_scan": twist_scan(raw, anc, primes, [-1, 2, -2, 3, -3, 23, -23, 109, -109, 3863, -3863]),
    }

    raw_controls = compare_to_controls("Reyssat_raw_E_2_6436341", raw, controls, primes)
    anc_controls = compare_to_controls("Reyssat_ANC_E_6436341_2", anc, controls, primes)
    raw_old_controls = compare_to_old_controls("Reyssat_raw_E_2_6436341", raw, old_controls, primes)
    anc_old_controls = compare_to_old_controls("Reyssat_ANC_E_6436341_2", anc, old_controls, primes)

    q_hits = [
        row
        for row in raw_controls + anc_controls
        if row["diff"]["q_divides_all_sampled_deltas"] or row["sum"]["q_divides_all_sampled_deltas"]
    ]
    cross_class_q_hits = [row for row in q_hits if not row["same_expected_isogeny_class"]]
    tautological_same_class_hits = [row for row in q_hits if row["same_expected_isogeny_class"]]
    old_q_hits = [
        row
        for row in raw_old_controls + anc_old_controls
        if row["diff"]["q_divides_all_sampled_deltas"] or row["sum"]["q_divides_all_sampled_deltas"]
    ]

    payload = {
        "date": DATE,
        "purpose": "Probe whether Reyssat modular-degree prime 3863 is visible as a same-level Hecke-trace congruence.",
        "method_guardrail": "No congruence_number() or isogeny_class() calls; compare ap traces against local LMFDB control ainvs.",
        "q": Q,
        "trace_bound": TRACE_BOUND,
        "prime_count": len(primes),
        "source": {
            "controls": str(CONTROLS.relative_to(ROOT)),
            "controls_source_note": controls_payload.get("source"),
            "old_controls": str(OLD_CONTROLS.relative_to(ROOT)),
            "old_controls_source_note": old_controls_payload.get("source"),
            "old_controls_guardrail": old_controls_payload.get("note"),
        },
        "frey_curves": {
            "raw": basic_curve_record("Reyssat_raw_E_2_6436341", raw),
            "anc_orientation": basic_curve_record("Reyssat_ANC_E_6436341_2", anc),
            "same_conductor": int(raw.conductor()) == int(anc.conductor()),
            "same_j": str(raw.j_invariant()) == str(anc.j_invariant()),
        },
        "raw_vs_anc": raw_vs_anc,
        "raw_against_N240672_controls": raw_controls,
        "anc_against_N240672_controls": anc_controls,
        "raw_against_old_N15042_controls": raw_old_controls,
        "anc_against_old_N15042_controls": anc_old_controls,
        "same_source_classes_modular_degrees": same_class_modular_degree_records(controls),
        "sampled_q_congruence_hits": q_hits,
        "sampled_cross_class_q_congruence_hits": cross_class_q_hits,
        "sampled_same_isogeny_class_hits": tautological_same_class_hits,
        "sampled_old_level_q_congruence_hits": old_q_hits,
        "summary": {
            "raw_modular_degree_factor": factor_string(int(raw.modular_degree())),
            "anc_modular_degree_factor": factor_string(int(anc.modular_degree())),
            "q_divides_modular_degree": int(raw.modular_degree()) % Q == 0,
            "q_hits_count": len(q_hits),
            "same_isogeny_class_hits_count": len(tautological_same_class_hits),
            "cross_class_q_hits_count": len(cross_class_q_hits),
            "old_level_15042_q_hits_count": len(old_q_hits),
            "raw_vs_anc_q_congruent": raw_vs_anc["diff"]["q_divides_all_sampled_deltas"],
            "interpretation": (
                "Same-isogeny-class hits are tautological L-series equality. "
                "A nonzero cross_class_q_hits_count would expose a sampled same-level trace congruence. "
                "If zero, the 3863 factor is not explained by these 14 local LMFDB controls "
                "outside the source isogeny classes, nor by the raw/ANC orientation pair. "
                "old_level_15042_q_hits_count tests the available radical-level old controls."
            ),
        },
    }

    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print("raw_vs_anc diff", json.dumps(raw_vs_anc["diff"], indent=2, ensure_ascii=False))
    print("q hits", [row["source"] + " -> " + row["target_label"] for row in q_hits])
    print("cross-class q hits", [row["source"] + " -> " + row["target_label"] for row in cross_class_q_hits])
    print("old-level q hits", [row["source"] + " -> " + row["target_label"] for row in old_q_hits])


if __name__ == "__main__":
    main()
