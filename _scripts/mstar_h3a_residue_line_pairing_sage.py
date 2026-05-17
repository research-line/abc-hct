#!/usr/bin/env sage -python
"""Sage-backed pairing test for H3a residue-line witnesses."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from sage.all import GF, matrix  # type: ignore


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def load_mixed(case_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_json(case_dir / "manifest.json")
    q_lift = int(manifest["q"])
    rows_path = case_dir / str(manifest["rows_file"])
    records: list[dict[str, Any]] = []
    for index, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        raw = json.loads(line)
        row: dict[int, int] = {}
        for col, value in raw["row"]:
            lifted = symmetric_lift(int(value), q_lift)
            if lifted:
                row[int(col)] = lifted
        records.append(
            {
                "index": index,
                "origin": str(raw.get("origin", "")),
                "row_id": str(raw.get("row_id", f"row/{index}")),
                "stage": str(raw.get("stage", "")),
                "stage_row_index": raw.get("stage_row_index"),
                "row": row,
            }
        )
    return manifest, records


def sparse_matrix_from_rows(rows: list[dict[int, int]], ncols: int, prime: int) -> Any:
    field = GF(prime)
    entries: dict[tuple[int, int], Any] = {}
    for i, row in enumerate(rows):
        for col, value in row.items():
            reduced = int(value) % prime
            if reduced:
                entries[(i, int(col))] = field(reduced)
    return matrix(field, len(rows), ncols, entries, sparse=True)


def dot_row_vector(row: dict[int, int], vector: Any, prime: int) -> int:
    total = 0
    for col, value in row.items():
        total += (int(value) % prime) * int(vector[int(col)])
    return total % prime


def analyze(case_dir: Path, prime: int) -> dict[str, Any]:
    started = time.perf_counter()
    manifest, records = load_mixed(case_dir)
    ncols = int(manifest["ncols"])
    source_records = [record for record in records if record["origin"] == "source"]
    repair_records = [record for record in records if record["origin"] == "repair_only"]
    source_rows = [record["row"] for record in source_records]

    build_started = time.perf_counter()
    source_matrix = sparse_matrix_from_rows(source_rows, ncols, prime)
    build_seconds = time.perf_counter() - build_started

    rank_started = time.perf_counter()
    source_rank = int(source_matrix.rank())
    rank_seconds = time.perf_counter() - rank_started

    kernel_started = time.perf_counter()
    kernel_basis = source_matrix.right_kernel().basis()
    kernel_seconds = time.perf_counter() - kernel_started

    pairing_matrix: list[list[int]] = []
    for vector in kernel_basis:
        pairing_matrix.append(
            [dot_row_vector(record["row"], vector, prime) for record in repair_records]
        )

    superset_rank = source_rank
    if repair_records:
        superset_matrix = sparse_matrix_from_rows(
            source_rows + [record["row"] for record in repair_records],
            ncols,
            prime,
        )
        superset_rank = int(superset_matrix.rank())

    defect_dim = int(ncols - source_rank)
    pairing_nonzero = any(any(value % prime for value in row) for row in pairing_matrix)
    saturates = bool(defect_dim == 0 or (superset_rank == ncols and pairing_nonzero))

    return {
        "tool": "mstar_h3a_residue_line_pairing_sage",
        "case": case_dir.name,
        "path": str(case_dir),
        "prime": int(prime),
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
        "source_rank": source_rank,
        "defect_dim": defect_dim,
        "right_kernel_dim": len(kernel_basis),
        "pairing_matrix": pairing_matrix,
        "pairing_nonzero": pairing_nonzero,
        "superset_rank": superset_rank,
        "saturates": saturates,
        "kernel_support_sizes": [
            sum(1 for value in vector if value != 0) for vector in kernel_basis
        ],
        "kernel_support_samples": [
            [idx for idx, value in enumerate(vector) if value != 0][:40]
            for vector in kernel_basis
        ],
        "seconds": time.perf_counter() - started,
        "build_seconds": build_seconds,
        "rank_seconds": rank_seconds,
        "kernel_seconds": kernel_seconds,
    }


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# H3a Residue-Line Pairing")
    lines.append("")
    lines.append(f"Case: `{payload['case']}`.")
    lines.append(f"Prime: `{payload['prime']}`.")
    lines.append(f"Columns: `{payload['ncols']}`.")
    lines.append("")
    lines.append("## Repair Rows")
    lines.append("")
    lines.append("| index | row id | stage |")
    lines.append("|---:|---|---|")
    for row in payload["repair_rows"]:
        lines.append(f"| {row['index']} | `{row['row_id']}` | `{row['stage']}` |")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("| source rank | defect dim | right kernel dim | pairing nonzero | superset rank | saturates | seconds |")
    lines.append("|---:|---:|---:|---|---:|---|---:|")
    lines.append(
        f"| {payload['source_rank']} | {payload['defect_dim']} | "
        f"{payload['right_kernel_dim']} | {payload['pairing_nonzero']} | "
        f"{payload['superset_rank']} | {payload['saturates']} | "
        f"{payload['seconds']:.3f} |"
    )
    lines.append("")
    lines.append("## Pairing Matrix")
    lines.append("")
    if payload["pairing_matrix"]:
        lines.append("```text")
        for row in payload["pairing_matrix"]:
            lines.append(" ".join(str(value) for value in row))
        lines.append("```")
    else:
        lines.append("`[]`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "`saturates=True` means the repair row(s) pair nontrivially with the "
        "right-kernel residue and restore full rank over the tested prime."
    )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--prime", type=int, default=3863)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args.case_dir, args.prime)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps({"saturates": payload["saturates"], "seconds": payload["seconds"]}))


if __name__ == "__main__":
    main()
