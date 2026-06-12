#!/usr/bin/env python3
"""
T7 Replay Fingerprint v3 — Witness-replay + Hecke eigenvalue isolation, second-q capable.
Level 240672, sign=+1, Cremona Hecke family.
Eigenvalues: a3=1, a5=2, a7=0, a11=0, a13=-6 (LMFDB-verified).

v3 changes (2026-06-10):
  - --q parameter: run the certificate mod an arbitrary prime q (default 3863).
  - Symmetric witness lift: source_rows.jsonl stores values reduced mod the
    WITNESS prime (3863). For q != witness-q the stored values are lifted to
    the symmetric range [-(wq-1)/2, (wq-1)/2] BEFORE reduction mod q.
    Validity: the true integer entries of all witness rows are structurally
    tiny (manin_T relations: coefficients in {-1,+1}; Hecke witness rows:
    bounded by #Heilbronn matrices + |a_p| <= ~50), far below wq/2 = 1931.
    Hence the symmetric lift recovers the EXACT integer matrix, and the
    conservative-direction principle (qdim_observed >= qdim_full,Q) applies
    verbatim for the new q. A hard assertion |lifted| <= LIFT_SAFETY_BOUND
    aborts loudly if the small-entry assumption were ever violated.
  - Lift statistics are printed (max |lifted value| seen).

Motivation (2026-06-10): deg phi(240672.g1) = 8900352000 = 2^11*3^2*5^3*3863
(LMFDB). 3863 | deg phi => a congruence f_E = g mod 3863 exists in
S_2(Gamma_0(240672)) (Ribet: deg phi | c_f). The congruent eigensystem
survives EVERY T_p - a_p mod 3863, so qdim=1 is unreachable mod 3863
(observed: qdim=3 plateau across T_7, T_11, T_13). A second q with
q not dividing deg phi (e.g. 5077) removes the obstruction.

v2 changes (2026-06-08):
  - Saturation detection: skip prime after N stale batches (--saturation-patience)
  - Prime reordering: --t13-first runs T13->T11->T7 (strongest discriminator first)
"""
import argparse, json, time, sys
from pathlib import Path
import numpy as np

# === Defaults ===
N = 240672
DEFAULT_Q = 3863
WITNESS_Q = 3863
LIFT_SAFETY_BOUND = 200
SIGN = 1
RAW_A, RAW_B = 2, 6
AP_VALUES = {7: 0, 11: 0, 13: -6, 17: 6, 19: 0, 23: 1, 29: -2, 31: 4, 37: -6, 41: 2, 43: -4, 47: -8, 53: 10, 59: 4, 61: -14}
HECKE_BATCH_SIZE = 1000
DEFAULT_MAX_BATCHES = 96
DEFAULT_PATIENCE = 3
WITNESS_PATH = Path("_results/rc3c_cremona_witness_240672_raw_q3863_2026-06-05/N240672_raw_sign1/source_rows.jsonl")
PIVOT_STRATEGY = "max"

q = DEFAULT_Q  # set from --q in main()


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--q", type=int, default=DEFAULT_Q,
                   help="Prime modulus for the rank/qdim certificate (default: %(default)s)")
    p.add_argument("--witness-q", type=int, default=WITNESS_Q,
                   help="Prime the witness rows were stored mod (default: %(default)s)")
    p.add_argument("--t13-first", action="store_true",
                   help="Run T13->T11->T7 instead of T7->T11->T13 (recommended)")
    p.add_argument("--primes", type=int, nargs="+", default=None,
                   help="Explicit prime order, e.g. --primes 13 (overrides --t13-first)")
    p.add_argument("--saturation-patience", type=int, default=DEFAULT_PATIENCE,
                   help="Skip prime after N stale batches (default: %(default)s, 0=off)")
    p.add_argument("--max-batches", type=int, default=DEFAULT_MAX_BATCHES,
                   help="Max batches per prime (default: %(default)s)")
    p.add_argument("--witness-path", type=str, default=str(WITNESS_PATH),
                   help="Path to source_rows.jsonl")
    return p.parse_args()


# === Ranker Classes ===

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
    global q
    args = parse_args()
    q = int(args.q)
    wq = int(args.witness_q)
    t_total = time.time()

    if args.primes:
        primes_to_run = args.primes
    elif args.t13_first:
        primes_to_run = [13, 11, 7]
    else:
        primes_to_run = [7, 11, 13]

    patience = args.saturation_patience
    max_batches = args.max_batches
    witness_path = Path(args.witness_path)
    lift_needed = (q != wq)
    half_wq = wq // 2
    max_abs_lifted = 0

    print("=== t7_replay_fingerprint v3 ===")
    print(f"Level: {N}, q: {q}, sign: {SIGN}")
    print(f"Witness stored mod: {wq}; symmetric lift: {'ON' if lift_needed else 'off (q == witness-q)'}")
    ap_str = ", ".join(f"{p}:{AP_VALUES[p]}" for p in primes_to_run)
    print(f"Primes: {primes_to_run} (eigenvalues: {{{ap_str}}})")
    print(f"Saturation patience: {patience} (0=disabled)")
    print(f"Max batches/prime: {max_batches}")
    print(f"Witness: {witness_path}")
    print()

    # Phase 0: Sage setup
    ts = lambda: time.strftime("%H:%M:%S")
    print(f"[{ts()}] Importing Sage...")
    from sage.all import GF as SageGF
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient
    from sage.modular.modsym.heilbronn import HeilbronnCremona

    F = SageGF(q)
    print(f"[{ts()}] Building ManinSymbolList_gamma0({N}, 2)...")
    syms = ManinSymbolList_gamma0(N, 2)
    nsyms = len(syms)
    print(f"[{ts()}] Manin symbols: nsyms={nsyms}")

    print(f"[{ts()}] Computing S/I relations...")
    rels = set(modS_relations(syms))
    rels.update(modI_relations(syms, SIGN))
    print(f"[{ts()}] S/I relations: {len(rels)}")

    print(f"[{ts()}] sparse_2term_quotient...")
    mod = sparse_2term_quotient(rels, nsyms, F)
    print(f"[{ts()}] 2-term quotient done, entries={len(mod)}")

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
    print(f"[{ts()}] ncols after 2-term: {ncols}")

    def lift_value(v):
        # Symmetric lift from [0, wq-1] to [-(wq-1)/2, (wq-1)/2].
        nonlocal max_abs_lifted
        v = int(v)
        if v > half_wq:
            v -= wq
        a = abs(v)
        if a > max_abs_lifted:
            max_abs_lifted = a
        if a > LIFT_SAFETY_BOUND:
            raise AssertionError(
                f"Lifted witness value {v} exceeds LIFT_SAFETY_BOUND={LIFT_SAFETY_BOUND}; "
                f"small-entry assumption violated, second-q replay would be unsound.")
        return v

    # Phase 1: Replay witness into py_ranker
    print(f"[{ts()}] Replaying witness rows from {witness_path}...")
    py_ranker = SparseIncrementalRank(ncols, q, PIVOT_STRATEGY)
    hecke_witness_rows = []
    manin_count = 0
    t_replay = time.time()

    with open(witness_path) as f:
        for line_num, line in enumerate(f, 1):
            record = json.loads(line)
            if lift_needed:
                row = {int(c): lift_value(v) for c, v in record["row"]}
            else:
                row = {int(c): int(v) for c, v in record["row"]}
            stage = record["stage"]
            if "manin" in stage:
                py_ranker.add(row)
                manin_count += 1
            else:
                hecke_witness_rows.append(row)
            if line_num % 10000 == 0:
                print(f"  ... {line_num} rows read, py_ranker.rank={py_ranker.rank}", end="\r")

    print(f"\n[{ts()}] Manin replay done: {manin_count} rows, py_ranker.rank={py_ranker.rank}")
    print(f"[{ts()}] Hecke witness rows buffered: {len(hecke_witness_rows)}")
    if lift_needed:
        print(f"[{ts()}] Lift statistics: max |lifted value| = {max_abs_lifted} (safety bound {LIFT_SAFETY_BOUND}, wq/2 = {half_wq})")

    # Phase 2: Build quotient
    pivot_cols = set(py_ranker.basis.keys())
    free_cols = [c for c in range(ncols) if c not in pivot_cols]
    quotient_col_map = {c: i for i, c in enumerate(free_cols)}
    quotient_ncols = len(free_cols)
    print(f"[{ts()}] Quotient: quotient_ncols={quotient_ncols}")

    quotient_ranker = DenseNumpyIncrementalRank(quotient_ncols, q, PIVOT_STRATEGY)

    # Phase 3: Replay Hecke witness rows through quotient
    for row in hecke_witness_rows:
        rem = py_ranker.reduce(row)
        projected = {quotient_col_map[col]: val for col, val in rem.items() if col in quotient_col_map}
        if projected:
            quotient_ranker.add(projected)

    qdim = quotient_ncols - quotient_ranker.rank
    replay_time = time.time() - t_replay
    print(f"[{ts()}] Replay complete: quotient_rank={quotient_ranker.rank}, qdim={qdim}")
    print(f"[{ts()}] Replay time: {replay_time:.1f}s")
    if q == 3863:
        expected = 48
        print(f"[{ts()}] Expected: qdim={expected}. {'OK' if qdim == expected else 'MISMATCH!'}")
    else:
        print(f"[{ts()}] (q={q} != 3863: no expected baseline; mod-3863 baseline was 48. "
              f"qdim may differ because witness rows were rank-selected mod 3863.)")
    sys.stdout.flush()

    # Phase 4: Hecke operators
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

    for p in primes_to_run:
        ap = AP_VALUES[p]
        print(f"\n[{ts()}] === T_{p} (a_{p}={ap}) ===")
        mats = HeilbronnCremona(p).to_list()
        print(f"[{ts()}] Heilbronn matrices: {len(mats)}")

        batch_count = 0
        rows_in_batch = 0
        stale_count = 0
        prev_qdim = qdim
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
                print(f"[{ts()}] T_{p} batch {batch_count}: qdim={qdim} ({elapsed:.1f}s total)")
                sys.stdout.flush()
                rows_in_batch = 0

                if qdim <= 1:
                    print(f"[{ts()}] *** qdim={qdim} REACHED at T_{p} batch {batch_count}! ***")
                    break

                if batch_count >= max_batches:
                    print(f"[{ts()}] Max batches reached for T_{p}")
                    break

                # Saturation detection
                if patience > 0:
                    if qdim == prev_qdim:
                        stale_count += 1
                        if stale_count >= patience:
                            print(f"[{ts()}] Saturation: qdim={qdim} unchanged for {stale_count} batches, advancing to next prime")
                            break
                    else:
                        stale_count = 0
                    prev_qdim = qdim

        qdim = quotient_ncols - quotient_ranker.rank
        elapsed = time.time() - t_prime
        print(f"[{ts()}] T_{p} DONE: qdim={qdim}, time={elapsed:.1f}s, batches={batch_count}")
        sys.stdout.flush()

        if qdim <= 1:
            print(f"\n[{ts()}] *** GATE 2 GREEN: qdim={qdim} ***")
            break

    total_time = time.time() - t_total
    qdim = quotient_ncols - quotient_ranker.rank
    print(f"\n[{ts()}] === FINAL RESULT ===")
    print(f"Level: {N}, q: {q}, primes run: {primes_to_run}")
    if lift_needed:
        print(f"Witness lift: stored mod {wq}, max |lifted value| = {max_abs_lifted}")
    print(f"Final qdim: {qdim}")
    print(f"Total time: {total_time:.1f}s ({total_time/3600:.1f}h)")
    if qdim == 1:
        print("STATUS: GATE 2 GREEN - f_E uniquely isolated!")
    elif qdim == 0:
        print("STATUS: BUG - qdim=0 impossible (f_E in kernel)")
    else:
        print(f"STATUS: qdim={qdim} > 1 - more operators needed")


if __name__ == "__main__":
    main()
