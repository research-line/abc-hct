#!/usr/bin/env python3
"""
source_canonicality_verifier.py — Verifier fuer den Source Canonicality Contract CQ-3/S2a (HCT/abc).

Erzwingt: A liefert die kanonische Praesentation rho_E: F_E -> M_E (Q_E = coker(rho_E)).
source_canonicality=true NUR wenn ALLE:
  F_E_defined AND M_E_defined AND rho_E_defined AND ap7_equivalence_to_export AND lattice_canonical
  AND source_block_hash gesetzt (kein '<<FILL>>').
WICHTIG: full_rank_witness == true ALLEIN liefert NIE source_ready (AP-4 != CQ-3). Expliziter Guard.
canonical_level wird NIE gesetzt (nur Gesamt-Gate CQ-4).

Schema: _scripts/source_canonicality_schema.json
Note:   _proof-notes/source_canonicality_contract_2026-06-01.md
Angelegt 2026-06-01.
"""
import argparse, json, sys

CANON = ["F_E_defined", "M_E_defined", "rho_E_defined", "ap7_equivalence_to_export", "lattice_canonical"]

def _filled(s):
    return isinstance(s, str) and s.strip() != "" and "<<FILL" not in s

def verify_sc(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checklist": {}}
    sb = M.get("source_block", {})
    cp = M.get("canonical_presentation", {})

    rep["checklist"]["source_block_hash_set"] = _filled(sb.get("source_block_hash"))
    rep["full_rank_witness"] = bool(sb.get("full_rank_witness") is True)
    for k in CANON:
        if k not in cp:
            rep["structural_ok"] = False
            rep["errors"].append(f"canonical_presentation.{k} fehlt")
        rep["checklist"][k] = bool(cp.get(k) is True)

    source_ready = (rep["checklist"]["source_block_hash_set"]
                    and all(rep["checklist"].get(k) for k in CANON))
    rep["source_ready"] = source_ready
    rep["missing"] = [k for k in (["source_block_hash_set"] + CANON) if not rep["checklist"].get(k)]

    # Expliziter Rank-Witness-Only-Guard
    if rep["full_rank_witness"] and not source_ready:
        rep["warnings"].append("full_rank_witness=true ist notwendig, aber NICHT hinreichend (AP-4 schuetzt nur "
                               "Basiswechsel im selben Lattice; CQ-3 verlangt Lattice-Kanonizitaet).")

    lab = M.get("labels", {})
    if bool(lab.get("source_canonicality")) and not source_ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: source_canonicality=true, aber nicht ready. Offen: {rep['missing']}")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true (nur Gesamt-Gate CQ-4).")
    rep["source_canonicality"] = bool(lab.get("source_canonicality")) and source_ready
    rep["canonical_level"] = False

    rep["status"] = ("SOURCE CANONICAL (CQ-3/S2a fuer diesen Block)" if (rep["source_canonicality"] and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Rangzeuge ggf. ja, Kanonizitaet offen)" if rep["structural_ok"]
                     else "INVALID (Overclaim/Strukturfehler)")
    return rep

def _good():
    return {
        "meta": {"case": "selftest", "created": "2026-06-01"},
        "source_block": {"source_block_hash": "d"*64, "full_rank_witness": True},
        "canonical_presentation": {k: True for k in CANON},
        "labels": {"source_canonicality": True, "canonical_level": False},
        "no_overclaim": {"canonicality_holds_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    g = verify_sc(_good())
    c1 = g["source_ready"] and g["source_canonicality"] and not g["canonical_level"] and g["structural_ok"]
    print(f"[+] full canonical: ready={g['source_ready']} canon={g['source_canonicality']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # rank-witness only: full_rank_witness true, canonical flags false -> not ready, warning present
    m = _good()
    m["canonical_presentation"] = {k: False for k in CANON}
    m["labels"]["source_canonicality"] = False
    n = verify_sc(m)
    c2 = (not n["source_ready"]) and n["structural_ok"] and any("hinreichend" in w for w in n["warnings"])
    print(f"[-] rank-witness-only: ready={n['source_ready']} warn={'yes' if n['warnings'] else 'no'} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # overclaim
    m2 = _good(); m2["canonical_presentation"]["lattice_canonical"] = False
    o = verify_sc(m2)
    c3 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] overclaim (label true, lattice not canonical): struct={o['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Source Canonicality Verifier (CQ-3/S2a)")
    ap.add_argument("manifest", nargs="?", default="_results/source_canonicality_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_sc(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
