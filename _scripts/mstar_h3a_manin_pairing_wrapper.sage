#!/usr/bin/env sage
# H3a-B Manin Intersection Pairing Wrapper.
#
# Testet auf einem kleinen Smoke (N=109), ob die strukturelle Identitaet
#
#     phi_N = B_N(r_N, -)   in M_N
#
# stimmt, wobei B_N = M.intersection_pairing() (Sage), r_N der primale
# Restvektor (Repair-Row aus dem Splitlast-Witness) und phi_N der duale
# Nullvektor aus mstar_h3a_residue_line_dual_nullvector.py ist.
#
# Konvention: Nutzt Sages ModularSymbols(Gamma0(N), 2, sign=1). Wenn die
# Spaltenbasis des Witness-Outputs mit Sages manin_basis() übereinstimmt,
# ist der direkte Matrix-Vektor-Vergleich aussagekraeftig. Andernfalls muss
# die Spalten-zu-Manin-Symbol-Abbildung explizit aus dem Witness rekonstruiert
# werden (siehe Hinweis am Ende).
#
# Aufruf (auf Mac Studio):
#     sage _scripts/mstar_h3a_manin_pairing_wrapper.sage \
#          --case-dir _results/h3a_wait_postprocess_smoke_n109_2026-05-16/N109_raw_sign1_splitlast \
#          --phi-json _results/mstar_h3a_residue_line_dual_nullvector_smoke_n109_2026-05-16.json \
#          --out-md _results/mstar_h3a_manin_pairing_wrapper_n109_2026-05-16.md \
#          --out-json _results/mstar_h3a_manin_pairing_wrapper_n109_2026-05-16.json

import argparse
import json
import sys
from pathlib import Path

from sage.all import (
    ModularSymbols,
    Gamma0,
    GF,
    vector,
    matrix,
    ZZ,
)


def signed_lift(value, q):
    v = value % q
    if v > q // 2:
        v -= q
    return v


def load_manifest(case_dir):
    return json.loads((Path(case_dir) / "manifest.json").read_text(encoding="utf-8"))


def load_repair_row(case_dir):
    manifest = load_manifest(case_dir)
    rows_path = Path(case_dir) / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    target = manifest.get("repair_only_row_id")
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("origin") == "repair_only" and row.get("row_id") == target:
                return row, manifest
    raise ValueError(f"repair row not found in {case_dir}")


def load_phi(phi_json):
    data = json.loads(Path(phi_json).read_text(encoding="utf-8"))
    if "results" in data and data["results"]:
        return data["results"][0]
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--phi-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    repair, manifest = load_repair_row(args.case_dir)
    N = int(manifest["level"])
    q = int(manifest["q"])
    ncols = int(manifest["ncols"])

    Fq = GF(q)
    M = ModularSymbols(Gamma0(N), 2, sign=1)
    sage_dim = M.dimension()

    # Sanity: Sage's modular-symbol dimension must agree with the witness ncols
    # before a direct B*r comparison is meaningful.  The RC3 witness columns are
    # currently the sparse_2term_quotient columns after S/I; T-Manin relations
    # are source rows, not yet quotient coordinates.  Sage's ModularSymbols
    # object is already fully T-Manin-reduced, so this usually does not match.
    bases_match = (sage_dim == ncols)

    pairing_method = None
    B = None
    pairing_error = None
    if bases_match:
        try:
            if hasattr(M, "intersection_pairing"):
                B_int = M.intersection_pairing()
                pairing_method = "intersection_pairing"
            else:
                # Sage 10.x exposes the PARI duality matrix here.  It is not
                # the same API as the proposed intersection_pairing(), but it
                # is the available canonical Hecke-compatible pairing matrix in
                # this local runtime when it exists.
                B_int = M._pari_pairing()
                pairing_method = "_pari_pairing"
            B = matrix(Fq, sage_dim, sage_dim, B_int.list(), sparse=False)
        except Exception as exc:
            pairing_error = f"{type(exc).__name__}: {exc}"

    if not bases_match or B is None:
        payload = {
            "tool": "mstar_h3a_manin_pairing_wrapper",
            "case_dir": args.case_dir,
            "N": N,
            "q": q,
            "witness_ncols": ncols,
            "sage_dim": int(sage_dim),
            "bases_match": bool(bases_match),
            "pairing_method": pairing_method,
            "pairing_error": pairing_error,
            "status": "blocked_basis_projection_required"
            if not bases_match
            else "blocked_pairing_unavailable",
            "next_step": (
                "Construct the projection matrix from RC3 S/I quotient columns "
                "to Sage ModularSymbols coordinates before comparing B_N*r_N "
                "with the dual nullvector."
            ),
        }
        Path(args.out_json).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        lines = [
            "# H3a Manin Intersection Pairing Wrapper",
            "",
            f"Case: `{args.case_dir}`",
            f"N: `{N}`, q: `{q}`, witness ncols: `{ncols}`, Sage dim: `{sage_dim}`",
            f"Bases match (ncols == sage_dim): `{bases_match}`",
            f"Pairing method: `{pairing_method}`",
            f"Pairing error: `{pairing_error}`",
            "",
            "## Ergebnis",
            "",
            "`B_N * r_N` wurde bewusst nicht verglichen.",
            "",
            "Der Witness lebt im RC3-Spaltenraum nach S/I-Quotient, während",
            "`ModularSymbols(Gamma0(N),2,sign=1)` in Sage bereits vollständig",
            "T-Manin-reduziert ist. Es fehlt also die Projektionsmatrix vom",
            "Witness-Spaltenraum in die Sage-ModularSymbols-Koordinaten.",
            "",
            "## Nächster Schritt",
            "",
            "Die Basisbrücke konstruieren: RC3-Spalte -> Manin-Symbol-Repräsentant",
            "-> Sage-ModularSymbols-Koordinate. Erst danach ist der Vergleich",
            "`phi_N = B_N(r_N,-)` aussagekräftig.",
            "",
        ]
        Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
        print(json.dumps({"status": payload["status"], "bases_match": bases_match}))
        return

    # Build r_N as a Sage vector in the column basis.
    r_vec = vector(Fq, sage_dim)
    for col, value in repair["row"]:
        col = int(col)
        if col < sage_dim:
            r_vec[col] = Fq(int(value))

    # Predicted phi: B * r (treating B as a column-symmetric pairing).
    phi_pred = B * r_vec

    # Load smoke phi
    smoke = load_phi(args.phi_json)
    smoke_support = sorted(int(k) for k, v in smoke.get("phi_prefix_0_15_signed", {}).items() if v)
    # Better: reconstruct full support from any available field
    # For our N=109 smoke, the smoke gives only the 0..15 prefix; full support
    # range is stored as min/max.  We will only compare the prefix here.
    smoke_prefix_signed = {int(k): int(v) for k, v in smoke.get("phi_prefix_0_15_signed", {}).items()}

    # Predicted prefix in symmetric form
    pred_prefix_signed = {i: signed_lift(int(phi_pred[i]), q) for i in range(min(16, sage_dim))}

    # Compare up to a global scale.  Find the first nonzero index in both.
    scale = None
    consistent = True
    mismatch_examples = []
    for i in range(min(16, sage_dim)):
        s = smoke_prefix_signed.get(i, 0)
        p = pred_prefix_signed.get(i, 0)
        if s == 0 and p == 0:
            continue
        if s == 0 or p == 0:
            consistent = False
            mismatch_examples.append({"i": i, "smoke": s, "pred": p, "note": "one zero, other nonzero"})
            continue
        if scale is None:
            scale = (Fq(s) / Fq(p))
        else:
            current = Fq(s) / Fq(p)
            if current != scale:
                consistent = False
                mismatch_examples.append({"i": i, "smoke": s, "pred": p, "scale_observed": str(current), "scale_expected": str(scale)})

    payload = {
        "tool": "mstar_h3a_manin_pairing_wrapper",
        "case_dir": args.case_dir,
        "N": N,
        "q": q,
        "witness_ncols": ncols,
        "sage_dim": int(sage_dim),
        "bases_match": bool(bases_match),
        "pairing_method": pairing_method,
        "intersection_pairing_present": bool(B is not None),
        "smoke_phi_prefix": smoke_prefix_signed,
        "predicted_phi_prefix": pred_prefix_signed,
        "consistent_up_to_scale": bool(consistent),
        "observed_scale_factor": str(scale) if scale is not None else None,
        "mismatch_examples": mismatch_examples,
    }

    Path(args.out_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# H3a Manin Intersection Pairing Wrapper",
        "",
        f"Case: `{args.case_dir}`",
        f"N: `{N}`, q: `{q}`, witness ncols: `{ncols}`, Sage dim: `{sage_dim}`",
        f"Bases match (ncols == sage_dim): `{bases_match}`",
        "",
        "## Vergleich Smoke phi vs B * r",
        "",
        "| i | smoke phi[i] (signed) | predicted phi[i] (signed) |",
        "|---:|---:|---:|",
    ]
    for i in range(min(16, sage_dim)):
        s = smoke_prefix_signed.get(i, 0)
        p = pred_prefix_signed.get(i, 0)
        lines.append(f"| {i} | {s} | {p} |")
    lines.extend([
        "",
        f"Consistent up to global scale: `{consistent}`",
        f"Observed scale factor: `{scale}`",
        "",
    ])
    if mismatch_examples:
        lines.append("## Mismatches")
        lines.append("")
        for m in mismatch_examples[:10]:
            lines.append(f"- `{m}`")
        lines.append("")
    lines.extend([
        "## Hinweis zur Basis-Konvention",
        "",
        "Wenn `bases_match` false ist, weichen Witness-Spaltenbasis und",
        "`M.manin_basis()` voneinander ab. Dann muss die Spalten-zu-Manin-",
        "Symbol-Abbildung explizit aus dem Witness rekonstruiert werden",
        "(via `mstar_h3a_dump_manin_symbols.py` plus Permutationsmatrix).",
        "Solange die `sparse_2term_quotient`-Konvention identisch ist, sollte",
        "die direkte Identifikation funktionieren.",
        "",
    ])
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "consistent_up_to_scale": consistent,
        "observed_scale": str(scale),
        "bases_match": bases_match,
    }))


if __name__ == "__main__":
    main()
