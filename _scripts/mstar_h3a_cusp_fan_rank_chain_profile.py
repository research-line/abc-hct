#!/usr/bin/env python3
"""Profile the H3a cusp-fan rank chain from an RC3c source witness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def build_profile(witness_dir: Path) -> dict[str, Any]:
    manifest = json.loads((witness_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = load_rows(witness_dir / "source_rows.jsonl")

    hecke_rows = []
    manin_rows = 0
    for pos, row in enumerate(rows):
        meta = row.get("row_metadata") or {}
        if meta.get("source_kind") == "manin_T":
            manin_rows += 1
        if meta.get("source_kind") == "hecke":
            rec = {
                "source_position": pos,
                "row_id": row.get("row_id"),
                "stage": row.get("stage"),
                "hecke_prime": meta.get("hecke_prime"),
                "hecke_ap": meta.get("hecke_ap"),
                "hecke_family": meta.get("hecke_family"),
                "manin_symbol_index": meta.get("manin_symbol_index"),
            }
            hecke_rows.append(rec)

    t5 = [r for r in hecke_rows if r.get("hecke_prime") == 5]
    t7 = [r for r in hecke_rows if r.get("hecke_prime") == 7]
    t5_indices = [int(r["manin_symbol_index"]) for r in t5]
    t5_positions = [int(r["source_position"]) for r in t5]
    quotient_rank = int(manifest.get("quotient_rank", -1))
    expected_t5_count = quotient_rank - 1 if quotient_rank >= 0 else None

    def is_exact_range(values: list[int], start: int, stop_inclusive: int) -> bool:
        return values == list(range(start, stop_inclusive + 1))

    t5_expected_stop = quotient_rank - 2 if quotient_rank >= 1 else None
    t5_is_prefix = (
        t5_expected_stop is not None
        and is_exact_range(t5_indices, 0, t5_expected_stop)
    )
    t5_positions_consecutive = (
        bool(t5_positions)
        and t5_positions == list(range(t5_positions[0], t5_positions[0] + len(t5_positions)))
    )

    first_t7 = t7[0] if t7 else None
    return {
        "witness_dir": str(witness_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": manifest.get("q"),
        "ncols": manifest.get("ncols"),
        "quotient_rank_d": quotient_rank,
        "source_row_count": manifest.get("source_row_count"),
        "base_rank": manifest.get("base_rank"),
        "manin_source_rows": manin_rows,
        "t5_source_rows": len(t5),
        "expected_t5_source_rows": expected_t5_count,
        "t5_indices_first": t5_indices[:10],
        "t5_indices_last": t5_indices[-10:],
        "t5_indices_min": min(t5_indices) if t5_indices else None,
        "t5_indices_max": max(t5_indices) if t5_indices else None,
        "t5_exact_affine_prefix_0_to_d_minus_2": t5_is_prefix,
        "t5_source_positions_consecutive": t5_positions_consecutive,
        "t5_source_position_first": t5_positions[0] if t5_positions else None,
        "t5_source_position_last": t5_positions[-1] if t5_positions else None,
        "t7_source_rows": len(t7),
        "t7_first_row": first_t7,
        "cfr3_diagnostic": {
            "meaning": (
                "RC3c source witnesses record only rows that increased rank "
                "during construction; if the T5 indices are exactly 0..d-2, "
                "the machine certificate supports the Cusp-Fan rank chain."
            ),
            "supports_cfr3_mod_q": (
                t5_is_prefix
                and len(t5) == expected_t5_count
                and t5_positions_consecutive
                and first_t7 is not None
                and first_t7.get("manin_symbol_index") == 1
            ),
        },
    }


def write_markdown(profile: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# H3a Cusp-Fan Rank Chain Profile",
        "",
        f"Witness: `{profile['witness_dir']}`",
        "",
        "```text",
        f"level/mode: {profile['level']}/{profile['mode']}",
        f"q: {profile['q']}",
        f"ncols: {profile['ncols']}",
        f"quotient rank d: {profile['quotient_rank_d']}",
        f"source rows: {profile['source_row_count']}",
        f"manin source rows: {profile['manin_source_rows']}",
        f"T5 source rows: {profile['t5_source_rows']}",
        f"expected T5 rows d-1: {profile['expected_t5_source_rows']}",
        f"T5 exact prefix 0..d-2: {profile['t5_exact_affine_prefix_0_to_d_minus_2']}",
        f"T5 source positions consecutive: {profile['t5_source_positions_consecutive']}",
        f"T5 source position interval: {profile['t5_source_position_first']}..{profile['t5_source_position_last']}",
        f"T5 index interval: {profile['t5_indices_min']}..{profile['t5_indices_max']}",
        f"T7 source rows: {profile['t7_source_rows']}",
        f"T7 first row: {profile['t7_first_row']}",
        f"supports CFR-3 mod q: {profile['cfr3_diagnostic']['supports_cfr3_mod_q']}",
        "```",
        "",
        "Interpretation: RC3c source witnesses contain only rows that increased",
        "rank during construction. Thus an exact T5 index chain `0..d-2` in",
        "consecutive source positions is a machine-level trace of the Cusp-Fan",
        "rank chain over the tested field.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness_dir", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    profile = build_profile(args.witness_dir)
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
