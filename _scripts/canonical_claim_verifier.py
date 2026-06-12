#!/usr/bin/env python3
"""
canonical_claim_verifier.py — Gesamt-Gate CQ-4 fuer canonical_level (HCT/abc).

canonical_level=true ist NUR zulaessig, wenn die ganze Kette steht:
  prerequisites: psc_certificate_level AND lm_certificate_level AND presentation_level AND h3_canonical_ready
  obligations:   cq1_transfer_iso AND cq2_trace_embedding AND cq3_source_canonicality
=> canonical_ready = AND aller sieben.
canonical_level (deklariert) darf nicht true sein, wenn nicht canonical_ready (sonst OVERCLAIM).
canonical_level beweist KEIN PCAT/FAQS/abc.

Schema: _scripts/canonical_hct_claim_schema.json
Note:   _proof-notes/canonical_hct_trace_quotient_blueprint_2026-06-01.md
Angelegt 2026-06-01.
"""

import argparse, json, sys

PRE = ["psc_certificate_level", "lm_certificate_level", "presentation_level", "h3_canonical_ready"]
OBL = ["cq1_transfer_iso", "cq2_trace_embedding", "cq3_source_canonicality"]

def verify_canonical(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checklist": {}}
    pre = M.get("prerequisites", {})
    obl = M.get("obligations", {})

    for k in PRE:
        v = bool(pre.get(k) is True)
        rep["checklist"][k] = v
        if k not in pre:
            rep["structural_ok"] = False
            rep["errors"].append(f"prerequisite {k} fehlt")
    for k in OBL:
        v = bool(obl.get(k) is True)
        rep["checklist"][k] = v
        if k not in obl:
            rep["structural_ok"] = False
            rep["errors"].append(f"obligation {k} fehlt")

    canonical_ready = all(rep["checklist"].get(k) for k in (PRE + OBL))
    rep["canonical_ready"] = canonical_ready
    rep["missing"] = [k for k in (PRE + OBL) if not rep["checklist"].get(k)]

    lab = M.get("labels", {})
    decl_canon = bool(lab.get("canonical_level"))
    if decl_canon and not canonical_ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: canonical_level=true, aber CQ-4 nicht erfuellt. Offen: {rep['missing']}")
    rep["canonical_level"] = decl_canon and canonical_ready

    if canonical_ready and rep["structural_ok"]:
        rep["warnings"].append("canonical-level erreicht fuer DEN BLOCK: ell_q=0 fuer Q_E. Das ist NICHT "
                               "PCAT/FAQS/abc — der globale Drache bleibt.")

    rep["status"] = (
        "CANONICAL-GRADE (Q_E, ganze Kette CQ-4 bestanden)" if (rep["canonical_level"] and rep["structural_ok"])
        else "TEMPLATE/INCOMPLETE (strukturell gueltig, Kette noch offen)" if rep["structural_ok"]
        else "INVALID (Overclaim / Strukturfehler)"
    )
    return rep

def _full_true():
    return {
        "meta": {"claim_id": "SELFTEST", "case": "selftest", "created": "2026-06-01"},
        "prerequisites": {k: True for k in PRE},
        "obligations": {k: True for k in OBL},
        "labels": {"presentation_level": True, "canonical_level": True},
        "no_overclaim": {"canonical_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    f = verify_canonical(_full_true())
    c1 = f["canonical_ready"] and f["canonical_level"] and f["structural_ok"]
    print(f"[+] full chain: ready={f['canonical_ready']} canon={f['canonical_level']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1

    # one prerequisite missing -> not ready, and overclaim if label true
    m = _full_true(); m["prerequisites"]["h3_canonical_ready"] = False
    g = verify_canonical(m)
    c2 = (not g["canonical_ready"]) and (not g["structural_ok"]) and any("OVERCLAIM" in e for e in g["errors"])
    print(f"[-] missing h3 + claim true: ready={g['canonical_ready']} struct={g['structural_ok']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2

    # honest template-like: all false, label false -> not ready, structural ok
    m2 = _full_true()
    m2["prerequisites"] = {k: False for k in PRE}
    m2["obligations"] = {k: False for k in OBL}
    m2["labels"]["canonical_level"] = False
    h = verify_canonical(m2)
    c3 = (not h["canonical_ready"]) and (not h["canonical_level"]) and h["structural_ok"]
    print(f"[-] all-false honest: ready={h['canonical_ready']} canon={h['canonical_level']} struct={h['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3

    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Canonical HCT Claim Verifier (CQ-4 gate)")
    ap.add_argument("manifest", nargs="?", default="_results/canonical_hct_claim_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_canonical(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
