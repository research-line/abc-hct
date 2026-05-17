#!/usr/bin/env python3
"""Verify RC3c/source and split-last witnesses by recomputing sparse rank."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Iterable


class SparseIncrementalRank:
    def __init__(self, ncols: int, p: int, pivot_strategy: str = "max"):
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.rows_seen = 0
        self.max_basis_row_len = 0

    def add(self, raw_row: dict[int, int]) -> bool:
        p = self.p
        self.rows_seen += 1
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in self.basis:
                factor = value
                basis_row = self.basis[pivot]
                for c, v in basis_row.items():
                    new = (row.get(c, 0) - factor * v) % p
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, p)
                normalized = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                self.basis[pivot] = normalized
                self.rank += 1
                if len(normalized) > self.max_basis_row_len:
                    self.max_basis_row_len = len(normalized)
                return True
        return False


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_to_dict(record: dict[str, Any]) -> dict[int, int]:
    return {int(c): int(v) for c, v in record["row"]}


def load_rows(case_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_json(case_dir / "manifest.json")
    rows_path = case_dir / str(manifest["rows_file"])
    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return manifest, rows


def iter_rows(case_dir: Path, manifest: dict[str, Any]) -> Iterable[dict[str, Any]]:
    rows_path = case_dir / str(manifest["rows_file"])
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def rank_records(
    records: Iterable[dict[str, Any]],
    ncols: int,
    q: int,
    pivot_strategy: str,
) -> dict[str, Any]:
    ranker = SparseIncrementalRank(ncols=ncols, p=q, pivot_strategy=pivot_strategy)
    t0 = time.time()
    independent = 0
    for record in records:
        if ranker.add(row_to_dict(record)):
            independent += 1
    return {
        "rows_seen": ranker.rows_seen,
        "independent_rows": independent,
        "rank": ranker.rank,
        "max_basis_row_len": ranker.max_basis_row_len,
        "seconds": time.time() - t0,
    }


def analyze(case_dir: Path, pivot_strategy: str) -> dict[str, Any]:
    manifest, rows = load_rows(case_dir)
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    full = rank_records(rows, ncols, q, pivot_strategy)

    source_rows = [row for row in rows if row.get("origin") == "source"]
    repair_rows = [row for row in rows if row.get("origin") == "repair_only"]
    split: dict[str, Any] | None = None
    if source_rows or repair_rows:
        source = rank_records(source_rows, ncols, q, pivot_strategy)
        split = {
            "source": source,
            "repair_only_count": len(repair_rows),
            "source_rank_is_ncols_minus_one": source["rank"] == ncols - 1,
            "full_rank_is_ncols": full["rank"] == ncols,
            "single_repair_row": len(repair_rows) == 1,
        }
        split["certified"] = (
            split["source_rank_is_ncols_minus_one"]
            and split["full_rank_is_ncols"]
            and split["single_repair_row"]
        )

    payload = {
        "tool": "mstar_h3a_rc3c_witness_verify_rank",
        "case_dir": str(case_dir),
        "case": case_dir.name,
        "level": int(manifest.get("level", 0)),
        "mode": str(manifest.get("mode", "")),
        "q": q,
        "ncols": ncols,
        "witness_type": manifest.get("witness_type"),
        "rows_file": manifest.get("rows_file"),
        "row_count": len(rows),
        "pivot_strategy": pivot_strategy,
        "full": full,
        "full_rank_is_ncols": full["rank"] == ncols,
        "source_row_count_matches_manifest": len(rows) == int(
            manifest.get("mixed_row_count", manifest.get("source_row_count", len(rows)))
        ),
        "split": split,
    }
    payload["certified"] = bool(payload["full_rank_is_ncols"]) if split is None else bool(split["certified"])
    return payload


def analyze_streaming(case_dir: Path, pivot_strategy: str, progress_every: int = 0) -> dict[str, Any]:
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    ranker = SparseIncrementalRank(ncols=ncols, p=q, pivot_strategy=pivot_strategy)
    t0 = time.time()
    row_count = 0
    source_rows = 0
    repair_rows = 0
    source_rank: int | None = None
    seen_repair = False
    independent = 0

    for record in iter_rows(case_dir, manifest):
        row_count += 1
        origin = record.get("origin")
        if origin == "repair_only":
            if source_rank is None:
                source_rank = ranker.rank
            seen_repair = True
            repair_rows += 1
        else:
            if seen_repair and origin == "source":
                raise RuntimeError("streaming split verifier requires all source rows before repair rows")
            source_rows += 1 if origin == "source" else 0
        if ranker.add(row_to_dict(record)):
            independent += 1
        if progress_every and row_count % progress_every == 0:
            print(
                json.dumps(
                    {
                        "rows_seen": row_count,
                        "rank": ranker.rank,
                        "seconds": round(time.time() - t0, 3),
                    }
                ),
                flush=True,
            )

    if source_rank is None:
        source_rank = ranker.rank if repair_rows else None

    full = {
        "rows_seen": ranker.rows_seen,
        "independent_rows": independent,
        "rank": ranker.rank,
        "max_basis_row_len": ranker.max_basis_row_len,
        "seconds": time.time() - t0,
    }
    split = None
    if repair_rows:
        split = {
            "source": {
                "rows_seen": source_rows,
                "independent_rows": source_rank,
                "rank": source_rank,
                "max_basis_row_len": None,
                "seconds": None,
            },
            "repair_only_count": repair_rows,
            "source_rank_is_ncols_minus_one": source_rank == ncols - 1,
            "full_rank_is_ncols": full["rank"] == ncols,
            "single_repair_row": repair_rows == 1,
        }
        split["certified"] = (
            split["source_rank_is_ncols_minus_one"]
            and split["full_rank_is_ncols"]
            and split["single_repair_row"]
        )

    payload = {
        "tool": "mstar_h3a_rc3c_witness_verify_rank",
        "case_dir": str(case_dir),
        "case": case_dir.name,
        "level": int(manifest.get("level", 0)),
        "mode": str(manifest.get("mode", "")),
        "q": q,
        "ncols": ncols,
        "witness_type": manifest.get("witness_type"),
        "rows_file": manifest.get("rows_file"),
        "row_count": row_count,
        "pivot_strategy": pivot_strategy,
        "full": full,
        "full_rank_is_ncols": full["rank"] == ncols,
        "source_row_count_matches_manifest": row_count == int(
            manifest.get("mixed_row_count", manifest.get("source_row_count", row_count))
        ),
        "split": split,
    }
    payload["certified"] = bool(payload["full_rank_is_ncols"]) if split is None else bool(split["certified"])
    return payload


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# H3a RC3c Witness Rank Verification",
        "",
        f"Case: `{payload['case']}`.",
        f"Level: `{payload['level']}`, mode: `{payload['mode']}`, q: `{payload['q']}`.",
        f"Columns: `{payload['ncols']}`.",
        f"Witness type: `{payload['witness_type']}`.",
        "",
        "## Full Rank",
        "",
        f"Rows: `{payload['row_count']}`.",
        f"Rank: `{payload['full']['rank']}`.",
        f"Full rank: `{payload['full_rank_is_ncols']}`.",
        f"Max basis row length: `{payload['full']['max_basis_row_len']}`.",
        f"Seconds: `{payload['full']['seconds']:.3f}`.",
    ]
    if payload["split"] is not None:
        split = payload["split"]
        source = split["source"]
        lines.extend([
            "",
            "## Split",
            "",
            f"Source rows: `{source['rows_seen']}`.",
            f"Source rank: `{source['rank']}`.",
            f"Repair-only rows: `{split['repair_only_count']}`.",
            f"Source rank is ncols-1: `{split['source_rank_is_ncols_minus_one']}`.",
            f"Split certified: `{split['certified']}`.",
        ])
    lines.extend([
        "",
        f"Certified: `{payload['certified']}`.",
        "",
    ])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--pivot-strategy", choices=["min", "max"], default="max")
    parser.add_argument("--legacy-two-pass", action="store_true")
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.legacy_two_pass:
        payload = analyze(args.case_dir, args.pivot_strategy)
    else:
        payload = analyze_streaming(args.case_dir, args.pivot_strategy, args.progress_every)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps({"certified": payload["certified"], "rank": payload["full"]["rank"]}))


if __name__ == "__main__":
    main()
