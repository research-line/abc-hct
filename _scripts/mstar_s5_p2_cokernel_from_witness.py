#!/usr/bin/env python3
"""Compute the GF(2) cokernel vector from the exported p=2 repair witness.

The p=2 repair witness contains 31680 independent rows, with exactly one T7 row
at the end.  Removing that final T7 row leaves 31679 independent rows in a
31680-column space.  Because the full T5-before-T7 matrix has rank 31679, this
independent subset has the same row span.  Its right kernel is the visible
one-dimensional quotient direction before T7.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


class BitsetBasisGF2:
    def __init__(self, ncols: int, pivot_strategy: str = "max"):
        self.ncols = int(ncols)
        self.pivot_strategy = pivot_strategy
        if pivot_strategy != "max":
            raise ValueError("bitset backend currently expects max pivot strategy")
        self.basis: dict[int, int] = {}

    def add(self, row: int) -> bool:
        while row:
            pivot = row.bit_length() - 1
            if pivot in self.basis:
                row ^= self.basis[pivot]
                continue
            self.basis[pivot] = row
            return True
        return False

    @property
    def rank(self) -> int:
        return len(self.basis)

    def kernel_vector_rank_defect_one(self) -> set[int]:
        pivots = set(self.basis)
        free = [c for c in range(self.ncols) if c not in pivots]
        if len(free) != 1:
            raise ValueError(f"expected exactly one free column, got {len(free)}")
        x = 1 << free[0]
        # With max-pivot rows, each basis row only contains columns below or
        # equal to its pivot after elimination.  Ascending order back-solves.
        for pivot in sorted(pivots):
            row = self.basis[pivot]
            parity = ((row & ~(1 << pivot) & x).bit_count()) % 2
            if parity:
                x |= 1 << pivot
            else:
                x &= ~(1 << pivot)
        return {i for i in range(self.ncols) if (x >> i) & 1}


def row_to_mod2_support(record: dict[str, Any], q: int) -> set[int]:
    support: set[int] = set()
    for col, value in record["row"]:
        if symmetric_lift(int(value), q) % 2:
            support.add(int(col))
    return support


def row_to_mod2_bitset(record: dict[str, Any], q: int) -> int:
    row = 0
    for col, value in record["row"]:
        if symmetric_lift(int(value), q) % 2:
            row |= 1 << int(col)
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness-dir", type=Path, required=True)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--sample-limit", type=int, default=300)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.witness_dir / "manifest.json").read_text(encoding="utf-8"))
    ncols = int(manifest["ncols"])
    rows_path = args.witness_dir / str(manifest["rows_file"])
    basis = BitsetBasisGF2(ncols, pivot_strategy=str(manifest.get("pivot_strategy", "max")))
    rows_before_t7 = 0
    t7_record = None
    stage_counts: dict[str, int] = {}

    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        stage = str(record["stage"])
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        if stage.startswith("T_7_"):
            t7_record = record
            continue
        support_bits = row_to_mod2_bitset(record, int(args.q))
        if not basis.add(support_bits):
            raise RuntimeError(f"witness row unexpectedly dependent before T7: {record['row_id']}")
        rows_before_t7 += 1

    kernel_support = sorted(basis.kernel_vector_rank_defect_one())
    t7_support = sorted(row_to_mod2_support(t7_record, int(args.q))) if t7_record is not None else []
    pairing = len(set(kernel_support) & set(t7_support)) % 2
    free_cols = [c for c in range(ncols) if c not in basis.basis]

    payload = {
        "tool": "mstar_s5_p2_cokernel_from_witness",
        "witness_dir": str(args.witness_dir),
        "ncols": ncols,
        "rows_before_t7": rows_before_t7,
        "rank_before_t7": basis.rank,
        "free_columns": free_cols,
        "kernel_support_size": len(kernel_support),
        "kernel_support": kernel_support,
        "kernel_support_sample": kernel_support[: int(args.sample_limit)],
        "t7_row_id": None if t7_record is None else t7_record["row_id"],
        "t7_row_line_sha256": None if t7_record is None else t7_record["row_line_sha256"],
        "t7_support_mod2": t7_support,
        "t7_pairing_mod2": pairing,
        "stage_counts": dict(sorted(stage_counts.items())),
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# S5 p=2 Cokernel From Witness",
        "",
        f"Witness: `{args.witness_dir}`",
        "",
        "## Summary",
        "",
        f"- ncols: `{ncols}`",
        f"- rows before T7: `{rows_before_t7}`",
        f"- rank before T7: `{basis.rank}`",
        f"- free columns: `{free_cols}`",
        f"- kernel support size: `{len(kernel_support)}`",
        f"- T7 row: `{payload['t7_row_id']}`",
        f"- T7 mod-2 support: `{t7_support}`",
        f"- T7 pairing with kernel mod 2: `{pairing}`",
        "",
        "## Stage Counts",
        "",
        "| stage | rows |",
        "|---|---:|",
    ]
    for stage, count in payload["stage_counts"].items():
        lines.append(f"| `{stage}` | {count} |")
    lines.extend(
        [
            "",
            "## Kernel Support Sample",
            "",
            "```text",
            " ".join(str(c) for c in payload["kernel_support_sample"]),
            "```",
            "",
        ]
    )
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
