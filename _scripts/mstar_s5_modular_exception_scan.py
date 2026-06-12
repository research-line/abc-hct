#!/usr/bin/env python3
"""S5 modular exception-prime scan for source-row witnesses.

Given a square source-row witness over GF(q), lift the rows symmetrically to
integers and recompute the rank modulo selected primes r.  If the lifted matrix
has full rank modulo r, then r does not divide the determinant of this specific
source minor.  If the rank drops, r is an exception candidate for this minor.

This avoids factoring a huge determinant, but it only scans the supplied prime
set and the supplied row set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any, Iterable


DEFAULT_CASES = [
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N109_raw_sign1",
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N218_raw_sign1",
    "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1",
]

DEFAULT_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]


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
        basis = self.basis
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in basis:
                factor = value
                b = basis[pivot]
                for c, v in b.items():
                    new = (row.get(c, 0) - factor * v) % p
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, p)
                normalized = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                basis[pivot] = normalized
                self.rank += 1
                self.max_basis_row_len = max(self.max_basis_row_len, len(normalized))
                return True
        return False


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def load_rows(case_dir: Path) -> tuple[dict[str, Any], list[dict[int, int]]]:
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    rows_path = case_dir / str(manifest["rows_file"])
    rows: list[dict[int, int]] = []
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_value in record["row"]:
            value = symmetric_lift(int(raw_value), q)
            if value:
                row[int(raw_col)] = value
        rows.append(row)
    return manifest, rows


def sage_matrix_rank_mod(rows: list[dict[int, int]], ncols: int, prime: int) -> int:
    from sage.all import GF, matrix  # type: ignore

    field = GF(prime)
    entries: dict[tuple[int, int], Any] = {}
    for i, row in enumerate(rows):
        for col, val in row.items():
            reduced = int(val) % prime
            if reduced:
                entries[(i, int(col))] = field(reduced)
    mat = matrix(field, len(rows), ncols, entries, sparse=True)
    return int(mat.rank())


def rank_mod_prime(
    rows: list[dict[int, int]],
    ncols: int,
    prime: int,
    pivot_strategy: str,
    rank_engine: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    if rank_engine == "sparse-order":
        ranker = SparseIncrementalRank(ncols, prime, pivot_strategy)
        for row in rows:
            ranker.add(row)
            if ranker.rank == ncols:
                break
        rank = ranker.rank
        rows_seen = ranker.rows_seen
        max_basis_row_len = ranker.max_basis_row_len
    elif rank_engine == "sage-matrix":
        rank = sage_matrix_rank_mod(rows, ncols, prime)
        rows_seen = len(rows)
        max_basis_row_len = None
    else:
        raise ValueError(f"unknown rank engine: {rank_engine}")
    seconds = time.perf_counter() - started
    return {
        "prime": prime,
        "rank": rank,
        "ncols": ncols,
        "full_rank": rank == ncols,
        "rows_seen": rows_seen,
        "seconds": seconds,
        "rank_engine": rank_engine,
        "max_basis_row_len": max_basis_row_len,
    }


def append_checkpoint(path: Path | None, record: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(record)
    payload["timestamp_unix"] = time.time()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def analyze_case(
    case_dir: Path,
    primes: list[int],
    pivot_strategy: str,
    max_ncols: int | None,
    rank_engine: str,
    checkpoint_jsonl: Path | None,
) -> dict[str, Any]:
    manifest, rows = load_rows(case_dir)
    ncols = int(manifest["ncols"])
    if max_ncols is not None and ncols > max_ncols:
        return {
            "case": case_dir.name,
            "path": str(case_dir),
            "ncols": ncols,
            "source_rows": len(rows),
            "status": "skipped_max_ncols",
            "prime_results": [],
        }
    prime_results = []
    for prime in primes:
        append_checkpoint(
            checkpoint_jsonl,
            {
                "event": "start_prime",
                "case": case_dir.name,
                "path": str(case_dir),
                "prime": prime,
                "ncols": ncols,
                "source_rows": len(rows),
                "rank_engine": rank_engine,
                "pivot_strategy": pivot_strategy,
            },
        )
        result = rank_mod_prime(rows, ncols, prime, pivot_strategy, rank_engine)
        prime_results.append(result)
        append_checkpoint(
            checkpoint_jsonl,
            {
                "event": "finish_prime",
                "case": case_dir.name,
                "path": str(case_dir),
                **result,
            },
        )
    return {
        "case": case_dir.name,
        "path": str(case_dir),
        "q": int(manifest["q"]),
        "ncols": ncols,
        "source_rows": len(rows),
        "square": len(rows) == ncols,
        "status": "ok",
        "pivot_strategy": pivot_strategy,
        "rank_engine": rank_engine,
        "prime_results": prime_results,
        "full_rank_primes": [item["prime"] for item in prime_results if item["full_rank"]],
        "exception_candidate_primes": [item["prime"] for item in prime_results if not item["full_rank"]],
    }


def write_markdown(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# S5 Modular Exception-Prime Scan",
        "",
        "The scan recomputes the rank of the lifted source-row witness modulo",
        "selected primes.  Full rank modulo `r` excludes `r` as a divisor of",
        "this source minor; rank drop marks `r` as an exception candidate.",
        "",
    ]
    for item in results:
        lines.append(f"## {item['case']}")
        lines.append("")
        if item["status"] != "ok":
            lines.append(f"Status: `{item['status']}` for ncols `{item['ncols']}`.")
            lines.append("")
            continue
        lines.append(
            f"ncols `{item['ncols']}`, source rows `{item['source_rows']}`, "
            f"pivot `{item['pivot_strategy']}`, engine `{item.get('rank_engine', 'sparse-order')}`."
        )
        lines.append("")
        lines.append("| prime | rank | full rank | rows seen | seconds | max basis row len |")
        lines.append("|---:|---:|---|---:|---:|---:|")
        for result in item["prime_results"]:
            lines.append(
                f"| {result['prime']} | {result['rank']} | {result['full_rank']} | "
                f"{result['rows_seen']} | {result['seconds']:.3f} | "
                f"{result.get('max_basis_row_len', '')} |"
            )
        lines.append("")
        lines.append(f"Full-rank primes: `{item['full_rank_primes']}`.")
        lines.append(f"Exception candidates: `{item['exception_candidate_primes']}`.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "This is a certified-recursion diagnostic.  It does not bound all",
            "exception primes, but it shows which tested primes are already",
            "excluded by the same integral source-row minor and which would need",
            "new baskets or a different integral witness.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_primes(raw: str | None) -> list[int]:
    if not raw:
        return DEFAULT_PRIMES
    return [int(part) for part in raw.replace(",", " ").split() if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", type=Path, default=[Path(p) for p in DEFAULT_CASES])
    parser.add_argument("--primes", default=None, help="Prime list, comma or space separated.")
    parser.add_argument("--pivot-strategy", choices=["min", "max"], default="max")
    parser.add_argument("--rank-engine", choices=["sparse-order", "sage-matrix"], default="sparse-order")
    parser.add_argument("--max-ncols", type=int, default=None)
    parser.add_argument("--checkpoint-jsonl", type=Path, help="Append per-prime start/finish records as JSONL.")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    primes = parse_primes(args.primes)
    results = [
        analyze_case(path, primes, args.pivot_strategy, args.max_ncols, args.rank_engine, args.checkpoint_jsonl)
        for path in args.cases
    ]
    payload = {
        "tool": "mstar_s5_modular_exception_scan",
        "description": "modular rank scan for S5 exception-prime recursion",
        "primes": primes,
        "pivot_strategy": args.pivot_strategy,
        "rank_engine": args.rank_engine,
        "results": results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(results, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
