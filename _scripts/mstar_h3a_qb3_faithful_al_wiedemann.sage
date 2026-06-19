#!/usr/bin/env sage
# Faithful-AL Schur certificate driver for R1.
#
# This script deliberately separates three cases:
# - small/dense smoke: compute the genuine PARI pairing, apply the
#   Atkin-Lehner twist, and verify the Schur certificate directly;
# - small/tensor-solve smoke: apply the same operator as
#   P * solve(_pari_tensor, W * P^T * x), avoiding _pari_pairing();
# - large levels: refuse naive dense Gram/Schur construction until a
#   matrix-free Schur/Wiedemann solver is wired on top of the operator.

import argparse
import hashlib
import json
import time
from pathlib import Path

from sage.all import GF, Gamma0, ModularSymbols, matrix, vector
from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
from sage.modular.modsym.relation_matrix import (
    modI_relations,
    modS_relations,
    sparse_2term_quotient,
)


TOOL = "mstar_h3a_qb3_faithful_al_wiedemann"
DATE = "2026-06-14"
OPERATOR_KIND_DENSE = "pari_pairing_atkin_lehner_twist"
OPERATOR_KIND_TENSOR_SOLVE = "pari_tensor_solve_atkin_lehner_twist"
OPERATOR_KIND = OPERATOR_KIND_DENSE


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def file_sha256(path):
    path = Path(path)
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
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


def signed_lift(value, q):
    v = int(value) % q
    if v > q // 2:
        v -= q
    return int(v)


def sparse_change_ring(M, F):
    out = matrix(F, M.nrows(), M.ncols(), sparse=True)
    for (i, j), value in M.dict().items():
        out[int(i), int(j)] = F(value)
    return out


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


def dict_row_to_pairs(row):
    return [[int(c), int(row[c])] for c in sorted(row)]


def build_t_projected_hecke_rows(case_dir, pi_data, q):
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

    ncols = int(read_manifest(case_dir)["ncols"])
    free_columns = [int(c) for c in pi_data["free_columns"]]
    free_col_to_qcol = {c: i for i, c in enumerate(free_columns)}
    computed_free = [c for c in range(ncols) if c not in t_basis.basis]
    if computed_free != free_columns:
        raise ValueError("computed T-quotient free columns differ from pi-json")

    projected_rows = []
    nnz = 0
    max_len = 0
    for row in hecke_records:
        reduced = t_basis.reduce_dict(sparse_pairs_to_dict(row["row"], q))
        projected = {}
        for col, value in reduced.items():
            if col not in free_col_to_qcol:
                raise RuntimeError("pivot column survived T reduction: %s" % col)
            projected[free_col_to_qcol[col]] = int(value) % q
        projected_rows.append(dict_row_to_pairs(projected))
        nnz += len(projected)
        max_len = max(max_len, len(projected))

    return {
        "rows": projected_rows,
        "t_rows": int(t_rows),
        "t_rank": int(t_basis.rank),
        "hecke_rows": int(len(projected_rows)),
        "rows_scanned": int(rows_scanned),
        "source_nnz": int(nnz),
        "source_max_row_len": int(max_len),
    }


def get_projected_hecke_rows(case_dir, pi_data, q):
    rows = pi_data.get("projected_hecke_rows_mod_q")
    if rows is not None:
        return rows, {
            "source": "pi_json.projected_hecke_rows_mod_q",
            "hecke_rows": int(len(rows)),
        }
    built = build_t_projected_hecke_rows(case_dir, pi_data, q)
    meta = dict(built)
    del meta["rows"]
    meta["source"] = "rebuilt_from_case_rows"
    return built["rows"], meta


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


def make_free_to_sage(case_dir, pi_data, manifest):
    N = int(manifest["level"])
    q = int(manifest["q"])
    sign = int(manifest.get("sign", 1))
    ncols = int(manifest["ncols"])
    free_columns = [int(c) for c in pi_data["free_columns"]]
    F = GF(q)

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

    M = ModularSymbols(Gamma0(N), 2, sign=sign)
    sage_dim = int(M.dimension())
    gens_to_basis = M.manin_gens_to_basis()

    col_to_sage = [None for _ in range(ncols)]
    consistency_errors = []
    for j, mapped in enumerate(mod_map):
        if mapped is None:
            continue
        col, scalar = mapped
        if col >= ncols:
            continue
        row = gens_to_basis.row(j)
        vec = vector(F, [F(x) for x in row]) / scalar
        if col_to_sage[col] is None:
            col_to_sage[col] = vec
        elif col_to_sage[col] != vec:
            consistency_errors.append({"col": int(col), "manin_index": int(j)})

    missing_columns = [int(c) for c, v in enumerate(col_to_sage) if v is None]
    free_to_sage_rows = [list(col_to_sage[col]) for col in free_columns]
    free_to_sage = matrix(F, free_to_sage_rows)

    def quotient_row_to_sage(entries):
        total = vector(F, sage_dim)
        for qcol, value in entries:
            total += F(int(value)) * vector(F, free_to_sage_rows[int(qcol)])
        return total

    return {
        "field": F,
        "N": N,
        "q": q,
        "sign": sign,
        "sage_dim": sage_dim,
        "free_columns": free_columns,
        "free_to_sage": free_to_sage,
        "free_to_sage_rank": int(free_to_sage.rank()),
        "free_to_sage_isomorphism": int(free_to_sage.rank()) == sage_dim == len(free_columns),
        "missing_columns": missing_columns,
        "consistency_errors": consistency_errors,
        "quotient_row_to_sage": quotient_row_to_sage,
    }


def build_gram_from_apply(F, C, bal_apply):
    applied_rows = []
    for j in range(C.nrows()):
        applied_rows.append(bal_apply(C.row(j)))
    return C * matrix(F, applied_rows).transpose()


def build_dense_bal(N, F):
    M0 = ModularSymbols(Gamma0(N), 2, sign=0)
    P = M0.plus_submodule().basis_matrix()
    E = M0._pari_pairing()
    W = M0.atkin_lehner_operator(N)
    try:
        Wm = W.matrix()
    except Exception:
        Wm = W

    EF = matrix(F, E.nrows(), E.ncols(), E.list())
    PF = matrix(F, P.nrows(), P.ncols(), P.list())
    WF = matrix(F, Wm.nrows(), Wm.ncols(), Wm.list())
    return PF * EF * WF * PF.transpose(), {
        "sign0_dim": int(M0.dimension()),
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(PF.dict())),
        "E_nnz": int(len(EF.dict())),
        "W_nnz": int(len(WF.dict())),
    }


def build_tensor_solve_bal_apply(N, F):
    M0 = ModularSymbols(Gamma0(N), 2, sign=0, base_ring=F)
    P = sparse_change_ring(M0.plus_submodule().basis_matrix(), F)
    T = sparse_change_ring(M0._pari_tensor(), F)
    W = M0.atkin_lehner_operator(N)
    try:
        Wm = W.matrix()
    except Exception:
        Wm = W
    WF = sparse_change_ring(Wm, F)

    def bal_apply(x):
        rhs = WF * (P.transpose() * x)
        solved = T.solve_right(rhs)
        return P * solved

    meta = {
        "sign0_dim": int(M0.dimension()),
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(P.dict())),
        "T_nnz": int(len(T.dict())),
        "W_nnz": int(len(WF.dict())),
        "P_sha256": matrix_sha256(P),
        "T_sha256": matrix_sha256(T),
        "W_sha256": matrix_sha256(WF),
    }
    return bal_apply, meta


def dense_comparison_enabled(mode, dense_comparison, free_dim, max_dense_dim):
    if dense_comparison == "on":
        return True
    if dense_comparison == "off":
        return False
    return mode == "tensor-solve" and free_dim <= max_dense_dim


def compute_dense(
    case_dir,
    pi_json,
    status_json,
    max_dense_dim,
    q_override=None,
    operator_mode="tensor-solve",
    dense_comparison="auto",
    max_tensor_gram_dim=256,
):
    t0 = time.time()
    case_dir = Path(case_dir)
    pi_json = Path(pi_json)
    manifest = read_manifest(case_dir)
    pi_data = load_json(pi_json)
    N = int(manifest["level"])
    q = int(manifest["q"])
    if q_override is not None and int(q_override) != q:
        raise ValueError("q override %s differs from manifest q %s" % (q_override, q))

    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    free_dim = len(pi_data.get("free_columns", []))
    operator_mode = str(operator_mode)
    if operator_mode not in ("dense", "tensor-solve"):
        raise ValueError("unknown operator mode: %s" % operator_mode)

    if operator_mode == "dense" and free_dim > max_dense_dim:
        return {
            "tool": TOOL,
            "date": DATE,
            "status": "blocked_matrix_free_faithful_al_required",
            "faithful_al_certificate_found": False,
            "reason": (
                "Quotient dimension exceeds dense guard. Refusing to fall back "
                "to identity-pairing; use the tensor-solve faithful-AL operator "
                "and a matrix-free Schur/Wiedemann solver for this level."
            ),
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "level": N,
            "N": N,
            "q": q,
            "quotient_dim_from_free_columns": free_dim,
            "max_dense_dim": int(max_dense_dim),
            "operator_mode": operator_mode,
            "operator_kind": "not_constructed",
            "operator_is_identity": False,
            "operator_kind_not_identity": True,
            "input_hashes": {
                "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                "case_rows_sha256": file_sha256(rows_path),
                "pi_json_sha256": file_sha256(pi_json),
                "operator_script_sha256": file_sha256(Path(__file__)),
            },
            "transcript": {
                "scope": "guard_only_no_matvec",
                "checkpoint_stride": 0,
                "matvec_checkpoints": [],
            },
            "transcript_metadata": {
                "scope": "guard_only_no_matvec",
                "checkpoint_stride": 0,
                "matvec_checkpoints": [],
                "operator_logic": "faithful_al_required_identity_fallback_refused",
            },
            "seconds": round(time.time() - t0, 3),
        }

    if operator_mode == "tensor-solve" and free_dim > max_tensor_gram_dim:
        return {
            "tool": TOOL,
            "date": DATE,
            "status": "blocked_matrix_free_schur_solver_required",
            "faithful_al_certificate_found": False,
            "reason": (
                "The faithful-AL operator is implemented as a tensor solve and "
                "does not call M0._pari_pairing(), but this driver still refuses "
                "to build the full source+repair Gram matrix at this dimension. "
                "Wire the tensor-solve apply into a matrix-free Schur/Wiedemann "
                "solver before queuing the large certificate."
            ),
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "level": N,
            "N": N,
            "q": q,
            "quotient_dim_from_free_columns": free_dim,
            "max_tensor_gram_dim": int(max_tensor_gram_dim),
            "operator_mode": operator_mode,
            "operator_kind": OPERATOR_KIND_TENSOR_SOLVE,
            "operator_is_identity": False,
            "operator_kind_not_identity": True,
            "pairing_kind": "_pari_tensor_solve",
            "primary_pairing_materialized": False,
            "input_hashes": {
                "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
                "case_rows_sha256": file_sha256(rows_path),
                "pi_json_sha256": file_sha256(pi_json),
                "operator_script_sha256": file_sha256(Path(__file__)),
            },
            "transcript": {
                "scope": "large_guard_tensor_solve_operator_available_no_gram",
                "checkpoint_stride": 0,
                "matvec_checkpoints": [],
            },
            "transcript_metadata": {
                "scope": "large_guard_tensor_solve_operator_available_no_gram",
                "checkpoint_stride": 0,
                "matvec_checkpoints": [],
                "operator_logic": "P_solve_pari_tensor_W_Pt_no_pari_pairing",
                "large_next_step": "matrix_free_schur_or_wiedemann_solver",
            },
            "seconds": round(time.time() - t0, 3),
        }

    bridge = make_free_to_sage(case_dir, pi_data, manifest)
    if not bridge["free_to_sage_isomorphism"]:
        raise ValueError("free quotient is not identified with Sage basis")
    F = bridge["field"]
    sage_dim = bridge["sage_dim"]
    quotient_row_to_sage = bridge["quotient_row_to_sage"]

    projected_hecke_rows, projected_rows_meta = get_projected_hecke_rows(case_dir, pi_data, q)
    hecke_sage_rows = [quotient_row_to_sage(entries) for entries in projected_hecke_rows]
    repair_entries, repair_source = get_repair_entries(pi_data)
    repair_sage = quotient_row_to_sage(repair_entries)

    phi_entries, phi_source = get_phi_entries(pi_data)
    phi_free = vector(F, len(bridge["free_columns"]))
    for qcol, value in phi_entries:
        phi_free[int(qcol)] = F(int(value))
    phi_sage = phi_free * bridge["free_to_sage"].transpose().inverse()

    source_repair_rows = hecke_sage_rows + [repair_sage]
    C = matrix(F, source_repair_rows)

    compare_dense = dense_comparison_enabled(
        operator_mode,
        dense_comparison,
        free_dim,
        max_dense_dim,
    )
    Bal = None
    dense_factor_meta = None
    operator_factor_meta = None
    tensor_solve_matches_dense = None
    G_dense_sha256 = None

    if operator_mode == "dense":
        if status_json:
            write_json(status_json, {
                "phase": "building_faithful_al_dense_operator",
                "level": N,
                "q": q,
                "sage_dim": int(sage_dim),
                "operator_kind": OPERATOR_KIND_DENSE,
                "seconds": round(time.time() - t0, 3),
            })
        Bal, dense_factor_meta = build_dense_bal(N, F)
        G = C * Bal * C.transpose()
        operator_kind = OPERATOR_KIND_DENSE
        pairing_kind = "_pari_pairing"
        primary_pairing_materialized = True
    else:
        if status_json:
            write_json(status_json, {
                "phase": "building_faithful_al_tensor_solve_operator",
                "level": N,
                "q": q,
                "sage_dim": int(sage_dim),
                "operator_kind": OPERATOR_KIND_TENSOR_SOLVE,
                "pairing_kind": "_pari_tensor_solve",
                "primary_pairing_materialized": False,
                "seconds": round(time.time() - t0, 3),
            })
        bal_apply, operator_factor_meta = build_tensor_solve_bal_apply(N, F)
        if status_json:
            write_json(status_json, {
                "phase": "building_source_repair_gram_by_tensor_solve_apply",
                "level": N,
                "q": q,
                "source_repair_rows": int(C.nrows()),
                "sage_dim": int(sage_dim),
                "operator_kind": OPERATOR_KIND_TENSOR_SOLVE,
                "seconds": round(time.time() - t0, 3),
            })
        G = build_gram_from_apply(F, C, bal_apply)
        operator_kind = OPERATOR_KIND_TENSOR_SOLVE
        pairing_kind = "_pari_tensor_solve"
        primary_pairing_materialized = False

        if compare_dense:
            if status_json:
                write_json(status_json, {
                    "phase": "building_dense_comparison_operator",
                    "level": N,
                    "q": q,
                    "sage_dim": int(sage_dim),
                    "operator_kind": OPERATOR_KIND_DENSE,
                    "seconds": round(time.time() - t0, 3),
                })
            Bal, dense_factor_meta = build_dense_bal(N, F)
            G_dense = C * Bal * C.transpose()
            G_dense_sha256 = matrix_sha256(G_dense)
            tensor_solve_matches_dense = bool(G == G_dense)

    d = G.nrows()
    A = G[: d - 1, : d - 1]
    b_col = vector(F, [G[i, d - 1] for i in range(d - 1)])
    d_row = vector(F, [G[d - 1, i] for i in range(d - 1)])
    c = G[d - 1, d - 1]

    if A.rank() == d - 1:
        x = A.solve_right(b_col)
        schur = c - sum(d_row[i] * x[i] for i in range(d - 1))
    else:
        schur = F(0)

    beta = sum(phi_sage[i] * repair_sage[i] for i in range(sage_dim))
    q_b_from_schur = (beta * beta) / schur if schur != 0 else F(0)
    q_b_direct = None
    if Bal is not None:
        q_b_direct = sum(
            phi_sage[i] * (phi_sage * Bal.inverse())[i]
            for i in range(sage_dim)
        )

    rank_A = int(A.rank())
    rank_A_target = int(d - 1)
    schur_nonzero = bool(schur != 0)
    direct_matches = None if q_b_direct is None else bool(q_b_direct == q_b_from_schur)
    direct_check_ok = direct_matches is not False
    dense_check_ok = tensor_solve_matches_dense is not False
    faithful_found = bool(
        rank_A == rank_A_target
        and schur_nonzero
        and direct_check_ok
        and dense_check_ok
    )

    payload = {
        "tool": TOOL,
        "date": DATE,
        "status": "computed",
        "faithful_al_certificate_found": faithful_found,
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "level": N,
        "N": N,
        "mode": manifest.get("mode"),
        "q": q,
        "operator_mode": operator_mode,
        "operator_kind": operator_kind,
        "operator_is_identity": False,
        "operator_kind_not_identity": True,
        "pairing_kind": pairing_kind,
        "primary_pairing_materialized": primary_pairing_materialized,
        "dense_comparison_requested": bool(compare_dense),
        "dense_comparison_pairing_materialized": bool(compare_dense and Bal is not None),
        "tensor_solve_matches_dense": tensor_solve_matches_dense,
        "atkin_lehner_twist": True,
        "sage_dim": int(sage_dim),
        "source_dim": rank_A_target,
        "projected_rows_source": projected_rows_meta,
        "repair_source": repair_source,
        "phi_source": phi_source,
        "rank_A": rank_A,
        "rank_A_target": rank_A_target,
        "rank_A_full": bool(rank_A == rank_A_target),
        "rank_G": int(G.rank()),
        "rank_G_target": int(d),
        "rank_G_full": bool(G.rank() == d),
        "schur_scalar_mod_q": int(schur),
        "schur_scalar_signed": signed_lift(schur, q),
        "schur_nonzero": schur_nonzero,
        "beta_mod_q": int(beta),
        "beta_signed": signed_lift(beta, q),
        "q_b_from_schur_mod_q": int(q_b_from_schur),
        "q_b_from_schur_signed": signed_lift(q_b_from_schur, q),
        "qb3_schur_signed": signed_lift(q_b_from_schur, q),
        "q_b_direct_mod_q": None if q_b_direct is None else int(q_b_direct),
        "q_b_direct_signed": None if q_b_direct is None else signed_lift(q_b_direct, q),
        "qb3_direct_signed": None if q_b_direct is None else signed_lift(q_b_direct, q),
        "direct_matches_schur": direct_matches,
        "Bal_rank": None if Bal is None else int(Bal.rank()),
        "Bal_det_signed": None if Bal is None else signed_lift(Bal.det(), q),
        "operator_factor_metadata": operator_factor_meta,
        "dense_factor_metadata": dense_factor_meta,
        "input_hashes": {
            "case_manifest_sha256": file_sha256(case_dir / "manifest.json"),
            "case_rows_sha256": file_sha256(rows_path),
            "pi_json_sha256": file_sha256(pi_json),
            "operator_script_sha256": file_sha256(Path(__file__)),
            "C_source_repair_sha256": matrix_sha256(C),
            "G_source_repair_sha256": matrix_sha256(G),
            "G_dense_comparison_sha256": G_dense_sha256,
            "B_AL_sha256": None if Bal is None else matrix_sha256(Bal),
            "B_AL_P_sha256": None if operator_factor_meta is None else operator_factor_meta.get("P_sha256"),
            "B_AL_tensor_sha256": None if operator_factor_meta is None else operator_factor_meta.get("T_sha256"),
            "B_AL_W_sha256": None if operator_factor_meta is None else operator_factor_meta.get("W_sha256"),
        },
        "transcript": {
            "scope": (
                "dense_smoke_direct_schur_and_direct_inverse"
                if operator_mode == "dense"
                else "tensor_solve_smoke_schur_with_optional_dense_comparison"
            ),
            "checkpoint_stride": 0,
            "matvec_checkpoints": [],
            "note": (
                "Small-level smoke. The tensor-solve mode applies B_AL as "
                "P * solve(_pari_tensor, W * P^T * x), so the primary path "
                "does not materialize M0._pari_pairing()."
            ),
        },
        "transcript_metadata": {
            "scope": (
                "dense_smoke_direct_schur_and_direct_inverse"
                if operator_mode == "dense"
                else "tensor_solve_smoke_schur_with_optional_dense_comparison"
            ),
            "checkpoint_stride": 0,
            "matvec_checkpoints": [],
            "operator_logic": (
                "pari_pairing_atkin_lehner_twist"
                if operator_mode == "dense"
                else "P_solve_pari_tensor_W_Pt_no_pari_pairing"
            ),
            "comparison": (
                "schur_and_direct_inverse"
                if operator_mode == "dense"
                else "schur_and_optional_dense_pairing_comparison"
            ),
            "seed_start": None,
            "seed_count": None,
            "suffix_terms": None,
        },
        "seconds": round(time.time() - t0, 3),
    }
    return payload


def write_md(payload, out_md):
    lines = [
        "# R1 Faithful-AL Schur Certificate",
        "",
        f"Level: `{payload.get('level')}`",
        f"q: `{payload.get('q')}`",
        f"Status: `{payload.get('status')}`",
        f"faithful_al_certificate_found: `{payload.get('faithful_al_certificate_found')}`",
        f"operator_kind: `{payload.get('operator_kind')}`",
        f"operator_is_identity: `{payload.get('operator_is_identity')}`",
        f"operator_kind_not_identity: `{payload.get('operator_kind_not_identity')}`",
        "",
    ]
    if payload.get("status") == "computed":
        lines.extend([
            "## Certificate",
            "",
            "```text",
            f"rank(A):          {payload.get('rank_A')} / {payload.get('rank_A_target')}",
            f"rank(A) full:     {payload.get('rank_A_full')}",
            f"s_N:              {payload.get('schur_scalar_signed')} mod {payload.get('q')}",
            f"s_N nonzero:      {payload.get('schur_nonzero')}",
            f"beta:             {payload.get('beta_signed')}",
            f"Q_B(schur):       {payload.get('q_b_from_schur_signed')}",
            f"Q_B(direct):       {payload.get('q_b_direct_signed')}",
            f"direct match:     {payload.get('direct_matches_schur')}",
            f"B_AL rank:        {payload.get('Bal_rank')}",
            "```",
            "",
            "Interpretation: this is a small-level faithful-AL smoke using",
            f"`{payload.get('operator_kind')}`. It is not an identity-pairing",
            "result.",
            "",
        ])
    else:
        lines.extend([
            "## Guard",
            "",
            payload.get("reason", ""),
            "",
            "No identity-pairing fallback was used.",
            "",
        ])
    lines.extend([
        "## Input Hashes",
        "",
        "```json",
        json.dumps(payload.get("input_hashes", {}), indent=2, ensure_ascii=False),
        "```",
        "",
        "## Transcript Metadata",
        "",
        "```json",
        json.dumps(payload.get("transcript_metadata", {}), indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--pi-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--status-json", default="")
    parser.add_argument("--q", type=int, default=None)
    parser.add_argument("--max-dense-dim", type=int, default=256)
    parser.add_argument(
        "--operator-mode",
        choices=["dense", "tensor-solve"],
        default="tensor-solve",
        help=(
            "Primary faithful-AL operator. tensor-solve applies "
            "P * solve(_pari_tensor, W * P^T * x) and avoids _pari_pairing()."
        ),
    )
    parser.add_argument(
        "--dense-comparison",
        choices=["auto", "on", "off"],
        default="auto",
        help=(
            "For small tensor-solve smokes, optionally build the dense "
            "_pari_pairing path only as a comparison. auto enables it under "
            "--max-dense-dim."
        ),
    )
    parser.add_argument(
        "--max-tensor-gram-dim",
        type=int,
        default=256,
        help=(
            "Guard for explicit source+repair Gram construction in tensor-solve "
            "mode. Large levels need a matrix-free Schur/Wiedemann solver."
        ),
    )
    # Accepted for queue-interface compatibility. Dense smoke does not use
    # scalar Wiedemann seeds, but the fields are retained in the transcript.
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--seed-count", type=int, default=16)
    parser.add_argument("--suffix-terms", type=int, default=4)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--projection-progress-every", type=int, default=1000)
    parser.add_argument("--checkpoint-stride", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()
    payload = compute_dense(
        args.case_dir,
        args.pi_json,
        args.status_json,
        args.max_dense_dim,
        q_override=args.q,
        operator_mode=args.operator_mode,
        dense_comparison=args.dense_comparison,
        max_tensor_gram_dim=args.max_tensor_gram_dim,
    )
    payload["queue_compat"] = {
        "seed_start": int(args.seed_start),
        "seed_count": int(args.seed_count),
        "suffix_terms": int(args.suffix_terms),
        "checkpoint_stride": int(args.checkpoint_stride),
        "operator_mode": args.operator_mode,
        "dense_comparison": args.dense_comparison,
        "max_tensor_gram_dim": int(args.max_tensor_gram_dim),
        "note": "Accepted for queue compatibility; small smokes use direct Schur.",
    }
    payload.setdefault("transcript_metadata", {})
    payload["transcript_metadata"].update({
        "seed_start": int(args.seed_start),
        "seed_count": int(args.seed_count),
        "suffix_terms": int(args.suffix_terms),
        "checkpoint_stride": int(args.checkpoint_stride),
    })
    write_json(args.out_json, payload)
    write_md(payload, args.out_md)
    if args.status_json:
        write_json(args.status_json, {
            "phase": "finished",
            "status": payload.get("status"),
            "faithful_al_certificate_found": payload.get("faithful_al_certificate_found"),
            "operator_kind": payload.get("operator_kind"),
            "seconds": payload.get("seconds"),
            "out_json": str(args.out_json),
        })
    print(json.dumps({
        "status": payload.get("status"),
        "faithful_al_certificate_found": payload.get("faithful_al_certificate_found"),
        "operator_kind": payload.get("operator_kind"),
        "rank_A": payload.get("rank_A"),
        "schur_nonzero": payload.get("schur_nonzero"),
        "direct_matches_schur": payload.get("direct_matches_schur"),
        "seconds": payload.get("seconds"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
