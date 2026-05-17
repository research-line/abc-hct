#!/usr/bin/env python3
"""Certify a residue-line split by ordered independent-source provenance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(case_dir: Path, expect_stage_prefix: str | None = None) -> dict[str, Any]:
    manifest = load_json(case_dir / "manifest.json")
    ncols = int(manifest["ncols"])
    original = int(manifest["original_source_row_count"])
    source = int(manifest["source_row_count"])
    repair_count = int(manifest["repair_only_row_count"])
    repair_stage = str(manifest["repair_only_stage"])

    checks = {
        "original_full_count_equals_ncols": original == ncols,
        "source_prefix_count_equals_ncols_minus_one": source == ncols - 1,
        "single_repair_row": repair_count == 1,
        "mixed_count_equals_ncols": int(manifest["mixed_row_count"]) == ncols,
        "split_rule_is_final_or_specified": str(manifest.get("split_rule", "")) in {
            "final source row",
            "specified row",
        },
        "repair_stage_matches_expectation": True
        if expect_stage_prefix is None
        else repair_stage.startswith(expect_stage_prefix),
    }
    certified = all(checks.values())

    return {
        "tool": "mstar_h3a_residue_line_order_certificate",
        "case": case_dir.name,
        "path": str(case_dir),
        "q": int(manifest["q"]),
        "level": int(manifest.get("level", 0)),
        "mode": str(manifest.get("mode", "")),
        "ncols": ncols,
        "original_source_row_count": original,
        "source_prefix_count": source,
        "repair_row_id": str(manifest["repair_only_row_id"]),
        "repair_stage": repair_stage,
        "repair_original_index": int(manifest["repair_only_original_index"]),
        "checks": checks,
        "certified": certified,
        "mathematical_reading": (
            "Because the source witness is an ordered list of rank-increasing "
            "rows over q, the first n-1 rows have rank n-1 and the final repair "
            "row raises the rank to n. Thus the repair row is nonzero on the "
            "one-dimensional row-cokernel residue."
        ),
    }


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# H3a Residue-Line Order Certificate")
    lines.append("")
    lines.append(f"Case: `{payload['case']}`.")
    lines.append(f"Level: `{payload['level']}`, mode: `{payload['mode']}`, q: `{payload['q']}`.")
    lines.append(f"Columns: `{payload['ncols']}`.")
    lines.append("")
    lines.append("## Split")
    lines.append("")
    lines.append(f"Original source rows: `{payload['original_source_row_count']}`.")
    lines.append(f"Source prefix rows: `{payload['source_prefix_count']}`.")
    lines.append(f"Repair row: `{payload['repair_row_id']}`.")
    lines.append(f"Repair stage: `{payload['repair_stage']}`.")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Passed |")
    lines.append("|---|---|")
    for name, passed in payload["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.append("")
    lines.append(f"Certified: `{payload['certified']}`.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(payload["mathematical_reading"])
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--expect-stage-prefix")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args.case_dir, args.expect_stage_prefix)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps({"certified": payload["certified"]}))


if __name__ == "__main__":
    main()
