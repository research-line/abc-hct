#!/usr/bin/env python3
"""
trace_row_embedding_verifier.py — Verifier fuer den Trace-Row Embedding Contract CQ-2 (HCT/abc).

Erzwingt [r_exp] = [T_ell - a_ell(E)] in Q_E. trace_row_embedding=true NUR wenn:
  rowhash gesetzt (kein '<<FILL>>') AND a_ell_E ganzzahlig gesetzt
  AND alle vier Konventionen verifiziert (hecke/compression/sign/integer_lift)
  AND canonical_trace_module_binding.bound == true (Klasse IM kanonischen Modul, nicht Rank-Witness-Ausschnitt).
canonical_level wird NIE gesetzt (nur Gesamt-Gate CQ-4).

Schema: _scripts/trace_row_embedding_schema.json
Note:   _proof-notes/trace_row_embedding_contract_2026-06-01.md
Angelegt 2026-06-01.
"""
import argparse, json, sys

CONV = ["hecke_convention_verified", "compression_convention_verified",
        "sign_convention_verified", "integer_lift_convention_verified"]

def _filled(s):
    return isinstance(s, str) and s.strip() != "" and "<<FILL" not in s

def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)

def verify_tre(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checklist": {}}
    tr = M.get("trace_row", {})
    conv = M.get("conventions", {})
    bind = M.get("canonical_trace_module_binding", {})

    rep["checklist"]["rowhash_set"] = _filled(tr.get("rowhash"))
    rep["checklist"]["a_ell_set"] = _is_int(tr.get("a_ell_E"))
    for c in CONV:
        if c not in conv:
            rep["structural_ok"] = False
            rep["errors"].append(f"convention {c} fehlt")
        rep["checklist"][c] = bool(conv.get(c) is True)
    rep["checklist"]["module_bound"] = bool(bind.get("bound") is True) and _filled(bind.get("module_id"))

    trace_row_ready = all(rep["checklist"].get(k) for k in
                          (["rowhash_set", "a_ell_set"] + CONV + ["module_bound"]))
    rep["trace_row_ready"] = trace_row_ready
    rep["missing"] = [k for k in (["rowhash_set", "a_ell_set"] + CONV + ["module_bound"])
                      if not rep["checklist"].get(k)]

    lab = M.get("labels", {})
    if bool(lab.get("trace_row_embedding")) and not trace_row_ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: trace_row_embedding=true, aber nicht ready. Offen: {rep['missing']}")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true (nur Gesamt-Gate CQ-4).")
    rep["trace_row_embedding"] = bool(lab.get("trace_row_embedding")) and trace_row_ready
    rep["canonical_level"] = False

    rep["status"] = ("TRACE-ROW EMBEDDED (CQ-2 fuer diese Zeile)" if (rep["trace_row_embedding"] and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Rowhash bekannt, Konventionen offen)" if rep["structural_ok"]
                     else "INVALID (Overclaim/Strukturfehler)")
    return rep

def _good():
    return {
        "meta": {"case": "selftest", "ell": 7, "created": "2026-06-01"},
        "trace_row": {"stage_id": "T_7_minus_0_batch_1/1", "rowhash": "a"*64, "a_ell_E": 0, "claimed_class": "T_7"},
        "conventions": {c: True for c in CONV},
        "canonical_trace_module_binding": {"module_id": "M_E", "bound": True},
        "labels": {"trace_row_embedding": True, "canonical_level": False},
        "no_overclaim": {"embedding_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    g = verify_tre(_good())
    c1 = g["trace_row_ready"] and g["trace_row_embedding"] and not g["canonical_level"] and g["structural_ok"]
    print(f"[+] full conventions: ready={g['trace_row_ready']} embed={g['trace_row_embedding']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # rowhash known but conventions missing -> not ready
    m = _good(); m["conventions"]["hecke_convention_verified"] = False; m["labels"]["trace_row_embedding"] = False
    n = verify_tre(m)
    c2 = (not n["trace_row_ready"]) and n["structural_ok"]
    print(f"[-] missing hecke conv: ready={n['trace_row_ready']} struct={n['structural_ok']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # overclaim: label true but module not bound
    m2 = _good(); m2["canonical_trace_module_binding"]["bound"] = False
    o = verify_tre(m2)
    c3 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] overclaim (label true, not ready): struct={o['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Trace-Row Embedding Verifier (CQ-2)")
    ap.add_argument("manifest", nargs="?", default="_results/trace_row_embedding_60168_raw_t7_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_tre(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
