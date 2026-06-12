#!/usr/bin/env python3
"""Trace raw Manin images that land on the S5 p=2 109-axis D.

The term profile says which source row and which term (id/T/TT) hits a D-column.
This script records the raw image before the sparse quotient reduction, the
quotient scalar, and compact distributions.  It is meant to expose the
S-/I-identifications behind the future hand CRT proof.
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


def image_relation(image_uv: tuple[int, int], target_uv: tuple[int, int], level: int) -> str:
    iu, iv = image_uv
    tu, tv = target_uv
    if (iu, iv) == (tu, tv):
        return "exact"
    if iu == tu and (iv - tv) % level == 0:
        return "same-u-same-v-mod-N"
    if iu == tu:
        return "same-u"
    if math.gcd(iu, level) == math.gcd(tu, level) and math.gcd(iv, level) == math.gcd(tv, level):
        return "same-gcd-pair"
    if math.gcd(iu, level) == math.gcd(tu, level):
        return "same-gcd-u"
    return "other"


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 109-Axis Transition Profile",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- q: `{payload['q']}`",
        f"- D-axis size: `{payload['d_axis_size']}`",
        f"- transition records: `{payload['transition_record_count']}`",
        f"- records per D-column: `{payload['records_per_d_distribution']}`",
        f"- term distribution: `{payload['term_distribution']}`",
        f"- relative bucket / term distribution: `{payload['relative_bucket_term_distribution']}`",
        f"- quotient scalar distribution: `{payload['quotient_scalar_distribution']}`",
        "",
        "## Image Relation Distribution",
        "",
        "| relation | count |",
        "|---|---:|",
    ]
    for item in payload["image_relation_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")

    lines.extend(
        [
            "",
            "## Relative Bucket / Term / Scalar",
            "",
            "| bucket:term:scalar | count |",
            "|---|---:|",
        ]
    )
    for item in payload["relative_bucket_term_scalar_distribution"][:40]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Relative Bucket / Term / Scalar / Image Relation",
            "",
            "| bucket:term:scalar:relation | count |",
            "|---|---:|",
        ]
    )
    for item in payload["relative_bucket_term_scalar_relation_distribution"][:40]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Per-D Full Signatures",
            "",
            "| signature | D columns |",
            "|---|---:|",
        ]
    )
    for item in payload["per_d_full_signature_distribution"][:20]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Raw Image gcd Pair",
            "",
            "| gcd(image_u,N),gcd(image_v,N) | count |",
            "|---|---:|",
        ]
    )
    for item in payload["image_gcd_pair_distribution"][:40]:
        lines.append(f"| `{item['key']}` | {item['count']} |")

    lines.extend(["", "## Samples", "", "```json"])
    lines.append(json.dumps(payload["sample_records"], indent=2, ensure_ascii=False))
    lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--example-limit", type=int, default=40)
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

    def col_uv(col: int) -> tuple[int, int]:
        return symbol_tuple_from_raw(raw_symbol_list[int(col_to_rep[col])])

    def raw_uv(index: int) -> tuple[int, int]:
        return symbol_tuple_from_raw(raw_symbol_list[int(index)])

    d_axis: set[int] = set()
    for col in range(len(col_to_rep)):
        u, v = col_uv(col)
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            d_axis.add(col)

    transition_records: list[dict[str, Any]] = []
    records_by_d: collections.Counter[int] = collections.Counter()
    term_distribution: collections.Counter[str] = collections.Counter()
    relative_bucket_term_distribution: collections.Counter[str] = collections.Counter()
    relative_bucket_term_scalar_distribution: collections.Counter[str] = collections.Counter()
    relative_bucket_term_scalar_relation_distribution: collections.Counter[str] = collections.Counter()
    quotient_scalar_distribution: collections.Counter[int] = collections.Counter()
    image_relation_distribution: collections.Counter[str] = collections.Counter()
    image_gcd_pair_distribution: collections.Counter[str] = collections.Counter()

    log("scanning raw term transitions")
    for i in range(nsyms):
        source_u, source_v = raw_uv(i)
        labelled_terms = {
            "id": [(i, field_q(1))],
            "T": list(syms.apply_T(i)),
            "TT": list(syms.apply_TT(i)),
        }
        for label in TERM_LABELS:
            for image_index_raw, coeff_raw in labelled_terms[label]:
                mapped = mod_map[int(image_index_raw)]
                if mapped is None:
                    continue
                target_col, quotient_scalar = mapped
                if target_col not in d_axis:
                    continue
                reduced = field_q(coeff_raw) * quotient_scalar
                if symmetric_lift(int(reduced), q) % 2 == 0:
                    continue
                target_u, target_v = col_uv(target_col)
                image_u, image_v = raw_uv(int(image_index_raw))
                relative_bucket = bucket_source_relative(source_u, target_u, target_v, level)
                quotient_scalar_i = symmetric_lift(int(quotient_scalar), q)
                coeff_i = symmetric_lift(int(coeff_raw), q)
                reduced_i = symmetric_lift(int(reduced), q)
                relation = image_relation((image_u, image_v), (target_u, target_v), level)
                record = {
                    "target_col": int(target_col),
                    "target_uv": [int(target_u), int(target_v)],
                    "target_d": int(target_u // 109),
                    "target_gcd_v": int(math.gcd(target_v, level)),
                    "source_index": int(i),
                    "source_uv": [int(source_u), int(source_v)],
                    "relative_source_bucket": relative_bucket,
                    "term": label,
                    "image_index": int(image_index_raw),
                    "image_uv": [int(image_u), int(image_v)],
                    "image_relation": relation,
                    "term_coeff": int(coeff_i),
                    "quotient_scalar": int(quotient_scalar_i),
                    "reduced_coeff": int(reduced_i),
                }
                transition_records.append(record)
                records_by_d[int(target_col)] += 1
                term_distribution[label] += 1
                relative_bucket_term_distribution[f"{relative_bucket}:{label}"] += 1
                relative_bucket_term_scalar_distribution[f"{relative_bucket}:{label}:{quotient_scalar_i}"] += 1
                relative_bucket_term_scalar_relation_distribution[
                    f"{relative_bucket}:{label}:{quotient_scalar_i}:{relation}"
                ] += 1
                quotient_scalar_distribution[quotient_scalar_i] += 1
                image_relation_distribution[relation] += 1
                image_gcd_pair_distribution[f"{math.gcd(image_u, level)},{math.gcd(image_v, level)}"] += 1

    records_by_target: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in transition_records:
        records_by_target[int(record["target_col"])].append(record)
    per_d_full_signature_distribution: collections.Counter[str] = collections.Counter()
    for records in records_by_target.values():
        signature_counter = collections.Counter(
            (
                f"{record['relative_source_bucket']}:{record['term']}:"
                f"{record['quotient_scalar']}:{record['image_relation']}"
            )
            for record in records
        )
        signature = "|".join(f"{key}:{signature_counter[key]}" for key in sorted(signature_counter))
        per_d_full_signature_distribution[signature] += 1

    payload: dict[str, Any] = {
        "tool": "mstar_s5_109_axis_transition_profile",
        "level": level,
        "weight": int(args.weight),
        "sign": int(args.sign),
        "q": q,
        "nsyms": nsyms,
        "ncols": len(col_to_rep),
        "d_axis_size": len(d_axis),
        "transition_record_count": len(transition_records),
        "records_per_d_distribution": counter_items(collections.Counter(records_by_d[col] for col in d_axis)),
        "term_distribution": counter_items(term_distribution),
        "relative_bucket_term_distribution": counter_items(relative_bucket_term_distribution),
        "relative_bucket_term_scalar_distribution": counter_items(relative_bucket_term_scalar_distribution),
        "relative_bucket_term_scalar_relation_distribution": counter_items(
            relative_bucket_term_scalar_relation_distribution
        ),
        "per_d_full_signature_distribution": counter_items(per_d_full_signature_distribution),
        "quotient_scalar_distribution": counter_items(quotient_scalar_distribution),
        "image_relation_distribution": counter_items(image_relation_distribution),
        "image_gcd_pair_distribution": counter_items(image_gcd_pair_distribution),
        "sample_records": transition_records[: int(args.example_limit)],
        "all_records": transition_records,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    log(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
