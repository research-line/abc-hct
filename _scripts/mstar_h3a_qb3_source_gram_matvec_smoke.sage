#!/usr/bin/env sage
# Smoke-test the matrix-free Q_B-3 source-Gram matvec contract.
#
# The large-level rank verifier should use only
#
#     A v = C_source * B_AL * C_source^T * v
#
# without materializing A.  This script checks the factorized matvec against a
# dense A on N=109 and emits guarded contracts for large levels.

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


def deterministic_test_vectors(F, n, count):
    vectors = []
    for k in range(1, count + 1):
        vectors.append(vector(F, [F((i + 1) ** k + 17 * k) for i in range(n)]))
    if n:
        e0 = vector(F, n)
        e0[0] = F(1)
        vectors.append(e0)
        elast = vector(F, n)
        elast[n - 1] = F(1)
        vectors.append(elast)
    return vectors


def compute(case_dir, pi_json, max_dense_dim, vector_count):
    manifest = read_manifest(case_dir)
    pi_data = load_json(pi_json)
    N = int(manifest["level"])
    q = int(manifest["q"])
    free_dim = len(pi_data.get("free_columns", []))
    source_rows = int(pi_data.get("hecke_rows", len(pi_data.get("projected_hecke_rows_mod_q", []))))

    if free_dim > max_dense_dim:
        return {
            "tool": "mstar_h3a_qb3_source_gram_matvec_smoke",
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "level": N,
            "q": q,
            "status": "blocked_by_dense_guard",
            "quotient_dim": free_dim,
            "source_rows": source_rows,
            "rank_A_target": free_dim - 1,
            "max_dense_dim": int(max_dense_dim),
            "contract": [
                "u = C_source^T v",
                "w = B_AL u",
                "out = C_source w",
            ],
        }

    if not pi_data.get("projected_hecke_rows_mod_q"):
        raise ValueError("pi-json has no projected_hecke_rows_mod_q for dense smoke mode")

    bridge = make_bridge(pi_data, manifest)
    if not bridge["free_to_sage_isomorphism"]:
        raise ValueError("free quotient is not identified with Sage basis")
    F = bridge["field"]
    N = bridge["N"]
    q = bridge["q"]
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
    A = C * Bal * C.transpose()

    n = C.nrows()
    tests = []
    for idx, v in enumerate(deterministic_test_vectors(F, n, vector_count)):
        dense_out = A * v
        factor_out = C * (Bal * (C.transpose() * v))
        diff = dense_out - factor_out
        tests.append({
            "index": int(idx),
            "matches": bool(diff == 0),
            "diff_support_size": sum(1 for x in diff if x != 0),
            "dense_out_head_signed": [
                signed_lift(dense_out[i], q) for i in range(min(8, len(dense_out)))
            ],
        })

    return {
        "tool": "mstar_h3a_qb3_source_gram_matvec_smoke",
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "level": N,
        "q": q,
        "status": "computed",
        "quotient_dim": int(bridge["sage_dim"]),
        "source_rows": int(n),
        "rank_A": int(A.rank()),
        "rank_A_target": int(n),
        "rank_A_full": bool(A.rank() == n),
        "Bal_rank": int(Bal.rank()),
        "matvec_tests": tests,
        "all_matvec_tests_pass": all(row["matches"] for row in tests),
    }


def write_md(payload, out_md):
    lines = [
        "# H3a Q_B-3 Source-Gram Matvec Smoke",
        "",
        f"Level: `{payload.get('level')}`",
        f"Status: `{payload.get('status')}`",
        "",
    ]
    if payload.get("status") == "computed":
        lines.extend([
            "## Smoke",
            "",
            "```text",
            f"quotient dim:          {payload['quotient_dim']}",
            f"source rows:           {payload['source_rows']}",
            f"rank(A):               {payload['rank_A']} / {payload['rank_A_target']}",
            f"rank(A) full:          {payload['rank_A_full']}",
            f"B_AL rank:             {payload['Bal_rank']}",
            f"matvec tests pass:     {payload['all_matvec_tests_pass']}",
            "```",
            "",
            "Each test checks `A*v == C_source*(B_AL*(C_source^T*v))`.",
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
            "\n".join(payload.get("contract", [])),
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
    parser.add_argument("--vector-count", type=int, default=4)
    args = parser.parse_args()

    payload = compute(
        Path(args.case_dir),
        Path(args.pi_json),
        args.max_dense_dim,
        args.vector_count,
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
        "rank_A_full": payload.get("rank_A_full"),
        "all_matvec_tests_pass": payload.get("all_matvec_tests_pass"),
    }))


if __name__ == "__main__":
    main()
