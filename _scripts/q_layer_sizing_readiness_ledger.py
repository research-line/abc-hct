#!/usr/bin/env python3
"""Build a non-compute readiness ledger for the abc/HCT q-layer gate."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ID = "2026-06-06"
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"
PAPER_B_RESULTS = ROOT / "PAPER_B__beneath_abc_landscape" / "_results"
QUEUE_JOBS = ROOT / "compute_queue" / "jobs"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path, limit_bytes: int = 50_000_000) -> str | None:
    if not path.exists() or path.stat().st_size > limit_bytes:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def exists_rel(path: Path) -> str:
    return rel(path) if path.exists() else f"MISSING:{rel(path)}"


def first_prime_result(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}
    results = data.get("prime_results") or []
    return results[0] if results else {}


def build_rows() -> list[dict[str, Any]]:
    q80224 = PAPER_B_RESULTS / "mstar_h3a_qb3_wiedemann_production_remod_q5077_80224_raw_identity_mac_2026-05-26.json"
    q80224_status = q80224.with_suffix(".status.json")
    q80224_data = read_json(q80224) or {}
    q80224_status_data = read_json(q80224_status) or {}

    q240672_job = QUEUE_JOBS / "hecke_cremona_240672_raw_2026-06-05.json"
    q240672_job_data = read_json(q240672_job) or {}
    q240672_json = RESULTS / "hecke_cremona_240672_raw_2026-06-05.json"
    q240672_md = RESULTS / "hecke_cremona_240672_raw_2026-06-05.md"

    q2_pairing = RESULTS / "mstar_s2_source_cokernel_pairing_60168_raw_q2_2026-05-15.json"
    q3_pairing = RESULTS / "mstar_s2_source_cokernel_pairing_60168_raw_q3_2026-05-15.json"
    q2_pairing_data = first_prime_result(read_json(q2_pairing))
    q3_pairing_data = first_prime_result(read_json(q3_pairing))

    psc2 = RESULTS / "psc2_60168_raw_q2_template.json"
    psc1 = RESULTS / "psc1_60168_raw_template.json"
    lm = RESULTS / "lm_60168_raw_template.json"
    transfer = RESULTS / "canonical_local_drainage_transfer_60168_raw_template.json"
    source_witness = RESULTS / "rc3c_source_witness_60168_raw_2026-05-12" / "N60168_raw_sign1" / "manifest.json"
    old_240672_witness = RESULTS / "rc3c_standard_witness_240672_raw_q3863_2026-05-16" / "N240672_raw_sign1" / "manifest.json"

    transfer_data = read_json(transfer) or {}
    lm_data = read_json(lm) or {}

    return [
        {
            "case": "80224/raw",
            "gate": "QB3 Wiedemann identity-pairing fingerprint",
            "status": "available_certificate_fingerprint" if q80224_data.get("accepted_certificate_found") else "missing_or_unaccepted",
            "evidence": {
                "json": exists_rel(q80224),
                "status_json": exists_rel(q80224_status),
                "q": q80224_data.get("q"),
                "target_rank": q80224_data.get("target_rank"),
                "degree": (q80224_data.get("accepted_certificate") or {}).get("degree"),
                "constant_signed": (q80224_data.get("accepted_certificate") or {}).get("constant_signed"),
                "phase": q80224_status_data.get("phase"),
                "seconds": q80224_status_data.get("seconds"),
                "sha256": sha256_file(q80224),
            },
            "next_action": "Nur als Zertifikatshärtungs-Kalibrator nutzen; das ist nicht der q-Layer-Sizing-Lauf.",
        },
        {
            "case": "240672/raw",
            "gate": "Cremona Hecke separator for current Frey class",
            "status": "local_output_missing_or_remote_running" if not q240672_json.exists() else "local_output_available_review_required",
            "evidence": {
                "queue_job": exists_rel(q240672_job),
                "queue_status": q240672_job_data.get("status"),
                "expected_json": exists_rel(q240672_json),
                "expected_md": exists_rel(q240672_md),
                "allowed_hosts": q240672_job_data.get("allowed_hosts"),
                "defer_while": q240672_job_data.get("defer_while_process_regex"),
            },
            "next_action": "240672/Cremona-Ausgabe holen oder fertigstellen, bevor sie als qdim=1-Input genutzt wird.",
        },
        {
            "case": "60168/raw q=2",
            "gate": "PSC-2 two-dimensional source-cokernel repair",
            "status": "pairing_available_template_not_certificate",
            "evidence": {
                "pairing_json": exists_rel(q2_pairing),
                "template": exists_rel(psc2),
                "source_defect_dim": q2_pairing_data.get("source_defect_dim"),
                "pairing_rank": q2_pairing_data.get("pairing_rank"),
                "saturates": q2_pairing_data.get("saturates"),
            },
            "next_action": "Row-Hashes, Kernelbasis und Source-Block-Hash binden, um das PSC-2-Zertifikat zu instanziieren.",
        },
        {
            "case": "60168/raw q=3",
            "gate": "PSC-1 one-row source-cokernel repair",
            "status": "pairing_available_template_not_certificate",
            "evidence": {
                "pairing_json": exists_rel(q3_pairing),
                "template": exists_rel(psc1),
                "source_defect_dim": q3_pairing_data.get("source_defect_dim"),
                "pairing_rank": q3_pairing_data.get("pairing_rank"),
                "saturates": q3_pairing_data.get("saturates"),
            },
            "next_action": "q=3-Kernelvektor und Repair-Rowhash binden, bevor certificate-level behauptet wird.",
        },
        {
            "case": "60168/raw q=5",
            "gate": "PSC-1 one-row repair candidate",
            "status": "template_only_missing_real_export",
            "evidence": {
                "template": exists_rel(psc1),
                "expected_certificate": "MISSING:_results/psc1_60168_raw_q5_certificate.json",
            },
            "next_action": "Echten q=5-Kernel-/Pairing-Witness exportieren; nicht aus q=2/q=3 folgern.",
        },
        {
            "case": "60168/raw q=31",
            "gate": "PSC-1 one-row repair candidate",
            "status": "template_only_missing_real_export",
            "evidence": {
                "template": exists_rel(psc1),
                "expected_certificate": "MISSING:_results/psc1_60168_raw_q31_certificate.json",
            },
            "next_action": "Echten q=31-Kernel-/Pairing-Witness exportieren; getrennt von q=5 führen.",
        },
        {
            "case": "LM-60168",
            "gate": "Local drainage manifest for q in {2,3,5,31}",
            "status": "manifest_template_not_certificate",
            "evidence": {
                "manifest": exists_rel(lm),
                "certificate_level": (lm_data.get("aggregate_labels") or {}).get("certificate_level"),
                "presentation_level": (lm_data.get("aggregate_labels") or {}).get("presentation_level"),
                "canonical_level": (lm_data.get("aggregate_labels") or {}).get("canonical_level"),
            },
            "next_action": "Keine Labels hochstufen, bevor alle vier PSC-Einträge real und verifiziert sind.",
        },
        {
            "case": "60168/raw transfer",
            "gate": "Canonical local drainage transfer",
            "status": "blocked_by_false_transfer_inputs",
            "evidence": {
                "transfer_template": exists_rel(transfer),
                "inputs": transfer_data.get("inputs"),
                "source_presentation_equality": transfer_data.get("source_presentation_equality"),
                "labels": transfer_data.get("labels"),
            },
            "next_action": "Embedding und Spaltenbasis-Kompatibilität klären, bevor canonical- oder PCAT-Sprache verwendet wird.",
        },
        {
            "case": "60168/raw witness base",
            "gate": "Source witness availability",
            "status": "available_source_witness",
            "evidence": {
                "manifest": exists_rel(source_witness),
                "sha256": sha256_file(source_witness),
            },
            "next_action": "Als Bindungsziel für PSC-Row-/Kernel-Provenienz verwenden.",
        },
        {
            "case": "240672/raw legacy witness",
            "gate": "Old standard-family witness",
            "status": "legacy_standard_witness_not_current_cremona_gate",
            "evidence": {
                "manifest": exists_rel(old_240672_witness),
                "sha256": sha256_file(old_240672_witness),
            },
            "next_action": "Nicht ohne explizites Replay/Übersetzung als 2026-06-05-Cremona-Gate wiederverwenden.",
        },
    ]


def paperstand() -> list[dict[str, str]]:
    return [
        {
            "source": "Cuevas Barrientos--Pasten, arXiv:2504.15971v3",
            "url": "https://arxiv.org/abs/2504.15971",
            "checked_status": "Subexponentieller Szpiro-in-Familien-Kontext; kein Frey-uniformes Polynomial-Closing.",
        },
        {
            "source": "Chan, arXiv:2407.13850",
            "url": "https://arxiv.org/abs/2407.13850",
            "checked_status": "Fast-alle-Szpiro-Ratio; bestätigt Statistik-gegen-Worst-Case-Barriere.",
        },
        {
            "source": "Sawin--Sutherland, arXiv:2504.12295v2",
            "url": "https://arxiv.org/abs/2504.12295",
            "checked_status": "Murmurations-Dichte als Mittelwert-/Evidenzkontext, nicht als individueller Frey-Hebel.",
        },
        {
            "source": "Dumas--Kaltofen--Thom\u00e9, arXiv:1507.01083",
            "url": "https://arxiv.org/abs/1507.01083",
            "checked_status": "Passender Zertifikatsrahmen für Wiedemann/Krylov; härtet Verifikation, nicht HCT-Transfer.",
        },
        {
            "source": "Pasten, arXiv:1705.09251v4",
            "url": "https://arxiv.org/abs/1705.09251",
            "checked_status": "Shimura-/abc-Kontext; keine neue Perioden-/Modulgrad-Schließung für diese Route.",
        },
        {
            "source": "Iyengar--Khare--Manning, arXiv:2510.05418v2",
            "url": "https://arxiv.org/abs/2510.05418",
            "checked_status": "Kongruenzideal-Sprache aktuell; für HCT bleibt uniforme Frey-Schranke das offene Gate.",
        },
        {
            "source": "Khan--Maithani, arXiv:2604.06446",
            "url": "https://arxiv.org/abs/2604.06446",
            "checked_status": "Determinantaler Wiles-Defekt ist Reformulierungskontext, kein unabhängiger abc-Beweis.",
        },
    ]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    blockers = [
        row for row in rows
        if any(token in row["status"] for token in ("missing", "template", "blocked", "legacy"))
    ]
    return {
        "run_id": RUN_ID,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": "abc / HCT Paper B q^r-layer sizing",
        "overall_status": "preflight_ready_but_compute_blocked",
        "claim_upgrade": False,
        "long_compute_started": False,
        "upload_started": False,
        "row_count": len(rows),
        "blocker_count": len(blockers),
        "main_blockers": [
            "240672/raw Cremona-Hecke output is not locally available as a completed gate.",
            "PSC certificates for q in {2,3,5,31} remain templates until row/kernel/source bindings are real.",
            "Canonical local drainage transfer labels remain false, so PCAT/FAQS/abc language is not licensed.",
        ],
        "next_action": "Finish or fetch the 240672 Cremona run, then instantiate PSC certificates before any q-layer sizing claim.",
    }


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any], sources: list[dict[str, str]]) -> dict[str, str]:
    json_path = RESULTS / f"Q_LAYER_SIZING_READINESS_LEDGER_{RUN_ID}.json"
    csv_path = RESULTS / f"Q_LAYER_SIZING_READINESS_LEDGER_{RUN_ID}.csv"
    md_path = RESULTS / f"Q_LAYER_SIZING_READINESS_LEDGER_{RUN_ID}.md"

    payload = {"summary": summary, "paperstand": sources, "rows": rows}
    with json_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case", "gate", "status", "evidence", "next_action"])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "case": row["case"],
                "gate": row["gate"],
                "status": row["status"],
                "evidence": json.dumps(row["evidence"], ensure_ascii=False, sort_keys=True),
                "next_action": row["next_action"],
            })

    lines = [
        f"# Q^r-Layer-Sizing Readiness Ledger ({RUN_ID})",
        "",
        "## Kurzbefund",
        "",
        "- Kein abc-, PCAT-, FAQS- oder canonical-level-Upgrade.",
        "- Kein Langlauf gestartet; dieser Check liest nur vorhandene Artefakte.",
        "- Gesamtstatus: `preflight_ready_but_compute_blocked`.",
        "- Nächster sinnvoller Schritt: 240672/Cremona-Fortschritt holen oder abschließen, danach PSC-Zertifikate q=2,3,5,31 mit echten Row-/Kernel-Bindungen instanziieren.",
        "",
        "## Externer Paperstand",
        "",
        "| Quelle | Einordnung |",
        "|---|---|",
    ]
    for source in sources:
        lines.append(f"| [{source['source']}]({source['url']}) | {source['checked_status']} |")

    lines.extend([
        "",
        "## Artefakt-Readiness",
        "",
        "| Fall | Gate | Status | Nächste Aktion |",
        "|---|---|---|---|",
    ])
    for row in rows:
        lines.append(f"| `{row['case']}` | {row['gate']} | `{row['status']}` | {row['next_action']} |")

    lines.extend([
        "",
        "## Blocker",
        "",
    ])
    for item in summary["main_blockers"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Maschinenlesbare Details",
        "",
        f"- JSON: `{rel(json_path)}`",
        f"- CSV: `{rel(csv_path)}`",
        f"- Dieser Markdownbericht: `{rel(md_path)}`",
        "",
    ])
    with md_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    return {"json": str(json_path), "csv": str(csv_path), "md": str(md_path)}


def main() -> int:
    rows = build_rows()
    sources = paperstand()
    summary = summarize(rows)
    outputs = write_outputs(rows, summary, sources)
    print(json.dumps({"summary": summary, "outputs": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
