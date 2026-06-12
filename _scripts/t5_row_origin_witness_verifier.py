#!/usr/bin/env python3
"""
t5_row_origin_witness_verifier.py — Verifier fuer den dedizierten T5-2 Row-Origin Witness (HCT/abc).

Prueft Metadaten, REALE Rowhash-Bindung, symmetrischen Lift, Quotientenbeitrags-Summe und Readiness.

REALE Checks (mechanisch, vom Verifier selbst gerechnet):
  - rowhash_bound: row_hash(stage, stage_row_index, final_sparse_row, q) == rowhash.expected
    (canonical_row/row_hash 1:1 wie im Generator _scripts/mstar_h3a_restline_minikill.py:156-164).
  - trace_value_verified: meta.a_ell == 2.
  - symmetric_lift_checked: alle Werte sind gueltige mod-q-Reps; balancierte Lifts werden ausgewiesen.
  - contributions_ready: quotient_contributions nicht leer UND  sum_per_col(contributions) == final_sparse_row (mod q).

EXTERN (nur gelesen, nicht entscheidbar ohne Formal-Origin + kanonischen Match):
  - hecke/compression/sign/integer_lift_convention_verified.

ready_for_trace_row_embedding = rowhash_bound AND trace_value_verified AND symmetric_lift_checked
                                AND contributions_ready AND alle vier Konventionen.
Setzt NIE canonical_level. Note: _proof-notes/t5_row_origin_witness_contract_2026-06-01.md. Angelegt 2026-06-01.
"""
import argparse, hashlib, json, sys

# --- 1:1 aus dem Generator (mstar_h3a_restline_minikill.py:156-164) ---
def canonical_row(pairs, q):
    return ",".join(f"{int(c)}:{int(v) % q}" for c, v in sorted(pairs) if int(v) % q)

def row_hash(stage, stage_row_index, pairs, q):
    line = f"{stage}\t{stage_row_index}\t{canonical_row(pairs, q)}\n"
    return hashlib.sha256(line.encode("utf-8")).hexdigest()

CONV = ["hecke_convention_verified", "compression_convention_verified",
        "sign_convention_verified", "integer_lift_convention_verified"]

def _balanced(v, q):
    v %= q
    return v - q if v > q // 2 else v

def verify_witness(W):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "checks": {}}
    meta = W.get("meta", {})
    q = meta.get("q", 3863)
    stage = meta.get("stage"); idx = meta.get("stage_row_index")
    expected = W.get("rowhash", {}).get("expected")
    row = [list(map(int, p)) for p in W.get("final_sparse_row", [])]
    rep["rowhash"] = expected
    rep["trace_value"] = meta.get("a_ell")

    # --- Metadaten-Sanity ---
    want = {"N": 60168, "mode": "raw", "sign": 1, "q": 3863, "ell": 5, "a_ell": 2,
            "row_id": "T_5_minus_2_batch_11/575", "stage": "T_5_minus_2_batch_11", "stage_row_index": 575}
    for k, v in want.items():
        if meta.get(k) != v:
            rep["structural_ok"] = False
            rep["errors"].append(f"meta.{k} = {meta.get(k)!r} != erwartet {v!r}")

    # --- REAL: rowhash-Bindung ---
    if row and stage is not None and idx is not None and expected:
        recomputed = row_hash(stage, idx, row, q)
        rep["rowhash_recomputed"] = recomputed
        rowhash_bound = (recomputed == expected)
    else:
        rep["rowhash_recomputed"] = None
        rowhash_bound = False
    rep["checks"]["rowhash_bound"] = rowhash_bound
    if not rowhash_bound and row:
        rep["errors"].append("rowhash_bound=false: final_sparse_row hasht NICHT auf rowhash.expected.")
        rep["structural_ok"] = False

    # --- REAL: trace value ---
    trace_value_verified = (meta.get("a_ell") == 2)
    rep["checks"]["trace_value_verified"] = trace_value_verified

    # --- REAL: symmetrischer Lift gueltig ---
    symmetric_lift_checked = all(0 <= (int(v) % q) < q for _, v in row) and bool(row)
    rep["checks"]["symmetric_lift_checked"] = symmetric_lift_checked
    rep["balanced_lifts"] = [[int(c), _balanced(int(v), q)] for c, v in row]

    # --- REAL: Quotientenbeitraege summieren ---
    contribs = W.get("quotient_contributions", [])
    if contribs:
        agg = {}
        for c, v in contribs:
            agg[int(c)] = (agg.get(int(c), 0) + int(v)) % q
        agg = {c: v for c, v in agg.items() if v}
        rowmap = {int(c): int(v) % q for c, v in row}
        rowmap = {c: v for c, v in rowmap.items() if v}
        contributions_ready = (agg == rowmap)
        rep["checks"]["contributions_match_row"] = contributions_ready
        if not contributions_ready:
            rep["warnings"].append("quotient_contributions summieren NICHT zur final_sparse_row (mod q).")
    else:
        contributions_ready = False
        rep["warnings"].append("quotient_contributions leer (<<FILL>>) -> Formal-Origin fehlt.")
    rep["checks"]["contributions_ready"] = contributions_ready

    # --- EXTERN gelesene Konventionen ---
    readi = W.get("readiness", {})
    conv_all = all(bool(readi.get(c) is True) for c in CONV)
    for c in CONV:
        rep["checks"][c] = bool(readi.get(c) is True)

    ready = (rowhash_bound and trace_value_verified and symmetric_lift_checked
             and contributions_ready and conv_all)
    rep["ready_for_trace_row_embedding"] = ready
    rep["missing"] = [k for k, v in rep["checks"].items() if not v]

    lab = W.get("labels", {})
    if bool(lab.get("ready_for_trace_row_embedding")) and not ready:
        rep["structural_ok"] = False
        rep["errors"].append(f"OVERCLAIM: ready_for_trace_row_embedding=true, aber nicht ready. Offen: {rep['missing']}")

    rep["status"] = ("ROW-ORIGIN COMPLETE (ready for TRE)" if (ready and rep["structural_ok"])
                     else "EVIDENCE-BOUND (rowhash real bestaetigt; Formal-Origin/Konventionen offen)" if rep["structural_ok"]
                     else "INVALID (Metadaten/Rowhash/Overclaim)")
    return rep

# ---------------- Selbsttest ----------------
_REAL_ROW = [[7037, 3862], [7038, 1], [7039, 3862], [7040, 3862], [7041, 3862], [10015, 2], [22583, 3862]]

def _template_like():
    return {
        "meta": {"case": "60168/raw", "N": 60168, "mode": "raw", "sign": 1, "q": 3863, "ell": 5, "a_ell": 2,
                 "row_id": "T_5_minus_2_batch_11/575", "stage": "T_5_minus_2_batch_11", "stage_row_index": 575,
                 "created": "2026-06-01"},
        "rowhash": {"expected": "2578c0ce429aef9be25542091120652f1809745705c80d5053aea547c898e3f5"},
        "final_sparse_row": [list(p) for p in _REAL_ROW],
        "quotient_contributions": [],
        "formal_origin": {"source_manin_symbol": "<<FILL>>", "formal_hecke_row": "<<FILL>>", "trace_subtraction": "<<FILL>>"},
        "readiness": {c: False for c in CONV},
        "labels": {"ready_for_trace_row_embedding": False},
        "no_overclaim": {"ready_if": "...", "but_not": ["abc"]},
    }

def selftest():
    ok = True
    # Template-artig: rowhash real true, aber ready false
    t = verify_witness(_template_like())
    c1 = (t["checks"]["rowhash_bound"] and t["trace_value"] == 2 and not t["checks"]["contributions_ready"]
          and not t["ready_for_trace_row_embedding"] and t["structural_ok"])
    print(f"[+] template: rowhash_bound={t['checks']['rowhash_bound']} contributions_ready={t['checks']['contributions_ready']} ready={t['ready_for_trace_row_embedding']} -> {'PASS' if c1 else 'FAIL'}")
    ok &= c1
    # vollstaendig: contributions = row, alle Konventionen true -> ready true
    full = _template_like()
    full["quotient_contributions"] = [list(p) for p in _REAL_ROW]
    full["readiness"] = {c: True for c in CONV}
    full["labels"]["ready_for_trace_row_embedding"] = True
    f = verify_witness(full)
    c2 = f["ready_for_trace_row_embedding"] and f["structural_ok"] and f["checks"]["contributions_ready"]
    print(f"[+] full: contributions_ready={f['checks']['contributions_ready']} ready={f['ready_for_trace_row_embedding']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # rowhash-Manipulation -> bound false, structural false
    bad = _template_like(); bad["final_sparse_row"][0][1] = 1234
    b = verify_witness(bad)
    c3 = (not b["checks"]["rowhash_bound"]) and (not b["structural_ok"])
    print(f"[-] tampered row: rowhash_bound={b['checks']['rowhash_bound']} struct={b['structural_ok']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # contributions falsch -> contributions_ready false
    wrong = _template_like(); wrong["quotient_contributions"] = [[7037, 1]]; wrong["readiness"] = {c: True for c in CONV}
    w = verify_witness(wrong)
    c4 = (not w["checks"]["contributions_ready"]) and (not w["ready_for_trace_row_embedding"])
    print(f"[-] wrong contributions: contributions_ready={w['checks']['contributions_ready']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    # overclaim ready -> structural false
    oc = _template_like(); oc["labels"]["ready_for_trace_row_embedding"] = True
    o = verify_witness(oc)
    c5 = (not o["structural_ok"]) and any("OVERCLAIM" in e for e in o["errors"])
    print(f"[-] overclaim ready: struct={o['structural_ok']} -> {'PASS' if c5 else 'FAIL'}")
    ok &= c5
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="T5-2 Row-Origin Witness Verifier (HCT/abc)")
    ap.add_argument("witness", nargs="?", default="_results/t5_row_origin_witness_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    with open(args.witness, encoding="utf-8") as f:
        W = json.load(f)
    rep = verify_witness(W)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
