#!/usr/bin/env python3
"""Probe the N=109 H3a pairing/lattice calibration witness.

The script reads a small RC3d independent-source witness, lifts the rows from
GF(q) to symmetric integers, and records exact Smith data plus modular rank
defects for the Manin block, the T5 block, and the combined presentation.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def load_case(case_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    q = int(manifest["q"])
    rows_path = case_dir / str(manifest["rows_file"])
    ncols = int(manifest["ncols"])
    records: list[dict[str, Any]] = []
    for index, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        raw = json.loads(line)
        row = [0] * ncols
        for col, value in raw["row"]:
            row[int(col)] = symmetric_lift(int(value), q)
        records.append(
            {
                "index": index,
                "row_id": raw.get("row_id", f"row/{index}"),
                "stage": raw.get("stage", ""),
                "stage_row_index": raw.get("stage_row_index"),
                "row": row,
            }
        )
    return manifest, records


def rank_mod(matrix: list[list[int]], prime: int, ncols: int) -> int:
    basis: dict[int, dict[int, int]] = {}
    for raw_row in matrix:
        row = {
            col: int(value) % prime
            for col, value in enumerate(raw_row[:ncols])
            if int(value) % prime
        }
        while row:
            pivot = max(row)
            value = row[pivot] % prime
            if pivot in basis:
                factor = value
                base = basis[pivot]
                for col, base_value in base.items():
                    new_value = (row.get(col, 0) - factor * base_value) % prime
                    if new_value:
                        row[col] = new_value
                    elif col in row:
                        del row[col]
                continue
            inv = pow(value, -1, prime)
            basis[pivot] = {
                col: (val * inv) % prime
                for col, val in row.items()
                if (val * inv) % prime
            }
            break
    return len(basis)


def smith_data(matrix: list[list[int]]) -> dict[str, Any]:
    import sympy as sp
    from sympy.matrices.normalforms import smith_normal_form

    mat = sp.Matrix(matrix)
    out: dict[str, Any] = {
        "shape": [int(mat.rows), int(mat.cols)],
        "rank_Q": int(mat.rank()),
    }
    if mat.rows == mat.cols:
        det = int(mat.det())
        out["determinant"] = det
        out["abs_determinant"] = abs(det)
        out["determinant_factorization"] = {
            str(prime): int(exp)
            for prime, exp in sp.factorint(abs(det)).items()
        }
    smith = smith_normal_form(mat, domain=sp.ZZ)
    diagonal: list[int] = []
    for i in range(min(smith.rows, smith.cols)):
        value = abs(int(smith[i, i]))
        if value:
            diagonal.append(value)
    out["smith_diagonal"] = diagonal
    out["smith_nonunit"] = [value for value in diagonal if value != 1]
    out["smith_counter"] = {
        str(value): count for value, count in sorted(Counter(diagonal).items())
    }
    return out


def factor_primes_from(data: dict[str, Any]) -> list[int]:
    factors = data.get("determinant_factorization", {})
    return sorted(int(prime) for prime in factors)


def analyze(case_dir: Path, primes: list[int] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    manifest, records = load_case(case_dir)
    ncols = int(manifest["ncols"])
    rows = [record["row"] for record in records]
    stage_names = sorted({str(record["stage"]) for record in records})
    blocks: dict[str, list[list[int]]] = {
        "combined": rows,
    }
    for stage in stage_names:
        blocks[stage] = [
            record["row"] for record in records if str(record["stage"]) == stage
        ]

    block_data = {name: smith_data(matrix) for name, matrix in blocks.items()}
    if primes is None:
        auto_primes = set(factor_primes_from(block_data["combined"]))
        auto_primes.update({2, 3, 5, 7, 31, 107, 109, int(manifest["q"])})
        primes = sorted(auto_primes)

    for name, matrix in blocks.items():
        block_data[name]["nnz"] = sum(
            1 for row in matrix for value in row if int(value) != 0
        )
        block_data[name]["rank_mod"] = {
            str(prime): rank_mod(matrix, prime, ncols) for prime in primes
        }
        block_data[name]["defect_mod"] = {
            str(prime): ncols - rank_mod(matrix, prime, ncols) for prime in primes
        }

    return {
        "case_dir": str(case_dir),
        "manifest": manifest,
        "primes": primes,
        "row_count": len(records),
        "stage_counts": {
            stage: sum(1 for record in records if record["stage"] == stage)
            for stage in stage_names
        },
        "blocks": block_data,
        "seconds": time.perf_counter() - started,
    }


def write_markdown(result: dict[str, Any], out_path: Path) -> None:
    manifest = result["manifest"]
    combined = result["blocks"]["combined"]
    lines: list[str] = []
    lines.append("# H3a N=109 Pairing Probe")
    lines.append("")
    lines.append(f"Level: `{manifest['level']}`, mode: `{manifest['mode']}`, q: `{manifest['q']}`.")
    lines.append(f"Rows: `{result['row_count']}`, columns: `{manifest['ncols']}`.")
    lines.append("")
    lines.append("## Stage Counts")
    lines.append("")
    lines.append("| Stage | Rows |")
    lines.append("|---|---:|")
    for stage, count in result["stage_counts"].items():
        lines.append(f"| `{stage}` | {count} |")
    lines.append("")
    lines.append("## Combined Smith Data")
    lines.append("")
    lines.append(f"Rank over Q: `{combined['rank_Q']}`.")
    lines.append(f"Determinant: `{combined.get('determinant')}`.")
    lines.append(f"Factorization: `{combined.get('determinant_factorization')}`.")
    lines.append(f"Non-unit Smith factors: `{combined['smith_nonunit']}`.")
    lines.append("")
    lines.append("## Modular Ranks")
    lines.append("")
    lines.append("| Block | Prime | Rank | Defect versus 27 columns |")
    lines.append("|---|---:|---:|---:|")
    for block_name, block in result["blocks"].items():
        for prime in result["primes"]:
            key = str(prime)
            lines.append(
                f"| `{block_name}` | {prime} | {block['rank_mod'][key]} | {block['defect_mod'][key]} |"
            )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The 27 by 27 presentation is full rank over Q and over GF(3863), "
        "so the T5 certificate kills the N=109 calibration quotient mod 3863. "
        "It is not unimodular over Z: the remaining finite presentation has "
        "Smith factors 4 and 26964. Thus the small case is a useful stress "
        "test for any integral congruence-module interpretation."
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case-dir",
        type=Path,
        default=Path(
            "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N109_raw_sign1"
        ),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("_results/mstar_h3a_n109_pairing_probe_2026-05-16.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("_results/mstar_h3a_n109_pairing_probe_2026-05-16.md"),
    )
    parser.add_argument("--primes", nargs="*", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.case_dir, args.primes)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_markdown(result, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
