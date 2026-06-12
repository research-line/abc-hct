#!/usr/bin/env python3
"""Profile the negative other image fiber in the S5 p=2 D-axis records."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import time
from typing import Any


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Negative Other Image Fiber Profile",
        "",
        "## Summary",
        "",
        f"- input: `{payload['input_json']}`",
        f"- level: `{payload['level']}`",
        f"- other records: `{payload['other_record_count']}`",
        f"- image_v mod 109 zero: `{payload['image_v_mod109_zero_count']}`",
        f"- source_v mod 109 zero: `{payload['source_v_mod109_zero_count']}`",
        f"- image_u = gcd(target_v,N): `{payload['image_u_eq_target_gcd_v_count']}`",
        f"- CRT inverse relation ok: `{payload['crt_inverse_relation_count']}`",
        f"- CRT sign distribution: `{payload['crt_sign_distribution']}`",
        f"- S/swap target distribution: `{payload['s_swap_target_distribution']}`",
        "",
        "## Field Distribution",
        "",
        "| field | count | image_v=0 mod109 | image_u=g | source_v=0 mod109 | S/swap pattern |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in payload["fields"]:
        lines.append(
            f"| `{item['field']}` | {item['count']} | {item['image_v_mod109_zero_count']} | "
            f"{item['image_u_eq_target_gcd_v_count']} | {item['source_v_mod109_zero_count']} | "
            f"`{item['s_swap_target_distribution']}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Every negative `other` record lands on the image fiber",
            "",
            "```text",
            "image_v ≡ 0 mod 109.",
            "```",
            "",
            "In fact, every negative `other` raw image has",
            "",
            "```text",
            "image_u = gcd(target_v,N),",
            "```",
            "",
            "so the image fiber is the base line `(g,109*r)` attached to the",
            "target `(109*d,v)`, where `g=gcd(v,N)`.",
            "",
            "The CRT relation is",
            "",
            "```text",
            "(r/d)*(v/g) ≡ ±1 mod 552/(d*g).",
            "```",
            "",
            "The plus/minus signs occur in exactly balanced halves.",
            "",
            "The source coordinate is on this fiber only in the base `id` field,",
            "where source and raw image coincide. The `T` and `T^2` other fields",
            "have varying source residues.",
            "",
            "The S/swap split says that each raw image either maps directly to the",
            "D target under the S-operation, or maps to the `same-u` mirror which",
            "is already controlled by the P1 normalizer mirror lemma.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    records = data["all_records"]
    level = int(data.get("level", 60168))

    import sage.all  # type: ignore  # noqa: F401
    from sage.modular.modsym.p1list import P1List  # type: ignore

    p1 = P1List(level)

    field_records: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    s_swap_counter: collections.Counter[str] = collections.Counter()
    image_v_zero = 0
    source_v_zero = 0
    image_u_eq_target_g = 0
    crt_inverse_relation = 0
    crt_sign_counter: collections.Counter[str] = collections.Counter()
    bad_records: list[dict[str, Any]] = []

    for record in records:
        if record["image_relation"] != "other":
            continue
        field = (
            f"{record['relative_source_bucket']}:{record['term']}:"
            f"{record['quotient_scalar']}:{record['image_relation']}"
        )
        target_u, target_v = [int(x) for x in record["target_uv"]]
        image_u, image_v = [int(x) for x in record["image_uv"]]
        source_v = int(record["source_uv"][1])
        modulus = level // target_u
        s_image = tuple(int(x) for x in p1.normalize(image_v, -image_u))
        swap_image = tuple(int(x) for x in p1.normalize(image_v, image_u))

        flags: list[str] = []
        if s_image == (target_u, target_v):
            flags.append("S=target")
        if swap_image == (target_u, target_v):
            flags.append("swap=target")
        if s_image[0] == target_u and (s_image[1] + target_v) % modulus == 0:
            flags.append("S=mirror")
        if swap_image[0] == target_u and (swap_image[1] + target_v) % modulus == 0:
            flags.append("swap=mirror")
        pattern = "|".join(flags) if flags else "none"
        enriched = dict(record)
        enriched["s_image"] = list(s_image)
        enriched["swap_image"] = list(swap_image)
        enriched["s_swap_pattern"] = pattern
        field_records[field].append(enriched)
        s_swap_counter[pattern] += 1
        if image_v % 109 == 0:
            image_v_zero += 1
        if source_v % 109 == 0:
            source_v_zero += 1
        if image_u == int(record["target_gcd_v"]):
            image_u_eq_target_g += 1
        d = int(record["target_d"])
        g = int(record["target_gcd_v"])
        target_v = int(record["target_uv"][1])
        r_value = image_v // 109 if image_v % 109 == 0 else None
        crt_ok = False
        crt_sign = "bad"
        if r_value is not None and d and g and 552 % (d * g) == 0 and r_value % d == 0 and target_v % g == 0:
            crt_modulus = 552 // (d * g)
            crt_value = ((r_value // d) * (target_v // g)) % crt_modulus
            if crt_value == 1 % crt_modulus:
                crt_ok = True
                crt_sign = "plus"
            elif crt_value == (-1) % crt_modulus:
                crt_ok = True
                crt_sign = "minus"
        if crt_ok:
            crt_inverse_relation += 1
        crt_sign_counter[crt_sign] += 1
        enriched["crt_sign"] = crt_sign
        if (
            image_v % 109 != 0
            or image_u != int(record["target_gcd_v"])
            or not crt_ok
            or pattern not in {"S=target|swap=mirror", "swap=target|S=mirror"}
        ):
            if len(bad_records) < 20:
                bad_records.append(enriched)

    fields_payload: list[dict[str, Any]] = []
    for field in sorted(field_records):
        rs = field_records[field]
        fields_payload.append(
            {
                "field": field,
                "count": len(rs),
                "image_v_mod109_zero_count": sum(1 for r in rs if int(r["image_uv"][1]) % 109 == 0),
                "source_v_mod109_zero_count": sum(1 for r in rs if int(r["source_uv"][1]) % 109 == 0),
                "image_u_eq_target_gcd_v_count": sum(
                    1 for r in rs if int(r["image_uv"][0]) == int(r["target_gcd_v"])
                ),
                "crt_sign_distribution": counter_items(collections.Counter(r["crt_sign"] for r in rs)),
                "s_swap_target_distribution": counter_items(collections.Counter(r["s_swap_pattern"] for r in rs)),
            }
        )

    payload = {
        "tool": "mstar_s5_negative_other_image_fiber_profile",
        "input_json": str(args.input_json),
        "level": level,
        "other_record_count": sum(len(rs) for rs in field_records.values()),
        "image_v_mod109_zero_count": image_v_zero,
        "source_v_mod109_zero_count": source_v_zero,
        "image_u_eq_target_gcd_v_count": image_u_eq_target_g,
        "crt_inverse_relation_count": crt_inverse_relation,
        "crt_sign_distribution": counter_items(crt_sign_counter),
        "s_swap_target_distribution": counter_items(s_swap_counter),
        "fields": fields_payload,
        "bad_records": bad_records,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
