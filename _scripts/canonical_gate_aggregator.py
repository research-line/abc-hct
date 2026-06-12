#!/usr/bin/env python3
"""
canonical_gate_aggregator.py — verdrahtet CQ-4 als ECHTES Gesamt-Gate (HCT/abc).

Statt die canonical_claim-Booleans von Hand zu setzen, FUEHRT dieser Aggregator die Leaf-Verifier real auf
ihren Claim-Dateien aus und speist deren Readiness in das canonical_claim-Gate:

  prerequisites:
    psc_certificate_level  <- lm_manifest_verifier(lm).aggregate_computed.certificate_level
    lm_certificate_level   <- dito
    presentation_level     <- presentation_upgrade_verifier(pres).presentation_level
    h3_canonical_ready     <- h3_direction_verifier(h3dir).canonical_ready  AND  h3_typecheck_verifier(h3tc).h3_type_checked
  obligations:
    cq2_trace_embedding    <- AND ueber alle trace_row_embedding_verifier(tre_i).trace_row_embedding
    cq3_source_canonicality<- source_canonicality_verifier(sc).source_canonicality
    cq1_transfer_iso       <- (kein eigener Leaf-Verifier; S2-Existenz) passthrough aus wiring.cq1_transfer_iso, default false

Dann verify_canonical(...) -> canonical_ready / canonical_level.
canonical_level=true ist nur moeglich, wenn ALLE Leaves grün sind. Default-Wiring zeigt auf die aktuellen
Templates => canonical_ready=false.

Hinweis cq1_transfer_iso: bewusst NICHT leaf-abgeleitet (es ist die S2a/S2b-Existenz des kanonischen Iso,
gekoppelt an CQ-3). Wird transparent als 'not leaf-wired' geloggt.

Liegt in _scripts/ neben den Leaf-Verifiern. Note: _proof-notes/canonical_hct_trace_quotient_blueprint_2026-06-01.md.
Angelegt 2026-06-01.
"""
import argparse, json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import lm_manifest_verifier as lmv
import presentation_upgrade_verifier as puv
import trace_row_embedding_verifier as trev
import source_canonicality_verifier as scv
import h3_direction_verifier as h3dv
import h3_typecheck_verifier as h3tv
import canonical_claim_verifier as ccv

# Default-Wiring: zeigt auf die aktuellen 60168/raw-Artefakte (Templates/Partial).
DEFAULT_WIRING = {
    "lm": "_results/lm_60168_raw_template.json",
    "presentation": "_results/presentation_upgrade_60168_raw_template.json",
    "tre": ["_results/trace_row_embedding_60168_raw_t7_partial.json"],
    "sc": "_results/source_canonicality_60168_raw_template.json",
    "h3_dir": "_results/h3_direction_60168_raw_template.json",
    "h3_tc": "_results/h3_typecheck_60168_raw_template.json",
    "cq1_transfer_iso": False,
}

def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def aggregate(wiring):
    leaves = {}

    lm_rep = lmv.verify_manifest(_load(wiring["lm"]))
    lm_cert = bool(lm_rep.get("aggregate_computed", {}).get("certificate_level"))
    leaves["lm"] = {"file": wiring["lm"], "certificate_level": lm_cert, "structural_ok": lm_rep.get("structural_ok")}

    pres_rep = puv.verify_upgrade(_load(wiring["presentation"]))
    pres = bool(pres_rep.get("presentation_level"))
    leaves["presentation"] = {"file": wiring["presentation"], "presentation_level": pres,
                              "presentation_ready": pres_rep.get("presentation_ready")}

    tre_results = []
    for p in wiring.get("tre", []):
        r = trev.verify_tre(_load(p))
        tre_results.append({"file": p, "trace_row_embedding": bool(r.get("trace_row_embedding")),
                            "trace_row_ready": r.get("trace_row_ready"), "missing": r.get("missing")})
    cq2 = bool(tre_results) and all(t["trace_row_embedding"] for t in tre_results)
    leaves["tre"] = tre_results

    sc_rep = scv.verify_sc(_load(wiring["sc"]))
    cq3 = bool(sc_rep.get("source_canonicality"))
    leaves["sc"] = {"file": wiring["sc"], "source_canonicality": cq3, "source_ready": sc_rep.get("source_ready")}

    h3d_rep = h3dv.verify_h3(_load(wiring["h3_dir"]))
    h3t_rep = h3tv.verify_h3tc(_load(wiring["h3_tc"]))
    h3_ready = bool(h3d_rep.get("canonical_ready")) and bool(h3t_rep.get("h3_type_checked"))
    leaves["h3"] = {"dir_file": wiring["h3_dir"], "tc_file": wiring["h3_tc"],
                    "h3_direction_canonical_ready": h3d_rep.get("canonical_ready"),
                    "h3_type_checked": h3t_rep.get("h3_type_checked"), "h3_canonical_ready": h3_ready}

    cq1 = bool(wiring.get("cq1_transfer_iso", False))

    synthetic_claim = {
        "meta": {"claim_id": "CANON-60168-AGGREGATED", "case": "60168/raw", "created": "2026-06-01"},
        "prerequisites": {
            "psc_certificate_level": lm_cert,
            "lm_certificate_level": lm_cert,
            "presentation_level": pres,
            "h3_canonical_ready": h3_ready,
        },
        "obligations": {
            "cq1_transfer_iso": cq1,
            "cq2_trace_embedding": cq2,
            "cq3_source_canonicality": cq3,
        },
        "labels": {"presentation_level": pres, "canonical_level": False},
        "no_overclaim": {"canonical_holds_if": "alle prerequisites+obligations", "but_not": ["PCAT", "FAQS", "abc"]},
    }
    canon_rep = ccv.verify_canonical(synthetic_claim)

    return {
        "wiring": {k: wiring[k] for k in wiring},
        "leaves": leaves,
        "aggregated_prerequisites": synthetic_claim["prerequisites"],
        "aggregated_obligations": synthetic_claim["obligations"],
        "cq1_note": "cq1_transfer_iso NICHT leaf-abgeleitet (S2-Existenz, manuell/gekoppelt an CQ-3).",
        "canonical_ready": canon_rep.get("canonical_ready"),
        "canonical_level": canon_rep.get("canonical_level"),
        "missing": canon_rep.get("missing"),
        "status": canon_rep.get("status"),
    }

def selftest():
    ok = True
    # Aggregations-Logik direkt testen ueber verify_canonical (Leaves sind einzeln selbst-getestet).
    all_true = {
        "prerequisites": {"psc_certificate_level": True, "lm_certificate_level": True,
                          "presentation_level": True, "h3_canonical_ready": True},
        "obligations": {"cq1_transfer_iso": True, "cq2_trace_embedding": True, "cq3_source_canonicality": True},
        "labels": {"presentation_level": True, "canonical_level": True},
        "no_overclaim": {"canonical_holds_if": "...", "but_not": ["abc"]},
    }
    r = ccv.verify_canonical(all_true)
    c1 = r["canonical_ready"] and r["canonical_level"]
    print(f"[+] all leaves green -> ready={r['canonical_ready']} canon={r['canonical_level']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    one_false = json.loads(json.dumps(all_true))
    one_false["obligations"]["cq2_trace_embedding"] = False
    r2 = ccv.verify_canonical(one_false)
    c2 = (not r2["canonical_ready"]) and (not r2["structural_ok"])  # label true + not ready -> overclaim
    print(f"[-] cq2 red + label true -> ready={r2['canonical_ready']} struct={r2['structural_ok']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Canonical Gate Aggregator (CQ-4 wiring)")
    ap.add_argument("wiring", nargs="?", help="Pfad zu einer Wiring-JSON (sonst DEFAULT_WIRING auf Templates)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    wiring = _load(args.wiring) if args.wiring else DEFAULT_WIRING
    rep = aggregate(wiring)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    # Exit 0 immer ok solange strukturell konsistent; Aggregat-false ist erlaubt (Templates).
    sys.exit(0)

if __name__ == "__main__":
    main()
