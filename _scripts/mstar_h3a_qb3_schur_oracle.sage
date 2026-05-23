#!/usr/bin/env sage
# Compute/guard the Q_B-3 Schur certificate.
#
# Dense mode is intentionally guarded.  It is meant to reproduce the N=109
# regression and to define the exact JSON contract for later matrix-free large
# level runs.

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


def iter_rows(case_dir):
    manifest = read_manifest(case_dir)
    rows_path = Path(case_dir) / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def signed_lift(value, q):
    v = int(value) % q
    if v > q // 2:
        v -= q
    return int(v)


def sparse_pairs_to_dict(row_pairs, q):
    return {int(c): int(v) % q for c, v in row_pairs if int(v) % q}


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

    missing_columns = [i for i, v in enumerate(col_to_sage) if v is None]
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


def compute_dense_schur(case_dir, pi_json, max_dense_dim):
    manifest = read_manifest(case_dir)
    pi_data = load_json(pi_json)
    bridge = make_free_to_sage(case_dir, pi_data, manifest)
    F = bridge["field"]
    q = bridge["q"]
    N = bridge["N"]
    sage_dim = bridge["sage_dim"]

    if sage_dim > max_dense_dim:
        return {
            "tool": "mstar_h3a_qb3_schur_oracle",
            "case_dir": str(case_dir),
            "pi_json": str(pi_json),
            "level": N,
            "q": q,
            "mode": "dense",
            "status": "blocked_by_dense_guard",
            "sage_dim": sage_dim,
            "max_dense_dim": int(max_dense_dim),
            "reason": "Use a matrix-free Schur oracle for this dimension.",
        }

    phi_entries = pi_data.get("phi_checks", {}).get("induced_phi_entries_mod_q")
    if not phi_entries:
        raise ValueError("pi-json has no phi_checks.induced_phi_entries_mod_q")
    if not bridge["free_to_sage_isomorphism"]:
        raise ValueError("free quotient is not identified with Sage basis")

    quotient_row_to_sage = bridge["quotient_row_to_sage"]
    repair_sage = quotient_row_to_sage(pi_data["projected_repair_entries_mod_q"])
    hecke_sage_rows = [
        quotient_row_to_sage(entries)
        for entries in pi_data.get("projected_hecke_rows_mod_q", [])
    ]

    phi_free = vector(F, len(bridge["free_columns"]))
    for qcol, value in phi_entries:
        phi_free[int(qcol)] = F(int(value))
    phi_sage = phi_free * bridge["free_to_sage"].transpose().inverse()

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

    source_repair_rows = hecke_sage_rows + [repair_sage]
    C = matrix(F, source_repair_rows)
    G = C * Bal * C.transpose()
    d = G.nrows()
    A = G[: d - 1, : d - 1]
    b_col = vector(F, [G[i, d - 1] for i in range(d - 1)])
    d_row = vector(F, [G[d - 1, i] for i in range(d - 1)])
    c = G[d - 1, d - 1]
    x = A.solve_right(b_col)
    schur = c - sum(d_row[i] * x[i] for i in range(d - 1))

    beta = sum(phi_sage[i] * repair_sage[i] for i in range(sage_dim))
    q_b_from_schur = (beta * beta) / schur if schur != 0 else F(0)
    # Direct check, available only in dense small mode.
    q_b_direct = sum(
        phi_sage[i] * (phi_sage * Bal.inverse())[i]
        for i in range(sage_dim)
    )

    return {
        "tool": "mstar_h3a_qb3_schur_oracle",
        "case_dir": str(case_dir),
        "pi_json": str(pi_json),
        "level": N,
        "q": q,
        "mode": "dense",
        "status": "computed",
        "sage_dim": sage_dim,
        "source_dim": d - 1,
        "rank_A": int(A.rank()),
        "rank_G": int(G.rank()),
        "rank_A_full": bool(A.rank() == d - 1),
        "schur_scalar_mod_q": int(schur),
        "schur_scalar_signed": signed_lift(schur, q),
        "schur_nonzero": bool(schur != 0),
        "beta_mod_q": int(beta),
        "beta_signed": signed_lift(beta, q),
        "q_b_from_schur_mod_q": int(q_b_from_schur),
        "q_b_from_schur_signed": signed_lift(q_b_from_schur, q),
        "q_b_direct_mod_q": int(q_b_direct),
        "q_b_direct_signed": signed_lift(q_b_direct, q),
        "direct_matches_schur": bool(q_b_direct == q_b_from_schur),
        "Bal_rank": int(Bal.rank()),
        "Bal_det_signed": signed_lift(Bal.det(), q),
    }


def write_markdown(payload, out_md):
    lines = [
        "# H3a Q_B-3 Schur Oracle",
        "",
        f"Level: `{payload.get('level')}`",
        f"Status: `{payload.get('status')}`",
        f"Mode: `{payload.get('mode')}`",
        "",
    ]
    if payload.get("status") == "computed":
        lines.extend(
            [
                "## Certificate",
                "",
                "```text",
                f"rank(A):       {payload['rank_A']} / {payload['source_dim']}",
                f"rank(G):       {payload['rank_G']} / {payload['sage_dim']}",
                f"beta:          {payload['beta_signed']}",
                f"s:             {payload['schur_scalar_signed']} mod {payload['q']}",
                f"Q_B(schur):    {payload['q_b_from_schur_signed']}",
                f"Q_B(direct):    {payload['q_b_direct_signed']}",
                f"direct match:  {payload['direct_matches_schur']}",
                f"Bal rank:      {payload['Bal_rank']}",
                f"Bal det:       {payload['Bal_det_signed']}",
                "```",
                "",
                "Interpretation: In dense smoke mode this verifies the Schur",
                "certificate formula against the direct `phi B_AL^-1 phi^T`",
                "calculation.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Guard",
                "",
                payload.get("reason", ""),
                "",
                f"Sage dimension `{payload.get('sage_dim')}` exceeds guard",
                f"`{payload.get('max_dense_dim')}`.",
                "",
            ]
        )
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--pi-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--max-dense-dim", type=int, default=256)
    args = parser.parse_args()
    payload = compute_dense_schur(Path(args.case_dir), Path(args.pi_json), args.max_dense_dim)
    Path(args.out_json).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, args.out_md)
    print(json.dumps({
        "status": payload.get("status"),
        "level": payload.get("level"),
        "schur_scalar_signed": payload.get("schur_scalar_signed"),
        "q_b_from_schur_signed": payload.get("q_b_from_schur_signed"),
        "direct_matches_schur": payload.get("direct_matches_schur"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
