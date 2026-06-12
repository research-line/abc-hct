#!/usr/bin/env python3
"""Search common full-rank square minors via left-kernel Pluecker coordinates.

For a rectangular matrix B with n+2 rows and n columns over F_p, full column
rank implies that the left kernel has dimension 2.  A maximal minor obtained by
deleting rows i,j is nonzero over F_p exactly when the two Pluecker coordinate
vectors at i and j are linearly independent in that two-dimensional left
kernel basis.

This script computes those row projective classes for selected primes and
searches for one deletion pair that is good for all tested primes.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any


def parse_primes(raw: str) -> list[int]:
    return [int(part) for part in raw.replace(",", " ").split() if part.strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def load_rows(case_dir: Path) -> tuple[dict[str, Any], list[dict[int, int]], list[str]]:
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    rows_path = case_dir / str(manifest["rows_file"])
    rows: list[dict[int, int]] = []
    row_ids: list[str] = []
    for idx, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        record = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_value in record["row"]:
            value = symmetric_lift(int(raw_value), q)
            if value:
                row[int(raw_col)] = value
        rows.append(row)
        row_ids.append(str(record.get("row_id", f"row/{idx}")))
    return manifest, rows, row_ids


def projective_class(a: int, b: int, p: int) -> tuple[int, int] | None:
    a %= p
    b %= p
    if not a and not b:
        return None
    if a:
        inv = pow(a, -1, p)
        return (1, (b * inv) % p)
    inv = pow(b, -1, p)
    return (0, (b * inv) % p)


def left_kernel_classes(rows: list[dict[int, int]], ncols: int, prime: int) -> dict[str, Any]:
    from sage.all import GF, matrix  # type: ignore

    started = time.perf_counter()
    field = GF(prime)
    entries: dict[tuple[int, int], Any] = {}
    for i, row in enumerate(rows):
        for col, val in row.items():
            reduced = int(val) % prime
            if reduced:
                entries[(i, int(col))] = field(reduced)
    mat = matrix(field, len(rows), ncols, entries, sparse=True)
    rank = int(mat.rank())
    basis = mat.left_kernel().basis()
    if len(basis) != len(rows) - rank:
        raise RuntimeError("left kernel dimension mismatch")
    if len(basis) != 2:
        raise RuntimeError(f"expected left kernel dimension 2, got {len(basis)} for p={prime}")
    b0 = basis[0]
    b1 = basis[1]
    classes: list[tuple[int, int] | None] = []
    class_counts: dict[str, int] = {}
    zero_count = 0
    for i in range(len(rows)):
        cls = projective_class(int(b0[i]), int(b1[i]), prime)
        classes.append(cls)
        if cls is None:
            zero_count += 1
        else:
            key = f"{cls[0]}:{cls[1]}"
            class_counts[key] = class_counts.get(key, 0) + 1
    return {
        "prime": prime,
        "rank": rank,
        "left_kernel_dim": len(basis),
        "classes": classes,
        "zero_rows": zero_count,
        "projective_class_count": len(class_counts),
        "largest_class_size": max(class_counts.values()) if class_counts else 0,
        "seconds": time.perf_counter() - started,
    }


def pair_good(classes_by_prime: dict[int, list[tuple[int, int] | None]], i: int, j: int) -> bool:
    for classes in classes_by_prime.values():
        ci = classes[i]
        cj = classes[j]
        if ci is None or cj is None or ci == cj:
            return False
    return True


def search_pair(
    classes_by_prime: dict[int, list[tuple[int, int] | None]],
    row_count: int,
    max_samples: int,
    seed: int,
) -> tuple[int, int] | None:
    valid = [
        i for i in range(row_count)
        if all(classes[i] is not None for classes in classes_by_prime.values())
    ]
    rng = random.Random(seed)
    if len(valid) < 2:
        return None

    # First try a deterministic scan against random partners.
    for i in valid[: min(len(valid), 1000)]:
        for _ in range(min(max_samples, 1000)):
            j = rng.choice(valid)
            if i != j and pair_good(classes_by_prime, i, j):
                return (i, j)

    # Then pure random pairs.
    for _ in range(max_samples):
        i, j = rng.sample(valid, 2)
        if pair_good(classes_by_prime, i, j):
            return (i, j)
    return None


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 Pluecker Pair Search",
        "",
        f"Case: `{payload['case']}`.",
        f"Rows: `{payload['row_count']}`, columns: `{payload['ncols']}`.",
        "",
        "## Prime Diagnostics",
        "",
        "| prime | rank | left kernel dim | projective classes | zero rows | largest class | seconds |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["prime_diagnostics"]:
        lines.append(
            f"| {item['prime']} | {item['rank']} | {item['left_kernel_dim']} | "
            f"{item['projective_class_count']} | {item['zero_rows']} | "
            f"{item['largest_class_size']} | {item['seconds']:.3f} |"
        )
    lines.extend(["", "## Pair", ""])
    if payload["common_pair"] is None:
        lines.append("No common deletion pair found in the sampled search.")
    else:
        pair = payload["common_pair"]
        lines.extend(
            [
                f"Common deletion indices: `{pair['indices']}`.",
                f"Common deletion row ids: `{pair['row_ids']}`.",
                "",
                "This means the square minor obtained by deleting this pair is",
                "full-rank modulo every tested prime.",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "For an `(n+2) x n` full-column-rank relation matrix, the maximal",
            "minor obtained by deleting two rows is controlled by a Pluecker",
            "coordinate of the two-dimensional left kernel.  A common deletion",
            "pair is therefore a single square determinant witness for all",
            "tested primes, not merely a prime-dependent rectangular rank",
            "certificate.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--primes", default="2 3 5 7 11 17 31")
    parser.add_argument("--max-samples", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=20260514)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    manifest, rows, row_ids = load_rows(args.case_dir)
    ncols = int(manifest["ncols"])
    diagnostics = []
    classes_by_prime: dict[int, list[tuple[int, int] | None]] = {}
    for prime in parse_primes(args.primes):
        diag = left_kernel_classes(rows, ncols, prime)
        classes_by_prime[prime] = diag.pop("classes")
        diagnostics.append(diag)
    pair = search_pair(classes_by_prime, len(rows), args.max_samples, args.seed)
    pair_payload = None
    if pair is not None:
        pair_payload = {
            "indices": [int(pair[0]), int(pair[1])],
            "row_ids": [row_ids[pair[0]], row_ids[pair[1]]],
        }
    payload = {
        "tool": "mstar_s5_plucker_pair_search",
        "case": args.case_dir.name,
        "path": str(args.case_dir),
        "q": int(manifest["q"]),
        "ncols": ncols,
        "row_count": len(rows),
        "primes": parse_primes(args.primes),
        "prime_diagnostics": diagnostics,
        "common_pair": pair_payload,
        "max_samples": args.max_samples,
        "seed": args.seed,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps(pair_payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
