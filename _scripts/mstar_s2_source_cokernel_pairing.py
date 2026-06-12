#!/usr/bin/env python3
"""Export source-cokernel saturation pairings for S2 witnesses.

For a mixed witness B=[A; repair rows], this script computes the right kernel
of the square source block A modulo selected primes and pairs the canonical
repair rows with that dual defect space.
"""

from __future__ import annotations

import argparse
import json
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


def load_mixed_rows(case_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_json(case_dir / "manifest.json")
    rows_path = case_dir / str(manifest["rows_file"])
    q_lift = int(manifest["q"])
    records: list[dict[str, Any]] = []
    for idx, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        raw = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_value in raw["row"]:
            value = symmetric_lift(int(raw_value), q_lift)
            if value:
                row[int(raw_col)] = value
        records.append(
            {
                "index": idx,
                "origin": str(raw.get("origin", "")),
                "row_id": str(raw.get("row_id", f"row/{idx}")),
                "stage": str(raw.get("stage", "")),
                "stage_row_index": raw.get("stage_row_index"),
                "row": row,
            }
        )
    return manifest, records


def sparse_entries(rows: list[dict[int, int]], prime: int) -> dict[tuple[int, int], int]:
    entries: dict[tuple[int, int], int] = {}
    for i, row in enumerate(rows):
        for col, val in row.items():
            reduced = int(val) % prime
            if reduced:
                entries[(i, int(col))] = reduced
    return entries


def dot_sparse_vector(row: dict[int, int], vector: Any, prime: int) -> int:
    total = 0
    for col, val in row.items():
        total += (int(val) % prime) * int(vector[int(col)])
    return total % prime


class BitsetBasisGF2:
    def __init__(self, ncols: int):
        self.ncols = int(ncols)
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

    def kernel_basis_supports(self) -> list[list[int]]:
        pivots = set(self.basis)
        free_cols = [c for c in range(self.ncols) if c not in pivots]
        vectors: list[list[int]] = []
        for free in free_cols:
            x = 1 << free
            for pivot in sorted(pivots):
                row = self.basis[pivot]
                parity = ((row & ~(1 << pivot) & x).bit_count()) % 2
                if parity:
                    x |= 1 << pivot
                else:
                    x &= ~(1 << pivot)
            vectors.append([i for i in range(self.ncols) if (x >> i) & 1])
        return vectors


def row_bitset_mod2(row: dict[int, int]) -> int:
    bits = 0
    for col, val in row.items():
        if int(val) % 2:
            bits |= 1 << int(col)
    return bits


def rank_small_mod2(rows: list[list[int]], ncols: int) -> int:
    basis: dict[int, int] = {}
    for row_values in rows:
        bits = 0
        for col, val in enumerate(row_values[:ncols]):
            if int(val) % 2:
                bits |= 1 << col
        while bits:
            pivot = bits.bit_length() - 1
            if pivot in basis:
                bits ^= basis[pivot]
            else:
                basis[pivot] = bits
                break
    return len(basis)


class SparseBasisModP:
    def __init__(self, ncols: int, p: int):
        self.ncols = int(ncols)
        self.p = int(p)
        self.basis: dict[int, dict[int, int]] = {}

    def add(self, raw_row: dict[int, int]) -> bool:
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = max(row)
            value = row[pivot] % p
            if pivot in self.basis:
                factor = value
                b = self.basis[pivot]
                for c, v in b.items():
                    new = (row.get(c, 0) - factor * v) % p
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
                continue
            inv = pow(value, -1, p)
            self.basis[pivot] = {
                c: (v * inv) % p
                for c, v in row.items()
                if (v * inv) % p
            }
            return True
        return False

    @property
    def rank(self) -> int:
        return len(self.basis)

    def kernel_basis_vectors(self) -> list[dict[int, int]]:
        p = self.p
        pivots = set(self.basis)
        free_cols = [c for c in range(self.ncols) if c not in pivots]
        vectors: list[dict[int, int]] = []
        for free in free_cols:
            x: dict[int, int] = {free: 1}
            for pivot in sorted(pivots):
                row = self.basis[pivot]
                total = 0
                for c, v in row.items():
                    if c == pivot:
                        continue
                    total = (total + v * x.get(c, 0)) % p
                value = (-total) % p
                if value:
                    x[pivot] = value
                elif pivot in x:
                    del x[pivot]
            vectors.append(x)
        return vectors


def dot_sparse_dict(row: dict[int, int], vector: dict[int, int], prime: int) -> int:
    total = 0
    for col, val in row.items():
        total += (int(val) % prime) * vector.get(int(col), 0)
    return total % prime


def rank_small_modp(rows: list[list[int]], ncols: int, p: int) -> int:
    basis = SparseBasisModP(ncols, p)
    for row_values in rows:
        basis.add({i: int(v) for i, v in enumerate(row_values) if int(v) % p})
    return basis.rank


def compute_prime_gf2(
    source_rows: list[dict[int, int]],
    repair_records: list[dict[str, Any]],
    ncols: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    basis = BitsetBasisGF2(ncols)
    for row in source_rows:
        basis.add(row_bitset_mod2(row))
    kernel_supports = basis.kernel_basis_supports()
    defect_dim = len(kernel_supports)
    repair_supports = [
        {col for col, val in record["row"].items() if int(val) % 2}
        for record in repair_records
    ]
    pairing_rows: list[list[int]] = []
    for support in kernel_supports:
        support_set = set(support)
        pairing_rows.append(
            [len(support_set & repair_support) % 2 for repair_support in repair_supports]
        )
    pairing_rank = rank_small_mod2(pairing_rows, len(repair_records)) if pairing_rows else 0

    superset_basis = BitsetBasisGF2(ncols)
    for row in source_rows:
        superset_basis.add(row_bitset_mod2(row))
    for record in repair_records:
        superset_basis.add(row_bitset_mod2(record["row"]))

    return {
        "prime": 2,
        "source_rank": basis.rank,
        "source_defect_dim": int(ncols - basis.rank),
        "right_kernel_dim": defect_dim,
        "repair_row_count": len(repair_records),
        "pairing_rank": pairing_rank,
        "superset_rank": superset_basis.rank,
        "saturates": bool(pairing_rank == defect_dim and superset_basis.rank == ncols),
        "pairing_matrix": pairing_rows,
        "kernel_support_sizes": [len(support) for support in kernel_supports],
        "kernel_support_samples": [support[:40] for support in kernel_supports],
        "seconds": time.perf_counter() - started,
        "engine": "gf2-bitset",
    }


def compute_prime(
    source_rows: list[dict[int, int]],
    repair_records: list[dict[str, Any]],
    ncols: int,
    prime: int,
) -> dict[str, Any]:
    if prime == 2:
        return compute_prime_gf2(source_rows, repair_records, ncols)

    started = time.perf_counter()
    basis = SparseBasisModP(ncols, prime)
    for row in source_rows:
        basis.add(row)
    kernel_vectors = basis.kernel_basis_vectors()
    defect_dim = len(kernel_vectors)

    pairing_rows: list[list[int]] = []
    for vec in kernel_vectors:
        pairing_rows.append(
            [dot_sparse_dict(record["row"], vec, prime) for record in repair_records]
        )

    if pairing_rows:
        pairing_rank = rank_small_modp(pairing_rows, len(repair_records), prime)
    else:
        pairing_rank = 0

    superset_basis = SparseBasisModP(ncols, prime)
    for row in source_rows:
        superset_basis.add(row)
    for record in repair_records:
        superset_basis.add(record["row"])

    return {
        "prime": prime,
        "source_rank": basis.rank,
        "source_defect_dim": int(ncols - basis.rank),
        "right_kernel_dim": defect_dim,
        "repair_row_count": len(repair_records),
        "pairing_rank": pairing_rank,
        "superset_rank": superset_basis.rank,
        "saturates": bool(pairing_rank == defect_dim and superset_basis.rank == ncols),
        "pairing_matrix": pairing_rows,
        "kernel_support_sizes": [len(vec) for vec in kernel_vectors],
        "kernel_support_samples": [sorted(vec)[:40] for vec in kernel_vectors],
        "seconds": time.perf_counter() - started,
        "engine": "sparse-modp",
    }


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S2 Source-Cokernel Pairing",
        "",
        f"Case: `{payload['case']}`.",
        f"Columns: `{payload['ncols']}`.",
        "",
        "## Repair Rows",
        "",
        "| index | row id | origin |",
        "|---:|---|---|",
    ]
    for item in payload["repair_rows"]:
        lines.append(f"| {item['index']} | `{item['row_id']}` | `{item['origin']}` |")

    lines.extend(
        [
            "",
            "## Prime Pairings",
            "",
            "| prime | source rank | defect dim | pairing rank | superset rank | saturates | seconds |",
            "|---:|---:|---:|---:|---:|---|---:|",
        ]
    )
    for item in payload["prime_results"]:
        lines.append(
            f"| {item['prime']} | {item['source_rank']} | {item['source_defect_dim']} | "
            f"{item['pairing_rank']} | {item['superset_rank']} | {item['saturates']} | "
            f"{item['seconds']:.3f} |"
        )

    lines.extend(["", "## Pairing Matrices", ""])
    for item in payload["prime_results"]:
        lines.append(f"### q = {item['prime']}")
        lines.append("")
        lines.append("Rows are a basis of `right_kernel(A mod q)`; columns are repair rows.")
        lines.append("")
        matrix_rows = item["pairing_matrix"]
        if not matrix_rows:
            lines.append("`[]`")
        else:
            lines.append("```text")
            for row in matrix_rows:
                lines.append(" ".join(str(x) for x in row))
            lines.append("```")
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "`saturates=True` means the repair rows generate the row-cokernel",
            "of the source block modulo the tested prime. This is the dual",
            "Cokernel form of the S2 determinant/Fitting witness.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--primes", default="2 3 5 31")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    manifest, records = load_mixed_rows(args.case_dir)
    ncols = int(manifest["ncols"])
    source_records = [record for record in records if record["origin"] == "source"]
    repair_records = [record for record in records if record["origin"] == "repair_only"]
    source_rows = [record["row"] for record in source_records]
    prime_results = [
        compute_prime(source_rows, repair_records, ncols, prime)
        for prime in parse_primes(args.primes)
    ]
    payload = {
        "tool": "mstar_s2_source_cokernel_pairing",
        "case": args.case_dir.name,
        "path": str(args.case_dir),
        "ncols": ncols,
        "source_row_count": len(source_records),
        "repair_rows": [
            {
                "index": int(record["index"]),
                "row_id": record["row_id"],
                "origin": record["origin"],
                "stage": record["stage"],
                "stage_row_index": record["stage_row_index"],
            }
            for record in repair_records
        ],
        "prime_results": prime_results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps({p["prime"]: p["saturates"] for p in prime_results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
