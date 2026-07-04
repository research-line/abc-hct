#!/usr/bin/env sage
# Production scalar-Wiedemann run for the Q_B-3 source-Gram operator.
#
# This script avoids materializing A = C_source B_AL C_source^T.  It rebuilds
# the sparse pi_N projection from a split-last witness, constructs the sparse
# bridge to Sage's M^+ basis, and generates scalar Wiedemann sequences from
# matrix-free matvecs.
#
# Loop 350 guardrail: for large levels do not build ModularSymbols over QQ
# unless explicitly requested.  The old sign=0 + plus_submodule() route over
# QQ triggers a rational IML/GMP nullspace with very large intermediate
# integers.  The default route below keeps the sign=1 bridge and the sign=0
# AL-pairing ambient over F_q.

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

from sage.all import GF, Gamma0, ModularSymbols, load, matrix, save, vector
from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
from sage.modular.modsym.relation_matrix import (
    modI_relations,
    modS_relations,
    sparse_2term_quotient,
)


TOOL = "mstar_h3a_qb3_wiedemann_production"
DATE = "2026-06-15"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def matrix_sha256(M):
    h = hashlib.sha256()
    try:
        items = sorted((int(i), int(j), int(x)) for (i, j), x in M.dict().items())
    except Exception:
        return None
    for i, j, x in items:
        h.update(("%d,%d,%d;" % (i, j, x)).encode("ascii"))
    return h.hexdigest()


def vector_sha256(v):
    h = hashlib.sha256()
    try:
        items = sorted((int(i), int(x)) for i, x in v.dict().items())
    except Exception:
        return None
    for i, x in items:
        h.update(("%d,%d;" % (i, x)).encode("ascii"))
    return h.hexdigest()


def signed_lift(value, q):
    v = int(value) % q
    if v > q // 2:
        v -= q
    return int(v)


def write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def read_manifest(case_dir):
    return load_json(Path(case_dir) / "manifest.json")


def iter_rows(case_dir):
    manifest = read_manifest(case_dir)
    rows_path = Path(case_dir) / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def sparse_pairs_to_dict(row_pairs, q):
    return {int(c): int(v) % q for c, v in row_pairs if int(v) % q}


class SparseRowBasis:
    def __init__(self, q):
        self.q = int(q)
        self.basis = {}
        self.rank = 0

    def add_dict(self, raw_row):
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot = max(row)
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
                self.basis[pivot] = {
                    c: (v * inv) % q for c, v in row.items() if (v * inv) % q
                }
                self.rank += 1
                return True
        return False

    def reduce_dict(self, raw_row):
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot_candidates = [c for c in row if c in self.basis]
            if not pivot_candidates:
                break
            pivot = max(pivot_candidates)
            factor = row[pivot] % q
            for c, v in self.basis[pivot].items():
                new = (row.get(c, 0) - factor * v) % q
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row


def berlekamp_massey(sequence, F):
    C = [F(1)]
    B = [F(1)]
    L = 0
    m = 1
    b = F(1)

    for n in range(len(sequence)):
        discrepancy = F(sequence[n])
        for i in range(1, L + 1):
            discrepancy += C[i] * sequence[n - i]
        if discrepancy == 0:
            m += 1
            continue

        T = list(C)
        coef = -discrepancy / b
        needed = len(B) + m
        if len(C) < needed:
            C.extend([F(0)] * (needed - len(C)))
        for j in range(len(B)):
            C[j + m] += coef * B[j]

        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = discrepancy
            m = 1
        else:
            m += 1

    return L, C[: L + 1]


def verify_connection(sequence, C, F):
    L = len(C) - 1
    failures = []
    for k in range(L, len(sequence)):
        total = F(sequence[k])
        for i in range(1, L + 1):
            total += C[i] * sequence[k - i]
        if total != 0:
            failures.append([int(k), int(total)])
            if len(failures) >= 8:
                break
    return failures


def get_repair_entries(pi_data):
    if "projected_repair_entries_mod_q" in pi_data:
        return pi_data["projected_repair_entries_mod_q"], "projected_repair_entries_mod_q"
    if "repair_projected_entries_mod_q" in pi_data:
        return pi_data["repair_projected_entries_mod_q"], "repair_projected_entries_mod_q"
    raise ValueError("pi-json has no projected repair entries")


def get_phi_entries(pi_data):
    phi_entries = pi_data.get("phi_checks", {}).get("induced_phi_entries_mod_q")
    if phi_entries:
        return phi_entries, "phi_checks.induced_phi_entries_mod_q"
    if pi_data.get("kernel_entries_mod_q"):
        return pi_data["kernel_entries_mod_q"], "kernel_entries_mod_q"
    raise ValueError("pi-json has no phi/kernel entries")


def quotient_vector_from_entries(F, n, entries):
    v = vector(F, int(n))
    for col, value in entries:
        v[int(col)] = F(int(value))
    return v


def dot_product(u, v):
    return sum(u[i] * v[i] for i in range(len(u)))


def beta_from_pi_or_entries(F, pi_data, q, repair_entries):
    if pi_data.get("repair_pairing_mod_q") is not None:
        return F(int(pi_data["repair_pairing_mod_q"])), "repair_pairing_mod_q"
    phi_entries, phi_source = get_phi_entries(pi_data)
    repair = {int(c): F(int(v)) for c, v in repair_entries}
    beta = F(0)
    for col, value in phi_entries:
        beta += F(int(value)) * repair.get(int(col), F(0))
    return beta, phi_source


def sparse_vector_dict(vec, F, scale=None):
    result = {}
    inv_scale = None if scale is None else F(scale) ** -1
    for i, value in vec.dict().items():
        y = F(value)
        if inv_scale is not None:
            y *= inv_scale
        if y:
            result[int(i)] = y
    return result


def sparse_matrix_from_row_dicts(F, nrows, ncols, rows):
    entries = {}
    for i, row in enumerate(rows):
        for j, value in row.items():
            if value:
                entries[(int(i), int(j))] = F(value)
    return matrix(F, int(nrows), int(ncols), entries, sparse=True)


def sparse_change_ring(M, F):
    entries = {}
    for key, value in M.dict().items():
        if value:
            i, j = key
            entries[(int(i), int(j))] = F(value)
    return matrix(F, int(M.nrows()), int(M.ncols()), entries, sparse=True)


def matrix_cache_paths(cache_dir, N, q, name):
    root = Path(cache_dir)
    base = root / ("N%d_q%d_%s" % (int(N), int(q), str(name)))
    return base, Path(str(base) + ".sobj"), Path(str(base) + ".json")


def load_cached_matrix(cache_dir, N, q, name, label, F, save_status,
                       expected_rows=None, expected_cols=None):
    if not cache_dir:
        return None, None
    base, obj_path, meta_path = matrix_cache_paths(cache_dir, N, q, name)
    save_status({
        "phase": "loading_B_AL_cache",
        "cache_label": label,
        "cache_path": str(obj_path),
    })
    if not obj_path.exists():
        save_status({
            "phase": "B_AL_cache_miss",
            "cache_label": label,
            "cache_path": str(obj_path),
        })
        return None, None
    M = sparse_change_ring(load(str(base)), F)
    if expected_rows is not None and int(M.nrows()) != int(expected_rows):
        raise ValueError("%s cache row mismatch: %s != %s" % (label, M.nrows(), expected_rows))
    if expected_cols is not None and int(M.ncols()) != int(expected_cols):
        raise ValueError("%s cache column mismatch: %s != %s" % (label, M.ncols(), expected_cols))
    sha = matrix_sha256(M)
    meta = load_json(meta_path) if meta_path.exists() else {}
    if meta.get("sha256") and meta.get("sha256") != sha:
        raise ValueError("%s cache sha256 mismatch" % label)
    cache_meta = {
        "label": label,
        "name": name,
        "path": str(obj_path),
        "metadata_path": str(meta_path),
        "loaded": True,
        "written": False,
        "rows": int(M.nrows()),
        "cols": int(M.ncols()),
        "nnz": int(len(M.dict())),
        "sha256": sha,
    }
    save_status({
        "phase": "loaded_B_AL_cache",
        "cache_label": label,
        "cache_path": str(obj_path),
        "%s_nnz" % label: cache_meta["nnz"],
        "%s_sha256" % label: sha,
    })
    return M, cache_meta


def write_cached_matrix(cache_dir, N, q, name, label, M, save_status,
                        overwrite=False, sha=None):
    if not cache_dir:
        return None
    root = Path(cache_dir)
    root.mkdir(parents=True, exist_ok=True)
    base, obj_path, meta_path = matrix_cache_paths(cache_dir, N, q, name)
    if obj_path.exists() and not overwrite:
        return {
            "label": label,
            "name": name,
            "path": str(obj_path),
            "metadata_path": str(meta_path),
            "loaded": False,
            "written": False,
            "rows": int(M.nrows()),
            "cols": int(M.ncols()),
            "nnz": int(len(M.dict())),
            "sha256": sha or matrix_sha256(M),
            "reason": "exists",
        }
    sha = sha or matrix_sha256(M)
    save_status({
        "phase": "writing_B_AL_cache",
        "cache_label": label,
        "cache_path": str(obj_path),
        "%s_nnz" % label: int(len(M.dict())),
        "%s_sha256" % label: sha,
    })
    save(M, str(base))
    meta = {
        "tool": TOOL,
        "date": DATE,
        "label": label,
        "name": name,
        "level": int(N),
        "q": int(q),
        "rows": int(M.nrows()),
        "cols": int(M.ncols()),
        "nnz": int(len(M.dict())),
        "sha256": sha,
        "created_unix": time.time(),
    }
    write_json(meta_path, meta)
    meta.update({
        "path": str(obj_path),
        "metadata_path": str(meta_path),
        "loaded": False,
        "written": True,
    })
    save_status({
        "phase": "wrote_B_AL_cache",
        "cache_label": label,
        "cache_path": str(obj_path),
        "%s_nnz" % label: int(len(M.dict())),
        "%s_sha256" % label: sha,
    })
    return meta


def build_t_projection(case_dir, pi_data, q, status, save_status, progress_every):
    t_basis = SparseRowBasis(q)
    hecke_records = []
    t_rows = 0
    rows_scanned = 0
    for row in iter_rows(case_dir):
        rows_scanned += 1
        meta = row.get("row_metadata") or {}
        if meta.get("source_kind") == "manin_T":
            t_rows += 1
            t_basis.add_dict(sparse_pairs_to_dict(row["row"], q))
        elif row.get("origin") == "source" and meta.get("source_kind") == "hecke":
            hecke_records.append(row)
        if progress_every and rows_scanned % progress_every == 0:
            save_status({
                "phase": "building_T_projection",
                "rows_scanned": int(rows_scanned),
                "t_rows": int(t_rows),
                "t_rank": int(t_basis.rank),
                "hecke_records_buffered": int(len(hecke_records)),
            })

    ncols = int(read_manifest(case_dir)["ncols"])
    free_columns = [int(c) for c in pi_data["free_columns"]]
    free_col_to_qcol = {c: i for i, c in enumerate(free_columns)}
    computed_free = [c for c in range(ncols) if c not in t_basis.basis]
    if computed_free != free_columns:
        raise ValueError("computed T-quotient free columns differ from pi-json")

    projected_rows = []
    nnz = 0
    max_len = 0
    for idx, row in enumerate(hecke_records, start=1):
        reduced = t_basis.reduce_dict(sparse_pairs_to_dict(row["row"], q))
        projected = {}
        for col, value in reduced.items():
            if col not in free_col_to_qcol:
                raise RuntimeError("pivot column survived T reduction: %s" % col)
            projected[free_col_to_qcol[col]] = int(value) % q
        projected_rows.append(projected)
        nnz += len(projected)
        max_len = max(max_len, len(projected))
        if progress_every and idx % progress_every == 0:
            save_status({
                "phase": "projecting_hecke_rows",
                "projected_hecke_rows": int(idx),
                "projected_nnz": int(nnz),
                "source_max_row_len": int(max_len),
            })

    status.update({
        "phase": "projected_source_rows",
        "t_rows": int(t_rows),
        "t_rank": int(t_basis.rank),
        "hecke_rows": int(len(projected_rows)),
        "source_nnz": int(nnz),
        "source_max_row_len": int(max_len),
    })
    return projected_rows


def build_free_to_sage(case_dir, pi_data, manifest, F, status, module_base_ring):
    N = int(manifest["level"])
    q = int(manifest["q"])
    sign = int(manifest.get("sign", 1))
    ncols = int(manifest["ncols"])
    free_columns = [int(c) for c in pi_data["free_columns"]]

    syms = ManinSymbolList_gamma0(N, 2)
    rels = set(modS_relations(syms))
    if sign in (-1, 1):
        rels.update(modI_relations(syms, sign))
    mod = sparse_2term_quotient(rels, len(syms), F)

    rep_to_col = {}
    mod_map = []
    for entry in mod:
        rep, scalar = entry
        if scalar == 0:
            mod_map.append(None)
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            rep_to_col[rep_i] = len(rep_to_col)
        mod_map.append((rep_to_col[rep_i], F(scalar)))

    if module_base_ring == "finite":
        M = ModularSymbols(Gamma0(N), 2, sign=sign, base_ring=F)
    elif module_base_ring == "rational":
        M = ModularSymbols(Gamma0(N), 2, sign=sign)
    else:
        raise ValueError("unknown module base ring: %s" % module_base_ring)
    sage_dim = int(M.dimension())
    gens_to_basis = M.manin_gens_to_basis()

    wanted = set(free_columns)
    col_to_sage = {}
    consistency_errors = []
    for j, mapped in enumerate(mod_map):
        if mapped is None:
            continue
        col, scalar = mapped
        if col >= ncols or col not in wanted:
            continue
        row = sparse_vector_dict(gens_to_basis.row(j), F, scale=scalar)
        if col not in col_to_sage:
            col_to_sage[col] = row
        elif col_to_sage[col] != row:
            consistency_errors.append({"col": int(col), "manin_index": int(j)})
            if len(consistency_errors) >= 10:
                break

    missing = [int(c) for c in free_columns if c not in col_to_sage]
    if missing:
        raise ValueError("missing free-to-Sage columns: %s" % missing[:10])
    if consistency_errors:
        raise ValueError("free-to-Sage consistency errors: %s" % consistency_errors[:3])

    rows = [col_to_sage[c] for c in free_columns]
    Fmat = sparse_matrix_from_row_dicts(F, len(rows), sage_dim, rows)
    status.update({
        "phase": "built_free_to_sage",
        "module_base_ring": str(module_base_ring),
        "sage_dim": int(sage_dim),
        "free_to_sage_nnz": int(Fmat.dict().__len__()),
    })
    return Fmat, sage_dim


def build_bal_factors(
    N,
    q,
    F,
    status,
    save_status,
    bal_mode,
    cache_dir=None,
    cache_read=False,
    cache_write=False,
    cache_overwrite=False,
    stop_after_plus_cache=False,
    pari_stack_mb=0,
):
    if bal_mode == "sign0-finite":
        save_status({
            "phase": "building_B_AL_modular_symbols",
            "bal_mode": bal_mode,
            "module_base_ring": "finite",
        })
        M0 = ModularSymbols(Gamma0(N), 2, sign=0, base_ring=F)
    elif bal_mode == "sign0-rational":
        save_status({
            "phase": "building_B_AL_modular_symbols",
            "bal_mode": bal_mode,
            "module_base_ring": "rational",
        })
        M0 = ModularSymbols(Gamma0(N), 2, sign=0)
    elif bal_mode == "sign0-tensor-solve":
        save_status({
            "phase": "building_B_AL_modular_symbols",
            "bal_mode": bal_mode,
            "module_base_ring": "finite",
            "pairing_kind": "_pari_tensor_solve",
        })
        M0 = ModularSymbols(Gamma0(N), 2, sign=0, base_ring=F)
    elif bal_mode == "sign1-direct":
        save_status({
            "phase": "building_B_AL_sign1_direct_probe",
            "bal_mode": bal_mode,
            "module_base_ring": "finite",
        })
        M1 = ModularSymbols(Gamma0(N), 2, sign=1, base_ring=F)
        try:
            E1 = sparse_change_ring(M1._pari_pairing(), F)
        except Exception as exc:
            raise RuntimeError(
                "sign1-direct pairing is unavailable/degenerate in Sage; "
                "use sign0-finite for the AL-twisted ambient pairing"
            ) from exc
        W1 = M1.atkin_lehner_operator(N)
        try:
            W1m = W1.matrix()
        except Exception:
            W1m = W1
        WF1 = sparse_change_ring(W1m, F)
        status.update({
            "phase": "built_B_AL_factors",
            "bal_mode": bal_mode,
            "sign1_dim": int(M1.dimension()),
            "P_nnz": None,
            "E_nnz": int(len(E1.dict())),
            "W_nnz": int(len(WF1.dict())),
            "pairing_kind": "_pari_pairing",
            "primary_pairing_materialized": True,
        })
        return None, E1, WF1, "direct"
    else:
        raise ValueError("unknown B_AL mode: %s" % bal_mode)

    save_status({
        "phase": "building_B_AL_plus_basis",
        "bal_mode": bal_mode,
        "sign0_dim": int(M0.dimension()),
        "bal_cache_dir": str(cache_dir) if cache_dir else None,
        "bal_cache_read": bool(cache_read),
        "bal_cache_write": bool(cache_write),
    })
    sign0_dim = int(M0.dimension())
    cache_metadata = {}
    P = None
    P_cache = None
    if cache_read:
        P, P_cache = load_cached_matrix(
            cache_dir,
            N,
            q,
            "sign0_plus_basis",
            "P",
            F,
            save_status,
            expected_cols=sign0_dim,
        )
    if P is None:
        save_status({
            "phase": "building_B_AL_plus_basis",
            "bal_mode": bal_mode,
            "sign0_dim": sign0_dim,
            "bal_cache_dir": str(cache_dir) if cache_dir else None,
            "bal_cache_read": bool(cache_read),
            "bal_cache_write": bool(cache_write),
        })
        P = sparse_change_ring(M0.plus_submodule().basis_matrix(), F)
        P_sha = matrix_sha256(P)
        if cache_write:
            P_cache = write_cached_matrix(
                cache_dir,
                N,
                q,
                "sign0_plus_basis",
                "P",
                P,
                save_status,
                overwrite=cache_overwrite,
                sha=P_sha,
            )
    else:
        P_sha = P_cache.get("sha256") if P_cache else matrix_sha256(P)
    if P_cache:
        cache_metadata["P"] = P_cache
    save_status({
        "phase": "built_B_AL_plus_basis",
        "bal_mode": bal_mode,
        "sign0_dim": sign0_dim,
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(P.dict())),
        "P_sha256": P_sha,
        "bal_cache": cache_metadata,
    })
    if stop_after_plus_cache:
        status.update({
            "phase": "stopped_after_B_AL_plus_basis",
            "bal_mode": bal_mode,
            "sign0_dim": sign0_dim,
            "plus_dim": int(P.nrows()),
            "P_nnz": int(len(P.dict())),
            "P_sha256": P_sha,
            "bal_cache": cache_metadata,
            "pairing_kind": "_pari_tensor_solve" if bal_mode == "sign0-tensor-solve" else None,
            "primary_pairing_materialized": False if bal_mode == "sign0-tensor-solve" else None,
        })
        return P, None, None, "plus-cache-only"
    if int(pari_stack_mb or 0) > 0:
        stack_bytes = int(pari_stack_mb) * 1024 * 1024
        save_status({
            "phase": "allocating_pari_stack",
            "pari_stack_mb": int(pari_stack_mb),
            "pari_stack_bytes": int(stack_bytes),
        })
        from sage.libs.pari import pari as _pari_alloc
        _pari_alloc.allocatemem(stack_bytes, silent=True)
        save_status({
            "phase": "allocated_pari_stack",
            "pari_stack_mb": int(pari_stack_mb),
            "pari_stack_bytes": int(stack_bytes),
        })
    if bal_mode == "sign0-tensor-solve":
        E = None
        T_cache = None
        if cache_read:
            E, T_cache = load_cached_matrix(
                cache_dir,
                N,
                q,
                "sign0_pari_tensor",
                "T",
                F,
                save_status,
                expected_rows=sign0_dim,
                expected_cols=sign0_dim,
            )
        save_status({
            "phase": "building_B_AL_tensor",
            "bal_mode": bal_mode,
            "sign0_dim": sign0_dim,
            "plus_dim": int(P.nrows()),
            "P_nnz": int(len(P.dict())),
            "P_sha256": P_sha,
        })
        if E is None:
            E = sparse_change_ring(M0._pari_tensor(), F)
            T_sha = matrix_sha256(E)
            if cache_write:
                T_cache = write_cached_matrix(
                    cache_dir,
                    N,
                    q,
                    "sign0_pari_tensor",
                    "T",
                    E,
                    save_status,
                    overwrite=cache_overwrite,
                    sha=T_sha,
                )
        else:
            T_sha = T_cache.get("sha256") if T_cache else matrix_sha256(E)
        if T_cache:
            cache_metadata["T"] = T_cache
        pairing_kind = "_pari_tensor_solve"
        primary_pairing_materialized = False
        pairing_nnz_key = "T_nnz"
        bal_apply_kind = "tensor-solve"
    else:
        save_status({
            "phase": "building_B_AL_pairing",
            "bal_mode": bal_mode,
            "sign0_dim": int(M0.dimension()),
            "plus_dim": int(P.nrows()),
            "P_nnz": int(len(P.dict())),
        })
        E = None
        E_cache = None
        if cache_read:
            E, E_cache = load_cached_matrix(
                cache_dir,
                N,
                q,
                "sign0_pari_pairing",
                "E",
                F,
                save_status,
                expected_rows=sign0_dim,
                expected_cols=sign0_dim,
            )
        if E is None:
            E = sparse_change_ring(M0._pari_pairing(), F)
            E_sha = matrix_sha256(E)
            if cache_write:
                E_cache = write_cached_matrix(
                    cache_dir,
                    N,
                    q,
                    "sign0_pari_pairing",
                    "E",
                    E,
                    save_status,
                    overwrite=cache_overwrite,
                    sha=E_sha,
                )
        else:
            E_sha = E_cache.get("sha256") if E_cache else matrix_sha256(E)
        if E_cache:
            cache_metadata["E"] = E_cache
        pairing_kind = "_pari_pairing"
        primary_pairing_materialized = True
        pairing_nnz_key = "E_nnz"
        bal_apply_kind = "dense-pairing"
    if bal_mode == "sign0-tensor-solve":
        pairing_sha = T_sha
    else:
        pairing_sha = E_sha
    save_status({
        "phase": "building_B_AL_atkin_lehner",
        "bal_mode": bal_mode,
        "sign0_dim": sign0_dim,
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(P.dict())),
        pairing_nnz_key: int(len(E.dict())),
        "pairing_kind": pairing_kind,
        "primary_pairing_materialized": primary_pairing_materialized,
    })
    WF = None
    W_cache = None
    if cache_read:
        WF, W_cache = load_cached_matrix(
            cache_dir,
            N,
            q,
            "sign0_atkin_lehner_W",
            "W",
            F,
            save_status,
            expected_rows=sign0_dim,
            expected_cols=sign0_dim,
        )
    if WF is None:
        W = M0.atkin_lehner_operator(N)
        try:
            Wm = W.matrix()
        except Exception:
            Wm = W
        WF = sparse_change_ring(Wm, F)
        W_sha = matrix_sha256(WF)
        if cache_write:
            W_cache = write_cached_matrix(
                cache_dir,
                N,
                q,
                "sign0_atkin_lehner_W",
                "W",
                WF,
                save_status,
                overwrite=cache_overwrite,
                sha=W_sha,
            )
    else:
        W_sha = W_cache.get("sha256") if W_cache else matrix_sha256(WF)
    if W_cache:
        cache_metadata["W"] = W_cache
    status.update({
        "phase": "built_B_AL_factors",
        "bal_mode": bal_mode,
        "sign0_dim": sign0_dim,
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(P.dict())),
        pairing_nnz_key: int(len(E.dict())),
        "W_nnz": int(len(WF.dict())),
        "pairing_kind": pairing_kind,
        "primary_pairing_materialized": primary_pairing_materialized,
        "P_sha256": P_sha,
        "pairing_tensor_or_E_sha256": pairing_sha,
        "W_sha256": W_sha,
        "bal_cache": cache_metadata,
    })
    return P, E, WF, bal_apply_kind


def deterministic_pair(F, n, seed):
    u = vector(F, [F((i + 3) ** (seed + 1) + 19 * seed + 5) for i in range(n)])
    v = vector(F, [F((i + 5) ** (seed + 2) + 31 * seed + 7) for i in range(n)])
    return u, v


def _ckpt_vec_ints(x):
    """Serialize a GF(q) vector to a plain list of ints in [0, q)."""
    return [int(v) for v in x]


def _ckpt_seq_ints(seq):
    """Serialize a list of GF(q) scalars to plain ints."""
    return [int(s) for s in seq]


def _ckpt_ints_vec(F, lst):
    return vector(F, [F(int(v)) for v in lst])


class Checkpointer:
    """Regel-2 checkpoint/resume for the Wiedemann rank/solve sequences.

    A single JSON file at ``path`` with a top-level ``stage`` field in
    {"rank", "rank_done", "solve", "solve_reconstruct", "solve_done"}.
    Sequences and vectors are stored as plain int lists mod q (portable and
    inspectable; deliberately NOT Sage .sobj to avoid pickle/version coupling;
    size is ~a few 10 KB for q=3863, dim ~10568).  Writes are atomic
    (``.tmp`` + ``os.replace``) and frequency-limited (every ``step_every``
    steps OR every ``min_seconds`` seconds).  Resume verifies the consistency
    anchors and ABORTS on any mismatch (never resume on inconsistent
    prerequisites).  Disabled (no-op) when ``path`` is falsy, so runs without
    --resume-from behave exactly as before.
    """

    _ANCHOR_KEYS = ("q", "target_rank", "case_dir", "pi_json",
                    "P_sha256", "T_sha256", "W_sha256")

    def __init__(self, path, anchors, step_every, min_seconds):
        self.path = str(path) if path else None
        self.anchors = dict(anchors)
        self.step_every = int(step_every) if step_every else 0
        self.min_seconds = int(min_seconds) if min_seconds else 0
        self.enabled = bool(self.path)
        self.loaded = None
        self._last_write = time.time()
        if self.enabled and os.path.exists(self.path):
            self.loaded = self._load_and_verify()

    def _load_and_verify(self):
        data = json.loads(Path(self.path).read_text(encoding="utf-8"))
        got = data.get("anchors", {})
        for k in self._ANCHOR_KEYS:
            if str(got.get(k)) != str(self.anchors.get(k)):
                raise RuntimeError(
                    "checkpoint anchor mismatch for %r: checkpoint=%r current=%r; "
                    "refusing to resume on inconsistent prerequisites (delete the "
                    "checkpoint to force a clean restart)."
                    % (k, got.get(k), self.anchors.get(k))
                )
        return data

    def _write(self, payload):
        payload = dict(payload)
        payload["anchors"] = self.anchors
        payload["written_unix"] = time.time()
        tmp = self.path + ".tmp"
        Path(tmp).write_text(json.dumps(payload, ensure_ascii=False),
                             encoding="utf-8")
        os.replace(tmp, self.path)
        self._last_write = time.time()

    def due(self, steps_done):
        if not self.enabled:
            return False
        if self.step_every and (steps_done % self.step_every == 0):
            return True
        if self.min_seconds and (time.time() - self._last_write) >= self.min_seconds:
            return True
        return False

    def resume_state(self, stage):
        """Return the mid-flight resume dict for ``stage``, or None."""
        if not self.loaded:
            return None
        if self.loaded.get("stage") != stage:
            return None
        return self.loaded

    def rank_result(self):
        """Return (attempts, accepted) if a completed rank stage is recorded."""
        if not self.loaded:
            return None
        if self.loaded.get("stage") in ("rank_done", "solve",
                                        "solve_reconstruct", "solve_done"):
            rr = self.loaded.get("rank_result")
            if rr is not None:
                return rr.get("attempts"), rr.get("accepted")
        return None

    def save_progress(self, stage, seed, step, seq, x, completed_seeds,
                      attempts, rank_result=None, extra=None):
        if not self.enabled:
            return
        payload = {
            "stage": stage,
            "seed": int(seed),
            "step": int(step),
            "seq": _ckpt_seq_ints(seq),
            "x": _ckpt_vec_ints(x),
            "completed_seeds": [int(s) for s in completed_seeds],
            "attempts": attempts,
            "rank_result": rank_result,
        }
        if extra:
            payload.update(extra)
        self._write(payload)

    def mark_stage(self, stage, rank_result=None):
        if not self.enabled:
            return
        self._write({"stage": stage, "rank_result": rank_result})


def scalar_wiedemann_rank_certificate(F, q, n, matvec, args, save_status,
                                      ckpt=None):
    sequence_length = int(args.sequence_length or (2 * n + args.suffix_terms))
    attempts = []
    completed_seeds = []
    accepted = None
    resume = ckpt.resume_state("rank") if ckpt else None
    if resume:
        attempts = list(resume.get("attempts") or [])
        completed_seeds = list(resume.get("completed_seeds") or [])
        resume_seed = int(resume["seed"])
    else:
        resume_seed = None
    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        if resume_seed is not None and seed in completed_seeds:
            continue
        u, x0 = deterministic_pair(F, n, seed)
        if resume_seed is not None and seed == resume_seed:
            seq = [F(int(s)) for s in resume["seq"]]
            x = _ckpt_ints_vec(F, resume["x"])
            start_step = int(resume["step"]) + 1
            resume_seed = None
        else:
            seq = []
            x = x0
            start_step = 0
        save_status({
            "phase": "matrix_free_schur_rank_seed",
            "seed": int(seed),
            "step": int(start_step),
            "sequence_length": int(sequence_length),
        })
        for step in range(start_step, sequence_length):
            seq.append(dot_product(u, x))
            if step + 1 < sequence_length:
                x = matvec(x)
            if args.progress_every and (step + 1) % args.progress_every == 0:
                save_status({
                    "phase": "matrix_free_schur_rank_seed",
                    "seed": int(seed),
                    "step": int(step + 1),
                    "sequence_tail_signed": [signed_lift(s, q) for s in seq[-5:]],
                })
            if ckpt and ckpt.due(step + 1):
                ckpt.save_progress("rank", seed, step, seq, x,
                                   completed_seeds, attempts)
            if args.max_steps and step + 1 >= args.max_steps:
                break

        degree, coeffs = berlekamp_massey(seq, F)
        bad = verify_connection(seq, coeffs, F)
        constant = coeffs[degree] if degree else F(0)
        row = {
            "seed": int(seed),
            "degree": int(degree),
            "sequence_length": int(len(seq)),
            "verification_suffix_terms": int(max(0, len(seq) - degree)),
            "constant_mod_q": int(constant),
            "constant_signed": signed_lift(constant, q),
            "constant_nonzero": bool(constant != 0),
            "connection_verified": len(bad) == 0,
            "verification_failures": bad,
            "connection_coefficients_mod_q": [int(x) for x in coeffs],
            "connection_coefficients_signed": [signed_lift(x, q) for x in coeffs],
            "sequence_head_signed": [signed_lift(x, q) for x in seq[: min(10, len(seq))]],
            "sequence_tail_signed": [signed_lift(x, q) for x in seq[-min(10, len(seq)):]],
        }
        attempts.append(row)
        completed_seeds.append(seed)
        save_status({
            "phase": "matrix_free_schur_rank_seed_finished",
            "seed": int(seed),
            "degree": int(degree),
            "constant_signed": signed_lift(constant, q),
            "connection_verified": len(bad) == 0,
        })
        if args.max_steps:
            break
        if degree == n and constant != 0 and not bad:
            accepted = row
            break
    if ckpt:
        ckpt.mark_stage("rank_done",
                        rank_result={"attempts": attempts, "accepted": accepted})
    return attempts, accepted


def vector_wiedemann_solve(F, q, n, matvec, rhs, args, save_status,
                           ckpt=None, rank_result=None):
    sequence_length = int(args.solve_sequence_length or args.sequence_length or (2 * n + args.suffix_terms))
    seed_start = int(args.solve_seed_start)
    seed_count = int(args.solve_seed_count or args.seed_count)
    attempts = []
    completed_seeds = []
    accepted = None
    resume_seq = ckpt.resume_state("solve") if ckpt else None
    resume_recon = ckpt.resume_state("solve_reconstruct") if ckpt else None
    resume = resume_seq or resume_recon
    if resume:
        attempts = list(resume.get("attempts") or [])
        completed_seeds = list(resume.get("completed_seeds") or [])
        resume_seed = int(resume["seed"])
    else:
        resume_seed = None
    for seed in range(seed_start, seed_start + seed_count):
        if resume_seed is not None and seed in completed_seeds:
            continue
        probe, _ = deterministic_pair(F, n, seed)
        recon_from = None
        if resume_seed is not None and seed == resume_seed:
            seq = [F(int(s)) for s in resume["seq"]]
            if resume_recon is not None:
                # Resume mid solution-reconstruction (seq is already complete).
                recon_from = resume_recon
            else:
                x = _ckpt_ints_vec(F, resume["x"])
                start_step = int(resume["step"]) + 1
            resume_seed = None
        else:
            seq = []
            x = vector(F, rhs)
            start_step = 0
        if recon_from is None:
            save_status({
                "phase": "matrix_free_schur_solve_seed",
                "seed": int(seed),
                "step": int(start_step),
                "sequence_length": int(sequence_length),
            })
            for step in range(start_step, sequence_length):
                seq.append(dot_product(probe, x))
                if step + 1 < sequence_length:
                    x = matvec(x)
                if args.progress_every and (step + 1) % args.progress_every == 0:
                    save_status({
                        "phase": "matrix_free_schur_solve_seed",
                        "seed": int(seed),
                        "step": int(step + 1),
                        "sequence_tail_signed": [signed_lift(s, q) for s in seq[-5:]],
                    })
                if ckpt and ckpt.due(step + 1):
                    ckpt.save_progress("solve", seed, step, seq, x,
                                       completed_seeds, attempts,
                                       rank_result=rank_result)
                if args.max_steps and step + 1 >= args.max_steps:
                    break

        degree, coeffs = berlekamp_massey(seq, F)
        bad = verify_connection(seq, coeffs, F)
        constant = coeffs[degree] if degree else F(0)
        row = {
            "seed": int(seed),
            "degree": int(degree),
            "sequence_length": int(len(seq)),
            "verification_suffix_terms": int(max(0, len(seq) - degree)),
            "constant_mod_q": int(constant),
            "constant_signed": signed_lift(constant, q),
            "constant_nonzero": bool(constant != 0),
            "connection_verified": len(bad) == 0,
            "verification_failures": bad,
        }
        if args.max_steps or degree <= 0 or constant == 0 or bad:
            attempts.append(row)
            completed_seeds.append(seed)
            if args.max_steps:
                break
            continue

        # Solution reconstruction (resumable: same matvec pattern as the
        # sequence loop, ~degree matvecs; checkpointed under stage
        # "solve_reconstruct" so a reboot on the accepting seed does not
        # discard it).
        if recon_from is not None:
            relation = _ckpt_ints_vec(F, recon_from["relation"])
            numerator = _ckpt_ints_vec(F, recon_from["numerator"])
            x = _ckpt_ints_vec(F, recon_from["x"])
            power_start = int(recon_from["step"]) + 1
        else:
            relation = vector(F, n)
            numerator = vector(F, n)
            x = vector(F, rhs)
            power_start = 0
        for power in range(power_start, degree + 1):
            if power == degree:
                rel_coeff = F(1)
            else:
                rel_coeff = coeffs[degree - power]
                numerator += coeffs[degree - 1 - power] * x
            relation += rel_coeff * x
            if power < degree:
                x = matvec(x)
            if ckpt and ckpt.due(power + 1):
                ckpt.save_progress(
                    "solve_reconstruct", seed, power, seq, x,
                    completed_seeds, attempts, rank_result=rank_result,
                    extra={
                        "relation": _ckpt_vec_ints(relation),
                        "numerator": _ckpt_vec_ints(numerator),
                    },
                )

        solution = -numerator / constant
        residual = matvec(solution) - rhs
        row.update({
            "vector_relation_zero": bool(relation == 0),
            "solve_residual_zero": bool(residual == 0),
            "relation_sha256": vector_sha256(relation),
            "residual_sha256": vector_sha256(residual),
            "solution_sha256": vector_sha256(solution),
            "connection_coefficients_mod_q": [int(x) for x in coeffs],
            "connection_coefficients_signed": [signed_lift(x, q) for x in coeffs],
        })
        attempts.append(row)
        completed_seeds.append(seed)
        save_status({
            "phase": "matrix_free_schur_solve_seed_finished",
            "seed": int(seed),
            "degree": int(degree),
            "constant_signed": signed_lift(constant, q),
            "vector_relation_zero": bool(relation == 0),
            "solve_residual_zero": bool(residual == 0),
        })
        if relation == 0 and residual == 0:
            accepted = row
            if ckpt:
                ckpt.mark_stage("solve_done", rank_result=rank_result)
            return solution, attempts, accepted
    if ckpt:
        ckpt.mark_stage("solve_done", rank_result=rank_result)
    return None, attempts, accepted


def run(args):
    t0 = time.time()
    case_dir = Path(args.case_dir)
    pi_json = Path(args.pi_json)
    manifest = read_manifest(case_dir)
    pi_data = load_json(pi_json)
    N = int(manifest["level"])
    q = int(manifest["q"])
    F = GF(q)
    status = {
        "tool": TOOL,
        "date": DATE,
        "pid": int(os.getpid()),
        "phase": "starting",
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "level": N,
        "mode": manifest.get("mode"),
        "q": q,
        "started_unix": t0,
    }

    def save_status(extra=None):
        if extra:
            status.update(extra)
        status["seconds"] = round(time.time() - t0, 3)
        write_json(args.status_json, status)

    estimated_source_dim = int(
        pi_data.get("hecke_rows")
        or pi_data.get("hecke_source_rows")
        or pi_data.get("projected_hecke_rank")
        or 0
    )
    if (
        args.certificate_mode == "matrix-free-schur"
        and not args.matrix_free_schur_preflight_only
        and not args.matrix_free_schur_allow_large
        and estimated_source_dim > int(args.matrix_free_schur_max_dim)
    ):
        payload = {
            "tool": TOOL,
            "date": DATE,
            "certificate_mode": args.certificate_mode,
            "status": "blocked_matrix_free_schur_large_run_guard",
            "faithful_al_certificate_found": False,
            "reason": (
                "Refusing a full matrix-free Schur run at this source dimension "
                "without --matrix-free-schur-allow-large. Use "
                "--matrix-free-schur-preflight-only first."
            ),
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
            "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
            "pi_json_sha256": file_sha256(pi_json),
            "operator_script_sha256": file_sha256(Path(__file__)),
            "level": N,
            "mode": manifest.get("mode"),
            "q": q,
            "estimated_source_dim": estimated_source_dim,
            "matrix_free_schur_max_dim": int(args.matrix_free_schur_max_dim),
            "operator_kind": "pari_tensor_solve_atkin_lehner_twist",
            "pairing_kind": "_pari_tensor_solve",
            "primary_pairing_materialized": False,
            "seconds": round(time.time() - t0, 3),
            "status_snapshot": status,
        }
        write_json(args.out_json, payload)
        write_md(payload, args.out_md)
        save_status({
            "phase": "finished",
            "status": payload.get("status"),
            "out_json": str(args.out_json),
        })
        return payload

    save_status()
    source_rows = build_t_projection(
        case_dir,
        pi_data,
        q,
        status,
        save_status,
        max(1, int(args.projection_progress_every)),
    )
    save_status()
    Fmat, sage_dim = build_free_to_sage(case_dir, pi_data, manifest, F, status, args.module_base_ring)
    save_status()
    P, E, WF, bal_apply_kind = build_bal_factors(
        N,
        q,
        F,
        status,
        save_status,
        args.bal_mode,
        cache_dir=args.bal_cache_dir,
        cache_read=args.bal_cache_read,
        cache_write=args.bal_cache_write,
        cache_overwrite=args.bal_cache_overwrite,
        stop_after_plus_cache=args.bal_stop_after_plus_cache,
        pari_stack_mb=args.pari_stack_mb,
    )
    save_status()

    n = int(len(source_rows))
    d = int(len(pi_data["free_columns"]))
    if bal_apply_kind == "plus-cache-only":
        payload = {
            "tool": TOOL,
            "date": DATE,
            "certificate_mode": args.certificate_mode,
            "status": "preflight_plus_basis_cached",
            "faithful_al_certificate_found": False,
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
            "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
            "pi_json_sha256": file_sha256(pi_json),
            "operator_script_sha256": file_sha256(Path(__file__)),
            "level": N,
            "mode": manifest.get("mode"),
            "q": q,
            "module_base_ring": args.module_base_ring,
            "bal_mode": args.bal_mode,
            "bal_apply_kind": bal_apply_kind,
            "operator_kind": "pari_tensor_solve_atkin_lehner_twist",
            "pairing_kind": status.get("pairing_kind"),
            "primary_pairing_materialized": status.get("primary_pairing_materialized"),
            "source_dim": n,
            "target_rank": n,
            "quotient_dim": d,
            "sage_dim": int(sage_dim),
            "operator_factor_metadata": {
                "sign0_dim": status.get("sign0_dim"),
                "plus_dim": status.get("plus_dim"),
                "P_nnz": status.get("P_nnz"),
                "P_sha256": status.get("P_sha256"),
                "T_nnz": None,
                "W_nnz": None,
                "bal_cache": status.get("bal_cache"),
            },
            "input_hashes": {
                "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
                "pi_json_sha256": file_sha256(pi_json),
                "operator_script_sha256": file_sha256(Path(__file__)),
            },
            "transcript_metadata": {
                "scope": "plus_basis_cache_preflight_no_tensor_no_wiedemann",
                "operator_logic": "P_cached_then_stop_before_pari_tensor_W_bal_apply_A_matvec",
                "preflight_aborted_before_tensor": True,
                "preflight_aborted_before_wiedemann": True,
            },
            "seconds": round(time.time() - t0, 3),
            "status_snapshot": status,
        }
        write_json(args.out_json, payload)
        write_md(payload, args.out_md)
        save_status({
            "phase": "finished",
            "status": payload.get("status"),
            "out_json": str(args.out_json),
        })
        return payload

    Cq = sparse_matrix_from_row_dicts(F, n, d, source_rows)
    save_status({
        "phase": "built_C_source",
        "target_rank": n,
        "quotient_dim": d,
        "C_source_nnz": int(len(Cq.dict())),
    })

    def bal_apply(x):
        if P is None:
            return E * (WF * x)
        if bal_apply_kind == "tensor-solve":
            rhs = WF * (P.transpose() * x)
            return P * E.solve_right(rhs)
        return P * (E * (WF * (P.transpose() * x)))

    def matvec(v):
        tmp = Cq.transpose() * v
        u = Fmat.transpose() * tmp
        w = bal_apply(u)
        z = Fmat * w
        return Cq * z

    def quotient_bal_apply(qvec):
        u = Fmat.transpose() * qvec
        w = bal_apply(u)
        return Fmat * w

    if args.certificate_mode == "matrix-free-schur":
        if bal_apply_kind != "tensor-solve":
            raise ValueError("matrix-free-schur requires --bal-mode sign0-tensor-solve")

        repair_entries, repair_source = get_repair_entries(pi_data)
        repair_q = quotient_vector_from_entries(F, d, repair_entries)
        beta, beta_source = beta_from_pi_or_entries(F, pi_data, q, repair_entries)

        save_status({
            "phase": "matrix_free_schur_building_b_c",
            "repair_source": repair_source,
            "repair_nnz": int(len(repair_q.dict())),
            "beta_source": beta_source,
            "beta_signed": signed_lift(beta, q),
        })
        repair_image = quotient_bal_apply(repair_q)
        b_col = Cq * repair_image
        c_scalar = dot_product(repair_q, repair_image)

        _, preflight_vec = deterministic_pair(F, n, args.seed_start)
        preflight_matvec = matvec(preflight_vec)
        preflight_dot = dot_product(preflight_vec, preflight_matvec)

        preflight = {
            "bal_apply_repair_image_sha256": vector_sha256(repair_image),
            "b_col_sha256": vector_sha256(b_col),
            "b_col_nnz": int(len(b_col.dict())),
            "c_mod_q": int(c_scalar),
            "c_signed": signed_lift(c_scalar, q),
            "deterministic_matvec_seed": int(args.seed_start),
            "deterministic_matvec_sha256": vector_sha256(preflight_matvec),
            "deterministic_quadratic_mod_q": int(preflight_dot),
            "deterministic_quadratic_signed": signed_lift(preflight_dot, q),
        }

        if args.matrix_free_schur_preflight_only:
            payload = {
                "tool": TOOL,
                "date": DATE,
                "certificate_mode": args.certificate_mode,
                "status": "preflight_matrix_free_schur_ready",
                "faithful_al_certificate_found": False,
                "case_dir": str(case_dir),
                "pi_json": str(pi_json),
                "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
                "pi_json_sha256": file_sha256(pi_json),
                "operator_script_sha256": file_sha256(Path(__file__)),
                "level": N,
                "mode": manifest.get("mode"),
                "q": q,
                "module_base_ring": args.module_base_ring,
                "bal_mode": args.bal_mode,
                "bal_apply_kind": bal_apply_kind,
                "operator_kind": "pari_tensor_solve_atkin_lehner_twist",
                "pairing_kind": status.get("pairing_kind"),
                "primary_pairing_materialized": status.get("primary_pairing_materialized"),
                "source_dim": n,
                "target_rank": n,
                "quotient_dim": d,
                "sage_dim": int(sage_dim),
                "repair_source": repair_source,
                "beta_mod_q": int(beta),
                "beta_signed": signed_lift(beta, q),
                "beta_source": beta_source,
                "preflight": preflight,
                "operator_factor_metadata": {
                    "sign0_dim": status.get("sign0_dim"),
                    "plus_dim": status.get("plus_dim"),
                    "P_nnz": status.get("P_nnz"),
                    "T_nnz": status.get("T_nnz"),
                    "W_nnz": status.get("W_nnz"),
                    "P_sha256": status.get("P_sha256"),
                    "T_sha256": status.get("pairing_tensor_or_E_sha256"),
                    "W_sha256": status.get("W_sha256"),
                },
                "input_hashes": {
                    "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                    "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
                    "pi_json_sha256": file_sha256(pi_json),
                    "operator_script_sha256": file_sha256(Path(__file__)),
                    "C_source_sha256": matrix_sha256(Cq),
                    "repair_q_sha256": vector_sha256(repair_q),
                },
                "transcript_metadata": {
                    "scope": "matrix_free_schur_preflight_no_wiedemann_sequence",
                    "operator_logic": "Cq_Fmat_P_solve_pari_tensor_W_Pt_FmatT_CqT",
                    "matvec_checkpoints": [],
                    "preflight_aborted_before_wiedemann": True,
                },
                "seconds": round(time.time() - t0, 3),
                "status_snapshot": status,
            }
            write_json(args.out_json, payload)
            write_md(payload, args.out_md)
            save_status({
                "phase": "finished",
                "status": payload.get("status"),
                "out_json": str(args.out_json),
            })
            return payload

        ckpt_path = args.resume_from
        ckpt_every = args.checkpoint_every or (1000 if args.resume_from else 0)
        if ckpt_path:
            ckpt = Checkpointer(
                ckpt_path,
                {
                    "q": int(q),
                    "target_rank": int(n),
                    "case_dir": str(case_dir),
                    "pi_json": str(pi_json),
                    "P_sha256": status.get("P_sha256"),
                    "T_sha256": status.get("pairing_tensor_or_E_sha256"),
                    "W_sha256": status.get("W_sha256"),
                },
                ckpt_every,
                args.checkpoint_min_seconds,
            )
        else:
            ckpt = None
        resumed_rank = ckpt.rank_result() if ckpt else None
        if resumed_rank is not None:
            rank_attempts, rank_cert = resumed_rank
        else:
            rank_attempts, rank_cert = scalar_wiedemann_rank_certificate(
                F, q, n, matvec, args, save_status, ckpt=ckpt)
        solution, solve_attempts, solve_cert = vector_wiedemann_solve(
            F, q, n, matvec, b_col, args, save_status, ckpt=ckpt,
            rank_result={"attempts": rank_attempts, "accepted": rank_cert})
        if solution is not None:
            source_combo = Cq.transpose() * solution
            source_combo_image = quotient_bal_apply(source_combo)
            d_x = dot_product(repair_q, source_combo_image)
            schur = c_scalar - d_x
        else:
            d_x = F(0)
            schur = F(0)
        q_b_from_schur = (beta * beta) / schur if schur != 0 else F(0)

        rank_full = bool(rank_cert is not None)
        solve_ok = bool(solve_cert is not None)
        schur_nonzero = bool(schur != 0)
        faithful_found = bool(rank_full and solve_ok and schur_nonzero)
        payload = {
            "tool": TOOL,
            "date": DATE,
            "certificate_mode": args.certificate_mode,
            "status": "computed" if not args.max_steps else "partial_max_steps",
            "faithful_al_certificate_found": faithful_found,
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
            "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
            "pi_json_sha256": file_sha256(pi_json),
            "operator_script_sha256": file_sha256(Path(__file__)),
            "level": N,
            "mode": manifest.get("mode"),
            "q": q,
            "module_base_ring": args.module_base_ring,
            "bal_mode": args.bal_mode,
            "bal_apply_kind": bal_apply_kind,
            "operator_kind": "pari_tensor_solve_atkin_lehner_twist",
            "pairing_kind": status.get("pairing_kind"),
            "primary_pairing_materialized": status.get("primary_pairing_materialized"),
            "source_dim": n,
            "target_rank": n,
            "quotient_dim": d,
            "sage_dim": int(sage_dim),
            "rank_A": n if rank_full else (rank_cert or {}).get("degree"),
            "rank_A_target": n,
            "rank_A_full": rank_full,
            "rank_certificate": rank_cert,
            "rank_attempts": rank_attempts,
            "solve_certificate": solve_cert,
            "solve_attempts": solve_attempts,
            "repair_source": repair_source,
            "beta_mod_q": int(beta),
            "beta_signed": signed_lift(beta, q),
            "beta_source": beta_source,
            "b_col_sha256": vector_sha256(b_col),
            "c_mod_q": int(c_scalar),
            "c_signed": signed_lift(c_scalar, q),
            "d_x_mod_q": int(d_x),
            "d_x_signed": signed_lift(d_x, q),
            "schur_scalar_mod_q": int(schur),
            "schur_scalar_signed": signed_lift(schur, q),
            "schur_nonzero": schur_nonzero,
            "q_b_from_schur_mod_q": int(q_b_from_schur),
            "q_b_from_schur_signed": signed_lift(q_b_from_schur, q),
            "qb3_schur_signed": signed_lift(q_b_from_schur, q),
            "direct_matches_schur": None,
            "preflight": preflight,
            "operator_factor_metadata": {
                "sign0_dim": status.get("sign0_dim"),
                "plus_dim": status.get("plus_dim"),
                "P_nnz": status.get("P_nnz"),
                "T_nnz": status.get("T_nnz"),
                "W_nnz": status.get("W_nnz"),
                "P_sha256": status.get("P_sha256"),
                "T_sha256": status.get("pairing_tensor_or_E_sha256"),
                "W_sha256": status.get("W_sha256"),
            },
            "input_hashes": {
                "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
                "pi_json_sha256": file_sha256(pi_json),
                "operator_script_sha256": file_sha256(Path(__file__)),
                "C_source_sha256": matrix_sha256(Cq),
                "repair_q_sha256": vector_sha256(repair_q),
            },
            "transcript_metadata": {
                "scope": "matrix_free_schur_blackbox_no_dense_G",
                "operator_logic": "Cq_Fmat_P_solve_pari_tensor_W_Pt_FmatT_CqT",
                "rank_seed_start": int(args.seed_start),
                "rank_seed_count": int(args.seed_count),
                "solve_seed_start": int(args.solve_seed_start),
                "solve_seed_count": int(args.solve_seed_count or args.seed_count),
                "suffix_terms": int(args.suffix_terms),
                "matvec_checkpoints": [],
            },
            "seconds": round(time.time() - t0, 3),
            "status_snapshot": status,
        }
        write_json(args.out_json, payload)
        write_md(payload, args.out_md)
        save_status({
            "phase": "finished",
            "status": payload.get("status"),
            "faithful_al_certificate_found": faithful_found,
            "rank_A_full": rank_full,
            "schur_nonzero": schur_nonzero,
            "out_json": str(args.out_json),
        })
        return payload

    attempts = []
    accepted = None
    sequence_length = int(args.sequence_length or (2 * n + args.suffix_terms))
    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        u, x = deterministic_pair(F, n, seed)
        seq = []
        save_status({
            "phase": "running_seed",
            "seed": int(seed),
            "step": 0,
            "sequence_length": sequence_length,
        })
        for step in range(sequence_length):
            seq.append(sum(u[i] * x[i] for i in range(n)))
            if step + 1 < sequence_length:
                x = matvec(x)
            if args.progress_every and (step + 1) % args.progress_every == 0:
                save_status({
                    "phase": "running_seed",
                    "seed": int(seed),
                    "step": int(step + 1),
                    "sequence_tail_signed": [signed_lift(s, q) for s in seq[-5:]],
                })
            if args.max_steps and step + 1 >= args.max_steps:
                break

        degree, coeffs = berlekamp_massey(seq, F)
        bad = verify_connection(seq, coeffs, F)
        constant = coeffs[degree] if degree else F(0)
        row = {
            "seed": int(seed),
            "degree": int(degree),
            "sequence_length": int(len(seq)),
            "verification_suffix_terms": int(max(0, len(seq) - degree)),
            "constant_mod_q": int(constant),
            "constant_signed": signed_lift(constant, q),
            "constant_nonzero": bool(constant != 0),
            "connection_verified": len(bad) == 0,
            "verification_failures": bad,
            "connection_coefficients_mod_q": [int(x) for x in coeffs],
            "connection_coefficients_signed": [signed_lift(x, q) for x in coeffs],
            "sequence_mod_q": [int(x) for x in seq],
            "sequence_head_signed": [signed_lift(x, q) for x in seq[: min(10, len(seq))]],
        }
        attempts.append(row)
        save_status({
            "phase": "seed_finished",
            "seed": int(seed),
            "degree": int(degree),
            "constant_signed": signed_lift(constant, q),
            "connection_verified": len(bad) == 0,
        })
        if args.max_steps:
            break
        if degree == n and constant != 0 and not bad:
            accepted = row
            break

    payload = {
        "tool": TOOL,
        "date": DATE,
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
        "case_rows_sha256": file_sha256(case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))),
        "pi_json_sha256": file_sha256(pi_json),
        "operator_script_sha256": file_sha256(Path(__file__)),
        "level": N,
        "mode": manifest.get("mode"),
        "q": q,
        "module_base_ring": args.module_base_ring,
        "bal_mode": args.bal_mode,
        "bal_apply_kind": bal_apply_kind,
        "pairing_kind": status.get("pairing_kind"),
        "primary_pairing_materialized": status.get("primary_pairing_materialized"),
        "status": "computed" if not args.max_steps else "partial_max_steps",
        "target_rank": n,
        "quotient_dim": d,
        "sequence_length_target": sequence_length,
        "accepted_certificate_found": accepted is not None,
        "accepted_certificate": accepted,
        "attempts": attempts,
        "seconds": round(time.time() - t0, 3),
        "status_snapshot": status,
    }
    write_json(args.out_json, payload)
    write_md(payload, args.out_md)
    save_status({
        "phase": "finished",
        "accepted_certificate_found": accepted is not None,
        "out_json": str(args.out_json),
    })
    return payload


def write_md(payload, out_md):
    if payload.get("certificate_mode") == "matrix-free-schur":
        lines = [
            "# H3a Q_B-3 Matrix-Free Schur Certificate",
            "",
            f"Level: `{payload.get('level')}`",
            f"Mode: `{payload.get('mode')}`",
            f"Status: `{payload.get('status')}`",
            "",
            "```text",
            f"operator kind:               {payload.get('operator_kind')}",
            f"pairing kind:                {payload.get('pairing_kind')}",
            f"primary pairing materialized:{payload.get('primary_pairing_materialized')}",
            f"target rank:                 {payload.get('target_rank')}",
            f"quotient dim:                {payload.get('quotient_dim')}",
            f"rank(A):                     {payload.get('rank_A')} / {payload.get('rank_A_target')}",
            f"rank(A) full:                {payload.get('rank_A_full')}",
            f"s_N signed:                  {payload.get('schur_scalar_signed')}",
            f"s_N nonzero:                 {payload.get('schur_nonzero')}",
            f"Q_B(schur) signed:           {payload.get('q_b_from_schur_signed')}",
            f"faithful AL found:           {payload.get('faithful_al_certificate_found')}",
            f"seconds:                     {payload.get('seconds')}",
            "```",
            "",
            "The JSON contains the scalar rank certificate, the vector",
            "Wiedemann solve certificate, input hashes, and status snapshot.",
            "",
        ]
        Path(out_md).write_text("\n".join(lines), encoding="utf-8")
        return

    cert = payload.get("accepted_certificate") or {}
    lines = [
        "# H3a Q_B-3 Wiedemann Production",
        "",
        f"Level: `{payload.get('level')}`",
        f"Mode: `{payload.get('mode')}`",
        f"Status: `{payload.get('status')}`",
        "",
        "```text",
        f"target rank:                 {payload.get('target_rank')}",
        f"quotient dim:                {payload.get('quotient_dim')}",
        f"sequence length target:      {payload.get('sequence_length_target')}",
        f"accepted certificate found:  {payload.get('accepted_certificate_found')}",
        f"accepted seed:               {cert.get('seed')}",
        f"degree:                      {cert.get('degree')}",
        f"constant signed:             {cert.get('constant_signed')}",
        f"seconds:                     {payload.get('seconds')}",
        "```",
        "",
        "The JSON contains the full scalar sequence and recurrence coefficients",
        "for independent verification.",
        "",
    ]
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--pi-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--status-json", required=True)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--seed-count", type=int, default=16)
    parser.add_argument("--suffix-terms", type=int, default=4)
    parser.add_argument("--sequence-length", type=int)
    parser.add_argument("--solve-seed-start", type=int, default=1001)
    parser.add_argument("--solve-seed-count", type=int, default=0)
    parser.add_argument("--solve-sequence-length", type=int)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--projection-progress-every", type=int, default=1000)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument(
        "--certificate-mode",
        choices=["scalar-wiedemann", "matrix-free-schur"],
        default="scalar-wiedemann",
        help=(
            "scalar-wiedemann keeps the historical rank/minpoly production "
            "run. matrix-free-schur computes rank(A), b, c, a blackbox solve "
            "A*x=b, and s_N=c-d*x without materializing G=C B_AL C^T."
        ),
    )
    parser.add_argument(
        "--matrix-free-schur-preflight-only",
        action="store_true",
        help=(
            "For large levels, build projection, free-to-Sage bridge, P, "
            "_pari_tensor, W, b/c, and one deterministic A_matvec, then stop "
            "before Wiedemann sequences."
        ),
    )
    parser.add_argument(
        "--matrix-free-schur-max-dim",
        type=int,
        default=256,
        help=(
            "Guard for full matrix-free Schur runs unless "
            "--matrix-free-schur-allow-large is set. Preflight-only bypasses "
            "this guard."
        ),
    )
    parser.add_argument(
        "--matrix-free-schur-allow-large",
        action="store_true",
        help="Allow a full matrix-free Schur Wiedemann run above the max-dim guard.",
    )
    parser.add_argument(
        "--module-base-ring",
        choices=["finite", "rational"],
        default="finite",
        help="Base ring for the sign=1 Sage bridge. Default finite avoids QQ kernel work.",
    )
    parser.add_argument(
        "--bal-mode",
        choices=["sign0-finite", "sign0-rational", "sign0-tensor-solve", "sign1-direct"],
        default="sign0-finite",
        help=(
            "How to build B_AL. Default sign0-finite keeps the ambient "
            "AL-twisted pairing over F_q. sign0-tensor-solve applies "
            "P * solve(_pari_tensor, W * P^T * x) and avoids materializing "
            "M0._pari_pairing(). sign0-rational is legacy/unsafe for large "
            "levels. sign1-direct is a diagnostic and usually fails because "
            "the sign=1 pairing is degenerate."
        ),
    )
    parser.add_argument(
        "--bal-cache-dir",
        default="",
        help=(
            "Optional directory for Sage .sobj caches of the sign0 plus basis, "
            "_pari_tensor/_pari_pairing, and Atkin-Lehner W. Relative paths are "
            "resolved from the current working directory."
        ),
    )
    parser.add_argument(
        "--bal-cache-read",
        action="store_true",
        help="Load B_AL factors from --bal-cache-dir when present.",
    )
    parser.add_argument(
        "--bal-cache-write",
        action="store_true",
        help="Write B_AL factors to --bal-cache-dir immediately after construction.",
    )
    parser.add_argument(
        "--bal-cache-overwrite",
        action="store_true",
        help="Overwrite existing B_AL cache files instead of leaving them intact.",
    )
    parser.add_argument(
        "--bal-stop-after-plus-cache",
        action="store_true",
        help=(
            "Stop after the sign0 plus-basis P has been loaded or constructed "
            "and, if requested, cached. This deliberately avoids _pari_tensor, "
            "Atkin-Lehner W, bal_apply, A_matvec, and Wiedemann sequences."
        ),
    )
    parser.add_argument(
        "--pari-stack-mb",
        type=int,
        default=0,
        help=(
            "If positive, allocate this many MiB of PARI stack immediately "
            "before constructing _pari_tensor/_pari_pairing. This is intended "
            "for Mac-only large-level preflights; default leaves Sage/PARI's "
            "stack unchanged."
        ),
    )
    parser.add_argument(
        "--resume-from",
        default=None,
        help=(
            "Path to a checkpoint.json for the rank/solve Wiedemann sequences "
            "(Regel 2, compute_queue). If the file exists, resume from it; "
            "otherwise this path is the checkpoint write target. Giving this "
            "flag enables checkpointing (default --checkpoint-every 1000)."
        ),
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=0,
        help=(
            "Write a Wiedemann checkpoint every N sequence steps (0 = disabled "
            "unless --resume-from is given, which implies 1000). Combined with "
            "--checkpoint-min-seconds."
        ),
    )
    parser.add_argument(
        "--checkpoint-min-seconds",
        type=int,
        default=1800,
        help=(
            "Also write a checkpoint if this many seconds elapsed since the "
            "last one, independent of step count (Regel 2: ~30 min)."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    payload = run(args)
    print(json.dumps({
        "status": payload.get("status"),
        "accepted_certificate_found": payload.get("accepted_certificate_found"),
        "faithful_al_certificate_found": payload.get("faithful_al_certificate_found"),
        "certificate_mode": payload.get("certificate_mode"),
        "target_rank": payload.get("target_rank"),
        "rank_A": payload.get("rank_A"),
        "schur_nonzero": payload.get("schur_nonzero"),
        "seconds": payload.get("seconds"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
