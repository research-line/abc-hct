#!/usr/bin/env python3
"""Profile RC3c witness row provenance for T5-prefix normal-form work."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _interval_stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "unique": 0,
            "contiguous": None,
            "starts_at_zero": None,
            "missing_count": None,
            "first_missing": [],
            "last_missing": [],
        }
    unique_values = sorted(set(values))
    unique_set = set(unique_values)
    lo = unique_values[0]
    hi = unique_values[-1]
    missing = [x for x in range(lo, hi + 1) if x not in unique_set]
    return {
        "count": len(values),
        "min": lo,
        "max": hi,
        "unique": len(unique_values),
        "contiguous": len(missing) == 0,
        "starts_at_zero": lo == 0,
        "missing_count": len(missing),
        "first_missing": missing[:20],
        "last_missing": missing[-20:] if missing else [],
    }


def load_profile(witness_dir: Path) -> dict[str, Any]:
    manifest_path = witness_dir / "manifest.json"
    rows_path = witness_dir / "source_rows.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    stage_counts: Counter[str] = Counter()
    source_kind_counts: Counter[str] = Counter()
    hecke_prime_counts: Counter[str] = Counter()
    stage_row_indices: dict[str, list[int]] = defaultdict(list)
    symbol_indices: dict[str, list[int]] = defaultdict(list)
    prime_symbol_indices: dict[str, list[int]] = defaultdict(list)
    last_record: dict[str, Any] | None = None

    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rec = json.loads(line)
            last_record = rec
            stage = rec.get("stage", "?")
            stage_counts[stage] += 1
            if isinstance(rec.get("stage_row_index"), int):
                stage_row_indices[stage].append(rec["stage_row_index"])
            meta = rec.get("row_metadata") or {}
            kind = meta.get("source_kind", "?")
            source_kind_counts[kind] += 1
            symbol_index = meta.get("manin_symbol_index")
            if isinstance(symbol_index, int):
                symbol_indices[stage].append(symbol_index)
            prime = meta.get("hecke_prime")
            if prime is not None:
                key = str(prime)
                hecke_prime_counts[key] += 1
                if isinstance(symbol_index, int):
                    prime_symbol_indices[key].append(symbol_index)

    stages = {}
    for stage, count in stage_counts.items():
        stages[stage] = {
            "rows": count,
            "stage_row_index": _interval_stats(stage_row_indices[stage]),
            "manin_symbol_index": _interval_stats(symbol_indices[stage]),
        }

    by_hecke_prime = {}
    for prime, values in sorted(prime_symbol_indices.items(), key=lambda kv: int(kv[0])):
        by_hecke_prime[prime] = _interval_stats(values)
        by_hecke_prime[prime]["rows"] = hecke_prime_counts[prime]

    rows_before_final = manifest.get("source_row_count")
    final_stage = manifest.get("final_stage")
    if last_record is not None and last_record.get("stage") == final_stage:
        rows_before_final = manifest.get("source_row_count", 0) - 1

    return {
        "witness_dir": str(witness_dir),
        "manifest": manifest,
        "source_kind_counts": dict(source_kind_counts),
        "stages": stages,
        "by_hecke_prime": by_hecke_prime,
        "last_record": last_record,
        "normalform_signals": {
            "rows_before_final_stage": rows_before_final,
            "ncols": manifest.get("ncols"),
            "rows_before_final_is_ncols_minus_one": (
                rows_before_final == manifest.get("ncols", -1) - 1
            ),
            "final_stage": final_stage,
            "final_row_id": None if last_record is None else last_record.get("row_id"),
            "final_row_metadata": None if last_record is None else last_record.get("row_metadata"),
        },
    }


def write_markdown(profile: dict[str, Any], out_md: Path) -> None:
    manifest = profile["manifest"]
    lines = [
        "# H3a RC3c Witness Prefix Profile",
        "",
        f"Witness: `{profile['witness_dir']}`",
        "",
        "## Manifest",
        "",
        "```text",
        f"level/mode: {manifest.get('level')}/{manifest.get('mode')}",
        f"q: {manifest.get('q')}",
        f"rank_engine: {manifest.get('rank_engine')}",
        f"final_stage: {manifest.get('final_stage')}",
        f"ncols: {manifest.get('ncols')}",
        f"source_row_count: {manifest.get('source_row_count')}",
        f"base_rank: {manifest.get('base_rank')}",
        f"quotient_rank: {manifest.get('quotient_rank')}",
        f"full_rank: {manifest.get('full_rank')}",
        "```",
        "",
        "## Normalform-Signale",
        "",
        "```text",
    ]
    signals = profile["normalform_signals"]
    for key, value in signals.items():
        lines.append(f"{key}: {value}")
    lines += ["```", "", "## Hecke-Prime-Profil", ""]
    for prime, stats in profile["by_hecke_prime"].items():
        lines += [
            f"### T{prime}",
            "",
            "```text",
            f"rows: {stats.get('rows')}",
            f"symbol interval: {stats.get('min')}..{stats.get('max')}",
            f"unique: {stats.get('unique')}",
            f"contiguous: {stats.get('contiguous')}",
            f"starts_at_zero: {stats.get('starts_at_zero')}",
            f"missing_count: {stats.get('missing_count')}",
            "```",
            "",
        ]
    lines += ["## Stage-Profil", ""]
    for stage, stats in profile["stages"].items():
        sym = stats["manin_symbol_index"]
        row = stats["stage_row_index"]
        lines += [
            f"### {stage}",
            "",
            "```text",
            f"rows: {stats['rows']}",
            f"stage-row interval: {row.get('min')}..{row.get('max')}",
            f"stage-row contiguous: {row.get('contiguous')}",
            f"symbol interval: {sym.get('min')}..{sym.get('max')}",
            f"symbol contiguous: {sym.get('contiguous')}",
            f"symbol starts_at_zero: {sym.get('starts_at_zero')}",
            f"symbol missing_count: {sym.get('missing_count')}",
            "```",
            "",
        ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness_dir", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    profile = load_profile(args.witness_dir)
    if args.out_json:
        args.out_json.write_text(
            json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.out_md:
        write_markdown(profile, args.out_md)
    if not args.out_json and not args.out_md:
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
