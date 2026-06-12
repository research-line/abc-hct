#!/usr/bin/env python3
"""Audit the oriented twelve-term identity for the S5 p=2 D-axis."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import time
from typing import Any


EXPECTED_PER_TARGET = {
    "base-gcd-v-line:TT:1:exact": 1,
    "base-gcd-v-line:TT:1:same-u": 1,
    "base-gcd-v-line:id:-1:other": 2,
    "even-intermediate:T:-1:other": 2,
    "even-intermediate:T:1:exact": 1,
    "even-intermediate:T:1:same-u": 1,
    "target-109d-axis:TT:-1:other": 2,
    "target-109d-axis:id:1:exact": 1,
    "target-109d-axis:id:1:same-u": 1,
}


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def record_key(record: dict[str, Any]) -> str:
    return (
        f"{record['relative_source_bucket']}:{record['term']}:"
        f"{record['quotient_scalar']}:{record['image_relation']}"
    )


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 Oriented Twelve Identity Audit",
        "",
        "## Summary",
        "",
        f"- input: `{payload['input_json']}`",
        f"- level: `{payload['level']}`",
        f"- D targets: `{payload['target_count']}`",
        f"- transition records: `{payload['transition_record_count']}`",
        f"- good targets: `{payload['good_target_count']}`",
        f"- bad targets: `{len(payload['bad_targets'])}`",
        f"- records per target: `{payload['records_per_target_distribution']}`",
        f"- scalar balance per target: `{payload['scalar_balance_distribution']}`",
        "",
        "## Expected Per Target",
        "",
        "| field | count |",
        "|---|---:|",
    ]
    for key, count in EXPECTED_PER_TARGET.items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "Thus each D target has six positive exact/same-u contributions and",
            "six negative other contributions, arranged in the three source buckets",
            "`base-gcd-v-line`, `even-intermediate`, and `target-109d-axis`.",
            "",
        ]
    )
    if payload["bad_targets"]:
        lines.extend(["## Bad Targets", "", "```json"])
        lines.append(json.dumps(payload["bad_targets"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
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

    by_target: dict[tuple[int, int], list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        target = tuple(int(x) for x in record["target_uv"])
        by_target[target].append(record)

    records_per_target: collections.Counter[int] = collections.Counter()
    scalar_balance: collections.Counter[str] = collections.Counter()
    good_targets = 0
    bad_targets: list[dict[str, Any]] = []
    for target, target_records in by_target.items():
        records_per_target[len(target_records)] += 1
        field_counter = collections.Counter(record_key(record) for record in target_records)
        positives = sum(1 for record in target_records if int(record["quotient_scalar"]) == 1)
        negatives = sum(1 for record in target_records if int(record["quotient_scalar"]) == -1)
        scalar_balance[f"+{positives}/-{negatives}"] += 1
        ok = dict(field_counter) == EXPECTED_PER_TARGET
        if ok:
            good_targets += 1
        elif len(bad_targets) < 20:
            bad_targets.append(
                {
                    "target": list(target),
                    "fields": dict(sorted(field_counter.items())),
                    "expected": EXPECTED_PER_TARGET,
                }
            )

    payload = {
        "tool": "mstar_s5_oriented_twelve_identity_audit",
        "input_json": str(args.input_json),
        "level": level,
        "target_count": len(by_target),
        "transition_record_count": len(records),
        "good_target_count": good_targets,
        "records_per_target_distribution": counter_items(records_per_target),
        "scalar_balance_distribution": counter_items(scalar_balance),
        "expected_per_target": EXPECTED_PER_TARGET,
        "bad_targets": bad_targets,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
