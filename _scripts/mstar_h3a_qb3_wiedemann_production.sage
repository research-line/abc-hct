#!/usr/bin/env sage
# Production scalar-Wiedemann run for the Q_B-3 source-Gram operator.
#
# This script avoids materializing A = C_source B_AL C_source^T.  It rebuilds
# the sparse pi_N projection from a split-last witness, constructs the sparse
# bridge to Sage's M^+ basis, and generates scalar Wiedemann sequences from
# matrix-free matvecs.

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

from sage.all import GF, Gamma0, ModularSymbols, matrix, vector
from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
from sage.modular.modsym.relation_matrix import (
    modI_relations,
    modS_relations,
    sparse_2term_quotient,
)


TOOL = "mstar_h3a_qb3_wiedemann_production"
DATE = "2026-05-23"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
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


def build_free_to_sage(case_dir, pi_data, manifest, F, status):
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

    M = ModularSymbols(Gamma0(N), 2, sign=sign)
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
        "sage_dim": int(sage_dim),
        "free_to_sage_nnz": int(Fmat.dict().__len__()),
    })
    return Fmat, sage_dim


def build_bal_factors(N, F, status):
    M0 = ModularSymbols(Gamma0(N), 2, sign=0)
    P = sparse_change_ring(M0.plus_submodule().basis_matrix(), F)
    E = sparse_change_ring(M0._pari_pairing(), F)
    W = M0.atkin_lehner_operator(N)
    try:
        Wm = W.matrix()
    except Exception:
        Wm = W
    WF = sparse_change_ring(Wm, F)
    status.update({
        "phase": "built_B_AL_factors",
        "sign0_dim": int(M0.dimension()),
        "plus_dim": int(P.nrows()),
        "P_nnz": int(len(P.dict())),
        "E_nnz": int(len(E.dict())),
        "W_nnz": int(len(WF.dict())),
    })
    return P, E, WF


def deterministic_pair(F, n, seed):
    u = vector(F, [F((i + 3) ** (seed + 1) + 19 * seed + 5) for i in range(n)])
    v = vector(F, [F((i + 5) ** (seed + 2) + 31 * seed + 7) for i in range(n)])
    return u, v


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
    Fmat, sage_dim = build_free_to_sage(case_dir, pi_data, manifest, F, status)
    save_status()
    P, E, WF = build_bal_factors(N, F, status)
    save_status()

    n = int(len(source_rows))
    d = int(len(pi_data["free_columns"]))
    Cq = sparse_matrix_from_row_dicts(F, n, d, source_rows)
    save_status({
        "phase": "built_C_source",
        "target_rank": n,
        "quotient_dim": d,
        "C_source_nnz": int(len(Cq.dict())),
    })

    def bal_apply(x):
        return P * (E * (WF * (P.transpose() * x)))

    def matvec(v):
        tmp = Cq.transpose() * v
        u = Fmat.transpose() * tmp
        w = bal_apply(u)
        z = Fmat * w
        return Cq * z

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
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--projection-progress-every", type=int, default=1000)
    parser.add_argument("--max-steps", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()
    payload = run(args)
    print(json.dumps({
        "status": payload.get("status"),
        "accepted_certificate_found": payload.get("accepted_certificate_found"),
        "target_rank": payload.get("target_rank"),
        "seconds": payload.get("seconds"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
