#!/usr/bin/env python3
"""
rowhash_line_verifier.py — wiederverwendbares Rowhash-Serialization Gate (HCT/abc).

Kapselt die ECHTE Generator-Serialisierung (1:1 aus _scripts/mstar_h3a_restline_minikill.py:156-164):
    canonical_row(row,q) = ",".join(f"{c}:{v%q}" for c,v in sorted(row) if v%q)
    rowhash(stage,idx,row,q) = sha256(f"{stage}\\t{idx}\\t{canonical_row}\\n")

Zweck: Artefaktidentitaet ("diese exportierte Zeile ist wirklich diese sparse row") portabel und REAL
nachpruefbar machen — getrennt von TRE/canonical. Rowhash-Bindung beweist NICHT, dass die Zeile kanonisch
T_ell - a_ell(E) in Q_E ist (dafuer TRE-Konventionen + Source-Canonicality).

Modi:
  python rowhash_line_verifier.py <manifest.json>   # prueft alle entries, aggregiert
  python rowhash_line_verifier.py --selftest          # reproduziert T7 + T5 Hash, Placeholder, Tamper
  python rowhash_line_verifier.py --row STAGE IDX Q "c:v,c:v,..."   # Direkt-Hash

Note: _proof-notes/rowhash_serialization_gate_2026-06-01.md. Angelegt 2026-06-01.
"""
import argparse, hashlib, json, sys

def canonical_row(pairs, q):
    return ",".join(f"{int(c)}:{int(v) % q}" for c, v in sorted(pairs) if int(v) % q)

def row_hash(stage, stage_row_index, pairs, q):
    line = f"{stage}\t{stage_row_index}\t{canonical_row(pairs, q)}\n"
    return hashlib.sha256(line.encode("utf-8")).hexdigest()

def _has_row(e):
    sr = e.get("sparse_row")
    return isinstance(sr, list) and len(sr) > 0

def verify_manifest(M):
    rep = {"structural_ok": True, "errors": [], "warnings": [], "entries": []}
    q = M.get("meta", {}).get("q", 3863)
    all_avail = True
    all_bound = True
    for e in M.get("entries", []):
        sink = e.get("sink") or e.get("row_id")
        exp = e.get("expected_rowhash")
        out = {"sink": sink, "row_id": e.get("row_id"), "expected_rowhash": exp}
        if _has_row(e):
            rec = row_hash(e.get("stage"), e.get("stage_row_index"),
                           [list(map(int, p)) for p in e["sparse_row"]], q)
            out["recomputed_rowhash"] = rec
            out["rowhash_bound"] = (rec == exp)
            if not out["rowhash_bound"]:
                rep["structural_ok"] = False
                rep["errors"].append(f"{sink}: recomputed {rec[:12]}… != expected {str(exp)[:12]}…")
        else:
            out["recomputed_rowhash"] = None
            out["rowhash_bound"] = False
            all_avail = False
            rep["warnings"].append(f"{sink}: sparse_row fehlt (<<FILL>>) -> rowhash nicht nachrechenbar.")
        all_bound = all_bound and out["rowhash_bound"]
        rep["entries"].append(out)

    rep["all_rows_available"] = all_avail
    rep["all_rowhashes_bound"] = all_bound and bool(rep["entries"])

    # Deklarierte Aggregate gegenpruefen (informativ)
    decl = M.get("aggregate", {})
    for k in ("all_rows_available", "all_rowhashes_bound"):
        if k in decl and bool(decl[k]) != rep[k]:
            rep["warnings"].append(f"aggregate.{k} deklariert {decl[k]} != berechnet {rep[k]}")

    rep["scope"] = ("ROWHASH-IDENTITY ONLY: beweist 'diese Zeile = diese sparse row'. "
                    "NICHT TRE (kanonisch T_ell - a_ell(E) in Q_E), NICHT canonical_level, NICHT abc.")
    rep["status"] = ("ROWHASH INTEGRITY COMPLETE (alle Zeilen real gebunden)" if (rep["all_rowhashes_bound"] and rep["structural_ok"])
                     else "PARTIAL (einige Zeilen warten auf sparse_row)" if rep["structural_ok"]
                     else "INVALID (Hash-Mismatch)")
    return rep

# ---------------- Selbsttest ----------------
_T7 = ("T_7_minus_0_batch_1", 1, [[0, 2], [1, 3862], [2, 3862], [3, 3862], [4, 3862], [5, 3862]],
       "a7c9b47d334f80801465ad60f61304c2e9ff7f4991419087c25105b801bbdabf")
_T5 = ("T_5_minus_2_batch_11", 575, [[7037, 3862], [7038, 1], [7039, 3862], [7040, 3862], [7041, 3862], [10015, 2], [22583, 3862]],
       "2578c0ce429aef9be25542091120652f1809745705c80d5053aea547c898e3f5")

def selftest():
    ok = True
    for name, (st, idx, row, exp) in (("T7", _T7), ("T5", _T5)):
        got = row_hash(st, idx, row, 3863)
        c = (got == exp)
        print(f"[+] {name}: recomputed=={exp[:12]}… -> {'PASS' if c else 'FAIL'}")
        ok &= c
    # Placeholder-Eintrag -> bound false
    man = {"meta": {"q": 3863},
           "entries": [{"sink": "t7", "row_id": "T_7_minus_0_batch_1/1", "stage": "T_7_minus_0_batch_1",
                        "stage_row_index": 1, "sparse_row": _T7[2], "expected_rowhash": _T7[3]},
                       {"sink": "t5", "row_id": "T_5_minus_2_batch_11/575", "stage": "T_5_minus_2_batch_11",
                        "stage_row_index": 575, "sparse_row": None, "expected_rowhash": _T5[3]}]}
    r = verify_manifest(man)
    c2 = (r["entries"][0]["rowhash_bound"] and not r["entries"][1]["rowhash_bound"]
          and not r["all_rowhashes_bound"] and not r["all_rows_available"] and r["structural_ok"])
    print(f"[-] placeholder T5: t7_bound={r['entries'][0]['rowhash_bound']} t5_bound={r['entries'][1]['rowhash_bound']} all_bound={r['all_rowhashes_bound']} -> {'PASS' if c2 else 'FAIL'}")
    ok &= c2
    # Beide voll -> all bound true
    man2 = {"meta": {"q": 3863},
            "entries": [{"sink": "t7", "stage": _T7[0], "stage_row_index": _T7[1], "sparse_row": _T7[2], "expected_rowhash": _T7[3]},
                        {"sink": "t5", "stage": _T5[0], "stage_row_index": _T5[1], "sparse_row": _T5[2], "expected_rowhash": _T5[3]}]}
    r2 = verify_manifest(man2)
    c3 = r2["all_rowhashes_bound"] and r2["all_rows_available"] and r2["structural_ok"]
    print(f"[+] both full: all_rowhashes_bound={r2['all_rowhashes_bound']} -> {'PASS' if c3 else 'FAIL'}")
    ok &= c3
    # Tamper -> mismatch
    man3 = json.loads(json.dumps(man2)); man3["entries"][1]["sparse_row"][0][1] = 99
    r3 = verify_manifest(man3)
    c4 = (not r3["structural_ok"]) and (not r3["entries"][1]["rowhash_bound"])
    print(f"[-] tamper T5: struct={r3['structural_ok']} t5_bound={r3['entries'][1]['rowhash_bound']} -> {'PASS' if c4 else 'FAIL'}")
    ok &= c4
    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser(description="Rowhash Line Verifier (HCT/abc reusable gate)")
    ap.add_argument("manifest", nargs="?", default="_results/t5_t7_rowhash_integrity_manifest_60168_raw_template.json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--row", nargs=4, metavar=("STAGE", "IDX", "Q", "CANON"),
                    help="Direkt-Hash: STAGE IDX Q 'c:v,c:v,...'")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.row:
        stage, idx, q, canon = args.row
        line = f"{stage}\t{int(idx)}\t{canon}\n"
        print(hashlib.sha256(line.encode("utf-8")).hexdigest())
        sys.exit(0)
    with open(args.manifest, encoding="utf-8") as f:
        M = json.load(f)
    rep = verify_manifest(M)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["structural_ok"] else 2)

if __name__ == "__main__":
    main()
