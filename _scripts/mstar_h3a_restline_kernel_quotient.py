#!/usr/bin/env python3
"""Extract the H3a quotient residue functional from a split-last witness.

This is the lightweight input stage for the AL scalar test.  It does not try
to find a nullvector in the full S/I column space.  Instead it:

1. rebuilds the T-Manin quotient from source_kind=manin_T rows,
2. projects the Hecke source rows and the final repair row,
3. computes the one-dimensional right kernel of the projected Hecke matrix,
4. pairs that kernel with the repair row.

The output vector is the quotient functional phi_free used by the later
`Q_B(phi) = phi B_AL^-1 phi^T` test.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

def signed_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return int(value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_rows(case_dir: Path):
    manifest = load_json(case_dir / "manifest.json")
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def row_to_dict(record: dict[str, Any], q: int) -> dict[int, int]:
    return {
        int(c): int(v) % q
        for c, v in record["row"]
        if int(v) % q
    }


class SparseRowBasis:
    def __init__(self, q: int, pivot_strategy: str = "max"):
        self.q = int(q)
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.max_basis_row_len = 0

    def add(self, raw_row: dict[int, int]) -> bool:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % q
            if pivot in self.basis:
                factor = value
                for c, v in self.basis[pivot].items():
                    new = (row.get(c, 0) - factor * v) % q
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, q)
                normalized = {
                    c: (v * inv) % q for c, v in row.items() if (v * inv) % q
                }
                self.basis[pivot] = normalized
                self.rank += 1
                self.max_basis_row_len = max(self.max_basis_row_len, len(normalized))
                return True
        return False

    def reduce(self, raw_row: dict[int, int]) -> dict[int, int]:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            candidates = [c for c in row if c in self.basis]
            if not candidates:
                break
            pivot = min(candidates) if self.pivot_strategy == "min" else max(candidates)
            factor = row[pivot] % q
            for c, v in self.basis[pivot].items():
                new = (row.get(c, 0) - factor * v) % q
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row

    def solve_null_vector(self, ncols: int, free_col: int | None = None) -> dict[int, int]:
        pivots = set(self.basis)
        free_cols = [c for c in range(ncols) if c not in pivots]
        if not free_cols:
            raise ValueError("matrix has full rank; no free column available")
        if free_col is None:
            free_col = free_cols[0]
        if free_col not in free_cols:
            raise ValueError(f"requested free column {free_col} is not free")

        q = self.q
        x: dict[int, int] = {free_col: 1}
        for pivot in sorted(pivots):
            row = self.basis[pivot]
            total = 0
            for col, value in row.items():
                if col == pivot:
                    continue
                total = (total + value * x.get(col, 0)) % q
            value = (-total) % q
            if value:
                x[pivot] = value
        return x


def dot_sparse(row: dict[int, int], vec: dict[int, int], q: int) -> int:
    return sum((int(v) % q) * vec.get(int(c), 0) for c, v in row.items()) % q


def sparse_entries(row: dict[int, int]) -> list[list[int]]:
    return [[int(c), int(row[c])] for c in sorted(row)]


def signed_entries(row: dict[int, int], q: int, limit: int | None = None) -> list[list[int]]:
    cols = sorted(row)
    if limit is not None:
        cols = cols[:limit]
    return [[int(c), signed_lift(row[c], q)] for c in cols]


def write_status(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def record_kind(record: dict[str, Any]) -> str:
    meta = record.get("row_metadata") or {}
    if meta.get("source_kind"):
        return str(meta["source_kind"])
    stage = str(record.get("stage", ""))
    if stage == "manin_T_relations_after_SI":
        return "manin_T"
    return "hecke"


def analyze(
    case_dir: Path,
    pivot_strategy: str,
    progress_every: int,
    kernel_engine: str,
    status_json: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    manifest = load_json(case_dir / "manifest.json")
    q = int(manifest["q"])
    ncols = int(manifest.get("ncols", manifest.get("columns_after_2term")))

    base = SparseRowBasis(q, pivot_strategy=pivot_strategy)
    quotient_basis = SparseRowBasis(q, pivot_strategy=pivot_strategy)
    hecke_projected: list[dict[int, int]] = []
    repair_projected: dict[int, int] | None = None
    quotient_col_map: dict[int, int] | None = None
    manin_rows = 0
    hecke_rows = 0
    rows_seen = 0
    sage_entries: dict[tuple[int, int], Any] = {}
    F = None
    if kernel_engine == "sage":
        from sage.all import GF  # type: ignore

        F = GF(q)
    status: dict[str, Any] = {
        "tool": "mstar_h3a_restline_kernel_quotient",
        "phase": "starting",
        "case_dir": str(case_dir),
        "q": q,
        "ncols_v_si": ncols,
        "kernel_engine": kernel_engine,
        "started_unix": time.time(),
    }
    write_status(status_json, status)

    def ensure_quotient() -> None:
        nonlocal quotient_col_map
        if quotient_col_map is not None:
            return
        free_cols = [c for c in range(ncols) if c not in base.basis]
        quotient_col_map = {c: i for i, c in enumerate(free_cols)}

    for record in iter_rows(case_dir):
        rows_seen += 1
        origin = str(record.get("origin", ""))
        kind = record_kind(record)
        row = row_to_dict(record, q)
        if origin == "repair_only":
            ensure_quotient()
            assert quotient_col_map is not None
            rem = base.reduce(row)
            repair_projected = {
                quotient_col_map[c]: v
                for c, v in rem.items()
                if c in quotient_col_map and int(v) % q
            }
            continue
        if origin != "source":
            continue
        if kind == "manin_T":
            manin_rows += 1
            base.add(row)
        else:
            ensure_quotient()
            assert quotient_col_map is not None
            rem = base.reduce(row)
            projected = {
                quotient_col_map[c]: v
                for c, v in rem.items()
                if c in quotient_col_map and int(v) % q
            }
            if kernel_engine == "sparse-python":
                quotient_basis.add(projected)
            else:
                assert F is not None
                for col, val in projected.items():
                    sage_entries[(hecke_rows, col)] = F(int(val) % q)
            hecke_projected.append(projected)
            hecke_rows += 1

        if progress_every and rows_seen % progress_every == 0:
            elapsed = time.perf_counter() - started
            qcols = len(quotient_col_map) if quotient_col_map is not None else None
            status.update({
                "phase": "collecting_projected_hecke_matrix",
                "rows_seen": rows_seen,
                "manin_t_rank": base.rank,
                "hecke_rows": hecke_rows,
                "quotient_ncols": qcols,
                "quotient_basis_rank": (
                    quotient_basis.rank if kernel_engine == "sparse-python" else None
                ),
                "matrix_entries": (
                    len(sage_entries) if kernel_engine == "sage" else None
                ),
                "seconds": round(elapsed, 3),
            })
            write_status(status_json, status)
            print(json.dumps(status), flush=True)

    ensure_quotient()
    assert quotient_col_map is not None
    if repair_projected is None:
        raise ValueError(f"repair_only row not found in {case_dir}")

    quotient_ncols = len(quotient_col_map)
    status.update({
        "phase": (
            "computing_sparse_python_kernel"
            if kernel_engine == "sparse-python"
            else "building_sage_sparse_matrix"
        ),
        "rows_seen": rows_seen,
        "manin_t_rank": base.rank,
        "hecke_rows": hecke_rows,
        "quotient_ncols": quotient_ncols,
        "quotient_basis_rank": (
            quotient_basis.rank if kernel_engine == "sparse-python" else None
        ),
        "matrix_entries": len(sage_entries) if kernel_engine == "sage" else None,
        "seconds": round(time.perf_counter() - started, 3),
    })
    write_status(status_json, status)

    kernel_started = time.perf_counter()
    matrix_seconds = None
    if kernel_engine == "sparse-python":
        status.update({
            "phase": "solving_sparse_python_kernel",
            "seconds": round(time.perf_counter() - started, 3),
        })
        write_status(status_json, status)
        quotient_rank = quotient_basis.rank
        kernel_dim = quotient_ncols - quotient_rank
        kernel_vector: dict[int, int] = (
            quotient_basis.solve_null_vector(quotient_ncols) if kernel_dim else {}
        )
    else:
        from sage.all import matrix  # type: ignore

        assert F is not None
        matrix_started = time.perf_counter()
        A = matrix(F, hecke_rows, quotient_ncols, sage_entries, sparse=True)
        matrix_seconds = time.perf_counter() - matrix_started
        status.update({
            "phase": "computing_sage_right_kernel",
            "matrix_seconds": matrix_seconds,
            "seconds": round(time.perf_counter() - started, 3),
        })
        write_status(status_json, status)
        K = A.right_kernel()
        kernel_dim = int(K.dimension())
        quotient_rank = quotient_ncols - kernel_dim
        kernel_vector = {}
        if kernel_dim:
            v = K.basis()[0]
            kernel_vector = {
                int(i): int(v[i]) % q
                for i in range(quotient_ncols)
                if int(v[i]) % q
            }
    kernel_seconds = time.perf_counter() - kernel_started

    repair_pairing = dot_sparse(repair_projected, kernel_vector, q)
    source_pairing_nonzero = 0
    source_pairing_examples: list[dict[str, Any]] = []
    for i, row in enumerate(hecke_projected):
        value = dot_sparse(row, kernel_vector, q)
        if value:
            source_pairing_nonzero += 1
            if len(source_pairing_examples) < 8:
                source_pairing_examples.append({
                    "hecke_row_index": int(i),
                    "dot_signed": signed_lift(value, q),
                })

    free_cols = [None] * quotient_ncols
    for original, mapped in quotient_col_map.items():
        free_cols[mapped] = original

    payload = {
        "tool": "mstar_h3a_restline_kernel_quotient",
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "ncols_v_si": ncols,
        "rows_seen": rows_seen,
        "manin_t_rows": manin_rows,
        "manin_t_rank": base.rank,
        "manin_t_max_basis_row_len": base.max_basis_row_len,
        "hecke_rows": hecke_rows,
        "quotient_ncols": quotient_ncols,
        "quotient_rank": quotient_rank,
        "quotient_kernel_dim": kernel_dim,
        "kernel_engine": kernel_engine,
        "matrix_entries": len(sage_entries) if kernel_engine == "sage" else None,
        "matrix_seconds": matrix_seconds,
        "kernel_seconds": kernel_seconds,
        "seconds": time.perf_counter() - started,
        "free_columns": [int(c) for c in free_cols],
        "kernel_support_size": len(kernel_vector),
        "kernel_entries_mod_q": sparse_entries(kernel_vector),
        "kernel_entries_signed_head": signed_entries(kernel_vector, q, limit=80),
        "repair_projected_support_size": len(repair_projected),
        "repair_projected_entries_mod_q": sparse_entries(repair_projected),
        "repair_projected_entries_signed": signed_entries(repair_projected, q),
        "repair_pairing_mod_q": int(repair_pairing),
        "repair_pairing_signed": signed_lift(repair_pairing, q),
        "repair_pairing_nonzero": bool(repair_pairing),
        "source_pairing_nonzero": source_pairing_nonzero,
        "source_annihilated": source_pairing_nonzero == 0,
        "source_pairing_examples": source_pairing_examples,
        "ready_for_al_scalar": bool(
            kernel_dim == 1 and repair_pairing and source_pairing_nonzero == 0
        ),
    }
    status.update({
        "phase": "done",
        "quotient_kernel_dim": kernel_dim,
        "repair_pairing_signed": payload["repair_pairing_signed"],
        "ready_for_al_scalar": payload["ready_for_al_scalar"],
        "seconds": round(payload["seconds"], 3),
    })
    write_status(status_json, status)
    return payload


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# H3a Quotient Restline Kernel",
        "",
        "This is the quotient-functional input for the later AL scalar test",
        "`Q_B(phi)=phi B_AL^{-1} phi^T`.",
        "",
        "```text",
        f"case:                   {payload['case_dir']}",
        f"level/mode/q:           {payload['level']} / {payload['mode']} / {payload['q']}",
        f"V_SI columns:           {payload['ncols_v_si']}",
        f"T-Manin rows/rank:      {payload['manin_t_rows']} / {payload['manin_t_rank']}",
        f"Hecke rows:             {payload['hecke_rows']}",
        f"quotient ncols:         {payload['quotient_ncols']}",
        f"quotient rank:          {payload['quotient_rank']}",
        f"quotient kernel dim:    {payload['quotient_kernel_dim']}",
        f"kernel support size:    {payload['kernel_support_size']}",
        f"repair pairing signed:  {payload['repair_pairing_signed']}",
        f"repair pairing nonzero: {payload['repair_pairing_nonzero']}",
        f"source annihilated:     {payload['source_annihilated']}",
        f"ready for AL scalar:    {payload['ready_for_al_scalar']}",
        f"kernel engine:          {payload['kernel_engine']}",
        f"seconds:                {payload['seconds']:.3f}",
        "```",
        "",
        "## Kernel Head",
        "",
        "```text",
        json.dumps(payload["kernel_entries_signed_head"], ensure_ascii=False),
        "```",
        "",
        "## Repair Projection",
        "",
        "```text",
        json.dumps(payload["repair_projected_entries_signed"], ensure_ascii=False),
        "```",
        "",
        "## Interpretation",
        "",
        "`ready_for_al_scalar=true` means the projected Hecke source has a unique",
        "right-kernel line, all source rows vanish on it, and the repair row pairs",
        "nontrivially with it.  The remaining step is to push this quotient",
        "functional through the Atkin-Lehner pairing.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--pivot-strategy", choices=["min", "max"], default="max")
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--kernel-engine", choices=["sage", "sparse-python"], default="sparse-python")
    parser.add_argument("--status-json", type=Path)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(
        args.case_dir,
        args.pivot_strategy,
        args.progress_every,
        args.kernel_engine,
        status_json=args.status_json,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, args.out_md)
    print(json.dumps({
        "level": payload["level"],
        "mode": payload["mode"],
        "quotient_kernel_dim": payload["quotient_kernel_dim"],
        "repair_pairing_signed": payload["repair_pairing_signed"],
        "ready_for_al_scalar": payload["ready_for_al_scalar"],
        "seconds": payload["seconds"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
