#!/usr/bin/env python3
"""
source_stage_classifier.py — Stage->Familie-Klassifikator fuer Source-Row-Manifeste (HCT/abc).

Liest ein source_rows.jsonl (Felder: stage, stage_row_index, row, row_line_sha256), ordnet jede Zeile
einer kanonischen Relationsfamilie zu und zaehlt; optional --verify-rowhash rechnet die Rowhash-Bindung
real nach (row_hash 1:1 aus dem Generator). --emit-registry gibt ein Registry-Geruest fuer den
source_row_embedding_registry_verifier aus (family_canonical_defined bleibt false: das ist Mathematik,
nicht Klassifikation).

Familienregeln (datengetrieben fuer 60168/raw, generisch erweiterbar):
  stage startswith 'manin'      -> 'manin'
  stage startswith 'T_5_minus'  -> 'T_5_minus_2'
  stage startswith 'T_7_minus'  -> 'T_7_minus_0'
  stage startswith 'T_11_minus' -> 'T_11_minus_0'
  stage startswith 'T_13_minus' -> 'T_13_minus'
  sonst                          -> stage (als eigene Familie)

Note: _proof-notes/source_row_embedding_registry_2026-06-01.md. Angelegt 2026-06-01.
"""
import argparse, hashlib, json, sys
from collections import OrderedDict

CANON_DEF = {
    "manin": "Manin-2-/3-Term-Relationen + T-Relationen nach S/I-Quotient (definieren H_1)",
    "T_5_minus_2": "T_5 v - a_5(E) v, a_5(E)=2 (Hecke-Eigenrelation)",
    "T_7_minus_0": "T_7 v - a_7(E) v, a_7(E)=0",
    "T_11_minus_0": "T_11 v - a_11(E) v, a_11(E)=0",
    "T_13_minus": "T_13 v - a_13(E) v, a_13(E)=-6",
}

def family_of(stage):
    s = str(stage)
    if s.startswith("manin"): return "manin"
    if s.startswith("T_5_minus"): return "T_5_minus_2"
    if s.startswith("T_7_minus"): return "T_7_minus_0"
    if s.startswith("T_11_minus"): return "T_11_minus_0"
    if s.startswith("T_13_minus"): return "T_13_minus"
    return s

def canonical_row(pairs, q):
    return ",".join(f"{int(c)}:{int(v) % q}" for c, v in sorted(pairs) if int(v) % q)

def row_hash(stage, idx, pairs, q):
    return hashlib.sha256(f"{stage}\t{idx}\t{canonical_row(pairs, q)}\n".encode("utf-8")).hexdigest()

def classify(path, q, verify_rowhash):
    fams = OrderedDict()
    total = 0; bound_total = 0
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln: continue
            d = json.loads(ln)
            st = d.get("stage") or d.get("stage_id") or ""
            fam = family_of(st)
            e = fams.setdefault(fam, {"family": fam, "stage_prefix": None, "row_count": 0,
                                      "n_rowhash_bound": 0, "sample_rowhash": None})
            e["row_count"] += 1; total += 1
            if e["stage_prefix"] is None: e["stage_prefix"] = st
            rh = d.get("row_line_sha256") or d.get("rowhash")
            if e["sample_rowhash"] is None and rh: e["sample_rowhash"] = rh
            if verify_rowhash and "row" in d and rh:
                if row_hash(st, d.get("stage_row_index"), d["row"], q) == rh:
                    e["n_rowhash_bound"] += 1; bound_total += 1
            elif not verify_rowhash and rh:
                e["n_rowhash_bound"] += 1; bound_total += 1
    return fams, total, bound_total

def main():
    ap = argparse.ArgumentParser(description="Source Stage Classifier (HCT/abc CQ-3w)")
    ap.add_argument("source_rows", help="Pfad zum source_rows.jsonl")
    ap.add_argument("--q", type=int, default=3863)
    ap.add_argument("--verify-rowhash", action="store_true", help="Rowhash-Bindung real nachrechnen")
    ap.add_argument("--emit-registry", action="store_true", help="Registry-JSON-Geruest ausgeben")
    args = ap.parse_args()
    fams, total, bound = classify(args.source_rows, args.q, args.verify_rowhash)

    if args.emit_registry:
        reg = {
            "_status": "AUTO-EMITTED by source_stage_classifier — Klassifikation+Rowhash real; family_canonical_defined=false (Mathematik offen).",
            "_schema": "_scripts/source_row_embedding_registry_schema.json",
            "meta": {"case": "60168/raw", "q": args.q, "n_source_rows": total, "created": "2026-06-01",
                     "source": args.source_rows},
            "families": [
                {"family": e["family"], "stage_prefix": e["stage_prefix"], "row_count": e["row_count"],
                 "n_rowhash_bound": e["n_rowhash_bound"], "family_canonical_defined": False,
                 "transcript_bound": False, "canonical_definition": CANON_DEF.get(e["family"], "<<FILL>>"),
                 "sample_rowhash": e["sample_rowhash"]}
                for e in fams.values()
            ],
            "column_basis": {"column_basis_compatible": False, "column_basis_hash": "<<FILL>>"},
            "labels": {"source_embedding_level": False, "source_presentation_equality": False, "canonical_level": False},
            "no_overclaim": {"embedding_holds_if": "alle Familien family_canonical_defined + transcript_bound + voll rowhash-gebunden + column_basis_compatible",
                             "but_not": ["CQ-3s", "H3", "PCAT/FAQS", "abc"]},
        }
        print(json.dumps(reg, indent=2, ensure_ascii=False))
    else:
        print(f"total rows = {total}")
        print(f"rowhash {'verified' if args.verify_rowhash else 'present'}: {bound}/{total}")
        for e in fams.values():
            print(f"  {e['family']:16s} stage={e['stage_prefix']:32s} rows={e['row_count']:6d} bound={e['n_rowhash_bound']:6d}")
    sys.exit(0)

if __name__ == "__main__":
    main()
