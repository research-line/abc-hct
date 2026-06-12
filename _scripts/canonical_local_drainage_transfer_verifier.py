#!/usr/bin/env python3
"""
canonical_local_drainage_transfer_verifier.py — Transfer-Gate (SRM-1), HCT/abc.

Laesst den lokalen Drainage-Transfer ell_q(exportiert)=0 => ell_q(Q_E)=0 zu OHNE full source equality:
  local_transfer_ready_computed = local_certificate_level AND source_embedding_level (CQ-3w)
                                  AND sink_embedding_level AND column_basis_compatible.
canonical_local_drainage_ready (Label) nur true wenn local_transfer_ready_computed.
Der Witz (SRM-1): source_presentation_equality (CQ-3s) ist NICHT erforderlich -> kann false bleiben.
pcat_ready MUSS false bleiben (braucht CQ-3s + H3-Type-Check + uniformes FAQS). canonical_level (global) nie.

Note: _proof-notes/source_sublattice_monotonicity_2026-06-01.md. Schema: _scripts/canonical_local_drainage_transfer_schema.json.
Angelegt 2026-06-01.
"""
import argparse, json, sys

REQ = ["local_certificate_level", "source_embedding_level", "sink_embedding_level", "column_basis_compatible"]

def verify_transfer(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "inputs_used": {}}
    inp = M.get("inputs", {})
    for k in REQ:
        if k not in inp:
            rep["structural_ok"] = False
            rep["errors"].append(f"inputs.{k} fehlt")
        rep["inputs_used"][k] = bool(inp.get(k) is True)

    computed = all(rep["inputs_used"].get(k) for k in REQ)
    rep["local_transfer_ready_computed"] = computed
    rep["missing"] = [k for k in REQ if not rep["inputs_used"].get(k)]

    lab = M.get("labels", {})
    decl = bool(lab.get("canonical_local_drainage_ready"))
    if decl and not computed:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: canonical_local_drainage_ready=true, aber nicht ready. Offen: {rep['missing']}")
    # PCAT-Overclaim-Guard: pcat_ready darf NIE true sein
    if bool(lab.get("pcat_ready")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: pcat_ready=true. Lokaler Transfer gibt KEIN PCAT (braucht CQ-3s + H3 + uniformes FAQS).")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: globales canonical_level=true wird hier nie gesetzt.")

    rep["canonical_local_drainage_ready"] = decl and computed
    rep["pcat_ready"] = False
    rep["canonical_level"] = False

    # Der Witz: equality NICHT erforderlich
    eq = bool(M.get("source_presentation_equality"))
    rep["source_presentation_equality"] = eq
    if computed and not eq:
        rep["warnings"].append("Drainage-ready OHNE source_presentation_equality (CQ-3s) — genau der SRM-1-Punkt: "
                               "Inklusion (CQ-3w) genuegt fuer ell_q=0. Exakter Content/H3 braucht aber CQ-3s.")
    if computed:
        rep["warnings"].append("Lokaler Transfer ell_q(Q_E)=0 fuer die kalibrierten Primes. KEIN PCAT/FAQS/abc "
                               "(kein uniformes Familienargument).")

    rep["status"] = ("CANONICAL LOCAL DRAINAGE READY (ell_q(Q_E)=0 lokal, ohne full equality)" if (rep["canonical_local_drainage_ready"] and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Inputs offen)" if rep["structural_ok"]
                     else "INVALID (Overclaim/Strukturfehler)")
    return rep

def _full(eq=False):
    return {
        "meta": {"case": "60168/raw", "primes": [2, 3, 5, 31], "created": "2026-06-01"},
        "inputs": {k: True for k in REQ},
        "source_presentation_equality": eq,
        "labels": {"canonical_local_drainage_ready": True, "pcat_ready": False, "canonical_level": False},
        "no_overclaim": {"drainage_ready_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    # Der Kernpunkt: drainage_ready=true OHNE equality
    f = verify_transfer(_full(eq=False))
    c1 = (f["canonical_local_drainage_ready"] and not f["source_presentation_equality"]
          and not f["pcat_ready"] and f["structural_ok"])
    print(f"[+] drainage WITHOUT equality: ready={f['canonical_local_drainage_ready']} eq={f['source_presentation_equality']} pcat={f['pcat_ready']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # ein Input fehlt -> nicht ready
    m = _full(); m["inputs"]["source_embedding_level"] = False; m["labels"]["canonical_local_drainage_ready"] = False
    n = verify_transfer(m)
    c2 = (not n["local_transfer_ready_computed"]) and n["structural_ok"] and "source_embedding_level" in n["missing"]
    print(f"[-] missing source_embedding: computed={n['local_transfer_ready_computed']} missing={n['missing']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # pcat overclaim
    m2 = _full(); m2["labels"]["pcat_ready"] = True
    o = verify_transfer(m2)
    c3 = (not o["structural_ok"]) and any("pcat_ready" in e for e in o["errors"])
    print(f"[-] pcat overclaim: struct={o['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # drainage overclaim (label true, input missing)
    m3 = _full(); m3["inputs"]["local_certificate_level"] = False
    p = verify_transfer(m3)
    c4 = (not p["structural_ok"]) and any("OVERCLAIM: canonical_local_drainage_ready" in e for e in p["errors"])
    print(f"[-] drainage overclaim: struct={p['structural_ok']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Canonical Local Drainage Transfer Verifier (SRM-1)")
    ap.add_argument("manifest", nargs="?", default="_results/canonical_local_drainage_transfer_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_transfer(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
