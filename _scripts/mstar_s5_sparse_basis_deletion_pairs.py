#!/usr/bin/env python3
"""Find deletion pairs from sparse incremental bases of an (n+2) x n witness."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


def parse_primes(raw: str) -> list[int]:
    return [int(part) for part in raw.replace(",", " ").split() if part.strip()]


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def load_case(case_dir: Path) -> tuple[dict[str, Any], list[dict[int, int]], list[str]]:
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    q = int(manifest["q"])
    rows_path = case_dir / str(manifest["rows_file"])
    rows: list[dict[int, int]] = []
    row_ids: list[str] = []
    for idx, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        rec = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_val in rec["row"]:
            val = symmetric_lift(int(raw_val), q)
            if val:
                row[int(raw_col)] = val
        rows.append(row)
        row_ids.append(str(rec.get("row_id", f"row/{idx}")))
    return manifest, rows, row_ids


class SparseIncrementalRank:
    def __init__(self, ncols: int, p: int, pivot_strategy: str):
        self.ncols = ncols
        self.p = p
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0

    def add(self, raw_row: dict[int, int]) -> bool:
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in self.basis:
                factor = value
                basis_row = self.basis[pivot]
                for col, basis_value in basis_row.items():
                    new = (row.get(col, 0) - factor * basis_value) % p
                    if new:
                        row[col] = new
                    elif col in row:
                        del row[col]
            else:
                inv = pow(value, -1, p)
                self.basis[pivot] = {
                    col: (val * inv) % p
                    for col, val in row.items()
                    if (val * inv) % p
                }
                self.rank += 1
                return True
        return False


def order_indices(nrows: int, order: str) -> list[int]:
    if order == "original":
        return list(range(nrows))
    if order == "reverse":
        return list(reversed(range(nrows)))
    if order == "extras-first":
        return list(range(nrows - 2, nrows)) + list(range(nrows - 2))
    if order == "extras-last-reverse-source":
        return list(reversed(range(nrows - 2))) + list(range(nrows - 2, nrows))
    raise ValueError(f"unknown order: {order}")


def analyze(rows: list[dict[int, int]], row_ids: list[str], ncols: int, prime: int, pivot: str, order: str) -> dict[str, Any]:
    started = time.perf_counter()
    ranker = SparseIncrementalRank(ncols, prime, pivot)
    selected: set[int] = set()
    seen = 0
    for idx in order_indices(len(rows), order):
        seen += 1
        if ranker.add(rows[idx]):
            selected.add(idx)
            if ranker.rank == ncols:
                break
    deleted = [idx for idx in range(len(rows)) if idx not in selected]
    return {
        "prime": prime,
        "pivot_strategy": pivot,
        "row_order": order,
        "rank": ranker.rank,
        "ncols": ncols,
        "full_rank": ranker.rank == ncols,
        "rows_seen_until_full": seen,
        "deleted_indices": deleted,
        "deleted_row_ids": [row_ids[idx] for idx in deleted],
        "deleted_count": len(deleted),
        "seconds": time.perf_counter() - started,
    }


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 Sparse Basis Deletion Pairs",
        "",
        f"Case: `{payload['case']}`.",
        f"Rows: `{payload['row_count']}`, columns: `{payload['ncols']}`.",
        "",
        "| prime | pivot | order | rank | deleted count | deleted row ids | seconds |",
        "|---:|---|---|---:|---:|---|---:|",
    ]
    for item in payload["results"]:
        lines.append(
            f"| {item['prime']} | {item['pivot_strategy']} | {item['row_order']} | "
            f"{item['rank']} | {item['deleted_count']} | `{item['deleted_row_ids']}` | "
            f"{item['seconds']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Each full-rank run selects `ncols` independent rows.  Since the mixed",
            "witness has `ncols + 2` rows, the complement is a deletion pair for",
            "a square maximal minor over that test prime.  Common deletion pairs",
            "across primes are candidates for a single determinant witness.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def append_checkpoint(path: Path | None, record: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(record)
    payload["timestamp_unix"] = time.time()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--primes", default="2 3 5 7 11 17 31")
    parser.add_argument("--pivot-strategies", default="max min")
    parser.add_argument("--row-orders", default="original reverse extras-first extras-last-reverse-source")
    parser.add_argument("--checkpoint-jsonl", type=Path)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    manifest, rows, row_ids = load_case(args.case_dir)
    ncols = int(manifest["ncols"])
    results = []
    for prime in parse_primes(args.primes):
        for pivot in args.pivot_strategies.split():
            for order in args.row_orders.split():
                append_checkpoint(
                    args.checkpoint_jsonl,
                    {"event": "start", "prime": prime, "pivot_strategy": pivot, "row_order": order},
                )
                result = analyze(rows, row_ids, ncols, prime, pivot, order)
                results.append(result)
                append_checkpoint(args.checkpoint_jsonl, {"event": "finish", **result})
    payload = {
        "tool": "mstar_s5_sparse_basis_deletion_pairs",
        "case": args.case_dir.name,
        "path": str(args.case_dir),
        "ncols": ncols,
        "row_count": len(rows),
        "results": results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
