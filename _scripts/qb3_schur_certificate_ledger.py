#!/usr/bin/env python3
"""Build a Q_B-3 Schur-complement certificate ledger.

The script does not construct the large Atkin-Lehner pairing matrix.  It
records the exact scalar criterion that the pairing oracle has to output and
calibrates it on the N=109 smoke case where Q_B is already known.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


Q_B_PRIME = 3863


def signed_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def div_mod(numerator: int, denominator: int, q: int) -> int:
    return (numerator % q) * pow(denominator % q, -1, q) % q


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def n109_calibration(project_root: Path) -> dict[str, Any]:
    path = project_root / "_results" / "mstar_h3a_pi_to_sage_basis_n109_2026-05-16.json"
    data = load_json(path)
    tests = data["pairing_tests"]
    q = int(data["q"])
    beta = int(tests["phi_on_repair_sage_signed"])
    q_b = int(tests["phi_on_u_right_signed"])
    inverse_diagonal = div_mod(q_b, beta * beta, q)
    schur_scalar = pow(inverse_diagonal, -1, q)
    return {
        "case": "109/raw",
        "source": str(path.relative_to(project_root)),
        "q": q,
        "beta_signed": beta,
        "q_b_signed": signed_lift(q_b, q),
        "det_b_al_signed": int(tests["Bal_determinant_signed"]),
        "inverse_repair_diagonal_mod_q": inverse_diagonal,
        "inverse_repair_diagonal_signed": signed_lift(inverse_diagonal, q),
        "schur_scalar_mod_q": schur_scalar,
        "schur_scalar_signed": signed_lift(schur_scalar, q),
        "criterion_status": "passed",
        "reading": (
            "With beta != 0, Q_B = beta^2 * (G^-1)_{rr}.  In the block "
            "form G=[[A,b],[b^T,c]], the repair Schur scalar is "
            "s=c-b^T A^-1 b and (G^-1)_{rr}=s^-1.  The smoke gives "
            "s=41 mod 3863."
        ),
    }


def restline_case(project_root: Path, result_name: str, label: str) -> dict[str, Any]:
    path = project_root / "_results" / result_name
    data = load_json(path)
    q = int(data["q"])
    beta_mod = int(data["repair_pairing_mod_q"])
    beta_signed = int(data["repair_pairing_signed"])
    heuristic: dict[str, Any] | None = None
    if label == "80224/raw":
        predicted_q_b = -239
        predicted_inverse = predicted_q_b % q
        predicted_schur = pow(predicted_inverse, -1, q)
        heuristic = {
            "source": "_proof-notes/MG_pari_intersection_pairing_alternative_2026-05-18.md",
            "predicted_q_b_signed": predicted_q_b,
            "predicted_schur_scalar_mod_q": predicted_schur,
            "predicted_schur_scalar_signed": signed_lift(predicted_schur, q),
            "use": "falsification heuristic only, not a proof input",
        }
    return {
        "case": label,
        "source": str(path.relative_to(project_root)),
        "q": q,
        "quotient_kernel_dim": int(data["quotient_kernel_dim"]),
        "source_annihilated": bool(data["source_annihilated"]),
        "beta_mod_q": beta_mod,
        "beta_signed": beta_signed,
        "repair_pairing_nonzero": bool(data["repair_pairing_nonzero"]),
        "ready_for_al_scalar": bool(data["ready_for_al_scalar"]),
        "criterion_status": "blocked_missing_al_pairing",
        "needed_certificate": {
            "source_block_A_rank": "full",
            "schur_scalar": "nonzero in GF(q)",
            "equivalent_rank_jump": "rank(G) = rank(A) + 1",
            "q_b_formula": "Q_B = beta^2 / schur_scalar",
        },
        "heuristic_prediction": heuristic,
    }


def missing_case(label: str, note: str) -> dict[str, Any]:
    return {
        "case": label,
        "criterion_status": "blocked_missing_restline_kernel_json",
        "note": note,
    }


def build_ledger(project_root: Path) -> dict[str, Any]:
    cases = [n109_calibration(project_root)]
    cases.append(
        restline_case(
            project_root,
            "mstar_h3a_restline_kernel_quotient_80224_raw_2026-05-17.json",
            "80224/raw",
        )
    )
    cases.append(
        restline_case(
            project_root,
            "mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json",
            "80224/anc",
        )
    )
    cases.append(
        missing_case(
            "120336/raw",
            "RC3c/order data exist, but the restline_kernel_quotient JSON with beta/source-annihilation fields is not present locally.",
        )
    )
    cases.append(
        missing_case(
            "240672/raw",
            "RC3c/order data exist and the minikill status file is present, but the restline_kernel_quotient JSON is not present locally.",
        )
    )
    return {
        "tool": "qb3_schur_certificate_ledger",
        "date": "2026-05-23",
        "project": "HCT/abc",
        "q": Q_B_PRIME,
        "formula": {
            "block_matrix": "G = [[A,b],[b^T,c]] = C B_AL C^T",
            "schur_scalar": "s = c - b^T A^-1 b",
            "inverse_entry": "(G^-1)_{rr} = s^-1",
            "q_b": "Q_B(phi) = beta^2 * s^-1",
            "nonvanishing_criterion": "beta != 0 and s != 0",
        },
        "cases": cases,
    }


def write_markdown(ledger: dict[str, Any], path: Path) -> None:
    lines: list[str] = [
        "# Q_B-3 Schur-Cofactor Ledger",
        "",
        "Datum: 2026-05-23",
        "Projekt: HCT/abc",
        "",
        "## Kriterium",
        "",
        "Für die Source+Repair-Basis schreibe",
        "",
        "```text",
        "G = [[A,b],[b^T,c]] = C B_AL C^T",
        "s = c - b^T A^-1 b",
        "Q_B(phi) = beta^2 * s^-1.",
        "```",
        "",
        "Damit ist Q_B-3 über dem Restkörper äquivalent zu `beta != 0` und",
        "`s != 0`, sofern der Source-Block `A` nichtsingulär ist.  Alternativ",
        "kann der Wrapper den Rangsprung `rank(G) = rank(A)+1` zertifizieren.",
        "",
        "## Fälle",
        "",
        "| Fall | Status | beta | Schur-/Q_B-Information |",
        "|---|---|---:|---|",
    ]
    for case in ledger["cases"]:
        status = case["criterion_status"]
        beta = case.get("beta_signed", "-")
        if status == "passed":
            info = (
                f"Q_B={case['q_b_signed']}, "
                f"(G^-1)_rr={case['inverse_repair_diagonal_signed']}, "
                f"s={case['schur_scalar_signed']} mod {case['q']}"
            )
        elif status == "blocked_missing_al_pairing":
            info = "A vollrangig + s != 0 aus AL-Pairing noch zu berechnen"
            heuristic = case.get("heuristic_prediction")
            if heuristic:
                info += (
                    f"; BSD-Heuristik Q_B={heuristic['predicted_q_b_signed']}, "
                    f"s={heuristic['predicted_schur_scalar_signed']}"
                )
        else:
            info = case.get("note", "")
        lines.append(f"| `{case['case']}` | `{status}` | {beta} | {info} |")
    lines.extend(
        [
            "",
            "## Wrapper-Auftrag",
            "",
            "Der nächste Pairing-Lauf soll nicht die vollständige inverse Matrix",
            "ausgeben.  Ausreichend sind:",
            "",
            "1. Rang von `A`.",
            "2. Schur-Skalar `s` oder äquivalent der letzte Cofaktor.",
            "3. Optional `Q_B = beta^2/s` als abgeleiteter Skalar.",
            "4. Bei `s=0` ein kurzer Nullvektor-/Rank-Failure-Zeuge.",
            "",
            "Der Smoke-Regressionstest ist `N=109`: `s=41 mod 3863` und",
            "`Q_B=722 mod 3863` müssen reproduziert werden.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("_results/qb3_schur_certificate_ledger_2026-05-23.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("_results/qb3_schur_certificate_ledger_2026-05-23.md"),
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    ledger = build_ledger(project_root)
    out_json = project_root / args.out_json
    out_md = project_root / args.out_md
    out_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(ledger, out_md)
    print(json.dumps({"out_json": str(out_json), "out_md": str(out_md)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
