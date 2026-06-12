#!/usr/bin/env python3
"""Count the two CRT-predicted negative basis-fiber images per S5 D target."""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
import time
from typing import Any


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Negative Other CRT Pair Count",
        "",
        "## Summary",
        "",
        f"- input: `{payload['input_json']}`",
        f"- level: `{payload['level']}`",
        f"- D representatives from P1List: `{payload['p1_d_representative_count']}`",
        f"- quotient D targets from transition records: `{payload['quotient_d_target_count']}`",
        f"- predicted image count per target: `{payload['predicted_image_count_distribution']}`",
        f"- actual image count per target: `{payload['actual_image_count_distribution']}`",
        f"- sign set per target: `{payload['sign_set_distribution']}`",
        f"- predicted equals actual: `{payload['predicted_equals_actual_distribution']}`",
        f"- bad targets: `{len(payload['bad_targets'])}`",
        "",
        "## Statement Checked",
        "",
        "For each D-target `(109*d,v)` with `g=gcd(v,N)`, set",
        "`h=552/(d*g)` and `v0=v/g`. The two predicted negative",
        "basis-fiber images are obtained from",
        "",
        "```text",
        "(r/d)*v0 == +1 mod h",
        "(r/d)*v0 == -1 mod h",
        "gcd(r,552) == d",
        "image = normalize(g,109*r).",
        "```",
        "",
        "The check compares this intrinsic CRT prediction with the negative",
        "`other` images observed in the transition profile.",
        "",
    ]
    if payload["bad_targets"]:
        lines.extend(["## Bad Targets", "", "```json"])
        lines.append(json.dumps(payload["bad_targets"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    records = data["all_records"]
    level = int(args.level)
    m109 = level // 109

    import sage.all  # type: ignore  # noqa: F401
    from sage.modular.modsym.p1list import P1List  # type: ignore

    p1 = P1List(level)

    actual_by_target: dict[tuple[int, int], set[tuple[int, int]]] = collections.defaultdict(set)
    for record in records:
        if record["image_relation"] != "other":
            continue
        target = tuple(int(x) for x in record["target_uv"])
        image = tuple(int(x) for x in record["image_uv"])
        actual_by_target[target].add(image)

    predicted_count_counter: collections.Counter[int] = collections.Counter()
    actual_count_counter: collections.Counter[int] = collections.Counter()
    sign_set_counter: collections.Counter[tuple[str, ...]] = collections.Counter()
    equality_counter: collections.Counter[str] = collections.Counter()
    h_counter: collections.Counter[int] = collections.Counter()
    dg_counter: collections.Counter[str] = collections.Counter()
    bad_targets: list[dict[str, Any]] = []

    p1_d_targets: list[tuple[int, int]] = []
    for u_raw, v_raw in p1.list():
        u = int(u_raw)
        v = int(v_raw)
        if v % 2 and u == math.gcd(u, level) and u % 2 and u % 109 == 0:
            p1_d_targets.append((u, v))

    d_targets = sorted(actual_by_target)
    for target in d_targets:
        u, v = target
        d = u // 109
        g = math.gcd(v, level)
        h = m109 // (d * g)
        v0 = v // g
        predicted: dict[tuple[int, int], set[str]] = collections.defaultdict(set)
        for r in range(m109):
            if math.gcd(r, m109) != d:
                continue
            r0 = r // d
            residue = (r0 * v0) % h
            if residue == 1 % h:
                sign = "+"
            elif residue == (-1) % h:
                sign = "-"
            else:
                continue
            image = tuple(int(x) for x in p1.normalize(g, 109 * r))
            predicted[image].add(sign)

        predicted_images = set(predicted)
        actual_images = actual_by_target.get(target, set())
        predicted_count_counter[len(predicted_images)] += 1
        actual_count_counter[len(actual_images)] += 1
        signs = tuple(sorted({sign for sign_set in predicted.values() for sign in sign_set}))
        sign_set_counter[signs] += 1
        h_counter[h] += 1
        dg_counter[f"d={d},g={g}"] += 1
        ok = predicted_images == actual_images and signs == ("+", "-")
        equality_counter[str(ok)] += 1
        if not ok and len(bad_targets) < 30:
            bad_targets.append(
                {
                    "target": list(target),
                    "d": d,
                    "g": g,
                    "h": h,
                    "v0": v0,
                    "predicted": {str(k): sorted(v) for k, v in predicted.items()},
                    "actual": sorted(list(img) for img in actual_images),
                }
            )

    payload = {
        "tool": "mstar_s5_negative_other_crt_pair_count",
        "input_json": str(args.input_json),
        "level": level,
        "p1_d_representative_count": len(p1_d_targets),
        "quotient_d_target_count": len(d_targets),
        "predicted_image_count_distribution": counter_items(predicted_count_counter),
        "actual_image_count_distribution": counter_items(actual_count_counter),
        "sign_set_distribution": counter_items(sign_set_counter),
        "predicted_equals_actual_distribution": counter_items(equality_counter),
        "h_distribution": counter_items(h_counter),
        "dg_distribution": counter_items(dg_counter),
        "bad_targets": bad_targets,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
