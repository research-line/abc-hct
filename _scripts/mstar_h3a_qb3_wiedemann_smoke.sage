#!/usr/bin/env sage
# Wiedemann-style smoke for the Q_B-3 source-Gram matvec operator.
#
# For a square operator A over F_q, a scalar Wiedemann sequence
#
#     s_k = u^T A^k v
#
# whose minimal generator has degree n and nonzero constant term is a
# strong nonsingularity certificate pattern: the scalar generator then has
# full degree and excludes a zero factor in the minimal polynomial.
#
# This script is a smoke and contract generator, not yet a production
# large-level certificate.

import argparse
import json
from pathlib import Path

from sage.all import GF, Gamma0, ModularSymbols, matrix, vector
from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
from sage.modular.modsym.relation_matrix import (
    modI_relations,
    modS_relations,
    sparse_2term_quotient,
)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_manifest(case_dir):
    return load_json(Path(case_dir) / "manifest.json")


def signed_lift(value, q):
    v = int(value) % q
    if v > q // 2:
        v -= q
    return int(v)


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

    C = C[: L + 1]
    return L, C


def verify_connection(sequence, C, F):
    L = len(C) - 1
    bad = []
    for k in range(L, len(sequence)):
        total = F(sequence[k])
        for i in range(1, L + 1):
            total += C[i] * sequence[k - i]
        if total != 0:
            bad.append([int(k), int(total)])
            if len(bad) >= 8:
                break
    return bad


def make_bridge(pi_data, manifest):
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
        "sage_dim": sage_dim,
        "free_columns": free_columns,
        "free_to_sage_rank": int(free_to_sage.rank()),
        "free_to_sage_isomorphism": int(free_to_sage.rank()) == sage_dim == len(free_columns),
        "consistency_errors": consistency_errors,
        "quotient_row_to_sage": quotient_row_to_sage,
    }


def deterministic_pair(F, n, seed):
    u = vector(F, [F((i + 3) ** (seed + 1) + 19 * seed + 5) for i in range(n)])
    v = vector(F, [F((i + 5) ** (seed + 2) + 31 * seed + 7) for i in range(n)])
    return u, v


def compute(case_dir, pi_json, max_dense_dim, max_seed):
    manifest = read_manifest(case_dir)
    pi_data = load_json(pi_json)
    N = int(manifest["level"])
    q = int(manifest["q"])
    free_dim = len(pi_data.get("free_columns", []))
    source_rows = int(pi_data.get("hecke_rows", len(pi_data.get("projected_hecke_rows_mod_q", []))))

    if free_dim > max_dense_dim:
        return {
            "tool": "mstar_h3a_qb3_wiedemann_smoke",
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "level": N,
            "q": q,
            "status": "blocked_by_dense_guard",
            "quotient_dim": free_dim,
            "source_rows": source_rows,
            "rank_A_target": free_dim - 1,
            "max_dense_dim": int(max_dense_dim),
            "large_level_contract": [
                "implement matvec v -> A*v",
                "build scalar Wiedemann sequences u^T A^k v",
                "seek full-degree generator with nonzero constant term",
            ],
        }

    bridge = make_bridge(pi_data, manifest)
    if not bridge["free_to_sage_isomorphism"]:
        raise ValueError("free quotient is not identified with Sage basis")

    F = bridge["field"]
    q = bridge["q"]
    N = bridge["N"]
    quotient_row_to_sage = bridge["quotient_row_to_sage"]
    source_rows_sage = [
        quotient_row_to_sage(entries)
        for entries in pi_data.get("projected_hecke_rows_mod_q", [])
    ]
    C = matrix(F, source_rows_sage)

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
    Bal = PF * EF * WF * PF.transpose()

    def matvec(v):
        return C * (Bal * (C.transpose() * v))

    n = C.nrows()
    A = C * Bal * C.transpose()
    attempts = []
    accepted = None
    for seed in range(1, max_seed + 1):
        u, v = deterministic_pair(F, n, seed)
        x = vector(F, v)
        seq = []
        for _ in range(2 * n + 4):
            seq.append(sum(u[i] * x[i] for i in range(n)))
            x = matvec(x)
        degree, coeffs = berlekamp_massey(seq, F)
        bad = verify_connection(seq, coeffs, F)
        constant = coeffs[degree] if degree else F(0)
        row = {
            "seed": int(seed),
            "degree": int(degree),
            "constant_mod_q": int(constant),
            "constant_signed": signed_lift(constant, q),
            "constant_nonzero": bool(constant != 0),
            "connection_verified": len(bad) == 0,
            "verification_failures": bad,
            "sequence_head_signed": [signed_lift(x, q) for x in seq[: min(10, len(seq))]],
        }
        attempts.append(row)
        if degree == n and constant != 0 and not bad:
            accepted = row
            break

    return {
        "tool": "mstar_h3a_qb3_wiedemann_smoke",
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "level": N,
        "q": q,
        "status": "computed",
        "source_rows": int(n),
        "rank_A": int(A.rank()),
        "rank_A_target": int(n),
        "rank_A_full": bool(A.rank() == n),
        "accepted_certificate_found": accepted is not None,
        "accepted_certificate": accepted,
        "attempts": attempts,
    }


def write_md(payload, out_md):
    lines = [
        "# H3a Q_B-3 Wiedemann Smoke",
        "",
        f"Level: `{payload.get('level')}`",
        f"Status: `{payload.get('status')}`",
        "",
    ]
    if payload.get("status") == "computed":
        cert = payload.get("accepted_certificate") or {}
        lines.extend([
            "## Smoke",
            "",
            "```text",
            f"source rows:                {payload['source_rows']}",
            f"rank(A):                    {payload['rank_A']} / {payload['rank_A_target']}",
            f"rank(A) full:               {payload['rank_A_full']}",
            f"accepted certificate found: {payload['accepted_certificate_found']}",
            f"accepted seed:              {cert.get('seed')}",
            f"degree:                     {cert.get('degree')}",
            f"constant signed:            {cert.get('constant_signed')}",
            "```",
            "",
            "The certificate pattern is: scalar generator degree equals `n` and",
            "its constant term is nonzero.",
            "",
        ])
    else:
        lines.extend([
            "## Guard",
            "",
            f"Quotient dimension `{payload.get('quotient_dim')}` exceeds dense guard",
            f"`{payload.get('max_dense_dim')}`.",
            "",
            "Large-level contract:",
            "",
            "```text",
            "\n".join(payload.get("large_level_contract", [])),
            "```",
            "",
            f"Target: `rank(A)={payload.get('rank_A_target')}`.",
            "",
        ])
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--pi-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--max-dense-dim", type=int, default=256)
    parser.add_argument("--max-seed", type=int, default=16)
    args = parser.parse_args()

    payload = compute(
        Path(args.case_dir),
        Path(args.pi_json),
        args.max_dense_dim,
        args.max_seed,
    )
    Path(args.out_json).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(payload, args.out_md)
    print(json.dumps({
        "status": payload.get("status"),
        "level": payload.get("level"),
        "rank_A": payload.get("rank_A"),
        "accepted_certificate_found": payload.get("accepted_certificate_found"),
        "accepted_certificate": payload.get("accepted_certificate"),
    }))


if __name__ == "__main__":
    main()
