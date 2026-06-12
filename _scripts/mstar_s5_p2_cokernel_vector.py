#!/usr/bin/env python3
"""Export the GF(2) cokernel vector before the S5 T7 repair row.

For a row relation matrix A over GF(2), rank ncols-1 means the quotient has
one visible dual direction.  This script reconstructs the fixed GF(3863)
quotient rows up to T5 batch 13, reduces them modulo 2, computes a right
kernel vector x with A*x=0, and pairs x with the T7 standard-edge row.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any


TRACE_VALUES = {
    "raw": {5: 2, 7: 0, 11: 0, 13: -6},
    "anc": {5: 2, 7: 0, 11: 0, 13: -6},
}


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def standard_hecke_matrices(p: int) -> list[list[int]]:
    return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Cokernel Vector Before T7",
        "",
        f"Level `{payload['level']}`, mode `{payload['mode']}`, sign `{payload['sign']}`, q `{payload['q']}`.",
        "",
        "## Summary",
        "",
        f"- ncols: `{payload['ncols']}`",
        f"- rows before T7: `{payload['rows_before_t7']}`",
        f"- rank before T7: `{payload['rank_before_t7']}`",
        f"- right-kernel dimension: `{payload['right_kernel_dimension']}`",
        f"- kernel support size: `{payload['kernel_support_size']}`",
        f"- T7 row dot kernel mod 2: `{payload['t7_pairing_mod2']}`",
        "",
        "## T7 Row",
        "",
        f"- stage row index: `{payload['t7_stage_row_index']}`",
        f"- row mod 2 support: `{payload['t7_row_mod2_support']}`",
        "",
        "## Kernel Support Sample",
        "",
        "| col | representative index | representative symbol | modular symbol |",
        "|---:|---:|---|---|",
    ]
    for item in payload["kernel_support_sample"]:
        lines.append(
            f"| {item['col']} | {item['representative_index']} | "
            f"`{item['representative_symbol']}` | `{item['modular_symbol_rep']}` |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--t5-batches", type=int, default=13)
    parser.add_argument("--t7-stage-row-index", type=int, default=1)
    parser.add_argument("--sample-limit", type=int, default=200)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    log("importing Sage")
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import GF, matrix  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    q = int(args.q)
    field_q = GF(q)
    field_2 = GF(2)
    log(f"building ManinSymbolList level={args.level}")
    syms = ManinSymbolList_gamma0(args.level, 2)
    nsyms = len(syms)
    log(f"Manin symbols: {nsyms}")
    rels = set(modS_relations(syms))
    if args.sign in (-1, 1):
        rels.update(modI_relations(syms, args.sign))
    log(f"S/I relations: {len(rels)}; building sparse_2term_quotient")
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

    rows_mod2: list[dict[int, int]] = []

    def add_raw_row(raw_row: dict[int, int]) -> None:
        reduced = row_mod2(raw_row)
        if reduced:
            rows_mod2.append(reduced)

    log("adding Manin T-relations")
    for i in range(nsyms):
        terms: list[tuple[int, Any]] = [(i, field_q(1))]
        terms.extend(syms.apply_T(i))
        terms.extend(syms.apply_TT(i))
        add_raw_row(reduce_terms(terms))

    log(f"adding T5 rows up to {args.t5_batches} batches")
    mats5 = standard_hecke_matrices(5)
    ap5 = TRACE_VALUES[args.mode][5]
    emitted = 0
    for i in range(nsyms):
        terms = [(i, field_q(-ap5))]
        for mat in mats5:
            terms.extend(syms.apply(i, mat))
        add_raw_row(reduce_terms(terms))
        emitted += 1
        if emitted >= args.t5_batches * 1000:
            break

    log(f"building sparse GF(2) matrix rows={len(rows_mod2)} ncols={ncols}")
    entries: dict[tuple[int, int], Any] = {}
    for r, row in enumerate(rows_mod2):
        for col, value in row.items():
            if value:
                entries[(r, int(col))] = field_2(1)
    mat = matrix(field_2, len(rows_mod2), ncols, entries, sparse=True)
    log("computing rank")
    rank = int(mat.rank())
    log(f"rank={rank}; computing right kernel")
    kernel = mat.right_kernel()
    basis = kernel.basis()
    log(f"right kernel dimension={int(kernel.dimension())}")
    if not basis:
        support: list[int] = []
        vector_values: dict[int, int] = {}
    else:
        vec = basis[0]
        support = [i for i, value in enumerate(vec) if int(value) % 2]
        vector_values = {int(i): 1 for i in support}

    mats7 = standard_hecke_matrices(7)
    ap7 = TRACE_VALUES[args.mode][7]
    i = int(args.t7_stage_row_index)
    terms7 = [(i, field_q(-ap7))]
    for mat7 in mats7:
        terms7.extend(syms.apply(i, mat7))
    t7_row = row_mod2(reduce_terms(terms7))
    pairing = sum(t7_row.get(col, 0) * vector_values.get(col, 0) for col in t7_row) % 2

    sample = []
    for col in support[: int(args.sample_limit)]:
        rep = col_to_rep[col]
        sample.append(
            {
                "col": int(col),
                "representative_index": int(rep),
                "representative_symbol": str(syms[int(rep)]),
                "modular_symbol_rep": str(syms[int(rep)].modular_symbol_rep()),
            }
        )

    payload = {
        "tool": "mstar_s5_p2_cokernel_vector",
        "level": args.level,
        "mode": args.mode,
        "sign": args.sign,
        "q": q,
        "nsyms": nsyms,
        "ncols": ncols,
        "rows_before_t7": len(rows_mod2),
        "rank_before_t7": rank,
        "right_kernel_dimension": int(kernel.dimension()),
        "kernel_support_size": len(support),
        "kernel_support": support,
        "kernel_support_sample": sample,
        "t7_stage_row_index": i,
        "t7_row_mod2_support": sorted(t7_row),
        "t7_pairing_mod2": int(pairing),
        "seconds_total": time.perf_counter() - started,
    }
    log(f"writing outputs: {args.out_json}, {args.out_md}")
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
