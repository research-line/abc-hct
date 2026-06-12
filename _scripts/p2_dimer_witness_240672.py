#!/usr/bin/env python3
"""
p2 Dimer Witness 240672 — mod-2-Kern-Schnitt + Dimer-Extraktion (B2 (p1)).

Ziel: Das 240672-Analogon des 60168-p2-Kernvektors v (Dimer-Komplement,
Frustrations-Gesetz). Der rc3c-Witness-Kern mod 2 ist 607-dimensional
(lokal verifiziert 2026-06-11); die Dimer-Eigenschaft zeichnet den
schmalen "Repair-artigen" Unterraum aus. Dieses Script schneidet den
Kern mit FRISCH generierten Hecke-Zeilen mod 2 (T3+1, T5, T7, T11, T13,
optional T17/T19/U23+1 — a_p mod 2 aus LMFDB-verifizierten Eigenwerten
a3=1, a5=2, a7=0, a11=0, a13=-6, a17=6, a19=0, a23=1), bis die
Kern-Dimension <= KSTOP ist, extrahiert die Kernbasis und testet ALLE
2^K-1 Kombinationen auf die Dimer-Eigenschaft (jedes manin-Dreieck
genau 2 Support-Kanten, m=0 verboten).

Methodik-Notizen (Lessons 2026-06-11):
  - mod 2 NUR ueber den symmetrischen Lift (Witness-q 3863 ist ungerade).
  - Kern-Extraktion aus Bitmasken-Basis (Pivot = hoechstes Bit) via
    AUFSTEIGENDER Substitution; jeder Kernvektor wird gegen das System
    verifiziert (M*x == 0 mod 2) bevor er verwendet wird.
  - Konsistenz-Checks: ncols == 126720 (Abbruch sonst); Kern-Dim nach
    Witness-Replay == 607 erwartet (Warnung sonst).

Output: _results/p2_dimer_witness_240672_<date>.json,
        Kernbasis _results/p2_kernel_basis_final_240672_<date>.npz,
        Dimer-Vektor _results/p2_dimer_vector_240672_<date>.npy (falls gefunden).
"""
import argparse, json, time, sys
from datetime import date
from pathlib import Path
import numpy as np

N = 240672
WITNESS_Q = 3863
SIGN = 1
NCOLS_EXPECTED = 126720
KERNEL_DIM_EXPECTED_AFTER_WITNESS = 607
AP_VALUES = {3: 1, 5: 2, 7: 0, 11: 0, 13: -6, 17: 6, 19: 0, 23: 1}
DEFAULT_OPERATORS = [3, 5, 7, 11, 13, 17, 19, 23]
CHECK_EVERY = 2000
STALE_CHECKS_LIMIT = 3
WITNESS_PATH = Path("_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kstop", type=int, default=8, help="Kern-Schnitt-Ziel (default: %(default)s)")
    p.add_argument("--operators", type=int, nargs="+", default=DEFAULT_OPERATORS)
    p.add_argument("--max-rows-per-op", type=int, default=120000)
    p.add_argument("--witness-path", type=str, default=str(WITNESS_PATH))
    return p.parse_args()


class GF2Ranker:
    """Bitmasken-Gauss ueber F2; Pivot = hoechstes Bit."""

    def __init__(self):
        self.basis = {}  # pivot -> row (Python int)

    def add(self, row_int):
        row = row_int
        while row:
            p = row.bit_length() - 1
            if p in self.basis:
                row ^= self.basis[p]
            else:
                self.basis[p] = row
                return True
        return False

    @property
    def rank(self):
        return len(self.basis)

    def kernel_basis(self, ncols):
        free_cols = [c for c in range(ncols) if c not in self.basis]
        pivots_sorted = sorted(self.basis)
        vecs = []
        for fcol in free_cols:
            xbits = 1 << fcol
            for p in pivots_sorted:
                row = self.basis[p] & ~(1 << p)
                if (row & xbits).bit_count() & 1:
                    xbits |= 1 << p
            vecs.append(xbits)
        return free_cols, vecs


def main():
    args = parse_args()
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    half_wq = WITNESS_Q // 2

    print("=== p2_dimer_witness_240672 ===")
    print(f"Level: {N}, mod 2 (symmetric lift from witness q={WITNESS_Q}), sign={SIGN}")
    print(f"Operators (a_p mod 2): " + ", ".join(
        f"T{p}{'+1' if AP_VALUES[p] % 2 else ''}" for p in args.operators))
    print(f"KSTOP: {args.kstop} | Witness: {args.witness_path}")
    sys.stdout.flush()

    # Phase 0: Sage setup ueber GF(2)
    print(f"[{ts()}] Importing Sage...")
    from sage.all import GF as SageGF
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient
    from sage.modular.modsym.heilbronn import HeilbronnCremona

    # WICHTIG: Quotient ueber GF(WITNESS_Q) bauen — identische Spaltenbasis
    # zum Witness (ueber GF(2) ueberleben 16 sigma-Fixpunkt-Symbole, da
    # 2x=0 dort leer ist: ncols waere 126736 statt 126720; Crash 2026-06-11).
    # Die Hecke-Zeilen werden unten EXAKT ueber Z akkumuliert (Skalare +-1
    # via symmetrischem Lift) und erst am Ende mod 2 genommen.
    Fq = SageGF(WITNESS_Q)
    print(f"[{ts()}] Building ManinSymbolList_gamma0({N}, 2)...")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    rels = set(modS_relations(syms))
    rels.update(modI_relations(syms, SIGN))
    print(f"[{ts()}] S/I relations: {len(rels)}")
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
            if sc > WITNESS_Q // 2:
                sc -= WITNESS_Q
            assert abs(sc) <= 2, f"2-term scalar lift {sc} unexpectedly large"
            mod_map.append((rep_to_col[rep_i], sc))
    ncols = len(rep_to_col)
    print(f"[{ts()}] ncols after 2-term (GF({WITNESS_Q}), Z-lifted scalars): {ncols}")
    if ncols != NCOLS_EXPECTED:
        print(f"FATAL: ncols={ncols} != expected {NCOLS_EXPECTED} — Witness-Spaltenindizes "
              f"inkompatibel. ABBRUCH.")
        return 2

    # Phase 1: Witness mod 2 replizieren; manin-Dreiecke sammeln
    print(f"[{ts()}] Replaying witness mod 2...")
    ranker = GF2Ranker()
    triangles = []
    n_rows = 0
    with open(args.witness_path) as f:
        for line in f:
            rec = json.loads(line)
            row = 0
            odd_cols = []
            for c, v in rec["row"]:
                v = int(v)
                if v > half_wq:
                    v -= WITNESS_Q
                if v % 2 != 0:
                    row |= (1 << int(c))
                    odd_cols.append(int(c))
            if "manin" in rec["stage"] and len(odd_cols) == 3:
                triangles.append(odd_cols)
            if row:
                ranker.add(row)
            n_rows += 1
            if n_rows % 20000 == 0:
                print(f"  ... {n_rows} rows, rank={ranker.rank} ({time.time()-t0:.0f}s)")
                sys.stdout.flush()
    kdim = ncols - ranker.rank
    print(f"[{ts()}] Witness replay done: {n_rows} rows, rank={ranker.rank}, kernel dim={kdim}")
    if n_rows != 126672:
        print(f"FATAL: {n_rows} Witness-Zeilen gelesen, erwartet 126672 — Datei unvollstaendig "
              f"(Sync laeuft? Lesson 2026-06-11: mid-sync truncation). ABBRUCH.")
        return 3
    print(f"[{ts()}] Triangles (manin, odd-len 3): {len(triangles)}")
    if kdim != KERNEL_DIM_EXPECTED_AFTER_WITNESS:
        print(f"WARNUNG: kernel dim {kdim} != erwartet {KERNEL_DIM_EXPECTED_AFTER_WITNESS} "
              f"(lokaler Lauf 2026-06-11). Weiter, aber dokumentieren.")
    sys.stdout.flush()

    # Phase 2: Frische Hecke-Zeilen mod 2 bis Kern <= KSTOP
    def reduce_terms_mod2(terms):
        # exakte Z-Akkumulation (coeff, scalar klein-ganzzahlig), dann mod 2
        acc = {}
        for j, coeff in terms:
            mapped = mod_map[int(j)]
            if mapped is None:
                continue
            col, scalar = mapped
            acc[col] = acc.get(col, 0) + int(coeff) * scalar
        row = 0
        for col, v in acc.items():
            if v % 2 != 0:
                row |= (1 << col)
        return row

    op_log = []
    for p in args.operators:
        if ncols - ranker.rank <= args.kstop:
            break
        ap = AP_VALUES[p]
        mats = HeilbronnCremona(p).to_list()
        print(f"\n[{ts()}] === T_{p} mod 2 (a_{p}={ap} ≡ {ap % 2}) | Heilbronn: {len(mats)} ===")
        sys.stdout.flush()
        added = 0
        stale_checks = 0
        last_kdim = ncols - ranker.rank
        rows_done = 0
        for i in range(nsyms):
            terms = [(i, -ap)]
            for A in mats:
                terms.extend(syms.apply(i, A))
            row = reduce_terms_mod2(terms)
            if row and ranker.add(row):
                added += 1
            rows_done += 1
            if rows_done % CHECK_EVERY == 0:
                kdim = ncols - ranker.rank
                print(f"[{ts()}] T_{p}: {rows_done} rows, +{added} rank, kernel dim={kdim} "
                      f"({time.time()-t0:.0f}s)")
                sys.stdout.flush()
                if kdim <= args.kstop:
                    break
                if kdim == last_kdim:
                    stale_checks += 1
                    if stale_checks >= STALE_CHECKS_LIMIT:
                        print(f"[{ts()}] T_{p} saturiert (kernel dim {kdim} stabil), naechster Operator")
                        break
                else:
                    stale_checks = 0
                last_kdim = kdim
            if rows_done >= args.max_rows_per_op:
                break
        op_log.append({"p": p, "rows": rows_done, "rank_added": added,
                       "kernel_dim_after": ncols - ranker.rank})

    kdim = ncols - ranker.rank
    print(f"\n[{ts()}] Schnitt fertig: kernel dim={kdim} ({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    # Phase 3: Kernbasis + Verifikation + Dimer-Suche
    free_cols, kvecs_bits = ranker.kernel_basis(ncols)
    K = len(kvecs_bits)
    KV = np.zeros((K, ncols), dtype=np.uint8)
    for ki, xb in enumerate(kvecs_bits):
        bb = xb.to_bytes((ncols + 7) // 8, "little")
        KV[ki] = np.unpackbits(np.frombuffer(bb, dtype=np.uint8), bitorder="little")[:ncols]
    np.savez_compressed(f"_results/p2_kernel_basis_final_240672_{date.today()}.npz",
                        KV=KV, free_cols=np.array(free_cols))
    print(f"[{ts()}] Kernbasis K={K} extrahiert + gespeichert")

    # Verifikation gegen die GESAMTE Basis (M*x == 0 <=> x von allen Basiszeilen annihiliert)
    ver_fail = 0
    for ki, xb in enumerate(kvecs_bits):
        for piv, row in ranker.basis.items():
            if (row & xb).bit_count() & 1:
                ver_fail += 1
                break
    print(f"[{ts()}] Kern-Verifikation: {K - ver_fail}/{K} ok")

    TRI = np.array(triangles, dtype=np.int64)
    results = []
    dimer_found = None

    def eval_combo(x, mask):
        nonlocal dimer_found
        m = x[TRI].sum(axis=1)
        d0 = int((m == 0).sum())
        mh = {str(k): int(c) for k, c in zip(*np.unique(m, return_counts=True))}
        results.append({"mask": mask, "support": int(x.sum()), "defects_m0": d0, "m_hist": mh})
        if d0 == 0 and set(mh.keys()) <= {"2"} and dimer_found is None:
            dimer_found = mask
            np.save(f"_results/p2_dimer_vector_240672_{date.today()}.npy", x)
            print(f"[{ts()}] *** DIMER GEFUNDEN: mask={mask}, support={int(x.sum())} "
                  f"({int(x.sum())/ncols:.4f} von ncols) ***")
        return d0

    if K <= 16:
        # Vollenumeration aller 2^K - 1 Kombinationen
        for mask in range(1, 1 << K):
            x = np.zeros(ncols, dtype=np.uint8)
            for ki in range(K):
                if (mask >> ki) & 1:
                    x ^= KV[ki]
            eval_combo(x, mask)
            if dimer_found is not None:
                break
    else:
        # K zu gross: Einzel + alle Paare + Greedy-Hill-Climb
        print(f"[{ts()}] K={K} > 16: Einzel + Paare + Greedy statt Vollenumeration")
        for ki in range(K):
            eval_combo(KV[ki].copy(), 1 << ki)
        for i in range(K):
            for j in range(i + 1, K):
                eval_combo(KV[i] ^ KV[j], (1 << i) | (1 << j))
                if dimer_found is not None:
                    break
            if dimer_found is not None:
                break
        if dimer_found is None:
            best = min(results, key=lambda r: r["defects_m0"])
            x = np.zeros(ncols, dtype=np.uint8)
            for ki in range(K):
                if (best["mask"] >> ki) & 1:
                    x ^= KV[ki]
            d0 = best["defects_m0"]
            mask = best["mask"]
            improved = True
            while improved and d0 > 0:
                improved = False
                for ki in range(K):
                    xc = x ^ KV[ki]
                    m = xc[TRI].sum(axis=1)
                    d1 = int((m == 0).sum())
                    if d1 < d0:
                        x, d0, mask = xc, d1, mask ^ (1 << ki)
                        improved = True
            print(f"[{ts()}] Greedy final: defects={d0}")
            eval_combo(x, mask)
    results.sort(key=lambda r: r["defects_m0"])

    report = {"date": str(date.today()), "level": N, "ncols": ncols,
              "kernel_dim_after_witness": KERNEL_DIM_EXPECTED_AFTER_WITNESS,
              "operators_log": op_log, "final_kernel_dim": K,
              "kernel_verified": K - ver_fail,
              "dimer_found_mask": dimer_found,
              "combo_results_best": results[:20],
              "total_seconds": time.time() - t0}
    with open(f"_results/p2_dimer_witness_240672_{date.today()}.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[{ts()}] === FINAL ===")
    print(f"Final kernel dim: {K} | Dimer: {'GEFUNDEN (mask=%d)' % dimer_found if dimer_found else 'NICHT gefunden'}")
    print(f"Total: {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
