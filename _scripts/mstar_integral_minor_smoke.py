#!/usr/bin/env python3
"""Small integral-minor smoke for RC3 source-row witnesses.

This is deliberately a small-level diagnostic. It lifts rows from GF(q) to
symmetric integer representatives and computes the determinant of the exported
square source-row matrix. A nonzero determinant D means the same row set proves
full rank over every field of characteristic not dividing D.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def analyze_manifest(manifest_path: Path, max_n: int) -> dict[str, Any]:
    import sympy as sp

    manifest = load_json(manifest_path)
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    rows_path = manifest_path.parent / str(manifest["rows_file"])
    records = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    result: dict[str, Any] = {
        "case": manifest_path.parent.name,
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "sign": manifest.get("sign"),
        "q": q,
        "ncols": ncols,
        "source_rows": len(records),
        "status": "skipped",
    }

    if len(records) != ncols:
        result["reason"] = "non_square_source_matrix"
        return result
    if ncols > max_n:
        result["reason"] = "above_max_n"
        return result

    rows: list[list[int]] = []
    for record in records:
        row = [0] * ncols
        for col, val in record["row"]:
            row[int(col)] = symmetric_lift(int(val), q)
        rows.append(row)

    matrix = sp.Matrix(rows)
    det = int(matrix.det(method="bareiss"))
    abs_det = abs(det)
    factors = {str(p): int(e) for p, e in sp.factorint(abs_det).items()} if abs_det else {}
    result.update(
        {
            "status": "ok" if det else "zero_det",
            "determinant": str(det),
            "det_abs_bits": abs_det.bit_length(),
            "det_divisible_by_q": bool(det % q == 0) if det else None,
            "factorization": factors,
            "exceptional_primes": sorted(int(p) for p in factors),
        }
    )
    return result


def write_markdown(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# Integral Minor Smoke",
        "",
        "Rows are lifted from `GF(q)` to symmetric integer representatives.",
        "A nonzero determinant `D` kills all field characteristics not dividing `D` for the same square row set.",
        "",
        "| Case | ncols | q | det bits | q divides det | exceptional primes | status |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for item in results:
        primes = ", ".join(str(p) for p in item.get("exceptional_primes", []))
        lines.append(
            f"| {item['case']} | {item['ncols']} | {item['q']} | "
            f"{item.get('det_abs_bits', '')} | {item.get('det_divisible_by_q', '')} | "
            f"{primes} | {item['status']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: this is only a smoke-level S5 diagnostic. It does not prove a global field-prime basket,",
            "but it shows how an integral source-row minor would reduce all-but-finitely-many field characteristics",
            "to the prime divisors of an explicit determinant.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("_results/rc3d_rowhash_source_witness_smoke_2026-05-12"),
    )
    parser.add_argument("--max-n", type=int, default=120)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    manifests = sorted(args.root.glob("*/manifest.json"))
    results = [analyze_manifest(path, args.max_n) for path in manifests]
    payload = {
        "tool": "mstar_integral_minor_smoke",
        "root": str(args.root),
        "max_n": args.max_n,
        "results": results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(results, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
