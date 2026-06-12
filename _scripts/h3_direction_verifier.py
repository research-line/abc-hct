#!/usr/bin/env python3
"""
h3_direction_verifier.py — Guard fuer die richtungssensitive H3/Fitting-Stelle
(HCT/abc canonical-level, Blueprint CQ + H3).

DVR-Fakt: Fitt_0(Q) = (pi^ell(Q)); (pi^a) superset (pi^b) <=> a <= b. Daher:
  Fitt_0(Q_E) superset eta_ext*D_H3   <=>   ell(Q_E) <= nu(eta_ext) + nu(D_H3)   (OBERE Laengenschranke).
Die Gegenrichtung (Fitt_0 subset Produkt) gibt eine UNTERE Schranke -> nutzlos fuer Laengenkontrolle.

Der Guard erzwingt:
  1. inclusion.direction == 'Fitt0_contains_product' (sonst WRONG-DIRECTION, strukturell ungueltig).
  2. bounded_quantity wird daraus abgeleitet: nur bei korrekter Richtung == 'hct_fitting_length'.
  3. Wenn alle Valuationen ganzzahlig gegeben sind, MUSS ell_Q_E_claimed <= nu_eta_ext + nu_D_H3 gelten.
  4. canonical_ready verlangt zusaetzlich fitting_object.is_canonical_Q_E (CQ-3) UND ikm_type_check.checked.
canonical_level wird NIE durch diesen Guard gesetzt (H3-Richtung allein kroent nicht).

Schema: _scripts/h3_direction_schema.json
Note:   _proof-notes/canonical_hct_trace_quotient_blueprint_2026-06-01.md
Angelegt 2026-06-01.
"""

import argparse, json, sys

def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)

def verify_h3(M):
    rep = {"structural_ok": True, "errors": [], "warnings": []}

    inc = M.get("inclusion", {})
    direction = inc.get("direction")
    direction_ok = (direction == "Fitt0_contains_product")
    if direction == "Fitt0_contained_in_product":
        rep["structural_ok"] = False
        rep["errors"].append("WRONG-DIRECTION: Fitt0_contained_in_product gibt eine UNTERE Laengenschranke; "
                             "fuer HCT/Fitting-Laengenkontrolle ist nur Fitt0_contains_product nuetzlich.")
    elif not direction_ok:
        rep["structural_ok"] = False
        rep["errors"].append(f"inclusion.direction unbekannt: {direction!r}")

    # bounded_quantity aus der Richtung ableiten
    rep["bounded_quantity"] = "hct_fitting_length" if direction_ok else "none_or_inverted"

    # Laengenungleichung pruefen, falls Valuationen ganzzahlig
    val = M.get("valuations", {})
    a, b, ell = val.get("nu_eta_ext"), val.get("nu_D_H3"), val.get("ell_Q_E_claimed")
    if _is_int(a) and _is_int(b) and _is_int(ell):
        ineq_ok = (ell <= a + b)
        rep["length_inequality"] = f"ell(Q_E)={ell} <= nu(eta_ext)+nu(D_H3)={a}+{b}={a+b}"
        rep["length_inequality_ok"] = ineq_ok
        if direction_ok and not ineq_ok:
            rep["structural_ok"] = False
            rep["errors"].append("INKONSISTENT: Richtung behauptet obere Schranke, aber "
                                 f"ell(Q_E)={ell} > {a+b}.")
    else:
        rep["length_inequality_ok"] = None
        rep["warnings"].append("Valuationen nicht alle ganzzahlig gesetzt (Template) -> Ungleichung nicht geprueft.")

    fo = M.get("fitting_object", {})
    fitting_canonical = bool(fo.get("is_canonical_Q_E") is True)
    rep["fitting_object_is_canonical_Q_E"] = fitting_canonical
    if not fitting_canonical:
        rep["warnings"].append("fitting_object ist (noch) nicht der kanonische Q_E (CQ-3 offen) -> "
                               "Fitting-Schranke gilt fuer einen nicht-kanonischen Schatten, nicht fuer Q_E.")

    itc = M.get("ikm_type_check", {})
    ikm_checked = bool(itc.get("checked") is True)
    rep["ikm_type_checked"] = ikm_checked

    # canonical_ready: korrekte Richtung + (Valuationen ok ODER noch offen, aber nicht falsch) + Q_E kanonisch + Type-Check
    length_not_violated = (rep["length_inequality_ok"] is not False)
    canonical_ready = direction_ok and length_not_violated and fitting_canonical and ikm_checked
    rep["canonical_ready"] = canonical_ready

    lab = M.get("labels", {})
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true wird vom H3-Guard nie gedeckt (nur Gesamt-Gate CQ-4).")
    rep["canonical_level"] = False

    rep["status"] = (
        "H3 DIRECTION CONSISTENT + READY (Richtung+Type-Check ok)" if (canonical_ready and rep["structural_ok"])
        else "H3 DIRECTION DECLARED (konsistent, aber nicht ready: Type-Check/Kanonizitaet offen)" if rep["structural_ok"]
        else "INVALID (Wrong-Direction / Inkonsistenz / Overclaim)"
    )
    return rep

def _good_manifest():
    return {
        "meta": {"case": "selftest", "created": "2026-06-01"},
        "fitting_object": {"name": "Q_E", "is_canonical_Q_E": True},
        "inclusion": {"direction": "Fitt0_contains_product", "statement": "Fitt_0(Q_E) superset eta*D"},
        "valuations": {"nu_eta_ext": 3, "nu_D_H3": 2, "ell_Q_E_claimed": 4},
        "ikm_type_check": {"checked": True, "category": "determinantal", "note": "ok"},
        "labels": {"canonical_ready": True, "canonical_level": False},
        "no_overclaim": {"direction_meaning": "obere Schranke", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    g = verify_h3(_good_manifest())
    c1 = (g["bounded_quantity"] == "hct_fitting_length" and g["canonical_ready"]
          and g["length_inequality_ok"] and not g["canonical_level"] and g["structural_ok"])
    print(f"[+] good: bounded={g['bounded_quantity']} ready={g['canonical_ready']} ineq={g['length_inequality_ok']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1

    # wrong direction
    m = _good_manifest(); m["inclusion"]["direction"] = "Fitt0_contained_in_product"
    w = verify_h3(m)
    c2 = (not w["structural_ok"]) and any("WRONG-DIRECTION" in e for e in w["errors"]) and w["bounded_quantity"] != "hct_fitting_length"
    print(f"[-] wrong-direction: struct={w['structural_ok']} bounded={w['bounded_quantity']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2

    # inconsistent inequality
    m2 = _good_manifest(); m2["valuations"]["ell_Q_E_claimed"] = 99
    i = verify_h3(m2)
    c3 = (not i["structural_ok"]) and (i["length_inequality_ok"] is False)
    print(f"[-] inconsistent length: struct={i['structural_ok']} ineq_ok={i['length_inequality_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3

    # missing type check -> not ready
    m3 = _good_manifest(); m3["ikm_type_check"]["checked"] = False; m3["labels"]["canonical_ready"] = False
    t = verify_h3(m3)
    c4 = (not t["canonical_ready"]) and t["structural_ok"] and t["bounded_quantity"] == "hct_fitting_length"
    print(f"[-] no type-check: ready={t['canonical_ready']} struct={t['structural_ok']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4

    # canonical overclaim
    m4 = _good_manifest(); m4["labels"]["canonical_level"] = True
    o = verify_h3(m4)
    c5 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] canonical overclaim: struct={o['structural_ok']} -> {'PASS' if c5 else 'FAIL'}")
    ok &= c5

    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="H3 Fitting Direction Verifier (HCT/abc canonical-level)")
    ap.add_argument("manifest", nargs="?", default="_results/h3_direction_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_h3(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
