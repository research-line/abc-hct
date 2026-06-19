#!/usr/bin/env python3
"""Local status checker for the R1 faithful-AL 80224/raw route.

This script intentionally does not run Sage or any matrix operation. It only
reads the current Mac-pulled status/final files and verifies that the local
canonical production driver matches the matrix-free Schur route.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-16"

DEFAULT_STATUS_JSON = "_results/r1_faithful_al_80224_raw_2026-06-14.status.json"
DEFAULT_FINAL_JSON = "_results/r1_faithful_al_80224_raw_2026-06-14.json"
DEFAULT_FINAL_MD = "_results/r1_faithful_al_80224_raw_2026-06-14.md"
DEFAULT_SCRIPT = "_scripts/mstar_h3a_qb3_wiedemann_production.sage"
DEFAULT_ASUS_ALIAS = "_scripts/mstar_h3a_qb3_wiedemann_production-ASUS-GEI.sage"
DEFAULT_OUT_JSON = f"_results/r1_faithful_al_80224_status_check_{DATE}.json"
DEFAULT_OUT_MD = f"_results/r1_faithful_al_80224_status_check_{DATE}.md"
EXPECTED_OPERATOR_KIND = "pari_tensor_solve_atkin_lehner_twist"
EXPECTED_PAIRING_KIND = "_pari_tensor_solve"
DEFAULT_SUFFIX_TERMS = 4


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def file_info(path: Path, hash_file: bool = False) -> dict[str, Any]:
    info: dict[str, Any] = {"path": rel(path), "exists": path.exists()}
    if path.exists() and path.is_file():
        stat = path.stat()
        info.update(
            {
                "bytes": int(stat.st_size),
                "mtime_local": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            }
        )
        if hash_file:
            info["sha256"] = file_sha256(path)
    return info


def check(name: str, passed: bool | None, detail: str) -> dict[str, Any]:
    if passed is True:
        state = "pass"
    elif passed is False:
        state = "fail"
    else:
        state = "unknown"
    return {"name": name, "state": state, "detail": detail}


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    status_path = ROOT / args.status_json
    final_json_path = ROOT / args.final_json
    final_md_path = ROOT / args.final_md
    script_path = ROOT / args.script
    asus_alias_path = ROOT / args.asus_alias

    status = load_json(status_path)
    final = load_json(final_json_path)

    script_hash = file_sha256(script_path)
    alias_hash = file_sha256(asus_alias_path)
    target_rank = (
        (final or {}).get("target_rank")
        or (final or {}).get("rank_A_target")
        or (status or {}).get("target_rank")
    )
    sequence_length = (status or {}).get("sequence_length") or (final or {}).get("sequence_length_target")
    expected_sequence_length = None
    if isinstance(target_rank, int):
        expected_sequence_length = 2 * target_rank + int(args.suffix_terms)

    checks: list[dict[str, Any]] = [
        check("status_json_present", status is not None, rel(status_path)),
        check("canonical_script_present", script_path.exists(), rel(script_path)),
        check("canonical_script_has_new_hash", script_hash is not None, script_hash or "missing"),
        check(
            "asus_alias_matches_canonical",
            (script_hash == alias_hash) if script_hash and alias_hash else None,
            f"canonical={script_hash}; alias={alias_hash}",
        ),
        check(
            "sequence_length_matches_rank_target",
            (sequence_length == expected_sequence_length)
            if sequence_length is not None and expected_sequence_length is not None
            else None,
            f"sequence_length={sequence_length}; expected={expected_sequence_length}",
        ),
        check(
            "status_pairing_tensor_solve",
            ((status or {}).get("pairing_kind") == EXPECTED_PAIRING_KIND) if status else None,
            str((status or {}).get("pairing_kind")),
        ),
        check(
            "status_primary_pairing_not_materialized",
            ((status or {}).get("primary_pairing_materialized") is False) if status else None,
            str((status or {}).get("primary_pairing_materialized")),
        ),
    ]

    final_checks: list[dict[str, Any]] = [
        check("final_json_present", final is not None, rel(final_json_path)),
        check("final_md_present", final_md_path.exists(), rel(final_md_path)),
    ]
    if final:
        rank_target = final.get("rank_A_target") or final.get("target_rank")
        final_checks.extend(
            [
                check(
                    "faithful_al_certificate_found",
                    final.get("faithful_al_certificate_found") is True,
                    str(final.get("faithful_al_certificate_found")),
                ),
                check(
                    "rank_A_full",
                    final.get("rank_A_full") is True,
                    str(final.get("rank_A_full")),
                ),
                check(
                    "rank_A_matches_target",
                    final.get("rank_A") == rank_target,
                    f"rank_A={final.get('rank_A')}; target={rank_target}",
                ),
                check("schur_nonzero", final.get("schur_nonzero") is True, str(final.get("schur_nonzero"))),
                check(
                    "operator_kind",
                    final.get("operator_kind") == EXPECTED_OPERATOR_KIND,
                    str(final.get("operator_kind")),
                ),
                check(
                    "primary_pairing_not_materialized",
                    final.get("primary_pairing_materialized") is False,
                    str(final.get("primary_pairing_materialized")),
                ),
            ]
        )

    hard_final_ok = bool(final) and all(c["state"] == "pass" for c in final_checks)
    if hard_final_ok:
        verdict = "faithful_al_certificate_ready"
    elif final:
        verdict = "final_output_present_but_not_certified"
    elif status:
        phase = str(status.get("phase", ""))
        verdict = "running_or_incomplete" if phase != "finished" else "finished_status_without_final_output"
    else:
        verdict = "missing_status"

    return {
        "date": DATE,
        "tool": "r1_faithful_al_80224_status_check",
        "claim_upgrade": False,
        "verdict": verdict,
        "status_file": file_info(status_path),
        "final_json_file": file_info(final_json_path),
        "final_md_file": file_info(final_md_path),
        "canonical_script": file_info(script_path, hash_file=True),
        "asus_alias_script": file_info(asus_alias_path, hash_file=True),
        "current_status": {
            "phase": (status or {}).get("phase"),
            "seconds": (status or {}).get("seconds"),
            "target_rank": target_rank,
            "quotient_dim": (status or {}).get("quotient_dim") or (final or {}).get("quotient_dim"),
            "sequence_length": sequence_length,
            "sequence_length_expected": expected_sequence_length,
            "pairing_kind": (status or {}).get("pairing_kind"),
            "primary_pairing_materialized": (status or {}).get("primary_pairing_materialized"),
            "P_sha256": (status or {}).get("P_sha256"),
            "T_sha256": (status or {}).get("T_sha256") or (status or {}).get("pairing_tensor_or_E_sha256"),
            "W_sha256": (status or {}).get("W_sha256"),
        },
        "checks": checks,
        "final_checks": final_checks,
        "next_action": (
            "Keinen lokalen Sage-Lauf starten. Auf Mac-Final-JSON/MD warten; "
            "danach faithful_al_certificate_found=true, rank_A_full=true, "
            "rank_A=target, schur_nonzero=true und nicht-identische "
            "Tensor-Solve-Operator-Metadaten verlangen."
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = payload["current_status"]
    lines = [
        "# R1 faithful-AL 80224/raw Statuscheck",
        "",
        f"Datum: `{payload['date']}`",
        f"Verdikt: `{payload['verdict']}`",
        "Claim-Upgrade: `false`",
        "",
        "## Laufstatus",
        "",
        f"- Phase: `{status.get('phase')}`",
        f"- Sekunden: `{status.get('seconds')}`",
        f"- Zielrang: `{status.get('target_rank')}`",
        f"- Sequenzlänge: `{status.get('sequence_length')}` "
        f"(erwartet `{status.get('sequence_length_expected')}`)",
        f"- Pairing: `{status.get('pairing_kind')}`",
        f"- Primary Pairing materialisiert: `{status.get('primary_pairing_materialized')}`",
        "",
        "## Prüfungen",
        "",
    ]
    for row in payload["checks"] + payload["final_checks"]:
        lines.append(f"- `{row['state']}` — {row['name']}: {row['detail']}")
    lines.extend(
        [
            "",
            "## Nächster Schritt",
            "",
            payload["next_action"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-json", default=DEFAULT_STATUS_JSON)
    parser.add_argument("--final-json", default=DEFAULT_FINAL_JSON)
    parser.add_argument("--final-md", default=DEFAULT_FINAL_MD)
    parser.add_argument("--script", default=DEFAULT_SCRIPT)
    parser.add_argument("--asus-alias", default=DEFAULT_ASUS_ALIAS)
    parser.add_argument("--suffix-terms", type=int, default=DEFAULT_SUFFIX_TERMS)
    parser.add_argument("--out-json", default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", default=DEFAULT_OUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(ROOT / args.out_json, payload)
    write_md(ROOT / args.out_md, payload)
    print(json.dumps({"verdict": payload["verdict"], "out_json": args.out_json}, ensure_ascii=False))


if __name__ == "__main__":
    main()
