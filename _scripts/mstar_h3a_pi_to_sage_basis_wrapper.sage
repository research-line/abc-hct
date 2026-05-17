#!/usr/bin/env sage
# Compare the witness pi_N quotient coordinates with Sage ModularSymbols basis.

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
    return json.loads((Path(case_dir) / "manifest.json").read_text(encoding="utf-8"))


def iter_rows(case_dir):
    manifest = read_manifest(case_dir)
    rows_path = Path(case_dir) / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def sparse_pairs_to_dict(row_pairs, q):
    return {int(c): int(v) % q for c, v in row_pairs if int(v) % q}


def compare_projective_rows(row_a, row_b, q):
    F = GF(q)
    scale = None
    mismatches = []
    for i in range(len(row_a)):
        a = F(row_a[i])
        b = F(row_b[i])
        if a == 0 and b == 0:
            continue
        if a == 0 or b == 0:
            mismatches.append({
                "i": int(i),
                "a": signed_lift(a, q),
                "b": signed_lift(b, q),
                "kind": "zero-mismatch",
            })
            continue
        current = a / b
        if scale is None:
            scale = current
        elif current != scale:
            mismatches.append({
                "i": int(i),
                "a": signed_lift(a, q),
                "b": signed_lift(b, q),
                "scale": str(current),
                "expected": str(scale),
            })
    return {
        "consistent": len(mismatches) == 0 and scale is not None,
        "scale": str(scale) if scale is not None else None,
        "mismatches": mismatches[:10],
    }


def signed_lift(value, q):
    v = int(value) % q
    if v > q // 2:
        v -= q
    return int(v)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--pi-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    manifest = read_manifest(args.case_dir)
    pi_data = load_json(args.pi_json)
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
            consistency_errors.append({
                "col": int(col),
                "manin_index": int(j),
            })
            if len(consistency_errors) > 10:
                break

    missing_columns = [i for i, v in enumerate(col_to_sage) if v is None]

    # Verify that T-Manin rows map to zero in Sage coordinates.
    t_nonzero = 0
    t_nonzero_examples = []
    for row in iter_rows(args.case_dir):
        if (row.get("row_metadata") or {}).get("source_kind") != "manin_T":
            continue
        total = vector(F, sage_dim)
        for col, value in row["row"]:
            total += F(int(value)) * col_to_sage[int(col)]
        if total != 0:
            t_nonzero += 1
            if len(t_nonzero_examples) < 5:
                t_nonzero_examples.append({
                    "row_id": row.get("row_id"),
                    "nonzero_entries": [
                        [int(i), signed_lift(total[i], q)]
                        for i in range(sage_dim) if total[i] != 0
                    ],
                })

    free_to_sage_rows = []
    for col in free_columns:
        free_to_sage_rows.append(list(col_to_sage[col]))
    free_to_sage = matrix(F, free_to_sage_rows)
    free_to_sage_rank = int(free_to_sage.rank())

    def quotient_row_to_sage(entries):
        total = vector(F, sage_dim)
        for qcol, value in entries:
            total += F(int(value)) * vector(F, free_to_sage_rows[int(qcol)])
        return total

    repair_sage = quotient_row_to_sage(pi_data["projected_repair_entries_mod_q"])
    hecke_sage_rows = [
        quotient_row_to_sage(entries)
        for entries in pi_data.get("projected_hecke_rows_mod_q", [])
    ]
    hecke_sage_rank = int(matrix(F, hecke_sage_rows).rank()) if hecke_sage_rows else 0
    hecke_plus_repair_rank = int(matrix(F, hecke_sage_rows + [repair_sage]).rank())

        # Transform the induced phi from free quotient coordinates to Sage M^+
        # coordinates.  With row-vector convention s = f * A for vectors,
        # functionals transform contravariantly: phi_sage = phi_free * A^{-T}.
    phi_sage_entries_signed = []
    pairing_tests = {"available": False}
    phi_entries = pi_data.get("phi_checks", {}).get("induced_phi_entries_mod_q")
    if phi_entries and free_to_sage_rank == sage_dim == len(free_columns):
        phi_free = vector(F, len(free_columns))
        for qcol, value in phi_entries:
            phi_free[int(qcol)] = F(int(value))
        phi_sage = phi_free * free_to_sage.transpose().inverse()
        phi_sage_entries_signed = [
            [int(i), signed_lift(phi_sage[i], q)]
            for i in range(sage_dim) if phi_sage[i] != 0
        ]
        phi_on_hecke = [
            sum(phi_sage[i] * row[i] for i in range(sage_dim))
            for row in hecke_sage_rows
        ]
        phi_on_hecke_nonzero = [
            [int(i), signed_lift(value, q)]
            for i, value in enumerate(phi_on_hecke) if value != 0
        ]
        phi_on_repair_sage = sum(
            phi_sage[i] * repair_sage[i] for i in range(sage_dim)
        )

        try:
            M0 = ModularSymbols(Gamma0(N), 2, sign=0)
            P = M0.plus_submodule().basis_matrix()
            Q = M0.minus_submodule().basis_matrix()
            E = M0._pari_pairing()
            EF = matrix(F, E.nrows(), E.ncols(), E.list())
            PF = matrix(F, P.nrows(), P.ncols(), P.list())
            QF = matrix(F, Q.nrows(), Q.ncols(), Q.list())
            Bpp = PF * EF * PF.transpose()
            Bpq = PF * EF * QF.transpose()
            Bqq = QF * EF * QF.transpose()
            W = M0.atkin_lehner_operator(N)
            try:
                Wm = W.matrix()
            except Exception:
                Wm = W
            WF = matrix(F, Wm.nrows(), Wm.ncols(), Wm.list())
            Bal = PF * EF * WF * PF.transpose()
            repair_row = vector(F, [repair_sage[i] for i in range(sage_dim)])
            pred_right = repair_row * Bpp
            pred_left = repair_row * Bpp.transpose()
            pred_al_right = repair_row * Bal
            pred_al_left = repair_row * Bal.transpose()
            al_preimage_right = phi_sage * Bal.inverse()
            al_preimage_left = phi_sage * Bal.transpose().inverse()
            al_defect_right = al_preimage_right - repair_row
            al_defect_left = al_preimage_left - repair_row
            phi_repair_pairing = sum(phi_sage[i] * repair_row[i] for i in range(sage_dim))
            phi_on_u_right = sum(phi_sage[i] * al_preimage_right[i] for i in range(sage_dim))
            phi_on_u_left = sum(phi_sage[i] * al_preimage_left[i] for i in range(sage_dim))
            alpha_right_from_phi = None
            alpha_left_from_phi = None
            if phi_repair_pairing != 0:
                alpha_right_from_phi = phi_on_u_right / phi_repair_pairing
                alpha_left_from_phi = phi_on_u_left / phi_repair_pairing

            source_repair_basis = matrix(F, hecke_sage_rows + [repair_sage])

            def signed_entries(vec):
                return [
                    [int(i), signed_lift(vec[i], q)]
                    for i in range(len(vec)) if vec[i] != 0
                ]

            def source_repair_decomposition(vec):
                if source_repair_basis.rank() != sage_dim:
                    return {
                        "available": False,
                        "source_repair_rank": int(source_repair_basis.rank()),
                    }
                rhs = vector(F, [vec[i] for i in range(sage_dim)])
                coeff = source_repair_basis.transpose().solve_right(rhs)
                alpha = coeff[len(hecke_sage_rows)]
                normalized = None
                normalized_minus_repair = None
                if alpha != 0:
                    normalized = vec / alpha
                    normalized_minus_repair = normalized - repair_row
                return {
                    "available": True,
                    "source_repair_rank": int(source_repair_basis.rank()),
                    "repair_coefficient_mod_q": int(alpha),
                    "repair_coefficient_signed": signed_lift(alpha, q),
                    "same_projective_restline_as_repair": bool(alpha != 0),
                    "source_coefficients_signed": [
                        [int(i), signed_lift(coeff[i], q)]
                        for i in range(len(hecke_sage_rows)) if coeff[i] != 0
                    ],
                    "normalized_minus_repair_entries_signed": (
                        signed_entries(normalized_minus_repair)
                        if normalized_minus_repair is not None else []
                    ),
                }

            pairing_tests = {
                "available": True,
                "full_sign0_dim": int(M0.dimension()),
                "plus_dim": int(P.nrows()),
                "minus_dim": int(Q.nrows()),
                "Bpp_rank": int(Bpp.rank()),
                "Bpq_rank": int(Bpq.rank()),
                "Bqq_rank": int(Bqq.rank()),
                "Bal_rank": int(Bal.rank()),
                "Bal_determinant_signed": signed_lift(Bal.det(), q),
                "phi_on_hecke_source_nonzero": phi_on_hecke_nonzero,
                "phi_on_repair_sage_signed": signed_lift(phi_on_repair_sage, q),
                "phi_repair_pairing_signed": signed_lift(phi_repair_pairing, q),
                "phi_on_u_right_signed": signed_lift(phi_on_u_right, q),
                "phi_on_u_left_signed": signed_lift(phi_on_u_left, q),
                "alpha_right_from_phi_signed": (
                    signed_lift(alpha_right_from_phi, q)
                    if alpha_right_from_phi is not None else None
                ),
                "alpha_left_from_phi_signed": (
                    signed_lift(alpha_left_from_phi, q)
                    if alpha_left_from_phi is not None else None
                ),
                "phi_vs_repair_Bpp_right": compare_projective_rows(phi_sage, pred_right, q),
                "phi_vs_repair_Bpp_left": compare_projective_rows(phi_sage, pred_left, q),
                "phi_vs_repair_Bal_right": compare_projective_rows(phi_sage, pred_al_right, q),
                "phi_vs_repair_Bal_left": compare_projective_rows(phi_sage, pred_al_left, q),
                "al_preimage_right_entries_signed": [
                    [int(i), signed_lift(al_preimage_right[i], q)]
                    for i in range(sage_dim) if al_preimage_right[i] != 0
                ],
                "al_preimage_left_entries_signed": [
                    [int(i), signed_lift(al_preimage_left[i], q)]
                    for i in range(sage_dim) if al_preimage_left[i] != 0
                ],
                "al_defect_right_entries_signed": [
                    [int(i), signed_lift(al_defect_right[i], q)]
                    for i in range(sage_dim) if al_defect_right[i] != 0
                ],
                "al_defect_left_entries_signed": [
                    [int(i), signed_lift(al_defect_left[i], q)]
                    for i in range(sage_dim) if al_defect_left[i] != 0
                ],
                "al_preimage_right_source_repair_decomposition": (
                    source_repair_decomposition(al_preimage_right)
                ),
                "al_preimage_left_source_repair_decomposition": (
                    source_repair_decomposition(al_preimage_left)
                ),
            }
        except Exception as exc:
            pairing_tests = {
                "available": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

    payload = {
        "tool": "mstar_h3a_pi_to_sage_basis_wrapper",
        "case_dir": args.case_dir,
        "N": N,
        "q": q,
        "sign": sign,
        "ncols_v_si": ncols,
        "sage_dim": sage_dim,
        "free_columns": free_columns,
        "free_to_sage_rank": free_to_sage_rank,
        "free_to_sage_isomorphism": free_to_sage_rank == sage_dim == len(free_columns),
        "missing_columns": missing_columns,
        "consistency_errors": consistency_errors,
        "t_rows_nonzero_in_sage": t_nonzero,
        "t_nonzero_examples": t_nonzero_examples,
        "projected_hecke_rank_in_sage": hecke_sage_rank,
        "projected_rank_with_repair_in_sage": hecke_plus_repair_rank,
        "repair_adds_sage_rank": hecke_plus_repair_rank > hecke_sage_rank,
        "repair_sage_entries_signed": [
            [int(i), signed_lift(repair_sage[i], q)]
            for i in range(sage_dim) if repair_sage[i] != 0
        ],
        "phi_sage_entries_signed": phi_sage_entries_signed,
        "pairing_tests": pairing_tests,
    }

    Path(args.out_json).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# H3a pi_N to Sage Basis Wrapper",
        "",
        "Compares the witness T-Manin quotient coordinates with Sage's",
        "`ModularSymbols(Gamma0(N),2,sign=1)` basis.",
        "",
        "```text",
        f"N/sign/q:                    {N} / {sign} / {q}",
        f"V_SI columns:                {ncols}",
        f"Sage dimension:              {sage_dim}",
        f"free columns from pi_N:       {free_columns}",
        f"free-to-Sage rank:           {free_to_sage_rank}",
        f"free-to-Sage isomorphism:    {payload['free_to_sage_isomorphism']}",
        f"missing V_SI columns:        {missing_columns}",
        f"S/I consistency errors:      {len(consistency_errors)}",
        f"T rows nonzero in Sage:      {t_nonzero}",
        f"Hecke rank in Sage:          {hecke_sage_rank}",
        f"Hecke+repair rank in Sage:   {hecke_plus_repair_rank}",
        f"repair adds Sage rank:       {payload['repair_adds_sage_rank']}",
        f"pairing tests available:     {pairing_tests.get('available')}",
        "```",
        "",
        "## Repair in Sage basis",
        "",
        "```text",
        f"{payload['repair_sage_entries_signed']}",
        "```",
        "",
        "## Induced phi in Sage basis",
        "",
        "```text",
        f"{phi_sage_entries_signed}",
        "```",
        "",
        "## Pairing tests",
        "",
        "```text",
        f"{pairing_tests}",
        "```",
        "",
        "## AL-corrected primal candidate",
        "",
        "```text",
        f"Bal rank:             {pairing_tests.get('Bal_rank')}",
        f"Bal determinant:      {pairing_tests.get('Bal_determinant_signed')}",
        f"phi on Hecke source:  {pairing_tests.get('phi_on_hecke_source_nonzero')}",
        f"phi(repair):          {pairing_tests.get('phi_repair_pairing_signed')}",
        f"phi(u_right):         {pairing_tests.get('phi_on_u_right_signed')}",
        f"alpha_right via phi:  {pairing_tests.get('alpha_right_from_phi_signed')}",
        f"phi(u_left):          {pairing_tests.get('phi_on_u_left_signed')}",
        f"alpha_left via phi:   {pairing_tests.get('alpha_left_from_phi_signed')}",
        f"repair * Bal matches phi:    {pairing_tests.get('phi_vs_repair_Bal_right', {}).get('consistent')}",
        f"repair * Bal^T matches phi:  {pairing_tests.get('phi_vs_repair_Bal_left', {}).get('consistent')}",
        f"u_right = phi * Bal^-1:      {pairing_tests.get('al_preimage_right_entries_signed')}",
        f"delta_right = u_right-repair:{pairing_tests.get('al_defect_right_entries_signed')}",
        f"u_left = phi * (Bal^T)^-1:   {pairing_tests.get('al_preimage_left_entries_signed')}",
        f"delta_left = u_left-repair:  {pairing_tests.get('al_defect_left_entries_signed')}",
        f"u_right over Source+repair:  {pairing_tests.get('al_preimage_right_source_repair_decomposition')}",
        f"u_left over Source+repair:   {pairing_tests.get('al_preimage_left_source_repair_decomposition')}",
        "```",
        "",
        "## Interpretation",
        "",
        "If `free-to-Sage isomorphism` is true and the T rows vanish in Sage,",
        "the operational basis bridge `pi_N : V_SI -> M^+` is verified for this",
        "small level.  In this smoke case the Atkin-Lehner-twisted plus-pairing",
        "is nondegenerate, but the raw repair vector is not the vector dual to",
        "phi.  The next object is therefore the AL-corrected primal candidate",
        "`u_N` and the defect `delta_N = u_N-r_N`.",
        "",
    ]
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "free_to_sage_isomorphism": payload["free_to_sage_isomorphism"],
        "t_rows_nonzero_in_sage": t_nonzero,
        "repair_adds_sage_rank": payload["repair_adds_sage_rank"],
    }))


if __name__ == "__main__":
    main()
