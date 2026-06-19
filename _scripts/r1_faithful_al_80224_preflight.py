#!/usr/bin/env python3
"""Lightweight preflight for the R1 faithful-AL 80224/raw certificate.

This script intentionally does not run Sage or any matrix operation.  It checks
that the existing 80224/raw inputs are present, classifies the old identity
certificate as insufficient for faithful AL, and emits a handoff report for the
next Mac Studio job.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-14"

DEFAULT_CASE_DIR = (
    "_results/h3a_residue_line_witness_80224_raw_remod_q5077_2026-05-23/"
    "N80224_raw_sign1_splitlast"
)
DEFAULT_PI_JSON = (
    "_results/mstar_h3a_restline_kernel_quotient_remod_q5077_"
    "80224_raw_mac_2026-05-24.json"
)
DEFAULT_IDENTITY_JSON = (
    "_results/mstar_h3a_qb3_wiedemann_production_remod_q5077_"
    "80224_raw_identity_mac_2026-05-26.json"
)
DEFAULT_QUEUE_JOB = "_compute_queue/jobs/qb3_wiedemann_80224_raw_2026-05-23.json"
DEFAULT_OUT_JSON = f"_results/r1_faithful_al_80224_preflight_{DATE}.json"
DEFAULT_OUT_MD = f"_results/r1_faithful_al_80224_preflight_{DATE}.md"


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


def file_info(path: Path, hash_file: bool = False) -> dict[str, Any]:
    exists = path.exists()
    info: dict[str, Any] = {
        "path": str(path.relative_to(ROOT) if path.is_absolute() else path),
        "exists": exists,
    }
    if exists and path.is_file():
        stat = path.stat()
        info.update(
            {
                "bytes": int(stat.st_size),
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
        )
        if hash_file:
            info["sha256"] = file_sha256(path)
    return info


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    case_dir = ROOT / args.case_dir
    pi_json = ROOT / args.pi_json
    identity_json = ROOT / args.identity_json
    queue_job = ROOT / args.queue_job

    manifest_path = case_dir / "manifest.json"
    manifest = load_json(manifest_path) or {}
    rows_file = manifest.get("rows_file", "mixed_rows.jsonl")
    rows_path = case_dir / str(rows_file)
    pi_data = load_json(pi_json) or {}
    identity_data = load_json(identity_json) or {}
    queue_data = load_json(queue_job) or {}

    identity_cert = identity_data.get("accepted_certificate") or {}
    identity_kind = identity_data.get("pairing_kind")
    identity_ok = bool(identity_data.get("accepted_certificate_found"))
    identity_target_rank = identity_data.get("target_rank")
    identity_degree = identity_cert.get("degree")

    inputs_ready = all(
        [
            case_dir.exists(),
            manifest_path.exists(),
            rows_path.exists(),
            pi_json.exists(),
            bool(pi_data.get("free_columns")),
        ]
    )

    old_job_command = queue_data.get("command", "")
    old_job_identity_like = (
        "mstar_h3a_qb3_wiedemann_production_finite_pairing.sage" in old_job_command
        and "--bal-mode sign0-finite" in old_job_command
    )

    return {
        "tool": "r1_faithful_al_80224_preflight",
        "date": DATE,
        "status": "ready_for_draft_job" if inputs_ready else "missing_inputs",
        "purpose": "Preflight only; no Sage and no heavy computation executed.",
        "inputs_ready": inputs_ready,
        "case": {
            "label": "80224/raw q'=5077 remod",
            "case_dir": rel(case_dir),
            "manifest": file_info(manifest_path, hash_file=True),
            "rows": file_info(rows_path, hash_file=bool(args.hash_rows)),
            "manifest_level": manifest.get("level"),
            "manifest_q": manifest.get("q"),
            "manifest_mode": manifest.get("mode"),
            "manifest_ncols": manifest.get("ncols"),
        },
        "pi_json": {
            "file": file_info(pi_json, hash_file=True),
            "free_columns": len(pi_data.get("free_columns", [])),
            "kernel_entries": len(pi_data.get("kernel_entries_mod_q", [])),
            "repair_entries": len(
                pi_data.get("repair_projected_entries_mod_q")
                or pi_data.get("projected_repair_entries_mod_q")
                or []
            ),
            "ready_for_al_scalar": pi_data.get("ready_for_al_scalar"),
        },
        "existing_identity_certificate": {
            "file": file_info(identity_json, hash_file=True),
            "accepted_certificate_found": identity_ok,
            "pairing_kind": identity_kind,
            "target_rank": identity_target_rank,
            "degree": identity_degree,
            "constant_signed": identity_cert.get("constant_signed"),
            "sufficient_for_r1_faithful_al": False,
            "reason": (
                "This is the old identity-pairing fingerprint. R1 now needs a "
                "faithful AL certificate for rank(A) and s_N != 0, not a "
                "reactivation of the identity run."
            ),
        },
        "queue_safety": {
            "old_job": file_info(queue_job, hash_file=True),
            "old_job_status": queue_data.get("status"),
            "old_job_identity_like": old_job_identity_like,
            "do_not_reactivate_old_job": True,
            "reason": (
                "The old job targets the identity finite-pairing production path "
                "and is marked blocked/completed-via-manual identity output."
            ),
        },
        "next_mac_job_contract": {
            "goal": "matrix-free faithful-AL Schur certificate for 80224/raw",
            "must_prove": [
                "rank(A) is full for the real C_src source block",
                "Schur scalar s_N is nonzero over q=5077 and ideally a second q",
                "operator construction is not identity-pairing",
            ],
            "must_not_do": [
                "do not start local Sage on the laptop",
                "do not mark identity-pairing output as faithful AL",
                "do not reactivate qb3_wiedemann_80224_raw_2026-05-23 without changing the operator path",
            ],
            "suggested_first_artifact": "_proof-notes/MG_r1_faithful_al_80224_job_plan_2026-06-14.md",
        },
    }


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    case = payload["case"]
    pi = payload["pi_json"]
    cert = payload["existing_identity_certificate"]
    safety = payload["queue_safety"]
    lines = [
        "# R1 Faithful-AL 80224/raw Preflight",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Befund",
        "",
        "- Lokaler Lauf: keiner. Dieses Preflight liest nur Metadaten und JSON-Dateien.",
        f"- Inputs bereit: `{payload['inputs_ready']}`.",
        f"- Case: `{case['case_dir']}`; Level `{case['manifest_level']}`, q `{case['manifest_q']}`, "
        f"ncols `{case['manifest_ncols']}`.",
        f"- Pi-JSON: `{pi['file']['path']}`; free columns `{pi['free_columns']}`, "
        f"ready_for_al_scalar `{pi['ready_for_al_scalar']}`.",
        f"- Vorhandener Identity-Nachweis: accepted `{cert['accepted_certificate_found']}`, "
        f"pairing_kind `{cert['pairing_kind']}`, degree `{cert['degree']}` / "
        f"target `{cert['target_rank']}`.",
        "",
        "## Entscheidung",
        "",
        "Der vorhandene 80224/raw-Nachweis ist ein Identity-Pairing-Fingerprint und darf nicht als "
        "faithful-AL-Zertifikat gezählt werden. Für R1 ist ein neuer Mac-Job nötig, der `rank(A)` "
        "und `s_N != 0` mit echtem `C_src` und nicht-identischem AL-Operatorpfad belegt.",
        "",
        "## Queue-Sicherheit",
        "",
        f"- Alter Queue-Job: `{safety['old_job']['path']}`.",
        f"- Status: `{safety['old_job_status']}`.",
        f"- Identity-artig: `{safety['old_job_identity_like']}`.",
        "- Nicht reaktivieren, solange der Operatorpfad nicht geändert ist.",
        "",
        "## Nächster Schritt",
        "",
        "Einen draft/blocked Mac-Job für `80224/raw` anlegen oder zuerst eine kurze Theorie-/Design-Note "
        "zum matrixfreien faithful-AL-Operator schreiben. Der Laptop bleibt für Sage-Läufe gesperrt.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", default=DEFAULT_CASE_DIR)
    parser.add_argument("--pi-json", default=DEFAULT_PI_JSON)
    parser.add_argument("--identity-json", default=DEFAULT_IDENTITY_JSON)
    parser.add_argument("--queue-job", default=DEFAULT_QUEUE_JOB)
    parser.add_argument("--out-json", default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", default=DEFAULT_OUT_MD)
    parser.add_argument(
        "--hash-rows",
        action="store_true",
        help="Also hash the large mixed_rows.jsonl file. Default is stat-only.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_report(args)
    out_json = ROOT / args.out_json
    out_md = ROOT / args.out_md
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, out_md)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "inputs_ready": payload["inputs_ready"],
                "out_json": rel(out_json),
                "out_md": rel(out_md),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
