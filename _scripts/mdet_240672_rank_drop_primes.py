#!/usr/bin/env python3
"""
M-DET 240672: Rangabfall-Primes der gestapelten Gate-2-Witness-Matrix (Sage, Mac).

Replikation von M-DET 1a am 240672-System gemaess Satz-Note Par. 8f
(MG_conditional_single_curve_theorem_2026-06-12.md): Dank pivot-freier
D(W)-Definition (D_r = ggT aller r x r-Minoren = e_1...e_r) braucht die
Replikation KEINE Minoren — GF(p)-Raenge der festen Z-Matrix genuegen:
    rank_{F_p}(M) < r  <=>  p | e_r  =>  p | D(W).

DIE FESTE MATRIX M_total (Zertifikatsobjekt, deterministisch):
  (1) Spaltenbasis: ManinSymbolList_gamma0(240672, 2), S/I-Relationen
      (sign=+1), sparse_2term_quotient ueber GF(3863), Z-Lift der
      Skalare (|s| <= 2 verifiziert). ncols = 126720 (FATAL sonst).
  (2) Witness-Zeilen: alle 126672 Zeilen aus dem Cremona-Witness
      (rc3c, q=3863), symmetrischer Z-Lift (|v| <= 200 Guard;
      Replay-Statistik: max 4). 84464 Manin-Stage + 42208 Hecke-Stage.
  (3) Operator-Bloecke: VEREINIGUNG der v2b- und v3-Replay-Abdeckungen
      (Symbole 0..k*1000-1 je Operator, HECKE_BATCH_SIZE=1000,
      Symbol-Reihenfolge aufsteigend wie t7_replay_fingerprint_v3.py):
        T13: 4000 (v2b 4 = v3 4), T7: 3000 (v3), T11: 3000 (v3),
        T17: 3000 (beide 3), T19: 3000 (beide 3), U23: 4000 (beide 4).
      Zeile fuer Symbol i: (i, -a_p) + Summe_A apply(i, A) ueber
      HeilbronnCremona(p); exakte Z-Akkumulation (KEINE mod-Reduktion).

ANKER (beweisbar erwartet, Implementierungs-Selbsttest):
  M_total enthaelt die v3-Zeilenmenge => rank mod 5077 >= v3-Endrang
  = 126719; und die v2b-Zeilenmenge => rank mod 3863 >= 126719.
  Strukturell rank <= 126719 (f_E-Linie ueberlebt ueber Q: qdim_Q >= 1).
  Beide Anker-Raenge MUESSEN also exakt 126719 sein; Abweichung =>
  Implementierungsfehler-Verdacht (Warnung, kein Abbruch der Messung).

ERGEBNIS: r = rank_Q = max_p rank_p (Modalwert), Drop-Primes
  {p : rank_p < r} = Trager von e_r | D(W). 60168-Vergleich: dort
  waren die Drops EXAKT das S5-Inventar {2, 3, 5, 31}.

Checkpoint: JSON wird nach JEDEM Prime geschrieben (OOM-/Abbruch-sicher).
Output: _results/mdet_240672_rank_drop_primes_<date>.{json,md}
"""
import json, sys, time
from datetime import date
from pathlib import Path

N = 240672
WITNESS_Q = 3863
SIGN = 1
NCOLS_EXPECTED = 126720
WITNESS_ROWS_EXPECTED = 126672
RANK_ANCHOR = 126719  # = ncols - 1 (qdim_Q = 1)
LIFT_GUARD = 200
AP_VALUES = {3: 1, 5: 2, 7: 0, 11: 0, 13: -6, 17: 6, 19: 0, 23: 1}
# Vereinigung v2b/v3: Operator -> Anzahl Symbole (Batches x 1000)
OPERATOR_COVERAGE = [(13, 4000), (7, 3000), (11, 3000), (17, 3000), (19, 3000), (23, 4000)]
# Anker zuerst (Selbsttest), dann S5-Kandidaten, dann Kontrollen
PRIMES = [5077, 3863, 2, 3, 5, 31, 7, 19, 23]
WITNESS_PATH = Path("_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl")
OUT_JSON = "_results/mdet_240672_rank_drop_primes_{}.json".format(date.today())
OUT_MD = "_results/mdet_240672_rank_drop_primes_{}.md".format(date.today())


def main():
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    half = WITNESS_Q // 2
    print("=== M-DET 240672: rank drop primes (stacked Gate-2 witness matrix) ===")
    print(f"Primes: {PRIMES} | Operator coverage: {OPERATOR_COVERAGE}")
    sys.stdout.flush()

    print(f"[{ts()}] Importing Sage...")
    from sage.all import GF, ZZ, matrix
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient
    from sage.modular.modsym.heilbronn import HeilbronnCremona

    # Phase 0: Spaltenbasis (identisch zu p2_dimer_witness_240672.py)
    Fq = GF(WITNESS_Q)
    print(f"[{ts()}] Building ManinSymbolList_gamma0({N}, 2)...")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    rels = set(modS_relations(syms))
    rels.update(modI_relations(syms, SIGN))
    mod = sparse_2term_quotient(rels, nsyms, Fq)
    mod_map = []
    rep_to_col = {}
    for entry in mod:
        rep, scalar = entry
        if scalar == 0:
            mod_map.append(None)
        else:
            rep_i = int(rep)
            if rep_i not in rep_to_col:
                rep_to_col[rep_i] = len(rep_to_col)
            sc = int(scalar)
            if sc > half:
                sc -= WITNESS_Q
            assert abs(sc) <= 2, f"2-term scalar lift {sc} unexpectedly large"
            mod_map.append((rep_to_col[rep_i], sc))
    ncols = len(rep_to_col)
    print(f"[{ts()}] ncols after 2-term: {ncols} ({time.time()-t0:.0f}s)")
    if ncols != NCOLS_EXPECTED:
        print(f"FATAL: ncols={ncols} != {NCOLS_EXPECTED}. ABBRUCH.")
        return 2
    sys.stdout.flush()

    # Phase 1: Witness-Zeilen (Z, symmetrischer Lift)
    entries = {}
    nrows = 0
    max_lift = 0
    with open(WITNESS_PATH) as f:
        for line in f:
            rec = json.loads(line)
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WITNESS_Q
                if abs(v) > LIFT_GUARD:
                    print(f"FATAL: Witness-Lift |{v}| > {LIFT_GUARD} (Zeile {nrows}). ABBRUCH.")
                    return 4
                if v:
                    entries[(nrows, int(c))] = v
                    if abs(v) > max_lift:
                        max_lift = abs(v)
            nrows += 1
    if nrows != WITNESS_ROWS_EXPECTED:
        print(f"FATAL: {nrows} Witness-Zeilen != {WITNESS_ROWS_EXPECTED} (mid-sync truncation?). ABBRUCH.")
        return 3
    print(f"[{ts()}] Witness geladen: {nrows} Zeilen, nnz={len(entries)}, max|lift|={max_lift} ({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    # Phase 2: Operator-Bloecke (Z-exakt, deterministisch)
    for p, n_symbols in OPERATOR_COVERAGE:
        ap = AP_VALUES[p]
        mats = HeilbronnCremona(p).to_list()
        t1 = time.time()
        block_nnz = 0
        for i in range(n_symbols):
            acc = {}
            terms = [(i, -ap)]
            for A in mats:
                terms.extend(syms.apply(i, A))
            for j, coeff in terms:
                mapped = mod_map[int(j)]
                if mapped is None:
                    continue
                col, scalar = mapped
                acc[col] = acc.get(col, 0) + int(coeff) * scalar
            for col, v in acc.items():
                if v:
                    entries[(nrows, col)] = v
                    block_nnz += 1
            nrows += 1
        print(f"[{ts()}] T_{p}: {n_symbols} Zeilen, +{block_nnz} nnz ({time.time()-t1:.0f}s)")
        sys.stdout.flush()

    print(f"[{ts()}] M_total: {nrows} x {ncols}, nnz={len(entries)} ({time.time()-t0:.0f}s)")
    MZ = matrix(ZZ, nrows, ncols, entries, sparse=True)
    del entries
    print(f"[{ts()}] Sage-Matrix gebaut ({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    # Phase 3: GF(p)-Raenge mit Checkpoint nach jedem Prime
    ranks = {}
    report = {"date": str(date.today()), "level": N, "nrows": nrows, "ncols": ncols,
              "operator_coverage": OPERATOR_COVERAGE, "rank_anchor": RANK_ANCHOR,
              "max_witness_lift": max_lift, "ranks": ranks, "status": "running"}
    for p in PRIMES:
        t1 = time.time()
        Mp = MZ.change_ring(GF(p))
        r = int(Mp.rank())
        del Mp
        ranks[str(p)] = r
        anchor = ""
        if p in (5077, 3863):
            anchor = " [ANKER OK]" if r == RANK_ANCHOR else f" [ANKER-VERLETZUNG: erwartet {RANK_ANCHOR} — Implementierungsfehler-Verdacht!]"
        print(f"[{ts()}] p={p}: rank={r}{anchor} ({time.time()-t1:.0f}s)")
        sys.stdout.flush()
        with open(OUT_JSON, "w") as f:
            json.dump(report, f, indent=2)

    r_max = max(ranks.values())
    drops = {p: r_max - r for p, r in ranks.items() if r < r_max}
    report["status"] = "done"
    report["rank_Q_modal"] = r_max
    report["rank_drop_primes"] = drops
    report["anchor_ok"] = (ranks.get("5077") == RANK_ANCHOR and ranks.get("3863") == RANK_ANCHOR)
    report["s5_comparison_60168"] = "Drops am 60168 waren exakt {2: 2, 3: 1, 5: 1, 31: 1}"
    report["total_seconds"] = time.time() - t0
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# M-DET 240672: Rangabfall-Primes ({})".format(date.today()), ""]
    lines.append("M_total: {} x {} (Witness 126672 + Operator-Bloecke v2b-union-v3)".format(nrows, ncols))
    lines.append("")
    lines.append("| p | rank_p | Defekt |")
    lines.append("|---|---|---|")
    for p in PRIMES:
        r = ranks[str(p)]
        lines.append("| {} | {} | {} |".format(p, r, r_max - r))
    lines.append("")
    lines.append("rank_Q (modal) = {}; Anker (5077/3863 = {}): {}".format(
        r_max, RANK_ANCHOR, "OK" if report["anchor_ok"] else "VERLETZT"))
    lines.append("Drop-Primes: {}".format(drops if drops else "KEINE"))
    lines.append("")
    lines.append("Total: {:.0f}s".format(report["total_seconds"]))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
