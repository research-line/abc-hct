#!/usr/bin/env python3
"""Prepare the Q_B-3 AL-pairing oracle inputs.

This script is deliberately not the large pairing computation.  It turns the
current restline data into a reviewable interface contract for the next Sage
or Mac job:

* regression: recover the N=109 Schur scalar from the known AL result,
* large-level preflight: extract beta/source-annihilation status,
* size guardrail: estimate why a dense inverse of G is the wrong target,
* certificate contract: list exactly what the AL oracle must output.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


Q = 3863


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def signed_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return int(value)


def div_mod(numerator: int, denominator: int, q: int) -> int:
    return (int(numerator) % q) * pow(int(denominator) % q, -1, q) % q


def int_or_zero(value: Any) -> int:
    return 0 if value is None else int(value)


def mib(bytes_: float) -> float:
    return bytes_ / (1024.0 * 1024.0)


def gib(bytes_: float) -> float:
    return bytes_ / (1024.0 * 1024.0 * 1024.0)


def n109_regression(project_root: Path) -> dict[str, Any]:
    source = project_root / "_results" / "mstar_h3a_pi_to_sage_basis_n109_2026-05-16.json"
    data = load_json(source)
    tests = data["pairing_tests"]
    q = int(data["q"])
    beta = int(tests["phi_on_repair_sage_signed"])
    q_b = int(tests["phi_on_u_right_signed"])
    inverse_repair_diagonal = div_mod(q_b, beta * beta, q)
    schur_scalar = pow(inverse_repair_diagonal, -1, q)
    return {
        "case": "109/raw",
        "kind": "regression",
        "source": str(source.relative_to(project_root)),
        "q": q,
        "beta_signed": beta,
        "q_b_signed": signed_lift(q_b, q),
        "inverse_repair_diagonal_mod_q": inverse_repair_diagonal,
        "inverse_repair_diagonal_signed": signed_lift(inverse_repair_diagonal, q),
        "schur_scalar_mod_q": schur_scalar,
        "schur_scalar_signed": signed_lift(schur_scalar, q),
        "expected": {
            "q_b_signed": 722,
            "schur_scalar_mod_q": 41,
        },
        "passes": signed_lift(q_b, q) == 722 and schur_scalar == 41,
    }


def restline_preflight(project_root: Path, result_name: str, label: str) -> dict[str, Any]:
    source = project_root / "_results" / result_name
    data = load_json(source)
    q = int(data["q"])
    d = int(data["quotient_ncols"])
    source_dim = d - 1
    dense_g_entries = d * d
    source_block_entries = source_dim * source_dim
    # Sage dense matrices over GF(p) generally cost much more than 8 bytes per
    # entry, but int64 is a useful absolute lower bound for a no-go estimate.
    dense_g_int64_gib = gib(dense_g_entries * 8)
    dense_a_int64_gib = gib(source_block_entries * 8)
    gf_uint16_lower_mib = mib(dense_g_entries * 2)
    pairing_count_symmetric = d * (d + 1) // 2
    return {
        "case": label,
        "kind": "large_preflight",
        "source": str(source.relative_to(project_root)),
        "q": q,
        "quotient_ncols": d,
        "source_block_dim": source_dim,
        "hecke_rows": int(data["hecke_rows"]),
        "quotient_rank": int(data["quotient_rank"]),
        "quotient_kernel_dim": int(data["quotient_kernel_dim"]),
        "kernel_support_size": int(data.get("kernel_support_size", 0)),
        "matrix_entries_projected_hecke": int_or_zero(data.get("matrix_entries", 0)),
        "beta_signed": int(data["repair_pairing_signed"]),
        "beta_mod_q": int(data["repair_pairing_mod_q"]),
        "source_annihilated": bool(data["source_annihilated"]),
        "ready_for_al_scalar": bool(data["ready_for_al_scalar"]),
        "dense_no_go": {
            "G_entries": dense_g_entries,
            "A_entries": source_block_entries,
            "symmetric_pairings_needed_if_full_G": pairing_count_symmetric,
            "uint16_lower_bound_G_MiB": round(gf_uint16_lower_mib, 2),
            "int64_lower_bound_G_GiB": round(dense_g_int64_gib, 3),
            "int64_lower_bound_A_GiB": round(dense_a_int64_gib, 3),
            "warning": (
                "A dense inverse is not the primary target.  The next job "
                "should emit rank(A), the Schur scalar s, and a failure witness "
                "if s=0 or A is singular."
            ),
        },
        "needed_certificate": {
            "source_block_rank": source_dim,
            "schur_scalar_mod_q": "nonzero",
            "q_b_formula": "Q_B = beta^2 / s",
            "failure_outputs": [
                "rank(A) if singular",
                "nullvector for A or G when available",
                "repair Schur scalar s when computable",
            ],
        },
    }


def missing_preflight(label: str, note: str) -> dict[str, Any]:
    return {
        "case": label,
        "kind": "missing_input",
        "status": "blocked",
        "note": note,
    }


def build_payload(project_root: Path) -> dict[str, Any]:
    cases = [
        n109_regression(project_root),
        restline_preflight(
            project_root,
            "mstar_h3a_restline_kernel_quotient_80224_raw_2026-05-17.json",
            "80224/raw",
        ),
        restline_preflight(
            project_root,
            "mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json",
            "80224/anc",
        ),
        missing_preflight(
            "120336/raw",
            "No local restline_kernel_quotient JSON yet; rank/order artifacts are not a beta/source-annihilation substitute.",
        ),
        missing_preflight(
            "240672/raw",
            "Restline kernel quotient is still running on the Mac; wait for the JSON/MD before Q_B-1/Q_B-2 status.",
        ),
    ]
    return {
        "tool": "qb3_pairing_oracle_preflight",
        "date": "2026-05-23",
        "project": "HCT/abc",
        "q": Q,
        "purpose": "Narrow the next AL-pairing job to a Schur-certificate oracle.",
        "formula": {
            "block_matrix": "G = [[A,b],[b^T,c]] = C B_AL C^T",
            "schur_scalar": "s = c - b^T A^-1 b",
            "q_b": "Q_B(phi) = beta^2 / s",
            "certificate": "beta != 0, rank(A)=dim(A), s != 0",
        },
        "cases": cases,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines: list[str] = [
        "# Q_B-3 Pairing-Oracle Preflight",
        "",
        "Datum: 2026-05-23",
        "Projekt: HCT/abc",
        "",
        "## Zweck",
        "",
        "Dieses Preflight trennt die fertigen Restlinien-Inputs vom noch offenen",
        "Atkin-Lehner-Pairing.  Der nächste große Lauf soll keine volle inverse",
        "Matrix ausgeben, sondern ein kleines Schur-Zertifikat:",
        "",
        "```text",
        "G = [[A,b],[b^T,c]] = C B_AL C^T",
        "s = c - b^T A^-1 b",
        "Q_B(phi) = beta^2 / s.",
        "```",
        "",
        "Pflichtausgabe: `rank(A)`, `s`, optional `Q_B`, und bei Fehlern ein",
        "Rank- oder Nullvektor-Zeuge.",
        "",
        "## Regression",
        "",
    ]
    reg = payload["cases"][0]
    lines.extend(
        [
            f"- `109/raw`: `passes={reg['passes']}`, `beta={reg['beta_signed']}`, "
            f"`s={reg['schur_scalar_signed']} mod {reg['q']}`, "
            f"`Q_B={reg['q_b_signed']}`.",
            "- Dieser Wert ist der harte Smoke-Test für jeden Schur-Wrapper.",
            "",
            "## Große Fälle",
            "",
            "| Fall | Status | beta | Dimension | Schur-Auftrag |",
            "|---|---|---:|---:|---|",
        ]
    )
    for case in payload["cases"][1:]:
        if case["kind"] == "large_preflight":
            ready = case["ready_for_al_scalar"]
            d = case["quotient_ncols"]
            beta = case["beta_signed"]
            status = "ready" if ready else "blocked"
            order = (
                f"`rank(A)={case['source_block_dim']}`, `s!=0`, "
                "`Q_B=beta^2/s`"
            )
            lines.append(f"| `{case['case']}` | `{status}` | {beta} | {d} | {order} |")
        else:
            lines.append(f"| `{case['case']}` | `blocked` | - | - | {case['note']} |")
    lines.extend(["", "## Größen-Guardrail", ""])
    for case in payload["cases"][1:]:
        if case["kind"] != "large_preflight":
            continue
        no_go = case["dense_no_go"]
        lines.extend(
            [
                f"### `{case['case']}`",
                "",
                f"- `G` hätte `{no_go['G_entries']}` Einträge; "
                f"int64-Untergrenze `{no_go['int64_lower_bound_G_GiB']} GiB`, "
                f"GF(3863)-uint16-Untergrenze `{no_go['uint16_lower_bound_G_MiB']} MiB`.",
                f"- `A` hätte `{no_go['A_entries']}` Einträge; "
                f"int64-Untergrenze `{no_go['int64_lower_bound_A_GiB']} GiB`.",
                f"- Voll-symmetrische Pairing-Auswertung: "
                f"`{no_go['symmetric_pairings_needed_if_full_G']}` Paarungen.",
                "- Entscheidung: kein dichtes `G^-1`; nur Schur-Cofactor-/Rangsprung-Zertifikat.",
                "",
            ]
        )
    lines.extend(
        [
            "## Nächster Befehl",
            "",
            "Der nächste Implementierungsschritt ist ein Sage-/Mac-Wrapper mit der",
            "Schnittstelle:",
            "",
            "```text",
            "sage _scripts/mstar_h3a_qb3_schur_oracle.sage \\",
            "  --case-dir <splitlast-case> \\",
            "  --restline-json <restline_kernel_quotient.json> \\",
            "  --out-json <certificate.json> \\",
            "  --out-md <certificate.md> \\",
            "  --mode schur-certificate",
            "```",
            "",
            "Der Wrapper gilt erst als einsatzbereit, wenn er auf `N=109` `s=41`",
            "und `Q_B=722 mod 3863` reproduziert.",
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
        default=Path("_results/qb3_pairing_oracle_preflight_2026-05-23.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("_results/qb3_pairing_oracle_preflight_2026-05-23.md"),
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    payload = build_payload(project_root)
    out_json = project_root / args.out_json
    out_md = project_root / args.out_md
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, out_md)
    print(json.dumps({"out_json": str(out_json), "out_md": str(out_md)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
