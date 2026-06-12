#!/usr/bin/env python3
"""Find suitable test levels for CQ-4 positive multi-dim selection test.

Criteria:
  - new_dim >= 10 (non-trivial eigenspace)
  - At least one rational newform (qdim should be 1)
  - Ideally 3 || M (to test U_3 in multi-dim regime)

Extracts eigenvalues from Sage's own Newforms() for each candidate.
"""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')

from sage.all import Gamma0, ModularSymbols, Newforms, GF, identity_matrix, block_matrix

Q_MOD = 3863

def search_levels(min_new_dim=10, max_level=300, want_3_divides=True):
    results = []
    for N in range(11, max_level + 1):
        MS = ModularSymbols(Gamma0(N), 2, sign=1)
        CS = MS.cuspidal_subspace()
        NS = CS.new_subspace()
        nd = NS.dimension()
        if nd < min_new_dim:
            continue

        three_div = (N % 3 == 0 and N % 9 != 0)

        try:
            nfs = Newforms(Gamma0(N), 2, names='a')
        except Exception as e:
            print(f"  Level {N}: Newforms() error: {e}")
            continue

        rational_forms = []
        for f in nfs:
            try:
                coeffs = {}
                all_rational = True
                for p in [2, 3, 5, 7, 11, 13]:
                    ap = f[p]
                    if ap not in ZZ:
                        all_rational = False
                        break
                    coeffs[p] = int(ap)
                if all_rational:
                    rational_forms.append(coeffs)
            except Exception:
                pass

        if rational_forms:
            results.append({
                'level': N,
                'new_dim': nd,
                '3_divides': three_div,
                'rational_forms': rational_forms,
            })
            tag = " [3||N]" if three_div else ""
            print(f"Level {N}: new_dim={nd}{tag}, {len(rational_forms)} rational newform(s)")
            for i, rf in enumerate(rational_forms):
                print(f"  form {i}: {rf}")

    return results

def verify_candidate(level, eigenvalues, primes, q=Q_MOD):
    """Run canonical Sage eigenspace computation to verify qdim=1."""
    MS = ModularSymbols(Gamma0(level), 2, sign=1)
    CS = MS.cuspidal_subspace()
    NS = CS.new_subspace()
    n = NS.dimension()
    if n == 0:
        return 0, n

    Fq = GF(q)
    rows_list = []
    for p in sorted(primes):
        ap = eigenvalues[p]
        Tp = NS.hecke_matrix(p)
        Tp_mod = Tp.change_ring(Fq)
        Ip = identity_matrix(Fq, n)
        rows_list.append(Tp_mod - ap * Ip)

    big = block_matrix([[r] for r in rows_list])
    ker = big.right_kernel()
    return ker.dimension(), n


if __name__ == '__main__':
    from sage.all import ZZ
    print("=" * 60)
    print("CQ-4 Level Search: new_dim >= 10, rational newforms")
    print("=" * 60)

    t0 = time.time()
    results = search_levels(min_new_dim=10, max_level=300, want_3_divides=True)
    t_search = time.time() - t0
    print(f"\nSearch completed in {t_search:.1f}s, found {len(results)} candidates")

    if results:
        prefer_3 = [r for r in results if r['3_divides']]
        candidates = prefer_3 if prefer_3 else results

        print(f"\n--- Verifying top candidates (preferring 3||N) ---")
        for r in candidates[:5]:
            level = r['level']
            for i, rf in enumerate(r['rational_forms']):
                primes = sorted(rf.keys())
                qdim, nd = verify_candidate(level, rf, primes)
                status = "PASS" if qdim == 1 else f"qdim={qdim}"
                print(f"  Level {level} form {i}: qdim={qdim}, new_dim={nd} [{status}]")
                if qdim == 1:
                    print(f"    -> GOOD CANDIDATE for CQ-4!")
                    print(f"    eigenvalues = {rf}")
                    print(f"    primes = {primes}")

    print("\nDone.")
