#!/usr/bin/env python3
"""Loop 151: no-Magma sparse Hecke quotient for Reyssat restlevels.

Primary use (with Sage, no Magma):

    sage -python _scripts/mstar_nomagma_sparse_hecke_quotient.py \
      --backend sage --levels 60168 --modes raw anc \
      --primes 5 7 11 13 --q 3863 \
      --out-json _results/mstar_nomagma_sparse_hecke_quotient_60168.json

Smoke use without Sage (plain Python; only small levels):

    python _scripts/mstar_nomagma_sparse_hecke_quotient.py \
      --backend plain --levels 109 218 --primes 5 --q 3863

Mathematical target
-------------------
For a level N and a mode in {raw, anc}, compute the quotient

    F_q<Manin symbols for Gamma0(N), weight 2>
      / (S-relations, optional I-sign relation, T-Manin relations,
         (T_p - a_p(E_mode)) for p in test_primes)

If the quotient dimension is zero after some stage, then no Hecke eigensystem
in the ambient modular-symbol module can carry the tested Frey traces. Since
new/cuspidal parts are subquotients, ambient zero is a rigorous kill for the
corresponding newform obstruction. If the quotient is nonzero, it is only a
survivor candidate; it may be Eisenstein/old/non-cuspidal and must be refined.

The Sage backend deliberately avoids Magma and avoids Sage's high-level
ModularSymbols/NewSubspace construction. It uses low-level ManinSymbolList and
Heilbronn matrices, then does one sparse rank computation per stage.

The plain backend is a small-level diagnostic. It uses a brute-force P1(Z/NZ)
normalizer and the standard p+1 double-coset matrices for T_p; it is not meant
for N=60168.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

DATE = "2026-05-10"
DEFAULT_Q = 3863
DEFAULT_PRIMES = [5, 7, 11, 13]
RAW_A = 2
RAW_B = 3**10 * 109

# Manin matrices in Sage/P1List convention (act on column vector (u,v)^t).
S_MATRIX = [0, -1, 1, 0]
T_MATRIX = [0, 1, -1, -1]
TT_MATRIX = [-1, -1, 1, 0]  # T_MATRIX^2
I_MATRIX = [-1, 0, 0, 1]


def progress(enabled: bool, message: str) -> None:
    if enabled:
        print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def trace_dict(mode: str, primes: Iterable[int]) -> dict[int, int]:
    return {int(p): frey_ap(mode, int(p)) for p in primes}


def factorint_plain(n: int) -> dict[int, int]:
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def gamma0_index(n: int) -> int:
    idx = n
    for p in factorint_plain(n):
        idx = idx * (p + 1) // p
    return idx


@dataclass
class StageResult:
    stage: str
    rows_added: int
    nnz_added: int
    total_rows: int
    total_nnz: int
    rank: int
    quotient_dim: int
    seconds_rank: float
    killed: bool


@dataclass
class RunResult:
    backend: str
    level: int
    q: int
    sign: int | None
    mode: str
    traces: dict[int, int]
    manin_symbols: int
    columns_after_2term: int | None
    gamma0_index: int
    stages: list[StageResult] = field(default_factory=list)
    status: str = "unknown"
    error: str | None = None
    seconds_total: float = 0.0


def sparse_rank_plain(rows: Iterable[dict[int, int]], ncols: int, p: int) -> int:
    """Sparse Gaussian elimination over F_p, tuned for smoke sizes."""
    ranker = SparseIncrementalRank(ncols, p)
    for row in rows:
        ranker.add(row)
    return ranker.rank


class SparseIncrementalRank:
    """Incremental sparse row rank over a prime field.

    This is slower per row than LinBox on small one-shot ranks, but it can reuse
    the Manin row basis when Hecke rows are added in batches.
    """

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
                if len(normalized) > self.max_basis_row_len:
                    self.max_basis_row_len = len(normalized)
                return True
        return False

    def reduce(self, raw_row: dict[int, Any]) -> dict[int, int]:
        """Return the normal-form remainder modulo the current basis."""
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        basis = self.basis
        while row:
            pivot_cols = [c for c in row if c in basis]
            if not pivot_cols:
                break
            pivot = min(pivot_cols) if self.pivot_strategy == "min" else max(pivot_cols)
            factor = row[pivot] % p
            b = basis[pivot]
            for c, v in b.items():
                new = (row.get(c, 0) - factor * v) % p
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row


class DenseNumpyIncrementalRank:
    """Incremental dense row rank over F_p, using NumPy for quotient phases."""

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
            basis_row = self.basis.get(pivot)
            if basis_row is None:
                inv = pow(value, -1, p)
                row = ((row * inv) % p).astype(self.dtype, copy=False)
                self.basis[pivot] = row
                self.rank += 1
                row_len = int(np.count_nonzero(row))
                if row_len > self.max_basis_row_len:
                    self.max_basis_row_len = row_len
                return True
            row -= value * basis_row
            np.remainder(row, p, out=row)


def sparse_rank_plain_old(rows: Iterable[dict[int, int]], ncols: int, p: int) -> int:
    """Deprecated one-shot implementation kept for reference."""
    basis: dict[int, dict[int, int]] = {}
    rank = 0
    for raw_row in rows:
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = max(row)  # deterministic; high pivots tend to keep rows short here
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
                basis[pivot] = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                rank += 1
                break
            if rank == ncols:
                # We still must consume no more rows; caller can stop stage-wise.
                pass
    return rank


class PlainP1:
    """Brute-force P^1(Z/NZ) for small N only."""

    def __init__(self, N: int):
        self.N = int(N)
        if self.N > 2000:
            raise ValueError("plain P1 backend is intentionally limited to small N; use --backend sage")
        self.units = [u for u in range(self.N) if math.gcd(u, self.N) == 1]
        reps: dict[tuple[int, int], int] = {}
        rep_list: list[tuple[int, int]] = []
        for c in range(self.N):
            for d in range(self.N):
                if math.gcd(math.gcd(c, d), self.N) != 1:
                    continue
                norm = self.normalize_pair(c, d)
                if norm not in reps:
                    reps[norm] = len(rep_list)
                    rep_list.append(norm)
        self.reps = rep_list
        self.index = reps

    def __len__(self) -> int:
        return len(self.reps)

    def normalize_pair(self, c: int, d: int) -> tuple[int, int]:
        N = self.N
        c %= N
        d %= N
        return min(((u * c) % N, (u * d) % N) for u in self.units)

    @lru_cache(maxsize=None)
    def normalize_index(self, c: int, d: int) -> int:
        return self.index[self.normalize_pair(c, d)]

    def act(self, i: int, matrix4: list[int]) -> int:
        a, b, c, d = matrix4
        u, v = self.reps[i]
        return self.normalize_index(a * u + b * v, c * u + d * v)


def plain_hecke_matrices(p: int) -> list[list[int]]:
    # Standard double-coset matrices for p not dividing N.
    return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]


def run_plain_level(
    N: int,
    q: int,
    mode: str,
    primes: list[int],
    sign: int | None,
    stop_on_zero: bool,
    show_progress: bool = False,
) -> RunResult:
    started = time.time()
    progress(show_progress, f"plain start N={N} mode={mode} primes={primes}")
    p1 = PlainP1(N)
    progress(show_progress, f"plain P1 built N={N} size={len(p1)}")
    rows: list[dict[int, int]] = []
    total_nnz = 0
    result = RunResult(
        backend="plain",
        level=N,
        q=q,
        sign=sign,
        mode=mode,
        traces=trace_dict(mode, primes),
        manin_symbols=len(p1),
        columns_after_2term=None,
        gamma0_index=gamma0_index(N),
    )

    def add_stage(stage: str, new_rows: list[dict[int, int]]) -> bool:
        nonlocal rows, total_nnz
        rows.extend(new_rows)
        nnz_added = sum(len(r) for r in new_rows)
        total_nnz += nnz_added
        t0 = time.time()
        rank = sparse_rank_plain(rows, len(p1), q)
        elapsed = time.time() - t0
        qdim = len(p1) - rank
        result.stages.append(StageResult(
            stage=stage,
            rows_added=len(new_rows),
            nnz_added=nnz_added,
            total_rows=len(rows),
            total_nnz=total_nnz,
            rank=rank,
            quotient_dim=qdim,
            seconds_rank=elapsed,
            killed=qdim == 0,
        ))
        return qdim == 0

    def add_coeff(row: dict[int, int], col: int, val: int) -> None:
        row[col] = row.get(col, 0) + val
        if row[col] == 0:
            del row[col]

    manin_rows: list[dict[int, int]] = []
    for i in range(len(p1)):
        jS = p1.act(i, S_MATRIX)
        rS: dict[int, int] = {}
        add_coeff(rS, i, 1)
        add_coeff(rS, jS, 1)
        manin_rows.append(rS)

        jT = p1.act(i, T_MATRIX)
        jTT = p1.act(i, TT_MATRIX)
        rT: dict[int, int] = {}
        add_coeff(rT, i, 1)
        add_coeff(rT, jT, 1)
        add_coeff(rT, jTT, 1)
        manin_rows.append(rT)

        if sign in (-1, 1):
            jI = p1.act(i, I_MATRIX)
            # x - sign*xI = 0.  This is diagnostic in plain mode; Sage mode is authoritative.
            rI: dict[int, int] = {}
            add_coeff(rI, i, 1)
            add_coeff(rI, jI, -sign)
            manin_rows.append(rI)
    if add_stage("manin_relations", manin_rows) and stop_on_zero:
        progress(show_progress, f"plain killed at manin_relations N={N} mode={mode}")
        result.status = "killed"
        result.seconds_total = time.time() - started
        return result

    for p in primes:
        ap = frey_ap(mode, p)
        progress(show_progress, f"plain building Hecke rows N={N} mode={mode} p={p} ap={ap}")
        mats = plain_hecke_matrices(p)
        hecke_rows = []
        for i in range(len(p1)):
            r = {i: -ap}
            for A in mats:
                j = p1.act(i, A)
                r[j] = r.get(j, 0) + 1
            hecke_rows.append(r)
        if add_stage(f"T_{p}_minus_{ap}", hecke_rows) and stop_on_zero:
            progress(show_progress, f"plain killed at T_{p}_minus_{ap} N={N} mode={mode}")
            result.status = "killed"
            result.seconds_total = time.time() - started
            return result

    result.status = "survivor_candidate" if result.stages[-1].quotient_dim > 0 else "killed"
    result.seconds_total = time.time() - started
    return result


def run_sage_level(
    N: int,
    q: int,
    mode: str,
    primes: list[int],
    sign: int | None,
    stop_on_zero: bool,
    hecke_family: str,
    show_progress: bool = False,
    rank_algorithm: str | None = None,
    hecke_batch_size: int = 0,
    rank_engine: str = "sage",
    pivot_strategy: str = "max",
    hecke_row_order: str = "natural",
    hecke_row_seed: int = 151,
    skip_existing_pivot: bool = False,
    max_hecke_batches_per_prime: int = 0,
    rc3_transcript_dir: Path | None = None,
    rc3_pivot_dir: Path | None = None,
    rc3_source_witness_dir: Path | None = None,
) -> RunResult:
    progress(show_progress, f"sage import start N={N} mode={mode} primes={primes}")
    try:
        from sage.all import GF, matrix  # type: ignore
        from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
        from sage.modular.modsym.relation_matrix import (  # type: ignore
            modI_relations,
            modS_relations,
            sparse_2term_quotient,
        )
        from sage.modular.modsym.heilbronn import HeilbronnCremona, HeilbronnMerel  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on Sage runtime
        raise RuntimeError("Sage backend requested, but Sage imports failed") from exc

    started = time.time()
    progress(show_progress, f"sage import ok N={N} mode={mode}")
    F = GF(q)
    progress(show_progress, f"sage building ManinSymbolList_gamma0 N={N}")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    progress(show_progress, f"sage Manin symbols built N={N} nsyms={nsyms}")
    result = RunResult(
        backend="sage",
        level=N,
        q=q,
        sign=sign,
        mode=mode,
        traces=trace_dict(mode, primes),
        manin_symbols=nsyms,
        columns_after_2term=None,
        gamma0_index=gamma0_index(N),
    )

    progress(show_progress, f"sage computing S/I relations N={N} sign={sign}")
    rels = set(modS_relations(syms))
    if sign in (-1, 1):
        rels.update(modI_relations(syms, sign))
    progress(show_progress, f"sage S/I relations ready N={N} count={len(rels)}")
    progress(show_progress, f"sage sparse_2term_quotient start N={N}")
    mod = sparse_2term_quotient(rels, nsyms, F)
    progress(show_progress, f"sage sparse_2term_quotient done N={N} entries={len(mod)}")

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
    result.columns_after_2term = ncols
    progress(show_progress, f"sage columns after 2-term quotient N={N} ncols={ncols}")

    entries: dict[tuple[int, int], Any] = {}
    nrows = 0
    total_nnz = 0
    py_ranker = (
        SparseIncrementalRank(ncols, q, pivot_strategy)
        if rank_engine in ("python-sparse", "quotient-python-sparse", "quotient-numpy-dense")
        else None
    )
    quotient_ranker: Any | None = None
    quotient_col_map: dict[int, int] | None = None
    quotient_ncols: int | None = None
    last_rank_update_seconds = 0.0
    rc3_stage_records: list[dict[str, Any]] = []
    rc3_run_dir: Path | None = None
    rc3_pivot_run_dir: Path | None = None
    rc3_source_run_dir: Path | None = None
    rc3_source_rows_path: Path | None = None
    rc3_source_count = 0
    rc3_source_nnz = 0
    if rc3_transcript_dir is not None:
        sign_tag = "none" if sign is None else str(sign)
        rc3_run_dir = rc3_transcript_dir / f"N{N}_{mode}_sign{sign_tag}"
        rc3_run_dir.mkdir(parents=True, exist_ok=True)
    if rc3_pivot_dir is not None:
        sign_tag = "none" if sign is None else str(sign)
        rc3_pivot_run_dir = rc3_pivot_dir / f"N{N}_{mode}_sign{sign_tag}"
        rc3_pivot_run_dir.mkdir(parents=True, exist_ok=True)
    if rc3_source_witness_dir is not None:
        sign_tag = "none" if sign is None else str(sign)
        rc3_source_run_dir = rc3_source_witness_dir / f"N{N}_{mode}_sign{sign_tag}"
        rc3_source_run_dir.mkdir(parents=True, exist_ok=True)
        rc3_source_rows_path = rc3_source_run_dir / "source_rows.jsonl"
        rc3_source_rows_path.write_text("", encoding="utf-8")

    def safe_stage_name(stage: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in stage)

    def canonical_row(row: dict[int, Any]) -> str:
        parts = []
        for col in sorted(row):
            val = int(row[col]) % q
            if val:
                parts.append(f"{int(col)}:{val}")
        return ",".join(parts)

    def write_rc3_manifest() -> None:
        if rc3_run_dir is None:
            return
        manifest = {
            "certificate_version": "rc3a-row-transcript-draft-1",
            "level": N,
            "mode": mode,
            "sign": sign,
            "q": q,
            "columns_after_2term": result.columns_after_2term,
            "rank_engine": rank_engine,
            "pivot_strategy": pivot_strategy,
            "hecke_row_order": hecke_row_order,
            "hecke_row_seed": hecke_row_seed,
            "hecke_family": hecke_family,
            "stages": rc3_stage_records,
            "scope": "row transcript hashes only; not yet a pivot/rank witness",
        }
        (rc3_run_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def sparse_basis_row(row: Any) -> list[list[int]]:
        if isinstance(row, dict):
            items = ((int(c), int(v) % q) for c, v in row.items())
            return [[c, v] for c, v in sorted(items) if v]
        nz = row.nonzero()[0]
        return [[int(c), int(row[int(c)]) % q] for c in nz if int(row[int(c)]) % q]

    def write_rc3_pivot_witness(stage: str) -> None:
        if rc3_pivot_run_dir is None or py_ranker is None:
            return
        if py_ranker.rank != ncols:
            return
        rows_file = "pivots.jsonl"
        rows_path = rc3_pivot_run_dir / rows_file
        pivot_records = []
        with rows_path.open("w", encoding="utf-8") as f:
            for pivot in sorted(py_ranker.basis):
                row_data = sparse_basis_row(py_ranker.basis[pivot])
                record = {"pivot": int(pivot), "row": row_data}
                pivot_records.append(record)
                f.write(json.dumps(record, sort_keys=True) + "\n")
        manifest = {
            "certificate_version": "rc3b-full-sparse-pivot-smoke-1",
            "level": N,
            "mode": mode,
            "sign": sign,
            "q": q,
            "columns_after_2term": result.columns_after_2term,
            "ncols": ncols,
            "rank_engine": rank_engine,
            "pivot_strategy": pivot_strategy,
            "witness_type": "full_sparse_basis",
            "final_stage": stage,
            "pivot_count": len(pivot_records),
            "rows_file": rows_file,
            "rows_file_sha256": file_sha256(rows_path),
            "scope": "full pivot basis from Python sparse ranker; smoke-grade row-derivation binding",
        }
        (rc3_pivot_run_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def write_rc3_source_row(stage: str, stage_row_index: int, row: dict[int, Any]) -> None:
        nonlocal rc3_source_count, rc3_source_nnz
        if rc3_source_rows_path is None:
            return
        record = {
            "row_id": f"{stage}/{stage_row_index}",
            "stage": stage,
            "stage_row_index": stage_row_index,
            "row": [[int(c), int(v) % q] for c, v in sorted(row.items()) if int(v) % q],
        }
        with rc3_source_rows_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        rc3_source_count += 1
        rc3_source_nnz += len(record["row"])

    def write_rc3_source_manifest(stage: str) -> None:
        if rc3_source_run_dir is None or rc3_source_rows_path is None or py_ranker is None:
            return
        if py_ranker.rank != ncols:
            return
        manifest = {
            "certificate_version": "rc3c-independent-source-rows-1",
            "level": N,
            "mode": mode,
            "sign": sign,
            "q": q,
            "columns_after_2term": result.columns_after_2term,
            "ncols": ncols,
            "rank_engine": rank_engine,
            "pivot_strategy": pivot_strategy,
            "witness_type": "independent_source_rows",
            "final_stage": stage,
            "source_row_count": rc3_source_count,
            "source_row_nnz": rc3_source_nnz,
            "rows_file": rc3_source_rows_path.name,
            "rows_file_sha256": file_sha256(rc3_source_rows_path),
            "scope": "original rows that increased the Python sparse rank; verifier recomputes rank",
        }
        (rc3_source_run_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def reduce_terms(terms: Iterable[tuple[int, Any]]) -> dict[int, Any]:
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

    def add_rows_to_entries(stage: str, row_iter: Iterable[dict[int, Any]]) -> tuple[int, int]:
        nonlocal nrows, total_nnz, last_rank_update_seconds
        added_rows = 0
        added_nnz = 0
        rank_t0 = time.time()
        stage_hash = hashlib.sha256() if rc3_run_dir is not None else None
        for row in row_iter:
            if not row:
                continue
            if stage_hash is not None:
                line = f"{stage}\t{added_rows}\t{canonical_row(row)}\n"
                stage_hash.update(line.encode("utf-8"))
            stage_row_index = added_rows
            if quotient_ranker is not None and quotient_col_map is not None and py_ranker is not None:
                rem = py_ranker.reduce(row)
                projected = {
                    quotient_col_map[col]: val
                    for col, val in rem.items()
                    if col in quotient_col_map
                }
                if projected:
                    quotient_ranker.add(projected)
            elif py_ranker is None:
                for col, val in row.items():
                    entries[(nrows, int(col))] = F(val)
            else:
                if py_ranker.add(row):
                    write_rc3_source_row(stage, stage_row_index, row)
            nrows += 1
            added_rows += 1
            added_nnz += len(row)
        total_nnz += added_nnz
        last_rank_update_seconds = time.time() - rank_t0 if py_ranker is not None else 0.0
        if stage_hash is not None and rc3_run_dir is not None:
            digest = stage_hash.hexdigest()
            record = {
                "stage": stage,
                "rows_added": added_rows,
                "nnz_added": added_nnz,
                "row_transcript_sha256": digest,
                "sha256_file": f"{safe_stage_name(stage)}.sha256",
            }
            rc3_stage_records.append(record)
            (rc3_run_dir / record["sha256_file"]).write_text(digest + "\n", encoding="utf-8")
            write_rc3_manifest()
        return added_rows, added_nnz

    def rank_stage(stage: str, added_rows: int, added_nnz: int) -> bool:
        progress(
            show_progress,
            f"sage rank start N={N} mode={mode} stage={stage} rows={nrows} nnz={total_nnz} ncols={ncols} engine={rank_engine}",
        )
        t0 = time.time()
        if quotient_ranker is not None and quotient_ncols is not None and py_ranker is not None:
            rank = py_ranker.rank + quotient_ranker.rank
            elapsed = last_rank_update_seconds
            qdim = quotient_ncols - quotient_ranker.rank
            extra = (
                f" quotient_ncols={quotient_ncols}"
                f" quotient_rank={quotient_ranker.rank}"
                f" max_basis_row_len={quotient_ranker.max_basis_row_len}"
            )
        elif py_ranker is None:
            A = matrix(F, nrows, ncols, entries, sparse=True)
            rank = int(A.rank(algorithm=rank_algorithm)) if rank_algorithm else int(A.rank())
            elapsed = time.time() - t0
            qdim = ncols - rank
            extra = ""
        else:
            rank = py_ranker.rank
            elapsed = last_rank_update_seconds
            qdim = ncols - rank
            extra = f" max_basis_row_len={py_ranker.max_basis_row_len}"
        progress(
            show_progress,
            f"sage rank done N={N} mode={mode} stage={stage} rank={rank} qdim={qdim} seconds={elapsed:.3f}{extra}",
        )
        result.stages.append(StageResult(
            stage=stage,
            rows_added=added_rows,
            nnz_added=added_nnz,
            total_rows=nrows,
            total_nnz=total_nnz,
            rank=rank,
            quotient_dim=qdim,
            seconds_rank=elapsed,
            killed=qdim == 0,
        ))
        return qdim == 0

    def manin_relation_rows() -> Iterator[dict[int, Any]]:
        for i in range(nsyms):
            terms: list[tuple[int, Any]] = [(i, F(1))]
            terms.extend(syms.apply_T(i))
            terms.extend(syms.apply_TT(i))
            yield reduce_terms(terms)

    progress(show_progress, f"sage building Manin T rows N={N}")
    added_rows, added_nnz = add_rows_to_entries("manin_T_relations_after_SI", manin_relation_rows())
    progress(show_progress, f"sage Manin T rows added N={N} rows={added_rows} nnz={added_nnz}")
    if rank_stage("manin_T_relations_after_SI", added_rows, added_nnz) and stop_on_zero:
        progress(show_progress, f"sage killed at manin_T_relations N={N} mode={mode}")
        result.status = "killed"
        result.seconds_total = time.time() - started
        write_rc3_pivot_witness("manin_T_relations_after_SI")
        write_rc3_source_manifest("manin_T_relations_after_SI")
        write_rc3_manifest()
        return result
    if rank_engine in ("quotient-python-sparse", "quotient-numpy-dense"):
        if py_ranker is None:
            raise RuntimeError(f"{rank_engine} requires a Python ranker")
        pivot_cols = set(py_ranker.basis)
        free_cols = [c for c in range(ncols) if c not in pivot_cols]
        quotient_col_map = {c: i for i, c in enumerate(free_cols)}
        quotient_ncols = len(free_cols)
        if rank_engine == "quotient-numpy-dense":
            quotient_ranker = DenseNumpyIncrementalRank(quotient_ncols, q, pivot_strategy)
        else:
            quotient_ranker = SparseIncrementalRank(quotient_ncols, q, pivot_strategy)
        progress(
            show_progress,
            f"sage quotient compression ready N={N} mode={mode} quotient_ncols={quotient_ncols}",
        )

    def matrices_for_p(p: int) -> list[list[int]]:
        if hecke_family == "cremona":
            return HeilbronnCremona(p).to_list()
        if hecke_family == "merel":
            return HeilbronnMerel(p).to_list()
        if hecke_family == "standard":
            return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]
        raise ValueError(f"unknown hecke family {hecke_family!r}")

    def hecke_indices(p: int) -> Iterable[int]:
        if hecke_row_order == "natural":
            return range(nsyms)
        if hecke_row_order == "reverse":
            return range(nsyms - 1, -1, -1)
        if hecke_row_order == "random":
            indices = list(range(nsyms))
            random.Random(hecke_row_seed + 1009 * p).shuffle(indices)
            return indices
        raise ValueError(f"unknown Hecke row order {hecke_row_order!r}")

    def hecke_relation_rows(p: int, ap: int) -> Iterator[dict[int, Any]]:
        mats = matrices_for_p(p)
        for i in hecke_indices(p):
            terms: list[tuple[int, Any]] = [(i, F(-ap))]
            for A in mats:
                terms.extend(syms.apply(i, A))
            yield reduce_terms(terms)

    for p in primes:
        ap = frey_ap(mode, p)
        progress(show_progress, f"sage building Hecke rows N={N} mode={mode} p={p} ap={ap} family={hecke_family}")
        if hecke_batch_size > 0:
            batch: list[dict[int, Any]] = []
            batch_index = 0
            skipped_rows = 0
            for row in hecke_relation_rows(p, ap):
                if skip_existing_pivot and py_ranker is not None and row:
                    candidate = min(row) if pivot_strategy == "min" else max(row)
                    if candidate in py_ranker.basis:
                        skipped_rows += 1
                        continue
                batch.append(row)
                if len(batch) < hecke_batch_size:
                    continue
                batch_index += 1
                stage = f"T_{p}_minus_{ap}_batch_{batch_index}"
                added_rows, added_nnz = add_rows_to_entries(stage, batch)
                progress(
                    show_progress,
                    f"sage Hecke batch added N={N} mode={mode} p={p} batch={batch_index} rows={added_rows} nnz={added_nnz} skipped={skipped_rows}",
                )
                if rank_stage(stage, added_rows, added_nnz) and stop_on_zero:
                    progress(show_progress, f"sage killed at {stage} N={N} mode={mode}")
                    result.status = "killed"
                    result.seconds_total = time.time() - started
                    write_rc3_pivot_witness(stage)
                    write_rc3_source_manifest(stage)
                    write_rc3_manifest()
                    return result
                batch = []
                if max_hecke_batches_per_prime > 0 and batch_index >= max_hecke_batches_per_prime:
                    progress(
                        show_progress,
                        f"sage max Hecke batches reached N={N} mode={mode} p={p} batches={batch_index}",
                    )
                    break
            if batch:
                batch_index += 1
                stage = f"T_{p}_minus_{ap}_batch_{batch_index}"
                added_rows, added_nnz = add_rows_to_entries(stage, batch)
                progress(
                    show_progress,
                    f"sage Hecke final batch added N={N} mode={mode} p={p} batch={batch_index} rows={added_rows} nnz={added_nnz} skipped={skipped_rows}",
                )
                if rank_stage(stage, added_rows, added_nnz) and stop_on_zero:
                    progress(show_progress, f"sage killed at {stage} N={N} mode={mode}")
                    result.status = "killed"
                    result.seconds_total = time.time() - started
                    write_rc3_pivot_witness(stage)
                    write_rc3_source_manifest(stage)
                    write_rc3_manifest()
                    return result
        else:
            stage = f"T_{p}_minus_{ap}"
            added_rows, added_nnz = add_rows_to_entries(stage, hecke_relation_rows(p, ap))
            progress(show_progress, f"sage Hecke rows added N={N} mode={mode} p={p} rows={added_rows} nnz={added_nnz}")
            if rank_stage(stage, added_rows, added_nnz) and stop_on_zero:
                progress(show_progress, f"sage killed at T_{p}_minus_{ap} N={N} mode={mode}")
                result.status = "killed"
                result.seconds_total = time.time() - started
                write_rc3_pivot_witness(stage)
                write_rc3_source_manifest(stage)
                write_rc3_manifest()
                return result

    result.status = "survivor_candidate" if result.stages[-1].quotient_dim > 0 else "killed"
    result.seconds_total = time.time() - started
    if result.status == "killed" and result.stages:
        write_rc3_pivot_witness(result.stages[-1].stage)
        write_rc3_source_manifest(result.stages[-1].stage)
    write_rc3_manifest()
    return result


def result_to_dict(r: RunResult) -> dict[str, Any]:
    return {
        "backend": r.backend,
        "level": r.level,
        "q": r.q,
        "sign": r.sign,
        "mode": r.mode,
        "traces": {str(k): v for k, v in r.traces.items()},
        "manin_symbols": r.manin_symbols,
        "columns_after_2term": r.columns_after_2term,
        "gamma0_index": r.gamma0_index,
        "status": r.status,
        "error": r.error,
        "seconds_total": r.seconds_total,
        "stages": [stage.__dict__ for stage in r.stages],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append("# No-Magma Sparse Hecke Quotient")
    lines.append("")
    lines.append(f"Date: {payload['date']}")
    lines.append(f"Backend requested: `{payload['backend_requested']}`")
    lines.append(f"q: `{payload['q']}`")
    lines.append(f"Primes: `{payload['primes']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |")
    lines.append("|---|---:|---|---:|---:|---:|---|---:|---:|")
    for r in payload["runs"]:
        stages = r.get("stages") or []
        final_dim = stages[-1]["quotient_dim"] if stages else ""
        lines.append(
            f"| {r['backend']} | {r['level']} | {r['mode']} | {r['sign']} | "
            f"{r['manin_symbols']} | {r.get('columns_after_2term')} | {r['status']} | "
            f"{final_dim} | {r['seconds_total']:.3f} |"
        )
    lines.append("")
    for r in payload["runs"]:
        lines.append(f"## Level {r['level']} / {r['mode']} / backend {r['backend']}")
        lines.append("")
        lines.append(f"Traces: `{r['traces']}`")
        if r.get("error"):
            lines.append(f"Error: `{r['error']}`")
            lines.append("")
            continue
        lines.append("")
        lines.append("| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|---:|")
        for s in r.get("stages", []):
            lines.append(
                f"| {s['stage']} | {s['rows_added']} | {s['nnz_added']} | "
                f"{s['total_rows']} | {s['total_nnz']} | {s['rank']} | "
                f"{s['quotient_dim']} | {s['killed']} | {s['seconds_rank']:.3f} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["auto", "sage", "plain"], default="auto")
    parser.add_argument("--levels", nargs="+", type=int, default=[109, 218])
    parser.add_argument("--modes", nargs="+", choices=["raw", "anc"], default=["raw", "anc"])
    parser.add_argument("--primes", nargs="+", type=int, default=DEFAULT_PRIMES)
    parser.add_argument("--q", type=int, default=DEFAULT_Q)
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1, help="0 means no I-sign relation")
    parser.add_argument("--hecke-family", choices=["cremona", "merel", "standard"], default="cremona")
    parser.add_argument(
        "--rank-engine",
        choices=["sage", "python-sparse", "quotient-python-sparse", "quotient-numpy-dense"],
        default="sage",
    )
    parser.add_argument("--pivot-strategy", choices=["max", "min"], default="max")
    parser.add_argument("--hecke-row-order", choices=["natural", "reverse", "random"], default="natural")
    parser.add_argument("--hecke-row-seed", type=int, default=151)
    parser.add_argument("--skip-existing-pivot", action="store_true")
    parser.add_argument(
        "--max-hecke-batches-per-prime",
        type=int,
        default=0,
        help="If positive, stop each Hecke prime after this many cumulative batches and continue to the next prime.",
    )
    parser.add_argument("--rank-algorithm", choices=["linbox", "generic"], help="Sage sparse rank algorithm.")
    parser.add_argument("--hecke-batch-size", type=int, default=0, help="Rank Hecke rows in cumulative batches.")
    parser.add_argument("--no-stop-on-zero", action="store_true")
    parser.add_argument("--progress", action="store_true", help="Print stage-level progress messages.")
    parser.add_argument(
        "--rc3-transcript-dir",
        type=Path,
        help="Optional RC3a directory for per-stage row-transcript hashes and manifests.",
    )
    parser.add_argument(
        "--rc3-pivot-dir",
        type=Path,
        help="Optional RC3b directory for smoke-grade pivot-basis witnesses.",
    )
    parser.add_argument(
        "--rc3-source-witness-dir",
        type=Path,
        help="Optional RC3c directory for independent original source-row witnesses.",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    sign = None if args.sign == 0 else args.sign
    stop_on_zero = not args.no_stop_on_zero

    backend = args.backend
    if backend == "auto":
        try:
            import sage.all  # type: ignore # noqa: F401
            backend = "sage"
        except Exception:
            backend = "plain"

    runs: list[dict[str, Any]] = []
    for N in args.levels:
        for mode in args.modes:
            try:
                if backend == "sage":
                    r = run_sage_level(
                        N,
                        args.q,
                        mode,
                        args.primes,
                        sign,
                        stop_on_zero,
                        args.hecke_family,
                        args.progress,
                        args.rank_algorithm,
                        args.hecke_batch_size,
                        args.rank_engine,
                        args.pivot_strategy,
                        args.hecke_row_order,
                        args.hecke_row_seed,
                        args.skip_existing_pivot,
                        args.max_hecke_batches_per_prime,
                        args.rc3_transcript_dir,
                        args.rc3_pivot_dir,
                        args.rc3_source_witness_dir,
                    )
                else:
                    r = run_plain_level(N, args.q, mode, args.primes, sign, stop_on_zero, args.progress)
            except Exception as exc:
                r = RunResult(
                    backend=backend,
                    level=N,
                    q=args.q,
                    sign=sign,
                    mode=mode,
                    traces=trace_dict(mode, args.primes),
                    manin_symbols=0,
                    columns_after_2term=None,
                    gamma0_index=gamma0_index(N),
                    status="error",
                    error=f"{type(exc).__name__}: {exc}",
                )
            runs.append(result_to_dict(r))
            print(f"N={N} mode={mode} backend={backend} status={r.status} error={r.error}")

    payload = {
        "date": DATE,
        "backend_requested": args.backend,
        "backend_used": backend,
        "q": args.q,
        "sign": sign,
        "primes": args.primes,
        "stop_on_zero": stop_on_zero,
        "runs": runs,
    }

    out_json = args.out_json or Path(f"mstar_nomagma_sparse_hecke_quotient_{DATE}.json")
    out_md = args.out_md or out_json.with_suffix(".md")
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, out_md)
    print(out_json)
    print(out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
