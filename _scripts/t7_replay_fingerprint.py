#!/usr/bin/env python3
"""
T7 Replay Fingerprint — Skip T3+T5 via witness replay, proceed directly to T7.
Level 240672, q=3863, sign=+1, Cremona Hecke family.
Eigenvalues: a3=1, a5=2, a7=0, a11=0, a13=-6 (LMFDB-verified).
"""
import json, time, sys, math
from pathlib import Path
import numpy as np

# === Configuration ===
N = 240672
q = 3863
SIGN = 1
RAW_A, RAW_B = 2, 6
PRIMES_TO_RUN = [7, 11, 13]
AP_VALUES = {7: 0, 11: 0, 13: -6}
HECKE_BATCH_SIZE = 1000
MAX_BATCHES_PER_PRIME = 96
WITNESS_PATH = Path("_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl")
PIVOT_STRATEGY = "max"


# === Ranker Classes (from main script) ===

class SparseIncrementalRank:
    def __init__(self, ncols, p, pivot_strategy="max"):
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.basis = {}
        self.rank = 0

    def add(self, raw_row):
        p = self.p
        basis = self.basis
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in basis:
                factor = value
                b = basis[pivot]
                for c, v in b.items():
                    new = (row.get(c, 0) - factor * v) % p
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, p)
                normalized = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                basis[pivot] = normalized
                self.rank += 1
                return True
        return False

    def reduce(self, raw_row):
        p = self.p
        row = {int(c): int(v) % p for c, v in raw_row.items() if int(v) % p}
        basis = self.basis
        while row:
            pivot_cols = [c for c in row if c in basis]
            if not pivot_cols:
                break
            pivot = min(pivot_cols) if self.pivot_strategy == "min" else max(pivot_cols)
            factor = row[pivot] % p
            b = basis[pivot]
            for c, v in b.items():
                new = (row.get(c, 0) - factor * v) % p
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row


class DenseNumpyIncrementalRank:
    def __init__(self, ncols, p, pivot_strategy="max"):
        self.ncols = int(ncols)
        self.p = int(p)
        self.pivot_strategy = pivot_strategy
        self.dtype = np.int32
        self.basis = {}
        self.rank = 0

    def add(self, raw_row):
        p = self.p
        row = np.zeros(self.ncols, dtype=self.dtype)
        for c, v in raw_row.items():
            val = int(v) % p
            if val:
                row[int(c)] = val
        while True:
            nonzero = np.flatnonzero(row)
            if nonzero.size == 0:
                return False
            pivot = int(nonzero[0] if self.pivot_strategy == "min" else nonzero[-1])
            value = int(row[pivot]) % p
            basis_row = self.basis.get(pivot)
            if basis_row is None:
                inv = pow(value, -1, p)
                row = ((row * inv) % p).astype(self.dtype, copy=False)
                self.basis[pivot] = row
                self.rank += 1
                return True
            row -= value * basis_row
            np.remainder(row, p, out=row)


# === Main ===

def main():
    t_total = time.time()

    # Phase 0: Sage setup
    print(f"[{time.strftime('%H:%M:%S')}] Importing Sage...")
    from sage.all import GF as SageGF
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient
    from sage.modular.modsym.heilbronn import HeilbronnCremona

    F = SageGF(q)
    print(f"[{time.strftime('%H:%M:%S')}] Building ManinSymbolList_gamma0({N}, 2)...")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    print(f"[{time.strftime('%H:%M:%S')}] Manin symbols: nsyms={nsyms}")

    print(f"[{time.strftime('%H:%M:%S')}] Computing S/I relations...")
    rels = set(modS_relations(syms))
    rels.update(modI_relations(syms, SIGN))
    print(f"[{time.strftime('%H:%M:%S')}] S/I relations: {len(rels)}")

    print(f"[{time.strftime('%H:%M:%S')}] sparse_2term_quotient...")
    mod = sparse_2term_quotient(rels, nsyms, F)
    print(f"[{time.strftime('%H:%M:%S')}] 2-term quotient done, entries={len(mod)}")

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
            mod_map.append((rep_to_col[rep_i], F(scalar)))
    ncols = len(rep_to_col)
    print(f"[{time.strftime('%H:%M:%S')}] ncols after 2-term: {ncols}")

    # Phase 1: Replay witness into py_ranker
    print(f"[{time.strftime('%H:%M:%S')}] Replaying witness rows from {WITNESS_PATH}...")
    py_ranker = SparseIncrementalRank(ncols, q, PIVOT_STRATEGY)
    hecke_witness_rows = []
    manin_count = 0
    t_replay = time.time()

    with open(WITNESS_PATH) as f:
        for line_num, line in enumerate(f, 1):
            record = json.loads(line)
            row = {int(c): int(v) for c, v in record["row"]}
            stage = record["stage"]
            if "manin" in stage:
                py_ranker.add(row)
                manin_count += 1
            else:
                hecke_witness_rows.append(row)
            if line_num % 10000 == 0:
                print(f"  ... {line_num} rows read, py_ranker.rank={py_ranker.rank}", end="\r")

    print(f"\n[{time.strftime('%H:%M:%S')}] Manin replay done: {manin_count} rows, py_ranker.rank={py_ranker.rank}")
    print(f"[{time.strftime('%H:%M:%S')}] Hecke witness rows buffered: {len(hecke_witness_rows)}")

    # Phase 2: Build quotient
    pivot_cols = set(py_ranker.basis.keys())
    free_cols = [c for c in range(ncols) if c not in pivot_cols]
    quotient_col_map = {c: i for i, c in enumerate(free_cols)}
    quotient_ncols = len(free_cols)
    print(f"[{time.strftime('%H:%M:%S')}] Quotient: quotient_ncols={quotient_ncols}")

    quotient_ranker = DenseNumpyIncrementalRank(quotient_ncols, q, PIVOT_STRATEGY)

    # Phase 3: Replay Hecke witness rows through quotient
    for row in hecke_witness_rows:
        rem = py_ranker.reduce(row)
        projected = {quotient_col_map[col]: val for col, val in rem.items() if col in quotient_col_map}
        if projected:
            quotient_ranker.add(projected)

    qdim = quotient_ncols - quotient_ranker.rank
    replay_time = time.time() - t_replay
    print(f"[{time.strftime('%H:%M:%S')}] Replay complete: quotient_rank={quotient_ranker.rank}, qdim={qdim}")
    print(f"[{time.strftime('%H:%M:%S')}] Replay time: {replay_time:.1f}s")
    print(f"[{time.strftime('%H:%M:%S')}] Expected: qdim=48. {'OK' if qdim == 48 else 'MISMATCH!'}")
    sys.stdout.flush()

    # Phase 4: T7 (and optionally T11, T13)
    def reduce_terms(terms):
        row = {}
        for j, coeff in terms:
            mapped = mod_map[int(j)]
            if mapped is None:
                continue
            col, scalar = mapped
            val = int(F(coeff) * scalar)
            if val == 0:
                continue
            row[col] = (row.get(col, 0) + val) % q
            if row[col] == 0:
                del row[col]
        return row

    for p in PRIMES_TO_RUN:
        ap = AP_VALUES[p]
        print(f"\n[{time.strftime('%H:%M:%S')}] === T_{p} (a_{p}={ap}) ===")
        mats = HeilbronnCremona(p).to_list()
        print(f"[{time.strftime('%H:%M:%S')}] Heilbronn matrices: {len(mats)}")

        batch_count = 0
        rows_in_batch = 0
        t_prime = time.time()

        for i in range(nsyms):
            terms = [(i, F(-ap))]
            for A in mats:
                terms.extend(syms.apply(i, A))
            row = reduce_terms(terms)
            if row:
                rem = py_ranker.reduce(row)
                projected = {quotient_col_map[col]: val for col, val in rem.items() if col in quotient_col_map}
                if projected:
                    quotient_ranker.add(projected)

            rows_in_batch += 1
            if rows_in_batch >= HECKE_BATCH_SIZE:
                batch_count += 1
                qdim = quotient_ncols - quotient_ranker.rank
                elapsed = time.time() - t_prime
                print(f"[{time.strftime('%H:%M:%S')}] T_{p} batch {batch_count}: qdim={qdim} ({elapsed:.1f}s total)")
                sys.stdout.flush()
                rows_in_batch = 0
                if qdim <= 1:
                    print(f"[{time.strftime('%H:%M:%S')}] *** qdim=1 REACHED at T_{p} batch {batch_count}! ***")
                    break
                if batch_count >= MAX_BATCHES_PER_PRIME:
                    print(f"[{time.strftime('%H:%M:%S')}] Max batches reached for T_{p}")
                    break

        qdim = quotient_ncols - quotient_ranker.rank
        elapsed = time.time() - t_prime
        print(f"[{time.strftime('%H:%M:%S')}] T_{p} DONE: qdim={qdim}, time={elapsed:.1f}s")
        sys.stdout.flush()

        if qdim <= 1:
            print(f"\n[{time.strftime('%H:%M:%S')}] *** GATE 2 GREEN: qdim={qdim} ***")
            break

    total_time = time.time() - t_total
    qdim = quotient_ncols - quotient_ranker.rank
    print(f"\n[{time.strftime('%H:%M:%S')}] === FINAL RESULT ===")
    print(f"Level: {N}, q: {q}, primes: {PRIMES_TO_RUN}")
    print(f"Final qdim: {qdim}")
    print(f"Total time: {total_time:.1f}s")
    if qdim == 1:
        print("STATUS: GATE 2 GREEN - f_E uniquely isolated!")
    elif qdim == 0:
        print("STATUS: BUG - qdim=0 impossible (f_E in kernel)")
    else:
        print(f"STATUS: qdim={qdim} > 1 - more operators or second prime needed")


if __name__ == "__main__":
    main()
