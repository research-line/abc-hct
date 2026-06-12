#!/usr/bin/env python3
"""
coupled_q2_tooth_gate_verifier.py — Gate fuer den gekoppelten q=2-PSC-2-Zahn (HCT/abc).

Koppelt die zwei Trace-Sinks t5=(T5-2) und t7=(T7):
  sink_ready_computed = inputs.t5_tre AND inputs.t7_tre AND inputs.psc2_certificate_level
  sink_canonical_ready (Label) darf nur true sein, wenn sink_ready_computed (Overclaim-Guard).
  canonical_level wird NIE gesetzt: selbst ein saturierender, embedding-sicherer q=2-Zahn ist erst canonical,
  wenn zusaetzlich Source-Canonicality (CQ-3) erfuellt ist (separat, Gesamt-Gate CQ-4).

Optional --wire: speist t5_tre/t7_tre real aus den TRE-Claims via trace_row_embedding_verifier.

Schema: _scripts/coupled_q2_tooth_gate_schema.json
Note:   _proof-notes/coupled_q2_canonical_tooth_contract_2026-06-01.md
Angelegt 2026-06-01.
"""
import argparse, json, os, sys

def verify_gate(M, wire=False):
    rep = {"structural_ok": True, "errors": [], "warnings": []}
    inp = dict(M.get("inputs", {}))

    if wire:
        _here = os.path.dirname(os.path.abspath(__file__))
        if _here not in sys.path:
            sys.path.insert(0, _here)
        import trace_row_embedding_verifier as trev
        for rr in M.get("repair_rows", []):
            claim = rr.get("tre_claim")
            sink = rr.get("sink")
            if claim and os.path.exists(claim):
                with open(claim, encoding="utf-8") as f:
                    r = trev.verify_tre(json.load(f))
                key = "t5_tre" if sink == "t5" else "t7_tre" if sink == "t7" else None
                if key:
                    inp[key] = bool(r.get("trace_row_embedding"))
                    rep.setdefault("wired", {})[key] = inp[key]

    t5 = bool(inp.get("t5_tre") is True)
    t7 = bool(inp.get("t7_tre") is True)
    psc2 = bool(inp.get("psc2_certificate_level") is True)
    rep["inputs_used"] = {"t5_tre": t5, "t7_tre": t7, "psc2_certificate_level": psc2}

    sink_ready_computed = t5 and t7 and psc2
    rep["sink_ready_computed"] = sink_ready_computed
    rep["missing"] = [k for k, v in (("t5_tre", t5), ("t7_tre", t7), ("psc2_certificate_level", psc2)) if not v]

    lab = M.get("labels", {})
    if bool(lab.get("sink_canonical_ready")) and not sink_ready_computed:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: sink_canonical_ready=true, aber nicht ready. Offen: {rep['missing']}")
    if bool(lab.get("canonical_level")):
        rep["structural_ok"] = False
        rep["errors"].append("OVERCLAIM: canonical_level=true wird vom q=2-Gate nie gesetzt (Source-Canonicality CQ-3 separat).")
    rep["sink_canonical_ready"] = bool(lab.get("sink_canonical_ready")) and sink_ready_computed
    rep["canonical_level"] = False

    # Paarungs-Evidenz nur informativ pruefen
    pe = M.get("pairing_evidence", {})
    if pe.get("pairing_matrix") == [[1, 1], [1, 0]] and pe.get("saturates") is True:
        rep["pairing_evidence_ok"] = True
    else:
        rep["pairing_evidence_ok"] = False
        rep["warnings"].append("pairing_evidence weicht von [[1,1],[1,0]]/saturates=true ab.")

    if sink_ready_computed and rep["structural_ok"]:
        rep["warnings"].append("q=2-Zahn embedding-sicher + saturiert, aber canonical_level erfordert noch "
                               "Source-Canonicality (CQ-3). Lokaler Baustein, KEIN PCAT/FAQS/abc.")

    rep["status"] = ("Q2-TOOTH SINK-READY (lokal; canonical braucht noch CQ-3)" if (rep["sink_canonical_ready"] and rep["structural_ok"])
                     else "TEMPLATE/INCOMPLETE (Paarung real, aber TRE/PSC-2 noch offen)" if rep["structural_ok"]
                     else "INVALID (Overclaim/Strukturfehler)")
    return rep

def _good():
    return {
        "meta": {"case": "selftest", "q": 2, "created": "2026-06-01"},
        "repair_rows": [
            {"sink": "t5", "row_id": "T_5_minus_2_batch_11/575", "tre_claim": ""},
            {"sink": "t7", "row_id": "T_7_minus_0_batch_1/1", "tre_claim": ""},
        ],
        "inputs": {"t5_tre": True, "t7_tre": True, "psc2_certificate_level": True},
        "pairing_evidence": {"witness": "w.json", "pairing_matrix": [[1, 1], [1, 0]], "saturates": True},
        "labels": {"sink_canonical_ready": True, "canonical_level": False},
        "no_overclaim": {"sink_ready_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    g = verify_gate(_good())
    c1 = g["sink_ready_computed"] and g["sink_canonical_ready"] and not g["canonical_level"] and g["structural_ok"]
    print(f"[+] all three green: computed={g['sink_ready_computed']} ready={g['sink_canonical_ready']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # one input false -> not ready
    m = _good(); m["inputs"]["t5_tre"] = False; m["labels"]["sink_canonical_ready"] = False
    n = verify_gate(m)
    c2 = (not n["sink_ready_computed"]) and n["structural_ok"] and n["missing"] == ["t5_tre"]
    print(f"[-] t5 missing: computed={n['sink_ready_computed']} missing={n['missing']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # overclaim sink_canonical_ready
    m2 = _good(); m2["inputs"]["psc2_certificate_level"] = False
    o = verify_gate(m2)
    c3 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] sink overclaim: struct={o['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # canonical overclaim
    m3 = _good(); m3["labels"]["canonical_level"] = True
    c = verify_gate(m3)
    c4 = (not c["structural_ok"]) and any("canonical_level=true" in e for e in c["errors"])
    print(f"[-] canonical overclaim: struct={c['structural_ok']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Coupled q=2 Tooth Gate Verifier (HCT/abc)")
    ap.add_argument("manifest", nargs="?", default="_results/coupled_q2_tooth_gate_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--wire", action="store_true", help="t5_tre/t7_tre real aus den TRE-Claims speisen")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_gate(M, wire=args.wire)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
