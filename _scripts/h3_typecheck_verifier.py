#!/usr/bin/env python3
"""
h3_typecheck_verifier.py — Verifier fuer den H3 Type-Check Contract (HCT/abc).

Prueft, ob das HCT-Fitting-Paket (A_E, M_E, lambda_E, rho_E, Q_E) konstruiert UND Q_E als Objekt der
IKM/determinantal-Kategorie nachgewiesen ist, plus Richtungskonsistenz. Behauptet NICHT H3.
  definitions_ready  = alle fuenf *_defined
  h3_type_checked    = definitions_ready AND category.Q_E_is_quotient_ring AND direction==Fitt0_contains_product
canonical_level wird NIE gesetzt.

Guard: "Sprache passt" (category.name gesetzt) genuegt NICHT; es braucht Q_E_is_quotient_ring=true.

Schema: _scripts/h3_typecheck_schema.json
Note:   _proof-notes/h3_typecheck_contract_2026-06-01.md
Angelegt 2026-06-01.
"""
import argparse, json, sys

DEFS = ["A_E_defined", "M_E_defined", "lambda_E_defined", "rho_E_defined", "Q_E_defined"]

def verify_h3tc(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checklist": {}}
    fp = M.get("fitting_package", {})
    cat = M.get("category", {})
    direction = M.get("direction", {})

    for k in DEFS:
        if k not in fp:
            rep["structural_ok"] = False
            rep["errors"].append(f"fitting_package.{k} fehlt")
        rep["checklist"][k] = bool(fp.get(k) is True)
    definitions_ready = all(rep["checklist"].get(k) for k in DEFS)
    rep["definitions_ready"] = definitions_ready

    q_is_ring = bool(cat.get("Q_E_is_quotient_ring") is True)
    rep["Q_E_is_quotient_ring"] = q_is_ring
    direction_ok = (direction.get("inclusion") == "Fitt0_contains_product")
    rep["direction_consistent"] = direction_ok
    if direction.get("inclusion") and not direction_ok:
        rep["structural_ok"] = False
        rep["errors"].append(f"direction.inclusion {direction.get('inclusion')!r} != 'Fitt0_contains_product' "
                             "(nur die enthaltende Richtung gibt eine obere Laengenschranke).")

    if cat.get("name") and not q_is_ring:
        rep["warnings"].append("category.name gesetzt ('Sprache passt'), aber Q_E_is_quotient_ring=false: "
                               "IKM/determinantal-Sprache noch NICHT auf HCT anwendbar (Type-Check offen).")

    h3_type_checked = definitions_ready and q_is_ring and direction_ok
    rep["h3_type_checked"] = h3_type_checked
    rep["missing"] = ([k for k in DEFS if not rep["checklist"].get(k)]
                      + ([] if q_is_ring else ["Q_E_is_quotient_ring"])
                      + ([] if direction_ok else ["direction"]))

    lab = M.get("labels", {})
    if bool(lab.get("h3_type_checked")) and not h3_type_checked:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: h3_type_checked=true, aber nicht erfuellt. Offen: {rep['missing']}")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true (H3-Type-Check behauptet kein H3).")
    rep["canonical_level"] = False

    rep["status"] = ("H3 TYPE-CHECKED (IKM/determinantal anwendbar auf HCT)" if (h3_type_checked and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Richtung deklariert, Definitionen/Type-Check offen)" if rep["structural_ok"]
                     else "INVALID (Wrong-Direction/Overclaim/Strukturfehler)")
    return rep

def _good():
    return {
        "meta": {"case": "selftest", "created": "2026-06-01"},
        "fitting_package": {k: True for k in DEFS},
        "category": {"name": "Khan-Maithani determinantal ring", "Q_E_is_quotient_ring": True},
        "direction": {"inclusion": "Fitt0_contains_product", "length_inequality": "ell(Q_E)<=nu(eta)+nu(D)"},
        "labels": {"definitions_ready": True, "h3_type_checked": True, "canonical_level": False},
        "no_overclaim": {"typecheck_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    g = verify_h3tc(_good())
    c1 = g["definitions_ready"] and g["h3_type_checked"] and not g["canonical_level"] and g["structural_ok"]
    print(f"[+] full package: defs={g['definitions_ready']} typechecked={g['h3_type_checked']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # language fits but not a quotient ring -> not type-checked, warning
    m = _good(); m["category"]["Q_E_is_quotient_ring"] = False; m["labels"]["h3_type_checked"] = False
    n = verify_h3tc(m)
    c2 = (not n["h3_type_checked"]) and n["structural_ok"] and any("noch NICHT" in w for w in n["warnings"])
    print(f"[-] language-only: typechecked={n['h3_type_checked']} warn={'yes' if n['warnings'] else 'no'} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # wrong direction
    m2 = _good(); m2["direction"]["inclusion"] = "Fitt0_contained_in_product"
    w = verify_h3tc(m2)
    c3 = (not w["structural_ok"]) and (not w["direction_consistent"])
    print(f"[-] wrong direction: struct={w['structural_ok']} dir_ok={w['direction_consistent']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # canonical overclaim
    m3 = _good(); m3["labels"]["canonical_level"] = True
    o = verify_h3tc(m3)
    c4 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] canonical overclaim: struct={o['structural_ok']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="H3 Type-Check Verifier (HCT/abc)")
    ap.add_argument("manifest", nargs="?", default="_results/h3_typecheck_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_h3tc(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
