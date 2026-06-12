#!/usr/bin/env python3
"""
source_row_embedding_registry_verifier.py — Verifier fuer das Source-Row Embedding Registry (SER-1, CQ-3w).

source_embedding_level=true NUR wenn:
  classification_complete : sum(family.row_count) == meta.n_source_rows
  rowhash_complete        : jede Familie n_rowhash_bound == row_count
  family_canonical_computed: JEDE Familie family_canonical_defined==true UND transcript_bound==true
  column_basis_compatible (SRM-2)
source_presentation_equality (CQ-3s) ist staerker, separat; canonical_level wird nie gesetzt.

Der Guard blockiert halbgruene Familien: eine einzige Familie mit family_canonical_defined=false
=> family_canonical_computed=false => nicht ready.

Note: _proof-notes/source_row_embedding_registry_2026-06-01.md. Schema: _scripts/source_row_embedding_registry_schema.json.
Angelegt 2026-06-01.
"""
import argparse, json, sys

def verify_registry(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "families": []}
    meta = M.get("meta", {})
    n = meta.get("n_source_rows")
    fams = M.get("families", [])

    total = 0; rowhash_complete = True; canon_all = True
    for e in fams:
        rc = e.get("row_count", 0); nb = e.get("n_rowhash_bound", 0)
        fc = bool(e.get("family_canonical_defined") is True)
        tb = bool(e.get("transcript_bound") is True)
        total += rc
        rh_ok = (nb == rc and rc > 0)
        rowhash_complete = rowhash_complete and rh_ok
        canon_all = canon_all and fc and tb
        rep["families"].append({"family": e.get("family"), "row_count": rc, "n_rowhash_bound": nb,
                                "rowhash_ok": rh_ok, "family_canonical_defined": fc, "transcript_bound": tb})

    classification_complete = isinstance(n, int) and total == n and n > 0
    col_ok = bool(M.get("column_basis", {}).get("column_basis_compatible") is True)

    rep["classification_complete"] = classification_complete
    rep["classified_total"] = total
    rep["n_source_rows"] = n
    rep["rowhash_complete"] = rowhash_complete and bool(fams)
    rep["family_canonical_computed"] = canon_all and bool(fams)
    rep["column_basis_compatible"] = col_ok

    ready = (classification_complete and rep["rowhash_complete"]
             and rep["family_canonical_computed"] and col_ok)
    rep["source_embedding_ready_computed"] = ready
    rep["missing"] = [k for k in ("classification_complete", "rowhash_complete",
                                  "family_canonical_computed", "column_basis_compatible") if not rep.get(k)]

    lab = M.get("labels", {})
    decl_emb = bool(lab.get("source_embedding_level"))
    if decl_emb and not ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: source_embedding_level=true, aber nicht ready. Offen: {rep['missing']}")
    cq3s = bool(lab.get("source_presentation_equality"))
    if cq3s and not ready:
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: source_presentation_equality (CQ-3s) behauptet, aber CQ-3w nicht ready "
                             "(Gleichheit impliziert Inklusion).")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true (nur Gesamt-Gate).")
    rep["source_embedding_level"] = decl_emb and ready
    rep["source_presentation_equality"] = cq3s and ready
    rep["canonical_level"] = False

    if ready and rep["structural_ok"]:
        rep["warnings"].append("CQ-3w erreicht (alle Familien kanonisch): lokale ell_q=0-Transfers (SRM-1) offen. "
                               "NICHT CQ-3s/H3/PCAT/FAQS/abc.")

    rep["status"] = ("CQ-3w READY (alle Familien kanonisch)" if (rep["source_embedding_level"] and rep["structural_ok"])
                     else "CLASSIFIED+BOUND, family-canonicity offen" if (classification_complete and rep["rowhash_complete"] and rep["structural_ok"])
                     else "INCOMPLETE" if rep["structural_ok"] else "INVALID (Overclaim)")
    return rep

def _reg(canon=True, n=31680):
    return {
        "meta": {"case": "60168/raw", "q": 3863, "n_source_rows": n, "created": "2026-06-01"},
        "families": [
            {"family": "manin", "stage_prefix": "manin_T_relations_after_SI", "row_count": 21104,
             "n_rowhash_bound": 21104, "family_canonical_defined": canon, "transcript_bound": canon},
            {"family": "T_5_minus_2", "stage_prefix": "T_5_minus_2", "row_count": 10576,
             "n_rowhash_bound": 10576, "family_canonical_defined": canon, "transcript_bound": canon},
        ],
        "column_basis": {"column_basis_compatible": canon},
        "labels": {"source_embedding_level": canon, "source_presentation_equality": False, "canonical_level": False},
        "no_overclaim": {"embedding_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    f = verify_registry(_reg(canon=True))
    c1 = (f["classification_complete"] and f["rowhash_complete"] and f["family_canonical_computed"]
          and f["source_embedding_level"] and not f["source_presentation_equality"] and f["structural_ok"])
    print(f"[+] all families canonical (eq NOT claimed): ready={f['source_embedding_ready_computed']} emb={f['source_embedding_level']} eq={f['source_presentation_equality']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # halbgruene Familie: manin canonical false -> blockiert
    m = _reg(canon=True); m["families"][0]["family_canonical_defined"] = False; m["labels"]["source_embedding_level"] = False
    h = verify_registry(m)
    c2 = (not h["family_canonical_computed"]) and (not h["source_embedding_ready_computed"]) and h["structural_ok"]
    print(f"[-] half-green (manin not canonical): family_canonical_computed={h['family_canonical_computed']} ready={h['source_embedding_ready_computed']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # rowhash unvollstaendig
    m2 = _reg(canon=True); m2["families"][1]["n_rowhash_bound"] = 9000; m2["labels"]["source_embedding_level"] = False
    r = verify_registry(m2)
    c3 = (not r["rowhash_complete"]) and (not r["source_embedding_ready_computed"])
    print(f"[-] incomplete rowhash: rowhash_complete={r['rowhash_complete']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # overclaim
    m3 = _reg(canon=False); m3["labels"]["source_embedding_level"] = True
    o = verify_registry(m3)
    c4 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] overclaim: struct={o['structural_ok']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Source-Row Embedding Registry Verifier (SER-1/CQ-3w)")
    ap.add_argument("registry", nargs="?", default="_results/source_row_embedding_registry_60168_raw.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.registry, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_registry(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
