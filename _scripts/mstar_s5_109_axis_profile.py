#!/usr/bin/env python3
"""Profile the 109-axis correction for the S5 p=2 parity class.

This is a compact follow-up to ``mstar_s5_parity_rule_relation_checker.py``.
It isolates the difference D between the naive 109-rule and the corrected
Sage-sparse parity class, then records how Manin T and T5 rows meet D.
"""

from __future__ import annotations

import argparse
import collections
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


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 109-Axis Profile",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- mode: `{payload['mode']}`",
        f"- q: `{payload['q']}`",
        f"- quotient columns: `{payload['ncols']}`",
        f"- D-axis size: `{payload['d_axis_size']}`",
        f"- Manin rows checked: `{payload['manin_rows_checked']}`",
        f"- Manin rows meeting D oddly: `{payload['manin_odd_d_count']}`",
        f"- Manin D-column hit frequency: `{payload['manin_d_column_hit_frequency']}`",
        f"- T5 rows checked: `{payload['t5_rows_checked']}`",
        f"- T5 rows meeting D oddly: `{payload['t5_odd_d_count']}`",
        "",
        "## D-Axis By u",
        "",
        "| u | count |",
        "|---:|---:|",
    ]
    for item in payload["d_axis_by_u"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## D-Axis Formula Check",
            "",
            "| d | u=109*d | count | expected 2*(69/d) |",
            "|---:|---:|---:|---:|",
        ]
    )
    for item in payload["d_axis_formula"]:
        lines.append(f"| {item['d']} | {item['u']} | {item['count']} | {item['expected']} |")
    lines.extend(
        [
            "",
            "## Manin Bad Source gcd(u,N)",
            "",
            "| gcd(u,N) | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["manin_odd_source_gcd_u_top"][:30]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## T5 Bad Source Residues",
            "",
            "| residue | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["t5_odd_source_v_mod_109"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(
        [
            "",
            "Formula: odd T5-D hits satisfy `5*v + a*u == 0 mod 109` for `[1,a;0,5]`, `a=1,2,3,4`. The earlier residues `87,65,43,21` are the `u=1` special case.",
            "",
            "## T5 Hit Matrices",
            "",
            "| matrix label | hit count |",
            "|---|---:|",
        ]
    )
    for item in payload["t5_odd_hit_matrix"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(["", "## Examples", "", "```json"])
    lines.append(json.dumps(payload["examples"], indent=2, ensure_ascii=False))
    lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--t5-rows", type=int, default=13000)
    parser.add_argument("--example-limit", type=int, default=20)
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
    level = int(args.level)
    log(f"building ManinSymbolList level={level}")
    syms = ManinSymbolList_gamma0(level, int(args.weight))
    nsyms = len(syms)
    raw_symbol_list = list(getattr(syms, "_symbol_list"))

    rels = set(modS_relations(syms))
    if int(args.sign) in (-1, 1):
        rels.update(modI_relations(syms, int(args.sign)))
    log("building sparse_2term_quotient")
    mod = sparse_2term_quotient(rels, nsyms, field_q)

    rep_to_col: dict[int, int] = {}
    col_to_rep: dict[int, int] = {}
    mod_map: list[tuple[int, Any] | None] = []
    for rep, scalar in mod:
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

    def row_mod2(raw_row: dict[int, int]) -> set[int]:
        return {
            int(col)
            for col, value in raw_row.items()
            if symmetric_lift(int(value), q) % 2
        }

    def col_uv(col: int) -> tuple[int, int]:
        return symbol_tuple_from_raw(raw_symbol_list[int(col_to_rep[col])])

    def source_uv(index: int) -> tuple[int, int]:
        return symbol_tuple_from_raw(raw_symbol_list[int(index)])

    d_axis: set[int] = set()
    d_by_u: collections.Counter[int] = collections.Counter()
    d_by_v_mod_109: collections.Counter[int] = collections.Counter()
    d_by_gcd_v: collections.Counter[int] = collections.Counter()
    for col in range(ncols):
        u, v = col_uv(col)
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            d_axis.add(col)
            d_by_u[u] += 1
            d_by_v_mod_109[v % 109] += 1
            d_by_gcd_v[math.gcd(v, level)] += 1

    d_axis_formula = []
    for d in [1, 3, 23, 69]:
        u = 109 * d
        d_axis_formula.append(
            {
                "d": d,
                "u": u,
                "count": int(d_by_u[u]),
                "expected": int(2 * (69 // d)),
            }
        )

    def d_hits_for_row(row: set[int]) -> list[int]:
        return sorted(row.intersection(d_axis))

    manin_odd_source_u: collections.Counter[int] = collections.Counter()
    manin_odd_source_gcd_u: collections.Counter[int] = collections.Counter()
    manin_odd_source_v_parity: collections.Counter[int] = collections.Counter()
    manin_d_hit_count: collections.Counter[int] = collections.Counter()
    manin_d_column_hits: collections.Counter[int] = collections.Counter()
    manin_odd_examples: list[dict[str, Any]] = []
    log("checking Manin D-intersections")
    for i in range(nsyms):
        terms: list[tuple[int, Any]] = [(i, field_q(1))]
        terms.extend(syms.apply_T(i))
        terms.extend(syms.apply_TT(i))
        row = row_mod2(reduce_terms(terms))
        hits = d_hits_for_row(row)
        manin_d_hit_count[len(hits)] += 1
        for col in hits:
            manin_d_column_hits[col] += 1
        if len(hits) % 2:
            u, v = source_uv(i)
            manin_odd_source_u[u] += 1
            manin_odd_source_gcd_u[math.gcd(u, level)] += 1
            manin_odd_source_v_parity[v % 2] += 1
            if len(manin_odd_examples) < int(args.example_limit):
                manin_odd_examples.append(
                    {
                        "row_index": i,
                        "source": [u, v],
                        "d_hit_count": len(hits),
                        "d_hits": [
                            {"col": col, "uv": list(col_uv(col))}
                            for col in hits[:10]
                        ],
                    }
                )

    t5_odd_source_u: collections.Counter[int] = collections.Counter()
    t5_odd_source_v_mod_109: collections.Counter[int] = collections.Counter()
    t5_odd_source_v_mod_872: collections.Counter[int] = collections.Counter()
    t5_odd_source_v_mod_8: collections.Counter[int] = collections.Counter()
    t5_odd_hit_matrix: collections.Counter[str] = collections.Counter()
    t5_d_hit_count: collections.Counter[int] = collections.Counter()
    t5_d_column_hits: collections.Counter[int] = collections.Counter()
    t5_odd_examples: list[dict[str, Any]] = []
    mats5 = standard_hecke_matrices(5)
    ap5 = TRACE_VALUES[str(args.mode)][5]
    t5_limit = min(nsyms, max(0, int(args.t5_rows)))
    log(f"checking T5 D-intersections rows={t5_limit}")
    for i in range(t5_limit):
        terms = [(i, field_q(-ap5))]
        matrix_hits: list[dict[str, Any]] = []
        for mat in mats5:
            mat_terms = syms.apply(i, mat)
            terms.extend(mat_terms)
            mat_row = row_mod2(reduce_terms(mat_terms))
            hits_for_mat = d_hits_for_row(mat_row)
            if hits_for_mat:
                label = f"a={mat[1]}" if mat[0] == 1 and mat[3] == 5 else "dual"
                matrix_hits.append(
                    {
                        "matrix": mat,
                        "label": label,
                        "hits": [
                            {"col": col, "uv": list(col_uv(col))}
                            for col in hits_for_mat[:10]
                        ],
                    }
                )
        row = row_mod2(reduce_terms(terms))
        hits = d_hits_for_row(row)
        t5_d_hit_count[len(hits)] += 1
        for col in hits:
            t5_d_column_hits[col] += 1
        if len(hits) % 2:
            u, v = source_uv(i)
            t5_odd_source_u[u] += 1
            t5_odd_source_v_mod_109[v % 109] += 1
            t5_odd_source_v_mod_872[v % 872] += 1
            t5_odd_source_v_mod_8[v % 8] += 1
            for item in matrix_hits:
                t5_odd_hit_matrix[item["label"]] += len(item["hits"])
            if len(t5_odd_examples) < int(args.example_limit):
                t5_odd_examples.append(
                    {
                        "row_index": i,
                        "source": [u, v],
                        "d_hit_count": len(hits),
                        "d_hits": [
                            {"col": col, "uv": list(col_uv(col))}
                            for col in hits[:10]
                        ],
                        "matrix_hits": matrix_hits,
                    }
                )

    payload: dict[str, Any] = {
        "tool": "mstar_s5_109_axis_profile",
        "level": level,
        "weight": int(args.weight),
        "mode": str(args.mode),
        "sign": int(args.sign),
        "q": q,
        "nsyms": nsyms,
        "ncols": ncols,
        "d_axis_definition": "v odd, gcd(u,N) odd, 109|gcd(u,N), and u=gcd(u,N)",
        "d_axis_size": len(d_axis),
        "d_axis_by_u": counter_items(d_by_u),
        "d_axis_by_v_mod_109": counter_items(d_by_v_mod_109),
        "d_axis_by_gcd_v": counter_items(d_by_gcd_v),
        "d_axis_formula": d_axis_formula,
        "manin_rows_checked": nsyms,
        "manin_odd_d_count": sum(count for key, count in manin_d_hit_count.items() if int(key) % 2),
        "manin_d_hit_count_distribution": counter_items(manin_d_hit_count),
        "manin_d_column_hit_frequency": counter_items(collections.Counter(manin_d_column_hits[col] for col in d_axis)),
        "manin_odd_source_u_top": counter_items(manin_odd_source_u),
        "manin_odd_source_gcd_u_top": counter_items(manin_odd_source_gcd_u),
        "manin_odd_source_v_parity": counter_items(manin_odd_source_v_parity),
        "t5_rows_checked": t5_limit,
        "t5_odd_d_count": sum(count for key, count in t5_d_hit_count.items() if int(key) % 2),
        "t5_d_hit_count_distribution": counter_items(t5_d_hit_count),
        "t5_d_column_hit_frequency": counter_items(collections.Counter(t5_d_column_hits[col] for col in d_axis)),
        "t5_odd_source_u": counter_items(t5_odd_source_u),
        "t5_odd_source_v_mod_109": counter_items(t5_odd_source_v_mod_109),
        "t5_odd_source_v_mod_872": counter_items(t5_odd_source_v_mod_872),
        "t5_odd_source_v_mod_8": counter_items(t5_odd_source_v_mod_8),
        "t5_odd_hit_matrix": counter_items(t5_odd_hit_matrix),
        "t5_residue_formula": "odd T5-D hits satisfy 5*v + a*u == 0 mod 109 for [1,a;0,5], a=1,2,3,4; the residues 87,65,43,21 are the u=1 special case",
        "examples": {
            "manin_odd": manin_odd_examples,
            "t5_odd": t5_odd_examples,
        },
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
