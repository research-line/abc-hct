#!/usr/bin/env python3
"""
presentation_upgrade_verifier.py — Verifier fuer das Presentation-Level Upgrade Manifest
(HCT/abc Trace-Plücker, AP-7/AP-8/AP-9).

Erzwingt AP-9 (Presentation-Level Upgrade Criterion). presentation_level darf NUR true sein, wenn
das berechnete presentation_ready true ist:

  presentation_ready =
        prerequisite.certificate_level == true          (0) certificate-level zuerst (LM-Manifest)
    AND source_reconstruction.reconstructed == true      (1) A aus Transcript/Rowhash rekonstruiert
        AND n_rows_covered == n_rows_required
        AND source_block_hash gesetzt (kein '<<FILL>>')
    AND alle sink_class_verification[*].sink_class_ok      (2) AP-8: jede Repair-Zeile = Sink-Class
        AND jeder stage_id gesetzt (kein '<<FILL>>')
    AND column_basis.bound == true
    AND presentation_moves nicht leer                      (3) AP-7: ehrliche Zuege M1-M4
        AND jeder move.type in ALLOWED_MOVES
        AND jeder move.honest == true

No-Overclaim: canonical_level MUSS false bleiben (AP-7/8/9 beweisen KEINE Kanonizitaet; S2a/S2b/H3 offen).
presentation_level==true beweist nur ell_q=0 fuer den FIXIERTEN Quotienten, NICHT canonical / PCAT / abc.

Schema: _scripts/presentation_upgrade_schema.json
Note:   _proof-notes/presentation_to_canonicity_bridge_2026-06-01.md
Angelegt 2026-06-01.
"""

import argparse, json, sys, copy

ALLOWED_MOVES = {
    "unimodular_row",                 # M1
    "unimodular_col",                 # M2
    "tietze_add_contractible",        # M3
    "tietze_remove_contractible",     # M3
    "sink_row_plus_source_relation",  # M4
}

def _is_filled(s):
    return isinstance(s, str) and s.strip() != "" and "<<FILL" not in s

def verify_upgrade(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "gate": {}}

    # --- (0) Prerequisite: certificate-level zuerst ---
    pre = M.get("prerequisite", {})
    cert_ok = bool(pre.get("certificate_level") is True)
    rep["gate"]["prerequisite_certificate_level"] = cert_ok

    # --- (1) Source-Rekonstruktion ---
    sr = M.get("source_reconstruction", {})
    n_req = sr.get("n_rows_required")
    n_cov = sr.get("n_rows_covered")
    recon_ok = (
        sr.get("reconstructed") is True
        and isinstance(n_req, int) and isinstance(n_cov, int) and n_req > 0 and n_cov == n_req
        and _is_filled(sr.get("source_block_hash"))
        and _is_filled(sr.get("rowhash_manifest"))
        and _is_filled(sr.get("transcript_tree"))
    )
    rep["gate"]["source_reconstructed"] = recon_ok

    # --- column basis fixiert ---
    cb = M.get("column_basis", {})
    colbasis_ok = bool(cb.get("bound") is True) and _is_filled(cb.get("column_basis_hash"))
    rep["gate"]["column_basis_bound"] = colbasis_ok

    # --- (2) Sink-Class-Verifikation (AP-8) ---
    scv = M.get("sink_class_verification", [])
    if not isinstance(scv, list) or len(scv) == 0:
        rep["structural_ok"] = False
        rep["errors"].append("sink_class_verification fehlt oder leer")
        sink_ok = False
    else:
        sink_ok = True
        for i, e in enumerate(scv):
            if not _is_filled(e.get("stage_id")):
                sink_ok = False
            if not _is_filled(e.get("rowhash")):
                sink_ok = False
            if e.get("sink_class_ok") is not True:
                sink_ok = False
    rep["gate"]["sink_classes_ok"] = sink_ok

    # --- (3) Presentation-Moves (AP-7) ---
    mv = M.get("presentation_moves", [])
    if not isinstance(mv, list) or len(mv) == 0:
        rep["structural_ok"] = False
        rep["errors"].append("presentation_moves fehlt oder leer")
        moves_ok = False
    else:
        moves_ok = True
        for i, m in enumerate(mv):
            t = m.get("type")
            if t not in ALLOWED_MOVES:
                rep["structural_ok"] = False
                rep["errors"].append(f"move[{i}].type '{t}' nicht in AP-7-Menge {sorted(ALLOWED_MOVES)}")
                moves_ok = False
            if m.get("honest") is not True:
                moves_ok = False
    rep["gate"]["moves_honest"] = moves_ok

    # --- AP-9 Gate ---
    presentation_ready = cert_ok and recon_ok and colbasis_ok and sink_ok and moves_ok
    rep["presentation_ready"] = presentation_ready

    # --- Labels pruefen ---
    lab = M.get("labels", {})
    for lv in ("certificate_level", "presentation_level", "canonical_level"):
        if lv not in lab:
            rep["structural_ok"] = False
            rep["errors"].append(f"label {lv} fehlt")
    decl_pres = bool(lab.get("presentation_level"))
    decl_canon = bool(lab.get("canonical_level"))

    # presentation_level darf NICHT true sein, wenn nicht ready
    if decl_pres and not presentation_ready:
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: presentation_level=true, aber AP-9-Gate nicht erfuellt "
                             f"(gate={rep['gate']})")
    # canonical_level MUSS false sein (AP-7/8/9 beweisen keine Kanonizitaet)
    if decl_canon:
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true ist durch AP-7/8/9 NICHT gedeckt "
                             "(S2a/S2b/H3 offen).")

    rep["presentation_level"] = decl_pres and presentation_ready
    rep["canonical_level"] = False  # nie durch dieses Verfahren

    if presentation_ready and not decl_canon:
        rep["warnings"].append("presentation-level erreichbar/erfuellt, aber canonical_level offen: "
                               "KEIN globales HCT-Theorem, KEIN PCAT/FAQS/abc. Nur fixierter Quotient.")

    rep["status"] = (
        "PRESENTATION-GRADE LOCAL (fixierter Quotient, certificate+presentation)"
        if (rep["presentation_level"] and rep["structural_ok"])
        else "TEMPLATE/INCOMPLETE (strukturell gueltig, aber AP-9 noch nicht erfuellt)"
        if rep["structural_ok"]
        else "INVALID (Overclaim oder Strukturfehler)"
    )
    return rep

# --------- Selbsttest: positiv (synthetisch ehrlich) + negativ (Template) ---------

def _honest_manifest():
    return {
        "meta": {"manifest_id": "PRES-SELFTEST", "case": "selftest", "created": "2026-06-01"},
        "prerequisite": {"certificate_manifest": "lm.json", "certificate_level": True},
        "source_reconstruction": {
            "source_block_hash": "deadbeef" * 8, "rowhash_manifest": "rows.json",
            "n_rows_required": 4, "n_rows_covered": 4, "transcript_tree": "tt.json",
            "reconstructed": True,
        },
        "column_basis": {"column_basis_hash": "cafe" * 16, "bound": True},
        "sink_class_verification": [
            {"stage_id": "T_5_minus_2_batch_11/575", "rowhash": "a" * 64, "q_roles": [2, 3], "sink_class_ok": True},
            {"stage_id": "T_7_minus_0_batch_1/1", "rowhash": "b" * 64, "q_roles": [2, 5, 31], "sink_class_ok": True},
        ],
        "presentation_moves": [
            {"type": "sink_row_plus_source_relation", "description": "R1 -> R1 + w*rho", "honest": True},
            {"type": "unimodular_col", "description": "fixierte Spaltenbasis", "honest": True},
        ],
        "labels": {"certificate_level": True, "presentation_level": True, "canonical_level": False},
        "no_overclaim": {"presentation_holds_if": "...", "but_not": ["abc"], "canonical_open": "S2a/S2b/H3"},
    }

def selftest():
    ok = True
    # Positiv: ehrliches Manifest -> ready true, presentation_level true, canonical false
    pos = verify_upgrade(_honest_manifest())
    cond_pos = (pos["presentation_ready"] and pos["presentation_level"]
                and not pos["canonical_level"] and pos["structural_ok"])
    print(f"[selftest +] honest manifest: ready={pos['presentation_ready']} "
          f"pres={pos['presentation_level']} canon={pos['canonical_level']} "
          f"struct={pos['structural_ok']} -> {'PASS' if cond_pos else 'FAIL'}")
    ok = ok and cond_pos

    # Negativ A: ein move unehrlich -> ready false
    m = _honest_manifest(); m["presentation_moves"][0]["honest"] = False
    m["labels"]["presentation_level"] = False
    neg = verify_upgrade(m)
    cond_neg = (not neg["presentation_ready"]) and (not neg["presentation_level"])
    print(f"[selftest -] dishonest move: ready={neg['presentation_ready']} "
          f"pres={neg['presentation_level']} -> {'PASS' if cond_neg else 'FAIL'}")
    ok = ok and cond_neg

    # Negativ B: presentation_level=true behauptet trotz nicht-ready -> Overclaim erkannt
    m2 = _honest_manifest(); m2["source_reconstruction"]["reconstructed"] = False
    over = verify_upgrade(m2)
    cond_over = (not over["structural_ok"]) and any("OVERCLAIM" in e for e in over["errors"])
    print(f"[selftest -] overclaim guard: struct_ok={over['structural_ok']} "
          f"errors={len(over['errors'])} -> {'PASS' if cond_over else 'FAIL'}")
    ok = ok and cond_over

    # Negativ C: canonical_level=true behauptet -> immer Overclaim
    m3 = _honest_manifest(); m3["labels"]["canonical_level"] = True
    can = verify_upgrade(m3)
    cond_can = (not can["structural_ok"]) and any("canonical_level=true" in e for e in can["errors"])
    print(f"[selftest -] canonical guard: struct_ok={can['structural_ok']} -> {'PASS' if cond_can else 'FAIL'}")
    ok = ok and cond_can

    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Presentation-Level Upgrade Verifier (HCT/abc, AP-7/8/9)")
    ap.add_argument("manifest", nargs="?",
                    default="_results/presentation_upgrade_60168_raw_template.json",
                    help="Pfad zum Upgrade-Manifest-JSON (default: Template)")
    ap.add_argument("--selftest", action="store_true", help="positiv+negativ Selbsttests laufen lassen")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_upgrade(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    # Exit 0 wenn strukturell ok (Template darf presentation_level=false haben); 2 bei Overclaim/Strukturfehler
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
