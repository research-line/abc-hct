#!/usr/bin/env python3
"""
lm_manifest_verifier.py — Verifier fuer das Local Drainage Manifest (LM, HCT/abc Trace-Plücker).

Prueft ein gebuendeltes Manifest (PSC-2 fuer q=2, PSC-1 fuer q=3,5,31 -> LM-60168):
  1. STRUKTUR: required_primes abgedeckt; je Eintrag korrekte psc_version (q=2->PSC-2/d=2,
     sonst PSC-1/d=1); labels vorhanden.
  2. AGGREGATION: Manifest-Level = logisches UND der Eintrags-Labels (certificate/presentation/canonical).
  3. NO-OVERCLAIM: Selbst bei certificate_level=true wird KEIN PCAT/FAQS/abc behauptet; canonical_level
     bleibt offen bis S2a/S2b+H3.

Das Manifest beweist (sobald alle certificate_level=true) NUR den lokalen Satz:
  sum_{q in required_primes} ell_q(coker[A;R_q]) log q = 0   (certificate-level, fuer den exportierten Block).

Schema: _scripts/lm_manifest_schema.json. Note: _proof-notes/local_drainage_manifest_2026-06-01.md.
Angelegt 2026-06-01.
"""

import argparse, json, sys

PSC_FOR_Q = {2: ("PSC-2", 2)}   # q=2 -> PSC-2/d=2; alle anderen -> PSC-1/d=1 (default)

def expected_psc(q):
    return PSC_FOR_Q.get(q, ("PSC-1", 1))

def verify_manifest(M):
    report = {"structural_ok": True, "errors": [], "warnings": []}
    req = sorted(M.get("required_primes", []))
    covered = sorted(e["q"] for e in M.get("entries", []))
    report["required_primes"] = req
    report["covered_primes"] = covered
    if covered != req:
        report["structural_ok"] = False
        report["errors"].append(f"covered_primes {covered} != required_primes {req}")
    # Pro-Eintrag-Struktur
    levels = ["certificate_level", "presentation_level", "canonical_level"]
    agg = {lv: True for lv in levels}
    seen = set()
    for e in M.get("entries", []):
        q = e["q"]; seen.add(q)
        exp_v, exp_d = expected_psc(q)
        if e.get("psc_version") != exp_v:
            report["structural_ok"] = False
            report["errors"].append(f"q={q}: psc_version {e.get('psc_version')} != erwartet {exp_v}")
        if e.get("d_q") != exp_d:
            report["structural_ok"] = False
            report["errors"].append(f"q={q}: d_q {e.get('d_q')} != erwartet {exp_d}")
        lab = e.get("labels", {})
        for lv in levels:
            if lv not in lab:
                report["structural_ok"] = False
                report["errors"].append(f"q={q}: label {lv} fehlt")
            else:
                agg[lv] = agg[lv] and bool(lab[lv])
    report["aggregate_computed"] = agg
    # Vergleich mit deklarierten aggregate_labels
    decl = M.get("aggregate_labels", {})
    for lv in levels:
        if lv in decl and bool(decl[lv]) != agg[lv]:
            report["warnings"].append(f"aggregate_labels.{lv} deklariert {decl[lv]} != berechnet {agg[lv]}")
    # No-Overclaim-Check
    if agg["certificate_level"] and not agg["canonical_level"]:
        report["warnings"].append("certificate-level erfuellt, aber canonical_level offen: KEIN globales HCT-Theorem, "
                                  "KEIN PCAT/FAQS/abc. Nur lokaler Block.")
    # Verdikt lokaler Satz
    report["LM_local_theorem_certificate_level"] = agg["certificate_level"] and report["structural_ok"]
    report["status"] = ("PROOF-GRADE LOCAL (certificate-level)" if report["LM_local_theorem_certificate_level"]
                        else "TEMPLATE/INCOMPLETE (strukturell gueltig, aber noch keine echten Zertifikate)")
    return report

def main():
    ap = argparse.ArgumentParser(description="Local Drainage Manifest Verifier (HCT/abc)")
    ap.add_argument("manifest", nargs="?", default="_results/lm_60168_raw_template.json",
                    help="Pfad zum Manifest-JSON (default: Template)")
    args = ap.parse_args()
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_manifest(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    # Exit 0 wenn strukturell ok (Template darf certificate_level=false haben)
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
