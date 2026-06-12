#!/usr/bin/env python3
"""Profile the Manin source rows hitting the S5 p=2 109-axis D.

This refines ``mstar_s5_109_axis_profile.py``.  The previous profile showed
that every D-column is hit by exactly 12 Manin T-relations.  This script records
the source decomposition per D-column, with bucketed source types and examples,
so the observed 109-boundary correction can be promoted to a small lemma.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
import time
from typing import Any


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


def bucket_source(u: int, v: int, level: int) -> str:
    gcd_u = math.gcd(u, level)
    if u == 1:
        return "standard-u=1"
    if u % 2 == 0 and u % 109 != 0:
        return "even-intermediate"
    if u % 109 == 0 and u % 2 == 1:
        return "odd-109-axis"
    return "other"


def bucket_source_relative(u: int, target_u: int, target_v: int, level: int) -> str:
    target_base = math.gcd(target_v, level)
    if u == target_base:
        return "base-gcd-v-line"
    if u == target_u:
        return "target-109d-axis"
    if u % 2 == 0 and u % 109 != 0:
        return "even-intermediate"
    return "other"


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 109-Axis Source Profile",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- q: `{payload['q']}`",
        f"- quotient columns: `{payload['ncols']}`",
        f"- D-axis size: `{payload['d_axis_size']}`",
        f"- Manin rows checked: `{payload['manin_rows_checked']}`",
        f"- D columns with source records: `{payload['d_columns_with_sources']}`",
        f"- source-count distribution per D-column: `{payload['source_count_distribution']}`",
        f"- absolute bucket-signature distribution: `{payload['bucket_signature_distribution']}`",
        f"- target-relative bucket-signature distribution: `{payload['relative_bucket_signature_distribution']}`",
        f"- relative nonstandard examples: `{len(payload['relative_nonstandard_bucket_examples'])}`",
        "",
        "## Target-Relative Bucket Signatures",
        "",
        "| signature | D columns |",
        "|---|---:|",
    ]
    for item in payload["relative_bucket_signature_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Absolute Bucket Signatures",
            "",
            "| signature | D columns |",
            "|---|---:|",
        ]
    )
    for item in payload["bucket_signature_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Target d Distribution",
            "",
            "| d | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["target_d_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(
        [
            "",
            "## Target gcd(v,N) Distribution",
            "",
            "| gcd(v,N) | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["target_gcd_v_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(
        [
            "",
            "## Target Joint Distribution",
            "",
            "| u/109,gcd(v,N) | count |",
            "|---|---:|",
        ]
    )
    for item in payload["target_u_gcd_v_joint_distribution"]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Relative Source Bucket Distribution",
            "",
            "| bucket | count |",
            "|---|---:|",
        ]
    )
    for item in payload["relative_source_bucket_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(
        [
            "",
            "## Source gcd(u,N) Distribution",
            "",
            "| gcd(u,N) | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["source_gcd_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(
        [
            "",
            "## Source u Distribution",
            "",
            "| u | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["source_u_distribution"][:40]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(["", "## Sample D Columns", "", "```json"])
    lines.append(json.dumps(payload["sample_d_columns"], indent=2, ensure_ascii=False))
    lines.extend(["```", ""])

    if payload["relative_nonstandard_bucket_examples"]:
        lines.extend(["## Relative Nonstandard Bucket Examples", "", "```json"])
        lines.append(json.dumps(payload["relative_nonstandard_bucket_examples"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])

    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--example-limit", type=int, default=12)
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
    for col in range(ncols):
        u, v = col_uv(col)
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            d_axis.add(col)

    records_by_d: dict[int, list[dict[str, Any]]] = {col: [] for col in sorted(d_axis)}
    hit_count_distribution: collections.Counter[int] = collections.Counter()
    source_u_distribution: collections.Counter[int] = collections.Counter()
    source_gcd_distribution: collections.Counter[int] = collections.Counter()
    source_bucket_distribution: collections.Counter[str] = collections.Counter()
    relative_source_bucket_distribution: collections.Counter[str] = collections.Counter()

    log("scanning Manin T-relations against D")
    for i in range(nsyms):
        terms: list[tuple[int, Any]] = [(i, field_q(1))]
        terms.extend(syms.apply_T(i))
        terms.extend(syms.apply_TT(i))
        row = row_mod2(reduce_terms(terms))
        hits = sorted(row.intersection(d_axis))
        hit_count_distribution[len(hits)] += 1
        if not hits:
            continue
        su, sv = source_uv(i)
        bucket = bucket_source(su, sv, level)
        source_u_distribution[su] += len(hits)
        source_gcd_distribution[math.gcd(su, level)] += len(hits)
        source_bucket_distribution[bucket] += len(hits)
        for col in hits:
            target_u, target_v = col_uv(col)
            relative_bucket = bucket_source_relative(su, target_u, target_v, level)
            relative_source_bucket_distribution[relative_bucket] += 1
            records_by_d[col].append(
                {
                    "row_index": int(i),
                    "source": [int(su), int(sv)],
                    "source_gcd_u": int(math.gcd(su, level)),
                    "source_bucket": bucket,
                    "relative_source_bucket": relative_bucket,
                }
            )

    per_d_source_count: collections.Counter[int] = collections.Counter()
    bucket_signature_distribution: collections.Counter[str] = collections.Counter()
    relative_bucket_signature_distribution: collections.Counter[str] = collections.Counter()
    target_d_distribution: collections.Counter[int] = collections.Counter()
    target_gcd_v_distribution: collections.Counter[int] = collections.Counter()
    target_u_gcd_v_joint_distribution: collections.Counter[str] = collections.Counter()
    relative_nonstandard_bucket_examples: list[dict[str, Any]] = []
    sample_d_columns: list[dict[str, Any]] = []
    missing_d_columns: list[dict[str, Any]] = []

    expected_relative_signature = "base-gcd-v-line:4|even-intermediate:4|target-109d-axis:4"
    for col in sorted(d_axis):
        target_u, target_v = col_uv(col)
        target_d = target_u // 109
        target_gcd_v = math.gcd(target_v, level)
        target_d_distribution[target_d] += 1
        target_gcd_v_distribution[target_gcd_v] += 1
        target_u_gcd_v_joint_distribution[f"{target_d},{target_gcd_v}"] += 1
        records = records_by_d[col]
        per_d_source_count[len(records)] += 1
        buckets = collections.Counter(record["source_bucket"] for record in records)
        signature = "|".join(f"{key}:{buckets[key]}" for key in sorted(buckets))
        bucket_signature_distribution[signature] += 1
        relative_buckets = collections.Counter(record["relative_source_bucket"] for record in records)
        relative_signature = "|".join(f"{key}:{relative_buckets[key]}" for key in sorted(relative_buckets))
        relative_bucket_signature_distribution[relative_signature] += 1
        item = {
            "col": int(col),
            "uv": [int(target_u), int(target_v)],
            "target_d": int(target_d),
            "target_gcd_v": int(target_gcd_v),
            "source_count": len(records),
            "bucket_counts": dict(sorted(buckets.items())),
            "relative_bucket_counts": dict(sorted(relative_buckets.items())),
            "sources": records,
        }
        if len(sample_d_columns) < int(args.example_limit):
            sample_d_columns.append(item)
        if (
            relative_signature != expected_relative_signature
            and len(relative_nonstandard_bucket_examples) < int(args.example_limit)
        ):
            relative_nonstandard_bucket_examples.append(item)
        if not records:
            missing_d_columns.append({"col": int(col), "uv": [int(target_u), int(target_v)]})

    payload: dict[str, Any] = {
        "tool": "mstar_s5_109_axis_source_profile",
        "level": level,
        "weight": int(args.weight),
        "sign": int(args.sign),
        "q": q,
        "nsyms": nsyms,
        "ncols": ncols,
        "d_axis_definition": "v odd, gcd(u,N) odd, 109|gcd(u,N), and u=gcd(u,N)",
        "d_axis_size": len(d_axis),
        "manin_rows_checked": nsyms,
        "manin_d_hit_count_distribution": counter_items(hit_count_distribution),
        "d_columns_with_sources": sum(1 for records in records_by_d.values() if records),
        "source_count_distribution": counter_items(per_d_source_count),
        "expected_relative_bucket_signature": expected_relative_signature,
        "bucket_signature_distribution": counter_items(bucket_signature_distribution),
        "relative_bucket_signature_distribution": counter_items(relative_bucket_signature_distribution),
        "target_d_distribution": counter_items(target_d_distribution),
        "target_gcd_v_distribution": counter_items(target_gcd_v_distribution),
        "target_u_gcd_v_joint_distribution": counter_items(target_u_gcd_v_joint_distribution),
        "source_bucket_distribution": counter_items(source_bucket_distribution),
        "relative_source_bucket_distribution": counter_items(relative_source_bucket_distribution),
        "source_gcd_distribution": counter_items(source_gcd_distribution),
        "source_u_distribution": counter_items(source_u_distribution),
        "missing_d_columns": missing_d_columns[: int(args.example_limit)],
        "sample_d_columns": sample_d_columns,
        "relative_nonstandard_bucket_examples": relative_nonstandard_bucket_examples,
        "seconds_total": time.perf_counter() - started,
    }

    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
