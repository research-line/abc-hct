#!/usr/bin/env python3
"""
source_row_embedding_verifier.py — Verifier fuer CQ-3w (schwache Source-Canonicality, HCT/abc).

CQ-3w: row(A_exp) subset im rho_E. source_embedding_ready NUR wenn:
  n_rowhash_bound == n_source_rows  (alle Zeilen rowhash-gebunden)
  AND n_identified_canonical == n_source_rows  (alle als kanonische Relation identifiziert)
  AND column_basis_compatible (SRM-2).
source_embedding_level (CQ-3w-Label) darf nur true sein, wenn ready.
source_presentation_equality (CQ-3s) ist STAERKER und bleibt separat; canonical_level wird nie gesetzt.

Note: _proof-notes/source_sublattice_monotonicity_2026-06-01.md. Schema: _scripts/source_row_embedding_manifest_schema.json.
Angelegt 2026-06-01.
"""
import argparse, json, sys

def verify_sre(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checklist": {}}
    meta = M.get("meta", {})
    sr = M.get("source_rows", {})
    cb = M.get("column_basis", {})
    n = meta.get("n_source_rows")

    n_bound = sr.get("n_rowhash_bound", 0)
    n_canon = sr.get("n_identified_canonical", 0)
    col_ok = bool(cb.get("column_basis_compatible") is True)

    rep["checklist"]["all_rowhash_bound"] = isinstance(n, int) and n_bound == n and n > 0
    rep["checklist"]["all_identified_canonical"] = isinstance(n, int) and n_canon == n and n > 0
    rep["checklist"]["column_basis_compatible"] = col_ok
    rep["coverage"] = {"n_source_rows": n, "n_rowhash_bound": n_bound, "n_identified_canonical": n_canon}

    source_embedding_ready = all(rep["checklist"].values())
    rep["source_embedding_ready"] = source_embedding_ready
    rep["missing"] = [k for k, v in rep["checklist"].items() if not v]

    lab = M.get("labels", {})
    decl_emb = bool(lab.get("source_embedding_level"))
    if decl_emb and not source_embedding_ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: source_embedding_level=true, aber nicht ready. Offen: {rep['missing']}")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true (nur Gesamt-Gate).")
    rep["source_embedding_level"] = decl_emb and source_embedding_ready

    # CQ-3s ist staerker und unabhaengig; nur pruefen, dass es CQ-3w impliziert (Konsistenz)
    cq3s = bool(lab.get("source_presentation_equality"))
    rep["source_presentation_equality"] = cq3s
    if cq3s and not source_embedding_ready:
        rep["warnings"].append("source_presentation_equality (CQ-3s) behauptet, aber CQ-3w nicht ready — inkonsistent "
                               "(Gleichheit impliziert Inklusion).")
    rep["canonical_level"] = False

    if source_embedding_ready and rep["structural_ok"]:
        rep["warnings"].append("CQ-3w erreicht: genuegt fuer lokale ell_q=0-Transfers (SRM-1, OBERE Schranke). "
                               "NICHT CQ-3s/exakter Content, NICHT PCAT/FAQS/abc.")

    rep["status"] = ("CQ-3w SOURCE-EMBEDDED (lokale Inklusion belegt)" if (rep["source_embedding_level"] and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Zeilen noch nicht als kanonische Relationen identifiziert)" if rep["structural_ok"]
                     else "INVALID (Overclaim/Strukturfehler)")
    return rep

def _full(n=31680):
    return {
        "meta": {"case": "60168/raw", "q": 3863, "n_source_rows": n, "created": "2026-06-01"},
        "source_rows": {"n_rowhash_bound": n, "n_identified_canonical": n, "relation_types": ["manin", "hecke", "trace", "boundary"]},
        "column_basis": {"column_basis_compatible": True, "column_basis_hash": "ab" * 32},
        "labels": {"source_embedding_level": True, "source_presentation_equality": False, "canonical_level": False},
        "no_overclaim": {"embedding_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    f = verify_sre(_full())
    c1 = f["source_embedding_ready"] and f["source_embedding_level"] and not f["source_presentation_equality"] and f["structural_ok"]
    print(f"[+] full CQ-3w (equality NOT claimed): ready={f['source_embedding_ready']} emb={f['source_embedding_level']} eq={f['source_presentation_equality']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # partial -> not ready
    m = _full(); m["source_rows"]["n_identified_canonical"] = 17000; m["labels"]["source_embedding_level"] = False
    n = verify_sre(m)
    c2 = (not n["source_embedding_ready"]) and n["structural_ok"] and "all_identified_canonical" in n["missing"]
    print(f"[-] partial identify: ready={n['source_embedding_ready']} missing={n['missing']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # overclaim
    m2 = _full(); m2["column_basis"]["column_basis_compatible"] = False
    o = verify_sre(m2)
    c3 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] overclaim (col basis incompatible): struct={o['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Source-Row Embedding Verifier (CQ-3w)")
    ap.add_argument("manifest", nargs="?", default="_results/source_row_embedding_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_sre(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
