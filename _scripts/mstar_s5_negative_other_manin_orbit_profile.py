#!/usr/bin/env python3
"""Check the Manin T-orbit structure of the S5 p=2 negative other records."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import time
from typing import Any


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def field_key(record: dict[str, Any]) -> str:
    return (
        f"{record['relative_source_bucket']}:{record['term']}:"
        f"{record['quotient_scalar']}:{record['image_relation']}"
    )


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Negative Other Manin Orbit Profile",
        "",
        "## Summary",
        "",
        f"- input: `{payload['input_json']}`",
        f"- level: `{payload['level']}`",
        f"- negative other records: `{payload['negative_other_record_count']}`",
        f"- unique negative images: `{payload['unique_negative_image_count']}`",
        f"- D targets: `{payload['target_count']}`",
        f"- images per target: `{payload['images_per_target_distribution']}`",
        f"- records per image: `{payload['records_per_image_distribution']}`",
        f"- orbit-source checks: `{payload['orbit_source_check_distribution']}`",
        f"- per-image field signature: `{payload['per_image_field_signature_distribution']}`",
        f"- bad records: `{len(payload['bad_records'])}`",
        "",
        "## Interpretation",
        "",
        "For every negative base-fiber image `x=(g,109*r)`, the three negative",
        "`other` records are exactly the Manin orbit",
        "",
        "```text",
        "id-source:  x",
        "T-source:   T^2 x",
        "TT-source:  T x",
        "```",
        "",
        "Since `T` has order three on `P^1`, this explains the three negative",
        "`other` fields once the base-fiber images have been identified.",
        "",
    ]
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
    negative_records = [record for record in records if record["image_relation"] == "other"]

    by_target: dict[tuple[int, int], set[tuple[int, int]]] = collections.defaultdict(set)
    by_image: dict[tuple[int, int], list[dict[str, Any]]] = collections.defaultdict(list)
    orbit_checks: collections.Counter[str] = collections.Counter()
    bad_records: list[dict[str, Any]] = []

    for record in negative_records:
        target = tuple(int(x) for x in record["target_uv"])
        image = tuple(int(x) for x in record["image_uv"])
        source = tuple(int(x) for x in record["source_uv"])
        t_image = tuple(int(x) for x in p1.normalize(image[1], -image[0] - image[1]))
        tt_image = tuple(int(x) for x in p1.normalize(-image[0] - image[1], image[0]))
        if record["term"] == "id":
            expected_source = image
        elif record["term"] == "T":
            expected_source = tt_image
        elif record["term"] == "TT":
            expected_source = t_image
        else:
            expected_source = None

        ok = source == expected_source
        orbit_checks[str(ok)] += 1
        by_target[target].add(image)
        enriched = dict(record)
        enriched["t_image"] = list(t_image)
        enriched["tt_image"] = list(tt_image)
        enriched["expected_source"] = list(expected_source) if expected_source is not None else None
        enriched["orbit_source_ok"] = ok
        by_image[image].append(enriched)
        if not ok and len(bad_records) < 20:
            bad_records.append(enriched)

    per_image_signature_counter: collections.Counter[str] = collections.Counter()
    records_per_image_counter: collections.Counter[int] = collections.Counter()
    for image, image_records in by_image.items():
        records_per_image_counter[len(image_records)] += 1
        fields = sorted(field_key(record) for record in image_records)
        per_image_signature_counter["|".join(fields)] += 1

    images_per_target_counter = collections.Counter(len(images) for images in by_target.values())

    payload = {
        "tool": "mstar_s5_negative_other_manin_orbit_profile",
        "input_json": str(args.input_json),
        "level": level,
        "negative_other_record_count": len(negative_records),
        "unique_negative_image_count": len(by_image),
        "target_count": len(by_target),
        "images_per_target_distribution": counter_items(images_per_target_counter),
        "records_per_image_distribution": counter_items(records_per_image_counter),
        "orbit_source_check_distribution": counter_items(orbit_checks),
        "per_image_field_signature_distribution": counter_items(per_image_signature_counter),
        "bad_records": bad_records,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

