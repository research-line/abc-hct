#!/usr/bin/env python3
"""Inspect the Manin-symbol origin of a fixed S5 Hecke row.

This is a small Sage-only diagnostic for the p=2 repair row
T_7_minus_0_batch_1/1.  It reconstructs the same fixed GF(3863) quotient as
the S5 repair run and reports which Manin symbol and quotient representatives
produce the row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRACE_VALUES = {
    "raw": {5: 2, 7: 0, 11: 0, 13: -6},
    "anc": {5: 2, 7: 0, 11: 0, 13: -6},
}


def canonical_row(row: dict[int, int], q: int) -> str:
    parts = []
    for col in sorted(row):
        val = int(row[col]) % q
        if val:
            parts.append(f"{int(col)}:{val}")
    return ",".join(parts)


def row_line_hash(stage: str, stage_row_index: int, row: dict[int, int], q: int) -> str:
    line = f"{stage}\t{stage_row_index}\t{canonical_row(row, q)}\n"
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def standard_hecke_matrices(p: int) -> list[list[int]]:
    return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--hecke-prime", type=int, default=7)
    parser.add_argument("--stage-row-index", type=int, default=1)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    q = int(args.q)
    field = GF(q)
    syms = ManinSymbolList_gamma0(args.level, 2)
    nsyms = len(syms)
    rels = set(modS_relations(syms))
    if args.sign in (-1, 1):
        rels.update(modI_relations(syms, args.sign))
    mod = sparse_2term_quotient(rels, nsyms, field)

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
        mod_map.append((rep_to_col[rep_i], field(scalar)))

    def reduce_terms(terms: list[tuple[int, Any]]) -> dict[int, int]:
        row: dict[int, Any] = {}
        for j, coeff in terms:
            mapped = mod_map[int(j)]
            if mapped is None:
                continue
            col, scalar = mapped
            val = field(coeff) * scalar
            if val == 0:
                continue
            row[col] = row.get(col, field(0)) + val
            if row[col] == 0:
                del row[col]
        return {int(col): int(val) % q for col, val in row.items() if int(val) % q}

    hecke_prime = int(args.hecke_prime)
    ap = TRACE_VALUES[args.mode][hecke_prime]
    i = int(args.stage_row_index)
    mats = standard_hecke_matrices(hecke_prime)
    raw_terms: list[tuple[int, Any]] = [(i, field(-ap))]
    raw_term_sources = [
        {
            "source": "trace_term",
            "matrix_index": None,
            "matrix": None,
            "symbol_index": i,
            "coefficient": int(field(-ap)) % q,
        }
    ]
    per_matrix = []
    for mat_index, mat in enumerate(mats):
        image_terms = list(syms.apply(i, mat))
        raw_terms.extend(image_terms)
        for j, coeff in image_terms:
            raw_term_sources.append(
                {
                    "source": "hecke_image",
                    "matrix_index": mat_index,
                    "matrix": [int(x) for x in mat],
                    "symbol_index": int(j),
                    "coefficient": int(coeff) % q,
                }
            )
        per_matrix.append(
            {
                "matrix_index": mat_index,
                "matrix": [int(x) for x in mat],
                "image_terms": [[int(j), int(coeff) % q, str(syms[int(j)])] for j, coeff in image_terms],
            }
        )
    reduced = reduce_terms(raw_terms)
    stage = f"T_{hecke_prime}_minus_{ap}_batch_1"
    digest = row_line_hash(stage, i, reduced, q)
    quotient_columns = []
    for col, value in sorted(reduced.items()):
        rep = col_to_rep[int(col)]
        quotient_columns.append(
            {
                "col": int(col),
                "value_mod_q": int(value) % q,
                "symmetric_lift": symmetric_lift(int(value), q),
                "value_mod_2": symmetric_lift(int(value), q) % 2,
                "representative_index": int(rep),
                "representative_symbol": str(syms[int(rep)]),
            }
        )
    mapped_terms = []
    for raw in raw_term_sources:
        j = int(raw["symbol_index"])
        mapped = mod_map[j]
        if mapped is None:
            raw.update(
                {
                    "symbol": str(syms[j]),
                    "quotient_col": None,
                    "quotient_scalar": 0,
                    "contribution": 0,
                }
            )
        else:
            col, scalar = mapped
            coeff = field(raw["coefficient"])
            contribution = coeff * scalar
            raw.update(
                {
                    "symbol": str(syms[j]),
                    "quotient_col": int(col),
                    "quotient_scalar": int(scalar) % q,
                    "contribution": int(contribution) % q,
                }
            )
        mapped_terms.append(raw)
    payload = {
        "tool": "mstar_s5_t7_row_origin",
        "level": args.level,
        "mode": args.mode,
        "sign": args.sign,
        "q": q,
        "nsyms": nsyms,
        "ncols": len(rep_to_col),
        "hecke_prime": hecke_prime,
        "ap": ap,
        "stage": stage,
        "stage_row_index": i,
        "source_symbol": str(syms[i]),
        "source_symbol_index": i,
        "row": [[int(col), int(reduced[col]) % q] for col in sorted(reduced)],
        "row_line_sha256": digest,
        "row_mod_2_support": [item["col"] for item in quotient_columns if item["value_mod_2"]],
        "quotient_columns": quotient_columns,
        "mapped_terms": mapped_terms,
        "per_matrix": per_matrix,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# S5 T7 Row Origin",
        "",
        f"Level `{args.level}`, mode `{args.mode}`, sign `{args.sign}`, q `{q}`.",
        f"Stage `{stage}`, row index `{i}`.",
        "",
        "## Source Symbol",
        "",
        f"`{payload['source_symbol']}`",
        "",
        "## Reduced Row",
        "",
        f"Row hash: `{digest}`",
        "",
        "| col | value mod q | lift | mod 2 | representative index | representative symbol |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for item in quotient_columns:
        lines.append(
            f"| {item['col']} | {item['value_mod_q']} | {item['symmetric_lift']} | "
            f"{item['value_mod_2']} | {item['representative_index']} | `{item['representative_symbol']}` |"
        )
    lines.extend(
        [
            "",
            "## Quotient Mapping Of Raw Terms",
            "",
            "| source | matrix | symbol | coeff | quotient col | scalar | contribution |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for item in mapped_terms:
        lines.append(
            f"| {item['source']} | `{item['matrix']}` | `{item['symbol']}` | "
            f"{item['coefficient']} | {item['quotient_col']} | "
            f"{item['quotient_scalar']} | {item['contribution']} |"
        )
    lines.extend(["", "## Hecke Images", "", "| matrix | image terms |", "|---:|---|"])
    for item in per_matrix:
        term_text = "; ".join(f"{term[1]}*`{term[2]}`" for term in item["image_terms"])
        lines.append(f"| `{item['matrix']}` | {term_text} |")
    lines.append("")
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
