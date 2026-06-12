#!/usr/bin/env python3
"""Profile the full T5 residue law for the S5 p=2 D-correction."""

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


def standard_hecke_matrices(p: int) -> list[list[int]]:
    return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


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
        "# S5 p=2 Full T5 Residue Law Profile",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- mode: `{payload['mode']}`",
        f"- q: `{payload['q']}`",
        f"- T5 rows checked: `{payload['t5_rows_checked']}`",
        f"- odd D-hit rows: `{payload['odd_d_hit_rows']}`",
        f"- odd rows with exactly one D hit: `{payload['odd_rows_one_d_hit']}`",
        f"- odd rows with exactly one matrix hit: `{payload['odd_rows_one_matrix_hit']}`",
        f"- residue-law good rows: `{payload['residue_law_good_rows']}`",
        f"- bad rows: `{len(payload['bad_rows'])}`",
        "",
        "## Law",
        "",
        "For an odd D-hit in the full `T_5-a_5(E)` row, the hit comes from",
        "exactly one standard matrix `[1,a;0,5]`, `a=1,2,3,4`, and the source",
        "`(u,v)` satisfies",
        "",
        "```text",
        "5*v + a*u == 0 mod 109.",
        "```",
        "",
        "The dual matrix and the `a=0` matrix do not contribute to odd D-hits.",
        "",
        "## Source u",
        "",
        "| u | count |",
        "|---:|---:|",
    ]
    for item in payload["source_u_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(["", "## Matrix a", "", "| a | count |", "|---:|---:|"])
    for item in payload["matrix_a_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(["", "## Source u x a", "", "| u,a | count |", "|---|---:|"])
    for item in payload["source_u_matrix_a_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    if payload["bad_rows"]:
        lines.extend(["", "## Bad Rows", "", "```json"])
        lines.append(json.dumps(payload["bad_rows"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    q = int(args.q)
    field_q = GF(q)
    level = int(args.level)
    syms = ManinSymbolList_gamma0(level, int(args.weight))
    nsyms = len(syms)
    raw_symbol_list = list(getattr(syms, "_symbol_list"))

    rels = set(modS_relations(syms))
    if int(args.sign) in (-1, 1):
        rels.update(modI_relations(syms, int(args.sign)))
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
    for col in range(len(rep_to_col)):
        u, v = col_uv(col)
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            d_axis.add(col)

    def d_hits_for_row(row: set[int]) -> list[int]:
        return sorted(row.intersection(d_axis))

    mats5 = standard_hecke_matrices(5)
    ap5 = TRACE_VALUES[str(args.mode)][5]
    source_u_counter: collections.Counter[int] = collections.Counter()
    source_u_matrix_counter: collections.Counter[str] = collections.Counter()
    matrix_counter: collections.Counter[int] = collections.Counter()
    target_u_counter: collections.Counter[int] = collections.Counter()
    odd_rows = 0
    odd_rows_one_d_hit = 0
    odd_rows_one_matrix_hit = 0
    residue_good = 0
    bad_rows: list[dict[str, Any]] = []

    for i in range(nsyms):
        terms = [(i, field_q(-ap5))]
        matrix_hits: list[dict[str, Any]] = []
        for mat in mats5:
            mat_terms = syms.apply(i, mat)
            terms.extend(mat_terms)
            mat_row = row_mod2(reduce_terms(mat_terms))
            hits = d_hits_for_row(mat_row)
            if hits:
                label = int(mat[1]) if mat[0] == 1 and mat[3] == 5 else -1
                matrix_hits.append(
                    {
                        "matrix": [int(x) for x in mat],
                        "a": label,
                        "hits": [{"col": col, "uv": list(col_uv(col))} for col in hits],
                    }
                )
        row = row_mod2(reduce_terms(terms))
        hits = d_hits_for_row(row)
        if len(hits) % 2 == 0:
            continue
        odd_rows += 1
        if len(hits) == 1:
            odd_rows_one_d_hit += 1
        hit_entries = [
            item
            for item in matrix_hits
            for _hit in item["hits"]
        ]
        if len(hit_entries) == 1:
            odd_rows_one_matrix_hit += 1
        u, v = source_uv(i)
        good = (
            len(hits) == 1
            and len(hit_entries) == 1
            and hit_entries[0]["a"] in (1, 2, 3, 4)
            and (5 * v + hit_entries[0]["a"] * u) % 109 == 0
            and level % u == 0
            and 69 % u == 0
        )
        if good:
            residue_good += 1
            a = int(hit_entries[0]["a"])
            source_u_counter[u] += 1
            matrix_counter[a] += 1
            source_u_matrix_counter[f"u={u},a={a}"] += 1
            target_u_counter[col_uv(hits[0])[0]] += 1
        elif len(bad_rows) < 30:
            bad_rows.append(
                {
                    "row_index": i,
                    "source": [u, v],
                    "d_hits": [{"col": col, "uv": list(col_uv(col))} for col in hits],
                    "matrix_hits": matrix_hits,
                    "formula_residues": [
                        {
                            "a": item["a"],
                            "residue": (5 * v + int(item["a"]) * u) % 109 if item["a"] != -1 else None,
                        }
                        for item in hit_entries
                    ],
                }
            )

    payload = {
        "tool": "mstar_s5_t5_residue_law_profile",
        "level": level,
        "weight": int(args.weight),
        "mode": str(args.mode),
        "sign": int(args.sign),
        "q": q,
        "nsyms": nsyms,
        "ncols": len(rep_to_col),
        "d_axis_size": len(d_axis),
        "t5_rows_checked": nsyms,
        "odd_d_hit_rows": odd_rows,
        "odd_rows_one_d_hit": odd_rows_one_d_hit,
        "odd_rows_one_matrix_hit": odd_rows_one_matrix_hit,
        "residue_law_good_rows": residue_good,
        "source_u_distribution": counter_items(source_u_counter),
        "matrix_a_distribution": counter_items(matrix_counter),
        "source_u_matrix_a_distribution": counter_items(source_u_matrix_counter),
        "target_u_distribution": counter_items(target_u_counter),
        "bad_rows": bad_rows,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
