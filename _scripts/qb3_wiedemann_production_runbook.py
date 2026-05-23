#!/usr/bin/env python3
"""Build the Q_B-3 Wiedemann production runbook.

This is deliberately a ledger, not a launcher.  It fixes the certificate
contract for the large 80224 source-Gram rank runs without starting another
heavy computation on the workstation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-23"
DEFAULT_GUARDS = [
    ROOT / "_results" / "mstar_h3a_qb3_wiedemann_smoke_80224_raw_guard_2026-05-23.json",
    ROOT / "_results" / "mstar_h3a_qb3_wiedemann_smoke_80224_anc_guard_2026-05-23.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def analyze_guard(path: Path, seed_count: int, suffix_terms: int) -> dict[str, Any]:
    data = load_json(path)
    n = int(data["rank_A_target"])
    sequence_length = 2 * n + suffix_terms
    matvecs_per_seed = max(0, sequence_length - 1)
    level = int(data["level"])
    mode = str(data.get("mode") or Path(data["pi_json"]).stem.split("_")[-2])
    q = int(data["q"])
    certificate_name = (
        f"mstar_h3a_qb3_wiedemann_certificate_{level}_{mode}_{DATE}.json"
    )
    verify_name = (
        f"qb3_wiedemann_certificate_verify_{level}_{mode}_{DATE}.json"
    )
    return {
        "guard_json": str(path.relative_to(ROOT)),
        "guard_sha256": sha256_file(path),
        "level": level,
        "mode": mode,
        "q": q,
        "target_rank": n,
        "sequence_length_per_seed": sequence_length,
        "matvecs_per_seed": matvecs_per_seed,
        "seed_count_budget": seed_count,
        "matvec_budget_if_all_seeds_used": matvecs_per_seed * seed_count,
        "expected_success_condition": (
            "some seed has Berlekamp-Massey degree target_rank and nonzero "
            "last connection coefficient"
        ),
        "required_certificate_fields": [
            "level",
            "mode",
            "q",
            "target_rank",
            "seed",
            "degree",
            "sequence_length",
            "connection_coefficients_mod_q",
            "sequence_mod_q",
            "case_manifest_sha256",
            "pi_json_sha256",
            "operator_script_sha256",
        ],
        "certificate_json": f"_results/{certificate_name}",
        "local_verifier_json": f"_results/{verify_name}",
        "local_verifier_command": (
            "python ./_scripts/qb3_wiedemann_certificate_verify.py "
            f"--certificate ./_results/{certificate_name} "
            f"--expected-rank {n} --expected-q {q} "
            f"--out-json ./_results/{verify_name} "
            f"--out-md ./_results/{verify_name[:-5]}.md"
        ),
    }


def build_payload(guards: list[Path], seed_count: int, suffix_terms: int) -> dict[str, Any]:
    cases = [analyze_guard(path.resolve(), seed_count, suffix_terms) for path in guards]
    return {
        "tool": "qb3_wiedemann_production_runbook",
        "date": DATE,
        "purpose": (
            "Fix the production certificate contract for the 80224 Q_B-3 "
            "source-Gram rank test rank(A)=10567."
        ),
        "does_start_computation": False,
        "algorithm": [
            "Build the matrix-free operator A v = C_source B_AL C_source^T v.",
            "For each deterministic seed, generate s_k = u^T A^k v.",
            "Run Berlekamp-Massey on the scalar sequence.",
            "Accept a seed only if degree = target_rank and the final coefficient is nonzero.",
            "Export the full sequence and connection coefficients for local verification.",
        ],
        "suffix_terms": suffix_terms,
        "cases": cases,
    }


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# Q_B-3 Wiedemann Production Runbook",
        "",
        f"Datum: `{payload['date']}`",
        "",
        "Dieses Ledger startet keinen Großlauf. Es legt nur fest, was ein",
        "produktionsfähiges Zertifikat für den Source-Gram-Rang liefern muss.",
        "",
        "## Algorithmus",
        "",
    ]
    for item in payload["algorithm"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Fälle",
        "",
        "| Level | Mode | q | target rank | seq/seed | matvecs/seed | seed budget | max matvecs |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ])
    for case in payload["cases"]:
        lines.append(
            "| {level} | {mode} | {q} | {target_rank} | {sequence_length_per_seed} | "
            "{matvecs_per_seed} | {seed_count_budget} | {matvec_budget_if_all_seeds_used} |".format(
                **case
            )
        )
    lines.extend([
        "",
        "## Pflichtfelder",
        "",
        "Jedes Produktionszertifikat muss mindestens diese Felder enthalten:",
        "",
        "```text",
        "\n".join(payload["cases"][0]["required_certificate_fields"]),
        "```",
        "",
        "## Lokale Verifikation",
        "",
    ])
    for case in payload["cases"]:
        lines.extend([
            f"### {case['level']} / {case['mode']}",
            "",
            "```powershell",
            case["local_verifier_command"],
            "```",
            "",
        ])
    lines.extend([
        "## Beweislogik",
        "",
        "Ein akzeptiertes Zertifikat beweist den portablen Sequenzteil:",
        "`degree = n` und letzter Rekurrenzkoeffizient ungleich null. Zusammen",
        "mit dem authentifizierten Matvec-Transcript für",
        "`A=C_source B_AL C_source^T` ist das die rechnerische Form von",
        "`rank(A)=n`.",
        "",
    ])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guards", nargs="*", type=Path, default=DEFAULT_GUARDS)
    parser.add_argument("--seed-count", type=int, default=16)
    parser.add_argument("--suffix-terms", type=int, default=4)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "_results" / f"qb3_wiedemann_production_runbook_{DATE}.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "_results" / f"qb3_wiedemann_production_runbook_{DATE}.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.guards, args.seed_count, args.suffix_terms)
    args.out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(payload, args.out_md)
    print(json.dumps({
        "cases": len(payload["cases"]),
        "does_start_computation": payload["does_start_computation"],
        "matvecs_per_seed": [case["matvecs_per_seed"] for case in payload["cases"]],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
