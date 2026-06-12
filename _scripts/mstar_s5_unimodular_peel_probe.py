#!/usr/bin/env python3
"""S5 near-unimodular peel diagnostic for source-row witnesses.

The probe lifts source rows from GF(q) to symmetric integer representatives and
performs a determinant-safe leaf peel.  If an active row or column has exactly
one active nonzero entry and that entry is ±1, Laplace expansion splits off a
unit determinant factor.  Repeating this gives a rigorous lower bound on the
number of unit Smith/determinant factors visible from the exported sparse row
set, without computing a large determinant.

This is a structural diagnostic, not a proof of the global S5 theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from pathlib import Path
from typing import Any


DEFAULT_CASES = [
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N109_raw_sign1",
    "_results/rc3d_rowhash_source_witness_smoke_2026-05-12/N218_raw_sign1",
    "_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def active_singleton(entries: dict[int, int], active_cols: list[bool]) -> tuple[int, int] | None:
    found: tuple[int, int] | None = None
    for col, value in entries.items():
        if active_cols[col]:
            if found is not None:
                return None
            found = (col, value)
    return found


def active_col_singleton(col_entries: list[dict[int, int]], col: int, active_rows: list[bool]) -> tuple[int, int] | None:
    found: tuple[int, int] | None = None
    for row, value in col_entries[col].items():
        if active_rows[row]:
            if found is not None:
                return None
            found = (row, value)
    return found


def analyze_case(case_dir: Path, max_core_det: int, pivot_abs_limit: int) -> dict[str, Any]:
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])
    rows_path = case_dir / str(manifest["rows_file"])

    row_entries: list[dict[int, int]] = []
    coeff_counter: Counter[int] = Counter()
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_value in record["row"]:
            col = int(raw_col)
            value = symmetric_lift(int(raw_value), q)
            if value:
                row[col] = value
                coeff_counter[value] += 1
        row_entries.append(row)

    nrows = len(row_entries)
    col_entries: list[dict[int, int]] = [dict() for _ in range(ncols)]
    for row_idx, row in enumerate(row_entries):
        for col, value in row.items():
            col_entries[col][row_idx] = value

    active_rows = [True] * nrows
    active_cols = [True] * ncols
    row_deg = [len(row) for row in row_entries]
    col_deg = [len(col_entries[col]) for col in range(ncols)]

    row_queue: deque[int] = deque(i for i, deg in enumerate(row_deg) if deg == 1)
    col_queue: deque[int] = deque(j for j, deg in enumerate(col_deg) if deg == 1)
    peeled = 0
    peeled_by_row = 0
    peeled_by_col = 0
    pivot_abs_counter: Counter[int] = Counter()

    def enqueue_neighbors_after_row(row: int) -> None:
        for col in row_entries[row]:
            if active_cols[col] and col_deg[col] == 1:
                col_queue.append(col)

    def enqueue_neighbors_after_col(col: int) -> None:
        for row in col_entries[col]:
            if active_rows[row] and row_deg[row] == 1:
                row_queue.append(row)

    def peel(row: int, col: int) -> None:
        active_rows[row] = False
        for c in row_entries[row]:
            if active_cols[c]:
                col_deg[c] -= 1
                if col_deg[c] == 1:
                    col_queue.append(c)
        active_cols[col] = False
        for r in col_entries[col]:
            if active_rows[r]:
                row_deg[r] -= 1
                if row_deg[r] == 1:
                    row_queue.append(r)
        row_deg[row] = 0
        col_deg[col] = 0
        enqueue_neighbors_after_row(row)
        enqueue_neighbors_after_col(col)

    while row_queue or col_queue:
        progressed = False
        while row_queue:
            row = row_queue.popleft()
            if not active_rows[row] or row_deg[row] != 1:
                continue
            singleton = active_singleton(row_entries[row], active_cols)
            if singleton is None:
                continue
            col, value = singleton
            if abs(value) > pivot_abs_limit or not active_cols[col]:
                continue
            peel(row, col)
            peeled += 1
            peeled_by_row += 1
            pivot_abs_counter[abs(value)] += 1
            progressed = True
            break
        if progressed:
            continue
        while col_queue:
            col = col_queue.popleft()
            if not active_cols[col] or col_deg[col] != 1:
                continue
            singleton = active_col_singleton(col_entries, col, active_rows)
            if singleton is None:
                continue
            row, value = singleton
            if abs(value) > pivot_abs_limit or not active_rows[row]:
                continue
            peel(row, col)
            peeled += 1
            peeled_by_col += 1
            pivot_abs_counter[abs(value)] += 1
            progressed = True
            break
        if not progressed:
            break

    core_rows = [idx for idx, active in enumerate(active_rows) if active]
    core_cols = [idx for idx, active in enumerate(active_cols) if active]
    core_nnz = 0
    core_l1 = 0
    core_max_abs = 0
    core_row_degrees: Counter[int] = Counter()
    core_col_degrees: Counter[int] = Counter()
    for row in core_rows:
        deg = 0
        for col, value in row_entries[row].items():
            if active_cols[col]:
                deg += 1
                core_nnz += 1
                core_l1 += abs(value)
                core_max_abs = max(core_max_abs, abs(value))
        core_row_degrees[deg] += 1
    for col in core_cols:
        deg = 0
        for row in col_entries[col]:
            if active_rows[row]:
                deg += 1
        core_col_degrees[deg] += 1

    core_det: dict[str, Any] | None = None
    if len(core_rows) == len(core_cols) and 0 < len(core_rows) <= max_core_det:
        import sympy as sp

        col_index = {col: idx for idx, col in enumerate(core_cols)}
        dense = []
        for row in core_rows:
            dense_row = [0] * len(core_cols)
            for col, value in row_entries[row].items():
                if col in col_index:
                    dense_row[col_index[col]] = value
            dense.append(dense_row)
        det = int(sp.Matrix(dense).det(method="bareiss"))
        abs_det = abs(det)
        core_det = {
            "determinant": str(det),
            "det_abs_bits": abs_det.bit_length(),
            "det_divisible_by_q": bool(det % q == 0) if det else None,
            "factorization": {str(p): int(e) for p, e in sp.factorint(abs_det).items()} if abs_det else {},
        }

    unit_edges = coeff_counter[1] + coeff_counter[-1]
    total_nnz = sum(coeff_counter.values())
    return {
        "case": case_dir.name,
        "path": str(case_dir),
        "q": q,
        "nrows": nrows,
        "ncols": ncols,
        "square": nrows == ncols,
        "total_nnz": total_nnz,
        "unit_edge_fraction": unit_edges / total_nnz if total_nnz else 0.0,
        "coefficient_counts": dict(sorted(coeff_counter.items())),
        "pivot_abs_limit": pivot_abs_limit,
        "pivot_abs_counts": dict(sorted(pivot_abs_counter.items())),
        "peeled_unit_pivots": peeled,
        "peeled_by_row": peeled_by_row,
        "peeled_by_col": peeled_by_col,
        "core_rows": len(core_rows),
        "core_cols": len(core_cols),
        "core_nnz": core_nnz,
        "core_avg_row_degree": core_nnz / len(core_rows) if core_rows else 0.0,
        "core_avg_col_degree": core_nnz / len(core_cols) if core_cols else 0.0,
        "core_l1": core_l1,
        "core_max_abs_entry": core_max_abs,
        "core_row_degree_histogram": dict(sorted(core_row_degrees.items())),
        "core_col_degree_histogram": dict(sorted(core_col_degrees.items())),
        "core_det_if_small": core_det,
        "interpretation": (
            "fully_peeled"
            if not core_rows and not core_cols
            else "large_core" if len(core_rows) > max_core_det else "small_core"
        ),
    }


def write_markdown(results: list[dict[str, Any]], out_md: Path) -> None:
    lines = [
        "# S5 Near-Unimodular Peel Probe",
        "",
        "This diagnostic performs a determinant-safe leaf peel on symmetric",
        "integer lifts of source-row witnesses.  A peeled pivot is an active row",
        "or column with exactly one active nonzero entry whose absolute value",
        "is at most the configured pivot bound, so it splits off an explicit",
        "small determinant factor by Laplace expansion.  With pivot bound `1`,",
        "this is a unit-factor probe.",
        "",
        "| Case | n | nnz | unit edge % | pivot bound | peeled pivots | pivot abs counts | core rows | core cols | core nnz | core avg row deg | interpretation |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| {item['case']} | {item['ncols']} | {item['total_nnz']} | "
            f"{100.0 * item['unit_edge_fraction']:.2f} | {item['pivot_abs_limit']} | "
            f"{item['peeled_unit_pivots']} | `{item['pivot_abs_counts']}` | "
            f"{item['core_rows']} | {item['core_cols']} | {item['core_nnz']} | "
            f"{item['core_avg_row_degree']:.3f} | {item['interpretation']} |"
        )
    lines.extend(["", "## Interpretation", ""])
    for item in results:
        lines.append(f"### {item['case']}")
        lines.append("")
        if item["interpretation"] == "fully_peeled":
            lines.append(
                "The exported source-row matrix peels completely into bounded "
                "leaf factors.  The determinant budget is the product of the "
                "recorded pivot factors."
            )
        elif item["interpretation"] == "small_core":
            lines.append(
                "The unit peel leaves a small core.  The determinant/SNF budget is "
                "reduced to this core rather than the full matrix."
            )
        else:
            lines.append(
                "The unit peel leaves a large core.  The current source-row witness "
                "does not visibly support a near-unimodular minor by this simple "
                "leaf-peeling certificate."
            )
        core_det = item.get("core_det_if_small")
        if core_det:
            lines.append("")
            lines.append(
                f"Small-core determinant bits: `{core_det['det_abs_bits']}`, "
                f"divisible by q: `{core_det['det_divisible_by_q']}`."
            )
            lines.append(f"Factorization: `{core_det['factorization']}`.")
        lines.append("")
    lines.extend(
        [
            "## Consequence",
            "",
            "A complete or small-core peel would be strong evidence for a",
            "near-unimodular or locally budgeted S5 route.  A large core means",
            "the current mod-q rank witness is good as a rank certificate but",
            "not optimized for a small integral-index certificate.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", type=Path, default=[Path(p) for p in DEFAULT_CASES])
    parser.add_argument("--max-core-det", type=int, default=160)
    parser.add_argument("--pivot-abs-limit", type=int, default=1)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    results = [analyze_case(path, args.max_core_det, args.pivot_abs_limit) for path in args.cases]
    payload = {
        "tool": "mstar_s5_unimodular_peel_probe",
        "description": "determinant-safe unit leaf peel for S5 near-unimodular route",
        "max_core_det": args.max_core_det,
        "pivot_abs_limit": args.pivot_abs_limit,
        "results": results,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(results, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
