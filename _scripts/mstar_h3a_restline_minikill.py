#!/usr/bin/env python3
"""Parallel residue-line minikill for a nearly closed RC3c source witness.

This helper is deliberately narrower than mstar_nomagma_sparse_hecke_quotient.py:
it starts from a live/partial `source_rows.jsonl` whose rank is expected to be
ncols-1, rebuilds that source rank basis, and then tests a bounded stream of
new Hecke rows for a single repair row.

If a repair row is found, it writes a split witness compatible with
mstar_h3a_rc3c_witness_verify_rank.py:

    source rows first, one `origin=repair_only` row last.

The script is meant for low-priority parallel Mac Studio runs while the main
long quotient run continues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import time
from pathlib import Path
from typing import Any, Iterable, Iterator


S_MATRIX = [0, -1, 1, 0]
T_MATRIX = [0, 1, -1, -1]
TT_MATRIX = [-1, -1, 1, 0]
I_MATRIX = [-1, 0, 0, 1]
RAW_A = 2
RAW_B = 3**10 * 109


class SparseIncrementalRank:
    def __init__(self, ncols: int, p: int, pivot_strategy: str = "max"):
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.rows_seen = 0
        self.max_basis_row_len = 0

    def add(self, raw_row: dict[int, Any]) -> bool:
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

    def reduce(self, raw_row: dict[int, Any]) -> dict[int, int]:
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot_cols = [c for c in row if c in self.basis]
            if not pivot_cols:
                break
            pivot = min(pivot_cols) if self.pivot_strategy == "min" else max(pivot_cols)
            factor = row[pivot] % p
            basis_row = self.basis[pivot]
            for c, v in basis_row.items():
                new = (row.get(c, 0) - factor * v) % p
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row


class DenseNumpyIncrementalRank:
    def __init__(self, ncols: int, p: int, pivot_strategy: str = "max"):
        import numpy as np  # type: ignore

        self.np = np
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.dtype = np.int32
        self.basis: dict[int, Any] = {}
        self.rank = 0
        self.rows_seen = 0
        self.max_basis_row_len = 0

    def add(self, raw_row: dict[int, Any]) -> bool:
        np = self.np
        p = self.p
        self.rows_seen += 1
        row = np.zeros(self.ncols, dtype=self.dtype)
        for c, v in raw_row.items():
            val = int(v) % p
            if val:
                row[int(c)] = val
        while True:
            nonzero = np.flatnonzero(row)
            if nonzero.size == 0:
                return False
            pivot = int(nonzero[0] if self.pivot_strategy == "min" else nonzero[-1])
            value = int(row[pivot]) % p
            if pivot in self.basis:
                row = (row - value * self.basis[pivot]) % p
            else:
                inv = pow(value, -1, p)
                normalized = (row * inv) % p
                self.basis[pivot] = normalized.astype(self.dtype, copy=False)
                self.rank += 1
                row_len = int(np.count_nonzero(normalized))
                if row_len > self.max_basis_row_len:
                    self.max_basis_row_len = row_len
                return True


def progress(enabled: bool, message: str) -> None:
    if enabled:
        print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row_to_dict(record: dict[str, Any]) -> dict[int, int]:
    return {int(c): int(v) for c, v in record["row"]}


def sparse_row_list(row: dict[int, Any], q: int) -> list[list[int]]:
    return [[int(c), int(v) % q] for c, v in sorted(row.items()) if int(v) % q]


def canonical_row(row: dict[int, Any], q: int) -> str:
    return ",".join(
        f"{int(c)}:{int(v) % q}" for c, v in sorted(row.items()) if int(v) % q
    )


def row_hash(stage: str, stage_row_index: int, row: dict[int, Any], q: int) -> str:
    line = f"{stage}\t{stage_row_index}\t{canonical_row(row, q)}\n"
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def legendre_symbol(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    r = pow(n, (p - 1) // 2, p)
    return -1 if r == p - 1 else int(r)


def frey_ap(mode: str, p: int) -> int:
    if mode == "raw":
        a, b = RAW_A, RAW_B
    elif mode == "anc":
        a, b = RAW_B, RAW_A
    else:
        raise ValueError(f"unknown mode {mode!r}")
    total = 0
    for x in range(p):
        total += legendre_symbol(x * (x - a) * (x + b), p)
    return -total


def write_status(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def snapshot_source(source_rows: Path, snapshot_path: Path, force: bool) -> dict[str, Any]:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    if force or not snapshot_path.exists():
        with source_rows.open("rb") as src, snapshot_path.open("wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
    row_count = 0
    with snapshot_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row_count += 1
    stat = snapshot_path.stat()
    return {
        "path": str(snapshot_path),
        "bytes": stat.st_size,
        "row_count": row_count,
        "sha256": file_sha256(snapshot_path),
    }


def load_source_ranker(
    rows_path: Path,
    ncols: int,
    q: int,
    pivot_strategy: str,
    progress_every: int,
    status_json: Path | None,
    status: dict[str, Any],
    show_progress: bool,
) -> tuple[SparseIncrementalRank, dict[str, Any]]:
    ranker = SparseIncrementalRank(ncols, q, pivot_strategy)
    independent = 0
    row_count = 0
    t0 = time.time()
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            row_count += 1
            if ranker.add(row_to_dict(record)):
                independent += 1
            if progress_every and row_count % progress_every == 0:
                elapsed = time.time() - t0
                progress(
                    show_progress,
                    (
                        f"source rows loaded={row_count} rank={ranker.rank} "
                        f"seconds={elapsed:.1f}"
                    ),
                )
                status.update(
                    {
                        "phase": "loading_source_rank_basis",
                        "source_rows_seen": row_count,
                        "source_rank": ranker.rank,
                        "seconds": elapsed,
                    }
                )
                write_status(status_json, status)
    elapsed = time.time() - t0
    summary = {
        "rows_seen": row_count,
        "independent_rows": independent,
        "rank": ranker.rank,
        "max_basis_row_len": ranker.max_basis_row_len,
        "seconds": elapsed,
    }
    return ranker, summary


def load_source_quotient_rankers(
    rows_path: Path,
    ncols: int,
    q: int,
    pivot_strategy: str,
    quotient_engine: str,
    progress_every: int,
    status_json: Path | None,
    status: dict[str, Any],
    show_progress: bool,
) -> tuple[SparseIncrementalRank, Any, dict[int, int], dict[str, Any]]:
    """Rebuild the same two-level rank structure used by the quotient engine.

    The live RC3c source file is ordered: Manin-T base rows first, then Hecke
    source rows that increased the quotient-compressed rank.  Replaying it in
    that structure avoids the expensive full sparse elimination of all Hecke
    rows against all earlier Hecke rows.
    """

    base_ranker = SparseIncrementalRank(ncols, q, pivot_strategy)
    quotient_ranker: Any | None = None
    quotient_col_map: dict[int, int] | None = None
    base_rows = 0
    hecke_rows = 0
    rows_seen = 0
    t0 = time.time()

    def ensure_quotient() -> None:
        nonlocal quotient_ranker, quotient_col_map
        if quotient_ranker is not None and quotient_col_map is not None:
            return
        free_cols = [c for c in range(ncols) if c not in base_ranker.basis]
        quotient_col_map = {c: i for i, c in enumerate(free_cols)}
        if quotient_engine == "dense-numpy":
            quotient_ranker = DenseNumpyIncrementalRank(len(free_cols), q, pivot_strategy)
        elif quotient_engine == "sparse":
            quotient_ranker = SparseIncrementalRank(len(free_cols), q, pivot_strategy)
        else:
            raise ValueError(f"unknown quotient engine {quotient_engine!r}")
        progress(
            show_progress,
            (
                f"quotient compression ready base_rank={base_ranker.rank} "
                f"quotient_ncols={len(free_cols)} engine={quotient_engine}"
            ),
        )

    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            rows_seen += 1
            row = row_to_dict(record)
            stage = str(record.get("stage", ""))
            if stage == "manin_T_relations_after_SI":
                base_rows += 1
                base_ranker.add(row)
            else:
                ensure_quotient()
                assert quotient_ranker is not None
                assert quotient_col_map is not None
                hecke_rows += 1
                rem = base_ranker.reduce(row)
                projected = {
                    quotient_col_map[col]: val
                    for col, val in rem.items()
                    if col in quotient_col_map
                }
                if projected:
                    quotient_ranker.add(projected)

            if progress_every and rows_seen % progress_every == 0:
                elapsed = time.time() - t0
                qr = quotient_ranker.rank if quotient_ranker is not None else 0
                qn = quotient_ranker.ncols if quotient_ranker is not None else None
                full_rank = base_ranker.rank + qr
                progress(
                    show_progress,
                    (
                        f"source quotient replay rows={rows_seen} "
                        f"base_rank={base_ranker.rank} quotient_rank={qr} "
                        f"full_rank={full_rank} seconds={elapsed:.1f}"
                    ),
                )
                status.update(
                    {
                        "phase": "loading_source_quotient_basis",
                        "source_rows_seen": rows_seen,
                        "base_rank": base_ranker.rank,
                        "quotient_rank": qr,
                        "quotient_ncols": qn,
                        "source_rank": full_rank,
                        "seconds": elapsed,
                    }
                )
                write_status(status_json, status)

    ensure_quotient()
    assert quotient_ranker is not None
    assert quotient_col_map is not None
    elapsed = time.time() - t0
    full_rank = base_ranker.rank + quotient_ranker.rank
    summary = {
        "rank_mode": "source_quotient",
        "quotient_engine": quotient_engine,
        "rows_seen": rows_seen,
        "base_rows": base_rows,
        "hecke_rows": hecke_rows,
        "base_rank": base_ranker.rank,
        "quotient_ncols": quotient_ranker.ncols,
        "quotient_rank": quotient_ranker.rank,
        "rank": full_rank,
        "qdim": ncols - full_rank,
        "base_max_basis_row_len": base_ranker.max_basis_row_len,
        "quotient_max_basis_row_len": quotient_ranker.max_basis_row_len,
        "seconds": elapsed,
    }
    return base_ranker, quotient_ranker, quotient_col_map, summary


def load_source_quotient_kernel(
    rows_path: Path,
    ncols: int,
    q: int,
    pivot_strategy: str,
    progress_every: int,
    status_json: Path | None,
    status: dict[str, Any],
    show_progress: bool,
) -> tuple[SparseIncrementalRank, dict[int, int], dict[int, int], dict[str, Any]]:
    """Build the one-dimensional right kernel of the source quotient matrix."""

    from sage.all import GF, matrix  # type: ignore

    F = GF(q)
    base_ranker = SparseIncrementalRank(ncols, q, pivot_strategy)
    quotient_col_map: dict[int, int] | None = None
    entries: dict[tuple[int, int], Any] = {}
    base_rows = 0
    hecke_rows = 0
    rows_seen = 0
    t0 = time.time()

    def ensure_quotient() -> None:
        nonlocal quotient_col_map
        if quotient_col_map is not None:
            return
        free_cols = [c for c in range(ncols) if c not in base_ranker.basis]
        quotient_col_map = {c: i for i, c in enumerate(free_cols)}
        progress(
            show_progress,
            (
                f"kernel quotient map ready base_rank={base_ranker.rank} "
                f"quotient_ncols={len(free_cols)}"
            ),
        )

    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            rows_seen += 1
            row = row_to_dict(record)
            stage = str(record.get("stage", ""))
            if stage == "manin_T_relations_after_SI":
                base_rows += 1
                base_ranker.add(row)
            else:
                ensure_quotient()
                assert quotient_col_map is not None
                rem = base_ranker.reduce(row)
                for col, val in rem.items():
                    mapped = quotient_col_map.get(col)
                    if mapped is not None and int(val) % q:
                        entries[(hecke_rows, mapped)] = F(int(val) % q)
                hecke_rows += 1

            if progress_every and rows_seen % progress_every == 0:
                elapsed = time.time() - t0
                progress(
                    show_progress,
                    (
                        f"source kernel collect rows={rows_seen} "
                        f"base_rank={base_ranker.rank} hecke_rows={hecke_rows} "
                        f"entries={len(entries)} seconds={elapsed:.1f}"
                    ),
                )
                status.update(
                    {
                        "phase": "collecting_source_quotient_matrix",
                        "source_rows_seen": rows_seen,
                        "base_rank": base_ranker.rank,
                        "hecke_rows": hecke_rows,
                        "matrix_entries": len(entries),
                        "seconds": elapsed,
                    }
                )
                write_status(status_json, status)

    ensure_quotient()
    assert quotient_col_map is not None
    quotient_ncols = len(quotient_col_map)
    status.update(
        {
            "phase": "computing_source_quotient_kernel",
            "base_rank": base_ranker.rank,
            "hecke_rows": hecke_rows,
            "quotient_ncols": quotient_ncols,
            "matrix_entries": len(entries),
            "seconds": time.time() - t0,
        }
    )
    write_status(status_json, status)
    progress(
        show_progress,
        (
            f"sage sparse kernel start rows={hecke_rows} "
            f"cols={quotient_ncols} entries={len(entries)}"
        ),
    )
    A = matrix(F, hecke_rows, quotient_ncols, entries, sparse=True)
    K = A.right_kernel()
    kernel_dim = int(K.dimension())
    quotient_rank = quotient_ncols - kernel_dim
    if kernel_dim:
        v = K.basis()[0]
        kernel_vector = {
            int(i): int(v[i])
            for i in range(quotient_ncols)
            if int(v[i]) % q
        }
    else:
        kernel_vector = {}
    elapsed = time.time() - t0
    summary = {
        "rank_mode": "source_quotient_kernel",
        "rows_seen": rows_seen,
        "base_rows": base_rows,
        "hecke_rows": hecke_rows,
        "base_rank": base_ranker.rank,
        "quotient_ncols": quotient_ncols,
        "quotient_rank": quotient_rank,
        "quotient_kernel_dim": kernel_dim,
        "quotient_kernel_nnz": len(kernel_vector),
        "rank": base_ranker.rank + quotient_rank,
        "qdim": ncols - (base_ranker.rank + quotient_rank),
        "matrix_entries": len(entries),
        "seconds": elapsed,
    }
    return base_ranker, quotient_col_map, kernel_vector, summary


def sage_context(N: int, q: int, sign: int | None, show_progress: bool) -> dict[str, Any]:
    progress(show_progress, f"sage import start N={N}")
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import (  # type: ignore
        modI_relations,
        modS_relations,
        sparse_2term_quotient,
    )
    from sage.modular.modsym.heilbronn import HeilbronnCremona, HeilbronnMerel  # type: ignore

    F = GF(q)
    progress(show_progress, f"sage building ManinSymbolList_gamma0 N={N}")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    progress(show_progress, f"sage computing S/I quotient N={N} nsyms={nsyms}")
    rels = set(modS_relations(syms))
    if sign in (-1, 1):
        rels.update(modI_relations(syms, sign))
    mod = sparse_2term_quotient(rels, nsyms, F)

    rep_to_col: dict[int, int] = {}
    mod_map: list[tuple[int, Any] | None] = []
    for entry in mod:
        rep, scalar = entry
        if scalar == 0:
            mod_map.append(None)
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            rep_to_col[rep_i] = len(rep_to_col)
        mod_map.append((rep_to_col[rep_i], F(scalar)))
    ncols = len(rep_to_col)
    progress(show_progress, f"sage quotient ready N={N} ncols={ncols}")
    return {
        "F": F,
        "syms": syms,
        "nsyms": nsyms,
        "mod_map": mod_map,
        "ncols": ncols,
        "HeilbronnCremona": HeilbronnCremona,
        "HeilbronnMerel": HeilbronnMerel,
    }


def reduce_terms(ctx: dict[str, Any], terms: Iterable[tuple[int, Any]]) -> dict[int, Any]:
    F = ctx["F"]
    mod_map = ctx["mod_map"]
    row: dict[int, Any] = {}
    for j, coeff in terms:
        mapped = mod_map[int(j)]
        if mapped is None:
            continue
        col, scalar = mapped
        val = F(coeff) * scalar
        if val == 0:
            continue
        row[col] = row.get(col, F(0)) + val
        if row[col] == 0:
            del row[col]
    return row


def matrices_for_p(ctx: dict[str, Any], p: int, hecke_family: str) -> list[list[int]]:
    if hecke_family == "cremona":
        return ctx["HeilbronnCremona"](p).to_list()
    if hecke_family == "merel":
        return ctx["HeilbronnMerel"](p).to_list()
    if hecke_family == "standard":
        return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]
    raise ValueError(f"unknown Hecke family {hecke_family!r}")


def hecke_indices(
    nsyms: int,
    order: str,
    seed: int,
    p: int,
    start_index: int,
    max_candidate_rows: int,
) -> Iterable[int]:
    if order == "natural":
        base: Iterable[int] = range(start_index, nsyms)
    elif order == "reverse":
        base = range(nsyms - 1 - start_index, -1, -1)
    elif order == "random":
        indices = list(range(nsyms))
        random.Random(seed + 1009 * p).shuffle(indices)
        base = indices[start_index:]
    else:
        raise ValueError(f"unknown Hecke row order {order!r}")

    if max_candidate_rows <= 0:
        yield from base
        return
    for count, idx in enumerate(base):
        if count >= max_candidate_rows:
            break
        yield int(idx)


def hecke_row(
    ctx: dict[str, Any],
    p: int,
    ap: int,
    idx: int,
    hecke_family: str,
    hecke_row_order: str,
) -> tuple[dict[str, Any], dict[int, Any]]:
    F = ctx["F"]
    syms = ctx["syms"]
    terms: list[tuple[int, Any]] = [(idx, F(-ap))]
    for A in matrices_for_p(ctx, p, hecke_family):
        terms.extend(syms.apply(idx, A))
    metadata = {
        "source_kind": "hecke",
        "hecke_prime": int(p),
        "hecke_ap": int(ap),
        "hecke_family": hecke_family,
        "hecke_row_order": hecke_row_order,
        "manin_symbol_index": int(idx),
    }
    return metadata, reduce_terms(ctx, terms)


def normalize_source_record(record: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "origin": "source",
        "row_id": str(record["row_id"]),
        "stage": str(record["stage"]),
        "stage_row_index": int(record["stage_row_index"]),
        "row": [[int(col), int(value)] for col, value in record["row"]],
    }
    if "row_line_sha256" in record:
        out["row_line_sha256"] = str(record["row_line_sha256"])
    if "row_metadata" in record:
        out["row_metadata"] = record["row_metadata"]
    return out


def write_split_witness(
    source_rows_snapshot: Path,
    out_case_dir: Path,
    level: int,
    mode: str,
    sign: int | None,
    q: int,
    ncols: int,
    repair_record: dict[str, Any],
    snapshot_info: dict[str, Any],
) -> dict[str, Any]:
    out_case_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_case_dir / "mixed_rows.jsonl"
    source_count = 0
    with source_rows_snapshot.open("r", encoding="utf-8") as src, rows_path.open(
        "w", encoding="utf-8"
    ) as dst:
        for line in src:
            if not line.strip():
                continue
            dst.write(json.dumps(normalize_source_record(json.loads(line)), sort_keys=True) + "\n")
            source_count += 1
        dst.write(json.dumps(repair_record, sort_keys=True) + "\n")

    manifest = {
        "certificate_version": "h3a-restline-minikill-witness-1",
        "witness_type": "source_prefix_plus_single_repair_row",
        "level": int(level),
        "mode": str(mode),
        "sign": sign,
        "q": int(q),
        "ncols": int(ncols),
        "columns_after_2term": int(ncols),
        "rows_file": rows_path.name,
        "rows_file_sha256": file_sha256(rows_path),
        "source_row_count": source_count,
        "repair_only_row_count": 1,
        "mixed_row_count": source_count + 1,
        "square": source_count + 1 == int(ncols),
        "repair_only_row_id": str(repair_record["row_id"]),
        "repair_only_stage": str(repair_record["stage"]),
        "repair_only_original_index": int(source_count),
        "split_rule": "source snapshot plus first independent minikill row",
        "source_rows_snapshot": snapshot_info,
    }
    (out_case_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    repair = payload.get("repair_row")
    lines = [
        "# H3a Restline Minikill",
        "",
        f"Level: `{payload['level']}`, mode: `{payload['mode']}`, q: `{payload['q']}`.",
        f"Source rank: `{payload['source_summary']['rank']}` / `{payload['ncols']}`.",
        f"Candidate prime: `{payload['candidate_prime']}`.",
        f"Candidate rows tested: `{payload['candidate_rows_tested']}`.",
        f"Status: `{payload['status']}`.",
    ]
    if repair:
        lines.extend(
            [
                "",
                "## Repair Row",
                "",
                f"Stage: `{repair['stage']}`.",
                f"Row id: `{repair['row_id']}`.",
                f"Manin symbol index: `{repair['row_metadata']['manin_symbol_index']}`.",
                f"Output witness: `{payload.get('out_case_dir')}`.",
            ]
        )
    if payload.get("message"):
        lines.extend(["", payload["message"]])
    lines.append("")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-rows", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--out-case-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--status-json", type=Path)
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--mode", choices=["raw", "anc"], required=True)
    parser.add_argument("--sign", type=int, default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--ncols", type=int, required=True)
    parser.add_argument("--prime", type=int, default=7)
    parser.add_argument("--ap", type=int)
    parser.add_argument("--hecke-family", choices=["standard", "cremona", "merel"], default="standard")
    parser.add_argument("--hecke-row-order", choices=["natural", "reverse", "random"], default="natural")
    parser.add_argument("--hecke-row-seed", type=int, default=151)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-candidate-rows", type=int, default=20000)
    parser.add_argument("--pivot-strategy", choices=["min", "max"], default="max")
    parser.add_argument(
        "--rank-mode",
        choices=["source-quotient-kernel", "source-quotient", "full"],
        default="source-quotient-kernel",
    )
    parser.add_argument("--quotient-engine", choices=["dense-numpy", "sparse"], default="dense-numpy")
    parser.add_argument("--progress-every-source", type=int, default=1000)
    parser.add_argument("--progress-every-candidate", type=int, default=50)
    parser.add_argument("--reuse-snapshot", action="store_true")
    parser.add_argument("--show-progress", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.time()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    status: dict[str, Any] = {
        "tool": "mstar_h3a_restline_minikill",
        "phase": "starting",
        "level": args.level,
        "mode": args.mode,
        "q": args.q,
        "ncols": args.ncols,
        "candidate_prime": args.prime,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    write_status(args.status_json, status)

    snapshot_path = args.work_dir / "source_rows_snapshot.jsonl"
    progress(args.show_progress, f"snapshot source rows -> {snapshot_path}")
    snapshot_info = snapshot_source(args.source_rows, snapshot_path, force=not args.reuse_snapshot)
    status.update({"phase": "snapshot_done", "snapshot": snapshot_info})
    write_status(args.status_json, status)

    base_ranker: SparseIncrementalRank | None = None
    quotient_ranker: Any | None = None
    quotient_col_map: dict[int, int] | None = None
    kernel_vector: dict[int, int] | None = None
    if args.rank_mode == "source-quotient-kernel":
        base_ranker, quotient_col_map, kernel_vector, source_summary = load_source_quotient_kernel(
            snapshot_path,
            args.ncols,
            args.q,
            args.pivot_strategy,
            args.progress_every_source,
            args.status_json,
            status,
            args.show_progress,
        )
        ranker = None
    elif args.rank_mode == "source-quotient":
        base_ranker, quotient_ranker, quotient_col_map, source_summary = load_source_quotient_rankers(
            snapshot_path,
            args.ncols,
            args.q,
            args.pivot_strategy,
            args.quotient_engine,
            args.progress_every_source,
            args.status_json,
            status,
            args.show_progress,
        )
        ranker = None
    else:
        ranker, source_summary = load_source_ranker(
            snapshot_path,
            args.ncols,
            args.q,
            args.pivot_strategy,
            args.progress_every_source,
            args.status_json,
            status,
            args.show_progress,
        )
    if source_summary["rank"] != args.ncols - 1:
        payload = {
            **status,
            "phase": "done",
            "status": "source_rank_not_residue_line",
            "source_summary": source_summary,
            "candidate_rows_tested": 0,
            "seconds_total": time.time() - started,
            "message": "Source rank is not ncols-1; minikill did not test repair rows.",
        }
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_markdown(payload, args.out_md)
        write_status(args.status_json, payload)
        return 2

    ctx = sage_context(args.level, args.q, args.sign, args.show_progress)
    if int(ctx["ncols"]) != args.ncols:
        payload = {
            **status,
            "phase": "done",
            "status": "sage_ncols_mismatch",
            "source_summary": source_summary,
            "sage_ncols": int(ctx["ncols"]),
            "candidate_rows_tested": 0,
            "seconds_total": time.time() - started,
            "message": "Sage quotient ncols did not match the supplied source ncols.",
        }
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_markdown(payload, args.out_md)
        write_status(args.status_json, payload)
        return 3

    ap = int(args.ap) if args.ap is not None else frey_ap(args.mode, args.prime)
    stage = f"T_{args.prime}_minus_{ap}_restline_minikill"
    tested = 0
    repair_record: dict[str, Any] | None = None
    status.update(
        {
            "phase": "testing_candidates",
            "source_summary": source_summary,
            "candidate_prime": args.prime,
            "candidate_ap": ap,
        }
    )
    write_status(args.status_json, status)

    for idx in hecke_indices(
        int(ctx["nsyms"]),
        args.hecke_row_order,
        args.hecke_row_seed,
        args.prime,
        args.start_index,
        args.max_candidate_rows,
    ):
        row_metadata, row = hecke_row(ctx, args.prime, ap, idx, args.hecke_family, args.hecke_row_order)
        stage_row_index = tested
        tested += 1
        independent = False
        if args.rank_mode == "source-quotient-kernel":
            assert base_ranker is not None
            assert quotient_col_map is not None
            assert kernel_vector is not None
            rem = base_ranker.reduce(row)
            projected = {
                quotient_col_map[col]: int(val) % args.q
                for col, val in rem.items()
                if col in quotient_col_map and int(val) % args.q
            }
            pairing = sum(
                (int(val) % args.q) * kernel_vector.get(int(col), 0)
                for col, val in projected.items()
            ) % args.q
            independent = bool(pairing)
            current_rank = args.ncols if independent else source_summary["rank"]
            row_metadata["restline_pairing_mod_q"] = int(pairing)
            row_metadata["source_rank_mode"] = args.rank_mode
        elif args.rank_mode == "source-quotient":
            assert base_ranker is not None
            assert quotient_ranker is not None
            assert quotient_col_map is not None
            rem = base_ranker.reduce(row)
            projected = {
                quotient_col_map[col]: val
                for col, val in rem.items()
                if col in quotient_col_map
            }
            if projected:
                independent = quotient_ranker.add(projected)
            current_rank = base_ranker.rank + quotient_ranker.rank
        else:
            assert ranker is not None
            independent = ranker.add(row)
            current_rank = ranker.rank

        if independent:
            repair_record = {
                "origin": "repair_only",
                "row_id": f"{stage}/{stage_row_index}",
                "stage": stage,
                "stage_row_index": stage_row_index,
                "row_line_sha256": row_hash(stage, stage_row_index, row, args.q),
                "row_metadata": row_metadata,
                "row": sparse_row_list(row, args.q),
            }
            break
        if args.progress_every_candidate and tested % args.progress_every_candidate == 0:
            elapsed = time.time() - started
            progress(
                args.show_progress,
                f"candidate rows tested={tested} rank={current_rank} seconds={elapsed:.1f}",
            )
            status.update(
                {
                    "phase": "testing_candidates",
                    "candidate_rows_tested": tested,
                    "rank": current_rank,
                    "seconds": elapsed,
                }
            )
            write_status(args.status_json, status)

    payload: dict[str, Any] = {
        **status,
        "phase": "done",
        "level": args.level,
        "mode": args.mode,
        "sign": args.sign,
        "q": args.q,
        "ncols": args.ncols,
        "candidate_prime": args.prime,
        "candidate_ap": ap,
        "hecke_family": args.hecke_family,
        "hecke_row_order": args.hecke_row_order,
        "start_index": args.start_index,
        "max_candidate_rows": args.max_candidate_rows,
        "source_summary": source_summary,
        "candidate_rows_tested": tested,
        "final_rank": (
            base_ranker.rank + quotient_ranker.rank
            if args.rank_mode == "source-quotient" and base_ranker is not None and quotient_ranker is not None
            else (args.ncols if repair_record is not None else source_summary["rank"])
            if args.rank_mode == "source-quotient-kernel"
            else ranker.rank
        ),
        "seconds_total": time.time() - started,
        "snapshot": snapshot_info,
    }

    if repair_record is not None:
        manifest = write_split_witness(
            snapshot_path,
            args.out_case_dir,
            args.level,
            args.mode,
            args.sign,
            args.q,
            args.ncols,
            repair_record,
            snapshot_info,
        )
        payload.update(
            {
                "status": "repair_row_found",
                "repair_row": repair_record,
                "out_case_dir": str(args.out_case_dir),
                "out_manifest": manifest,
                "certified_by_minikill_ranker": payload["final_rank"] == args.ncols,
            }
        )
    else:
        payload.update(
            {
                "status": "no_repair_row_in_tested_window",
                "message": "No candidate row increased rank in the tested window.",
            }
        )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    write_status(args.status_json, payload)
    print(json.dumps({"status": payload["status"], "tested": tested, "rank": payload["final_rank"]}))
    return 0 if repair_record is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
