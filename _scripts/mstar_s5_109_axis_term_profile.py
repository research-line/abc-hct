#!/usr/bin/env python3
"""Profile which Manin term hits each S5 p=2 D-axis column.

The source profile gives the 12 source rows per D-column.  This script refines
that by splitting each Manin triangle into its ``id``, ``T`` and ``TT`` terms.
The output is intended as a bridge from computation to a hand CRT proof.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
import time
from typing import Any


TERM_LABELS = ("id", "T", "TT")


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


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


def bucket_source_relative(u: int, target_u: int, target_v: int, level: int) -> str:
    if u == math.gcd(target_v, level):
        return "base-gcd-v-line"
    if u == target_u:
        return "target-109d-axis"
    if u % 2 == 0 and u % 109 != 0:
        return "even-intermediate"
    return "other"


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 109-Axis Term Profile",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- q: `{payload['q']}`",
        f"- D-axis size: `{payload['d_axis_size']}`",
        f"- D columns with records: `{payload['d_columns_with_records']}`",
        f"- per-D record count: `{payload['per_d_record_count_distribution']}`",
        f"- term signature distribution: `{payload['term_signature_distribution']}`",
        f"- relative-bucket/term signature distribution: `{payload['relative_bucket_term_signature_distribution']}`",
        f"- nonstandard examples: `{len(payload['nonstandard_examples'])}`",
        "",
        "## Term Signatures",
        "",
        "| signature | D columns |",
        "|---|---:|",
    ]
    for item in payload["term_signature_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Relative Bucket / Term Signatures",
            "",
            "| signature | D columns |",
            "|---|---:|",
        ]
    )
    for item in payload["relative_bucket_term_signature_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Global Relative Bucket By Term",
            "",
            "| bucket,term | count |",
            "|---|---:|",
        ]
    )
    for item in payload["global_relative_bucket_term_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(["", "## Samples", "", "```json"])
    lines.append(json.dumps(payload["sample_d_columns"], indent=2, ensure_ascii=False))
    lines.extend(["```", ""])

    if payload["nonstandard_examples"]:
        lines.extend(["## Nonstandard Examples", "", "```json"])
        lines.append(json.dumps(payload["nonstandard_examples"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])

    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--example-limit", type=int, default=10)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    level = int(args.level)
    q = int(args.q)

    log("importing Sage")
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    field_q = GF(q)
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
    for col in range(ncols):
        u, v = col_uv(col)
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            d_axis.add(col)

    records_by_d: dict[int, list[dict[str, Any]]] = {col: [] for col in sorted(d_axis)}
    global_relative_bucket_term: collections.Counter[str] = collections.Counter()
    row_d_hit_count: collections.Counter[int] = collections.Counter()

    log("scanning labelled Manin terms")
    for i in range(nsyms):
        labelled_terms = {
            "id": [(i, field_q(1))],
            "T": list(syms.apply_T(i)),
            "TT": list(syms.apply_TT(i)),
        }
        source_u, source_v = source_uv(i)
        row_hits: set[int] = set()
        for label in TERM_LABELS:
            hits = sorted(row_mod2(reduce_terms(labelled_terms[label])).intersection(d_axis))
            row_hits.update(hits)
            for col in hits:
                target_u, target_v = col_uv(col)
                relative_bucket = bucket_source_relative(source_u, target_u, target_v, level)
                key = f"{relative_bucket}:{label}"
                global_relative_bucket_term[key] += 1
                records_by_d[col].append(
                    {
                        "row_index": int(i),
                        "source": [int(source_u), int(source_v)],
                        "relative_source_bucket": relative_bucket,
                        "term": label,
                    }
                )
        row_d_hit_count[len(row_hits)] += 1

    per_d_record_count: collections.Counter[int] = collections.Counter()
    term_signature_distribution: collections.Counter[str] = collections.Counter()
    relative_bucket_term_signature_distribution: collections.Counter[str] = collections.Counter()
    sample_d_columns: list[dict[str, Any]] = []
    nonstandard_examples: list[dict[str, Any]] = []
    expected_term_signature = "T:768|TT:768|id:768"
    expected_relative_signature = (
        "base-gcd-v-line:TT:2|base-gcd-v-line:id:2|"
        "even-intermediate:T:4|"
        "target-109d-axis:TT:2|target-109d-axis:id:2"
    )

    for col in sorted(d_axis):
        records = records_by_d[col]
        per_d_record_count[len(records)] += 1
        term_counts = collections.Counter(record["term"] for record in records)
        term_signature = "|".join(f"{label}:{term_counts[label]}" for label in TERM_LABELS)
        term_signature_distribution[term_signature] += 1

        rb_term_counts = collections.Counter(
            f"{record['relative_source_bucket']}:{record['term']}" for record in records
        )
        rb_term_signature = "|".join(f"{key}:{rb_term_counts[key]}" for key in sorted(rb_term_counts))
        relative_bucket_term_signature_distribution[rb_term_signature] += 1

        target_u, target_v = col_uv(col)
        item = {
            "col": int(col),
            "uv": [int(target_u), int(target_v)],
            "target_d": int(target_u // 109),
            "target_gcd_v": int(math.gcd(target_v, level)),
            "term_counts": dict((label, int(term_counts[label])) for label in TERM_LABELS),
            "relative_bucket_term_counts": dict(sorted((key, int(val)) for key, val in rb_term_counts.items())),
            "records": records,
        }
        if len(sample_d_columns) < int(args.example_limit):
            sample_d_columns.append(item)
        if (
            term_signature != "id:4|T:4|TT:4"
            or rb_term_signature != expected_relative_signature
        ) and len(nonstandard_examples) < int(args.example_limit):
            nonstandard_examples.append(item)

    payload: dict[str, Any] = {
        "tool": "mstar_s5_109_axis_term_profile",
        "level": level,
        "weight": int(args.weight),
        "sign": int(args.sign),
        "q": q,
        "nsyms": nsyms,
        "ncols": ncols,
        "d_axis_size": len(d_axis),
        "d_columns_with_records": sum(1 for records in records_by_d.values() if records),
        "row_d_hit_count_distribution": counter_items(row_d_hit_count),
        "per_d_record_count_distribution": counter_items(per_d_record_count),
        "term_signature_distribution": counter_items(term_signature_distribution),
        "relative_bucket_term_signature_distribution": counter_items(relative_bucket_term_signature_distribution),
        "global_relative_bucket_term_distribution": counter_items(global_relative_bucket_term),
        "expected_global_term_signature": expected_term_signature,
        "expected_relative_bucket_term_signature": expected_relative_signature,
        "sample_d_columns": sample_d_columns,
        "nonstandard_examples": nonstandard_examples,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
