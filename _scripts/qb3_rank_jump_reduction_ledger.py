#!/usr/bin/env python3
"""Q_B-3 rank-jump reduction ledger.

This script records the part of the Q_B-3 rank-jump target that is already
forced by the restline-kernel outputs:

    source rank = d - 1,
    phi(source) = 0,
    phi(repair) != 0

imply

    rank(source + repair) = d.

With the standard nondegeneracy of the Atkin-Lehner twisted intersection
pairing on M^+, this makes the full Gram block G automatically full rank.
The remaining local Q_B-3 task is therefore the source-only Gram rank:

    rank(A) = d - 1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-23"


DEFAULT_CASES = [
    ROOT / "_results" / "mstar_h3a_restline_kernel_quotient_80224_raw_2026-05-17.json",
    ROOT / "_results" / "mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(path: Path) -> dict[str, Any]:
    data = load_json(path)
    d = int(data["quotient_ncols"])
    source_rank = int(data["quotient_rank"])
    kernel_dim = int(data["quotient_kernel_dim"])
    source_annihilated = bool(data.get("source_annihilated"))
    repair_pairing_nonzero = bool(data.get("repair_pairing_nonzero"))
    beta_signed = int(data.get("repair_pairing_signed", 0))
    hecke_rows = int(data.get("hecke_rows", 0))

    source_hyperplane_certified = (
        source_rank == d - 1
        and kernel_dim == 1
        and hecke_rows == d - 1
        and source_annihilated
    )
    repair_outside_source = source_hyperplane_certified and repair_pairing_nonzero
    source_repair_basis_certified = repair_outside_source
    full_gram_rank_by_theorem = source_repair_basis_certified

    return {
        "input_json": str(path.relative_to(ROOT)),
        "level": int(data["level"]),
        "mode": data.get("mode"),
        "q": int(data["q"]),
        "quotient_dim": d,
        "source_rows": hecke_rows,
        "source_rank": source_rank,
        "kernel_dim": kernel_dim,
        "source_annihilated": source_annihilated,
        "beta_signed": beta_signed,
        "repair_pairing_nonzero": repair_pairing_nonzero,
        "source_hyperplane_certified": source_hyperplane_certified,
        "repair_outside_source": repair_outside_source,
        "source_repair_basis_certified": source_repair_basis_certified,
        "full_gram_rank_by_theorem": full_gram_rank_by_theorem,
        "rank_G_target": d,
        "rank_G_status": "closed_by_basis_plus_B_AL_nondegenerate"
        if full_gram_rank_by_theorem
        else "open",
        "rank_A_target": d - 1,
        "rank_A_status": "open",
        "remaining_qb3_task": f"certify rank(A)={d - 1} for source-only B_AL Gram block",
    }


def build_payload(paths: list[Path]) -> dict[str, Any]:
    rows = [analyze(path) for path in paths]
    return {
        "tool": "qb3_rank_jump_reduction_ledger",
        "date": DATE,
        "interpretation": (
            "rank(G) is reduced to the standard nondegeneracy theorem for B_AL "
            "once Source+Repair is a quotient basis; Q_B-3 remains rank(A)."
        ),
        "rows": rows,
        "all_source_repair_basis_certified": all(
            row["source_repair_basis_certified"] for row in rows
        ),
        "all_rank_G_closed_by_reduction": all(
            row["full_gram_rank_by_theorem"] for row in rows
        ),
        "open_tasks": [
            {
                "level": row["level"],
                "mode": row["mode"],
                "task": row["remaining_qb3_task"],
            }
            for row in rows
            if row["rank_A_status"] == "open"
        ],
    }


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = [
        "# Q_B-3 Rank-Jump Reduction Ledger",
        "",
        f"Datum: `{payload['date']}`",
        "",
        "## Kernbefund",
        "",
        "Aus den vorhandenen Restlinien-JSONs folgt bereits:",
        "",
        "```text",
        "source rank = d-1",
        "phi(source) = 0",
        "phi(repair) = beta != 0",
        "```",
        "",
        "Also liegt die Repair-Zeile nicht im Source-Hyperplane, und",
        "`Source + Repair` ist eine Quotientenbasis. Mit der Standard-",
        "Nichtdegeneriertheit von `B_AL` ist der volle Gramblock",
        "`G=C B_AL C^T` damit vollrangig. Der offene Q_B-3-Kern ist nur noch",
        "der Source-only-Block `A`.",
        "",
        "## Fälle",
        "",
        "| Level | Mode | d | source rank | beta | Source+Repair Basis | rank(G) | offen |",
        "|---:|---|---:|---:|---:|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {level} | {mode} | {quotient_dim} | {source_rank} | {beta_signed} | "
            "{basis} | {rank_g} | rank(A)={rank_a_target} |".format(
                level=row["level"],
                mode=row["mode"],
                quotient_dim=row["quotient_dim"],
                source_rank=row["source_rank"],
                beta_signed=row["beta_signed"],
                basis="ja" if row["source_repair_basis_certified"] else "nein",
                rank_g=row["rank_G_status"],
                rank_a_target=row["rank_A_target"],
            )
        )

    lines.extend(
        [
            "",
            "## Reduktion",
            "",
            "Für jeden gelisteten Fall ist `rank(G)=d` nicht mehr der",
            "rechnerische Engpass. Es genügt, `rank(A)=d-1` für den",
            "Source-only-Gramblock zu zertifizieren. Bei `beta != 0` folgt dann",
            "`s != 0` und damit `Q_B(phi) != 0` über die Schur-Identität.",
            "",
            "## Nächster Verifier",
            "",
            "Der nächste Großlevel-Verifier sollte daher nicht `G^-1` und auch",
            "nicht sofort `A*x=b` berechnen, sondern zuerst ein matrixfreies",
            "Rangzertifikat für `A` erzeugen.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="*", type=Path, default=DEFAULT_CASES)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "_results" / f"qb3_rank_jump_reduction_ledger_{DATE}.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "_results" / f"qb3_rank_jump_reduction_ledger_{DATE}.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload([path.resolve() for path in args.inputs])
    args.out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(payload, args.out_md)
    print(json.dumps({
        "rows": len(payload["rows"]),
        "all_source_repair_basis_certified": payload["all_source_repair_basis_certified"],
        "all_rank_G_closed_by_reduction": payload["all_rank_G_closed_by_reduction"],
        "open_tasks": payload["open_tasks"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
