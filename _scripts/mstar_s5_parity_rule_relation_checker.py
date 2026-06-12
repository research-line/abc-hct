#!/usr/bin/env python3
"""Check the explicit S5 p=2 parity rule against generated relations.

The earlier profile found the rule

    chi(u,v) = 1 iff v is even or 2|gcd(u,N) or 109|gcd(u,N)

in a fast minimum-representative quotient.  In Sage's original
``sparse_2term_quotient`` representatives this rule has a small degeneracy
on the 109-branch; the checker therefore offers both the naive rule and the
corrected sparse-representative rule.  It reconstructs the fixed quotient and
tests that the explicit rule annihilates the actual Manin T-relations and the
first T5 rows used by the repair witness.  It also records the parity pairing
of the early T7 rows, especially row index 1.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time
from typing import Any


TRACE_VALUES = {
    "raw": {5: 2, 7: 0, 11: 0, 13: -6},
    "anc": {5: 2, 7: 0, 11: 0, 13: -6},
}


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def standard_hecke_matrices(p: int) -> list[list[int]]:
    return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]


def symbol_tuple_from_raw(raw_symbol: Any) -> tuple[int, int]:
    raw = tuple(int(x) for x in raw_symbol)
    if len(raw) >= 3:
        return raw[-2], raw[-1]
    if len(raw) == 2:
        return raw[0], raw[1]
    raise ValueError(f"unexpected Manin symbol tuple: {raw!r}")


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Parity Rule Relation Check",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- mode: `{payload['mode']}`",
        f"- q: `{payload['q']}`",
        f"- quotient method: `{payload['quotient_method']}`",
        f"- rule family: `{payload['rule_family']}`",
        f"- Manin symbols: `{payload['nsyms']}`",
        f"- quotient columns: `{payload['ncols']}`",
        f"- rule support size: `{payload['rule_support_size']}`",
        f"- optional support comparison mismatches: `{payload['input_support_mismatch_count']}`",
        "",
        "## Relation Pairings",
        "",
        "| family | checked | bad/odd | expectation |",
        "|---|---:|---:|---|",
        f"| Manin T | {payload['manin_rows_checked']} | {payload['manin_bad_count']} | all 0 |",
        f"| T5 | {payload['t5_rows_checked']} | {payload['t5_bad_count']} | all 0 |",
        f"| T7 | {payload['t7_rows_checked']} | {payload['t7_odd_count']} | row index 1 odd is desired |",
        "",
        "## Target T7 Row",
        "",
        f"- row index: `{payload['t7_target_row_index']}`",
        f"- pairing: `{payload['t7_target_pairing_mod2']}`",
        f"- support: `{payload['t7_target_support_mod2']}`",
        "",
    ]
    if payload["manin_bad_examples"]:
        lines.extend(["## Manin Bad Examples", "", "```json"])
        lines.append(json.dumps(payload["manin_bad_examples"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    if payload["t5_bad_examples"]:
        lines.extend(["## T5 Bad Examples", "", "```json"])
        lines.append(json.dumps(payload["t5_bad_examples"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    if payload["t7_odd_examples"]:
        lines.extend(["## T7 Odd Examples", "", "```json"])
        lines.append(json.dumps(payload["t7_odd_examples"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--manin-limit", type=int, default=0, help="0 means all Manin T rows")
    parser.add_argument("--t5-rows", type=int, default=13000)
    parser.add_argument("--t7-rows", type=int, default=1000)
    parser.add_argument("--t7-target-row-index", type=int, default=1)
    parser.add_argument("--progress-every", type=int, default=5000)
    parser.add_argument("--example-limit", type=int, default=20)
    parser.add_argument(
        "--rule-family",
        choices=["sparse-corrected", "naive-109", "input-support"],
        default="sparse-corrected",
        help="Rule to test. input-support uses --input-json directly.",
    )
    parser.add_argument("--input-json", type=Path, help="Optional kernel export for support comparison")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    log("importing Sage")
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    q = int(args.q)
    field_q = GF(q)
    log(f"building ManinSymbolList level={args.level} weight={args.weight}")
    syms = ManinSymbolList_gamma0(int(args.level), int(args.weight))
    nsyms = len(syms)
    raw_symbol_list = list(getattr(syms, "_symbol_list"))
    log(f"Manin symbols: {nsyms}")

    rels = set(modS_relations(syms))
    if int(args.sign) in (-1, 1):
        rels.update(modI_relations(syms, int(args.sign)))
    log(f"S/I relations: {len(rels)}; building sparse_2term_quotient over GF({q})")
    mod = sparse_2term_quotient(rels, nsyms, field_q)
    log(f"2-term quotient entries: {len(mod)}")

    rep_to_col: dict[int, int] = {}
    col_to_rep: dict[int, int] = {}
    mod_map: list[tuple[int, Any] | None] = []
    for entry in mod:
        rep, scalar = entry
        if scalar == 0:
            mod_map.append(None)
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            col = len(rep_to_col)
            rep_to_col[rep_i] = col
            col_to_rep[col] = rep_i
        mod_map.append((rep_to_col[rep_i], field_q(scalar)))
    ncols = len(rep_to_col)
    log(f"fixed quotient columns: {ncols}")

    def reduce_terms(terms: list[tuple[int, Any]]) -> dict[int, int]:
        row: dict[int, Any] = {}
        for j, coeff in terms:
            mapped = mod_map[int(j)]
            if mapped is None:
                continue
            col, scalar = mapped
            val = field_q(coeff) * scalar
            if val == 0:
                continue
            row[col] = row.get(col, field_q(0)) + val
            if row[col] == 0:
                del row[col]
        return {int(col): int(val) % q for col, val in row.items() if int(val) % q}

    def row_mod2(raw_row: dict[int, int]) -> dict[int, int]:
        return {
            int(col): symmetric_lift(int(value), q) % 2
            for col, value in raw_row.items()
            if symmetric_lift(int(value), q) % 2
        }

    input_support: set[int] | None = None
    input_support_mismatch_count: int | None = None
    input_support_mismatch_examples: list[dict[str, Any]] = []
    if args.input_json:
        data = json.loads(args.input_json.read_text(encoding="utf-8"))
        input_support = {int(col) for col in data["kernel_support"]}
    elif args.rule_family == "input-support":
        raise ValueError("--rule-family input-support requires --input-json")

    def rule_for_col(col: int) -> int:
        if args.rule_family == "input-support":
            if input_support is None:
                raise RuntimeError("input support not loaded")
            return int(int(col) in input_support)

        rep = int(col_to_rep[int(col)])
        u, v = symbol_tuple_from_raw(raw_symbol_list[rep])
        gcd_u = math.gcd(u, int(args.level))
        if (v % 2 == 0) or (gcd_u % 2 == 0):
            return 1
        if gcd_u % 109 != 0:
            return 0
        if args.rule_family == "naive-109":
            return 1

        # Sage's sparse_2term_quotient representatives leave one small
        # degenerate 109-branch out of the kernel support:
        #     u = gcd(u,N) = 109*d, d|69, with v odd.
        # In the present level this is exactly the 192-column set
        # u in {109, 327, 2507, 7521} seen in the naive branch.
        return int(u != gcd_u)

    rule_vector = [rule_for_col(col) for col in range(ncols)]
    rule_support = [col for col, bit in enumerate(rule_vector) if bit]

    if input_support is not None:
        rule_support_set = set(rule_support)
        mismatches = sorted(rule_support_set.symmetric_difference(input_support))
        input_support_mismatch_count = len(mismatches)
        for col in mismatches[: int(args.example_limit)]:
            rep = int(col_to_rep[int(col)])
            u, v = symbol_tuple_from_raw(raw_symbol_list[rep])
            input_support_mismatch_examples.append(
                {
                    "col": int(col),
                    "rule": int(col in rule_support_set),
                    "input": int(col in input_support),
                    "rep": rep,
                    "u": u,
                    "v": v,
                    "gcd_u_level": math.gcd(u, int(args.level)),
                }
            )
    else:
        input_support_mismatch_count = -1

    def pairing_mod2(row: dict[int, int]) -> int:
        return sum(bit * rule_vector[col] for col, bit in row.items()) % 2

    def row_support(row: dict[int, int], limit: int = 80) -> list[int]:
        return sorted(int(col) for col in row)[:limit]

    manin_checked = 0
    manin_bad = 0
    manin_bad_examples: list[dict[str, Any]] = []
    manin_limit = nsyms if int(args.manin_limit) <= 0 else min(nsyms, int(args.manin_limit))
    log(f"checking Manin T rows: {manin_limit}")
    for i in range(manin_limit):
        terms: list[tuple[int, Any]] = [(i, field_q(1))]
        terms.extend(syms.apply_T(i))
        terms.extend(syms.apply_TT(i))
        row = row_mod2(reduce_terms(terms))
        pair = pairing_mod2(row)
        manin_checked += 1
        if pair:
            manin_bad += 1
            if len(manin_bad_examples) < int(args.example_limit):
                manin_bad_examples.append({"row_index": i, "support": row_support(row), "pairing": pair})
        if args.progress_every > 0 and manin_checked % int(args.progress_every) == 0:
            log(f"Manin checked={manin_checked} bad={manin_bad}")

    t5_checked = 0
    t5_bad = 0
    t5_bad_examples: list[dict[str, Any]] = []
    mats5 = standard_hecke_matrices(5)
    ap5 = TRACE_VALUES[str(args.mode)][5]
    t5_limit = min(nsyms, max(0, int(args.t5_rows)))
    log(f"checking T5 rows: {t5_limit}")
    for i in range(t5_limit):
        terms = [(i, field_q(-ap5))]
        for mat in mats5:
            terms.extend(syms.apply(i, mat))
        row = row_mod2(reduce_terms(terms))
        pair = pairing_mod2(row)
        t5_checked += 1
        if pair:
            t5_bad += 1
            if len(t5_bad_examples) < int(args.example_limit):
                t5_bad_examples.append({"row_index": i, "support": row_support(row), "pairing": pair})
        if args.progress_every > 0 and t5_checked % int(args.progress_every) == 0:
            log(f"T5 checked={t5_checked} bad={t5_bad}")

    t7_checked = 0
    t7_odd = 0
    t7_odd_examples: list[dict[str, Any]] = []
    mats7 = standard_hecke_matrices(7)
    ap7 = TRACE_VALUES[str(args.mode)][7]
    t7_limit = min(nsyms, max(0, int(args.t7_rows)))
    log(f"checking T7 rows: {t7_limit}")
    t7_target_pairing: int | None = None
    t7_target_support: list[int] = []
    for i in range(t7_limit):
        terms = [(i, field_q(-ap7))]
        for mat in mats7:
            terms.extend(syms.apply(i, mat))
        row = row_mod2(reduce_terms(terms))
        pair = pairing_mod2(row)
        if i == int(args.t7_target_row_index):
            t7_target_pairing = pair
            t7_target_support = row_support(row, limit=200)
        t7_checked += 1
        if pair:
            t7_odd += 1
            if len(t7_odd_examples) < int(args.example_limit):
                t7_odd_examples.append({"row_index": i, "support": row_support(row), "pairing": pair})
        if args.progress_every > 0 and t7_checked % int(args.progress_every) == 0:
            log(f"T7 checked={t7_checked} odd={t7_odd}")

    if t7_target_pairing is None and 0 <= int(args.t7_target_row_index) < nsyms:
        i = int(args.t7_target_row_index)
        terms = [(i, field_q(-ap7))]
        for mat in mats7:
            terms.extend(syms.apply(i, mat))
        row = row_mod2(reduce_terms(terms))
        t7_target_pairing = pairing_mod2(row)
        t7_target_support = row_support(row, limit=200)

    payload: dict[str, Any] = {
        "tool": "mstar_s5_parity_rule_relation_checker",
        "level": int(args.level),
        "weight": int(args.weight),
        "mode": str(args.mode),
        "sign": int(args.sign),
        "q": q,
        "quotient_method": "sage.sparse_2term_quotient",
        "rule_family": str(args.rule_family),
        "nsyms": nsyms,
        "ncols": ncols,
        "rule": {
            "naive-109": "chi(u,v)=1 iff v even or 2|gcd(u,N) or 109|gcd(u,N)",
            "sparse-corrected": "chi(u,v)=1 iff v even or 2|gcd(u,N) or (109|gcd(u,N) and u!=gcd(u,N))",
            "input-support": "chi is read directly from input_json kernel_support",
        }[str(args.rule_family)],
        "rule_support_size": len(rule_support),
        "input_json": str(args.input_json) if args.input_json else None,
        "input_support_mismatch_count": input_support_mismatch_count,
        "input_support_mismatch_examples": input_support_mismatch_examples,
        "manin_rows_checked": manin_checked,
        "manin_bad_count": manin_bad,
        "manin_bad_examples": manin_bad_examples,
        "t5_rows_checked": t5_checked,
        "t5_bad_count": t5_bad,
        "t5_bad_examples": t5_bad_examples,
        "t7_rows_checked": t7_checked,
        "t7_odd_count": t7_odd,
        "t7_odd_examples": t7_odd_examples,
        "t7_target_row_index": int(args.t7_target_row_index),
        "t7_target_pairing_mod2": t7_target_pairing,
        "t7_target_support_mod2": t7_target_support,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
