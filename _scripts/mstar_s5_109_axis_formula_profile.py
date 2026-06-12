#!/usr/bin/env python3
"""Extract formula candidates from the S5 p=2 D-axis transition records.

This script is intentionally post-processing only: it reads the transition JSON
and tries to turn the nine transition fields into compact formula candidates.
It records which identities are already exact and where only distributions are
visible, so the future hand proof does not overstate the computation.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
from typing import Any


MODULI = [2, 3, 4, 8, 23, 46, 69, 92, 109, 218, 327, 552, 872, 2507, 7521, 60168]


def counter_items(counter: collections.Counter[Any], limit: int | None = None) -> list[dict[str, Any]]:
    items = counter.most_common(limit)
    return [{"key": str(key), "count": int(value)} for key, value in items]


def linear_rules(records: list[dict[str, Any]], y_getter, x_getter, moduli: list[int]) -> list[dict[str, Any]]:
    """Find congruences y = a*x + b mod m with small m and all records matched."""
    rules: list[dict[str, Any]] = []
    if not records:
        return rules
    for modulus in moduli:
        x0 = x_getter(records[0]) % modulus
        y0 = y_getter(records[0]) % modulus
        found: list[tuple[int, int]] = []
        for a in range(modulus):
            b = (y0 - a * x0) % modulus
            if all((y_getter(record) - a * x_getter(record) - b) % modulus == 0 for record in records):
                found.append((a, b))
                if len(found) >= 6:
                    break
        if found:
            rules.append(
                {
                    "modulus": modulus,
                    "examples": [{"a": int(a), "b": int(b)} for a, b in found],
                    "count": len(found),
                }
            )
    return rules


def expression_counts(records: list[dict[str, Any]], level: int) -> dict[str, Any]:
    counts: collections.Counter[str] = collections.Counter()
    for record in records:
        tu, tv = record["target_uv"]
        su, sv = record["source_uv"]
        iu, iv = record["image_uv"]
        d = record["target_d"]
        g = record["target_gcd_v"]
        if su == g:
            counts["source_u=g"] += 1
        if su == 109 * d:
            counts["source_u=109*d"] += 1
        if su % 2 == 0 and su % 109 != 0:
            counts["source_u even non-109"] += 1
        if iu == tu and iv == tv:
            counts["image=target"] += 1
        if iu == tu:
            counts["image_u=target_u"] += 1
        if math.gcd(iu, level) == math.gcd(tu, level):
            counts["gcd(image_u,N)=gcd(target_u,N)"] += 1
        if math.gcd(iv, level) == math.gcd(tv, level):
            counts["gcd(image_v,N)=gcd(target_v,N)"] += 1
    return {key: int(value) for key, value in sorted(counts.items())}


def quotient_v_relation_counts(records: list[dict[str, Any]], level: int) -> dict[str, int]:
    counts: collections.Counter[str] = collections.Counter()
    for record in records:
        tu, tv = record["target_uv"]
        su, sv = record["source_uv"]
        iu, iv = record["image_uv"]
        if tu == 0 or level % tu:
            continue
        modulus = level // tu
        if (iv - tv) % modulus == 0:
            counts["image_v=target_v mod N/u"] += 1
        if (iv + tv) % modulus == 0:
            counts["image_v=-target_v mod N/u"] += 1
        if (sv - tv) % modulus == 0:
            counts["source_v=target_v mod N/u"] += 1
        if (sv + tv) % modulus == 0:
            counts["source_v=-target_v mod N/u"] += 1
    return {key: int(value) for key, value in sorted(counts.items())}


def per_target_pair_signatures(records: list[dict[str, Any]], feature_getter) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        grouped[int(record["target_col"])].append(record)
    sigs: collections.Counter[str] = collections.Counter()
    for target_col, rs in grouped.items():
        values = sorted(str(feature_getter(record)) for record in rs)
        sigs["|".join(values)] += 1
    return counter_items(sigs)


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 109-Axis Formula Profile",
        "",
        "## Summary",
        "",
        f"- input: `{payload['input_json']}`",
        f"- transition records: `{payload['transition_record_count']}`",
        f"- fields: `{len(payload['fields'])}`",
        "",
        "## Field Overview",
        "",
        "| field | count | exact identities | source-v linear rules | image-v linear rules |",
        "|---|---:|---|---:|---:|",
    ]
    for item in payload["fields"]:
        identities = ", ".join(item["exact_identity_counts"].keys()) or "-"
        lines.append(
            f"| `{item['field']}` | {item['count']} | {identities} | "
            f"{len(item['source_v_linear_rules'])} | {len(item['image_v_linear_rules'])} |"
        )

    for item in payload["fields"]:
        lines.extend(
            [
                "",
                f"## `{item['field']}`",
                "",
                f"- count: `{item['count']}`",
                f"- exact identities: `{item['exact_identity_counts']}`",
                f"- quotient v-relations: `{item['quotient_v_relation_counts']}`",
                f"- target `(d,g)` distribution: `{item['target_d_g_distribution']}`",
                f"- source-u expression distribution: `{item['source_u_expression_distribution']}`",
                f"- source-v minus target-v mod 109: `{item['source_v_minus_target_v_mod109']}`",
                f"- source-v plus target-v mod 109: `{item['source_v_plus_target_v_mod109']}`",
                f"- image-v minus target-v mod 109: `{item['image_v_minus_target_v_mod109']}`",
                f"- source-v linear rules: `{item['source_v_linear_rules'][:8]}`",
                f"- image-v linear rules: `{item['image_v_linear_rules'][:8]}`",
                f"- per-target source-v mod109 signatures: `{item['per_target_source_v_mod109_signature'][:6]}`",
                f"- per-target image-v mod109 signatures: `{item['per_target_image_v_mod109_signature'][:6]}`",
            ]
        )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    records = data["all_records"]
    level = int(data.get("level", 60168))
    fields: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        field = (
            f"{record['relative_source_bucket']}:{record['term']}:"
            f"{record['quotient_scalar']}:{record['image_relation']}"
        )
        fields[field].append(record)

    field_payloads: list[dict[str, Any]] = []
    for field in sorted(fields):
        rs = fields[field]
        source_u_expr_counter: collections.Counter[str] = collections.Counter()
        for record in rs:
            su = record["source_uv"][0]
            d = record["target_d"]
            g = record["target_gcd_v"]
            if su == g:
                source_u_expr_counter["g"] += 1
            elif su == 109 * d:
                source_u_expr_counter["109*d"] += 1
            elif su % 2 == 0 and su % 109 != 0:
                source_u_expr_counter["even_non109"] += 1
            else:
                source_u_expr_counter[str(su)] += 1

        source_v_rules = linear_rules(
            rs,
            y_getter=lambda r: int(r["source_uv"][1]),
            x_getter=lambda r: int(r["target_uv"][1]),
            moduli=MODULI,
        )
        image_v_rules = linear_rules(
            rs,
            y_getter=lambda r: int(r["image_uv"][1]),
            x_getter=lambda r: int(r["target_uv"][1]),
            moduli=MODULI,
        )

        item = {
            "field": field,
            "count": len(rs),
            "exact_identity_counts": expression_counts(rs, level),
            "quotient_v_relation_counts": quotient_v_relation_counts(rs, level),
            "target_d_g_distribution": counter_items(
                collections.Counter(f"{r['target_d']},{r['target_gcd_v']}" for r in rs)
            ),
            "source_u_expression_distribution": counter_items(source_u_expr_counter),
            "source_u_distribution": counter_items(collections.Counter(r["source_uv"][0] for r in rs), limit=20),
            "source_v_minus_target_v_mod109": counter_items(
                collections.Counter((r["source_uv"][1] - r["target_uv"][1]) % 109 for r in rs),
                limit=20,
            ),
            "source_v_plus_target_v_mod109": counter_items(
                collections.Counter((r["source_uv"][1] + r["target_uv"][1]) % 109 for r in rs),
                limit=20,
            ),
            "image_v_minus_target_v_mod109": counter_items(
                collections.Counter((r["image_uv"][1] - r["target_uv"][1]) % 109 for r in rs),
                limit=20,
            ),
            "source_v_linear_rules": source_v_rules,
            "image_v_linear_rules": image_v_rules,
            "per_target_source_v_mod109_signature": per_target_pair_signatures(
                rs, lambda r: int(r["source_uv"][1]) % 109
            ),
            "per_target_image_v_mod109_signature": per_target_pair_signatures(
                rs, lambda r: int(r["image_uv"][1]) % 109
            ),
        }
        field_payloads.append(item)

    payload = {
        "tool": "mstar_s5_109_axis_formula_profile",
        "input_json": str(args.input_json),
        "level": level,
        "transition_record_count": len(records),
        "fields": field_payloads,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
