"""
WP4: Level-Lowering Cascade Analysis for Frey curves.

For each abc triple, analyze:
- Which primes l allow level-lowering (Ribet's theorem)
- Which primes are "stuck" (v_p(abc) = 1, never removable)
- Minimal achievable residual level
- dim S_2(Gamma_0(N')) at residual level
- Compare with FLT case (all primes removable, level -> 2)
"""

import math

def factorize(n):
    n = abs(n)
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def rad(n):
    return math.prod(factorize(abs(n)).keys()) if n != 0 else 0

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def legendre_symbol(a, p):
    if p == 2:
        return 0
    a = a % p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1

def euler_phi(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def dim_S2_Gamma0(N):
    if N <= 0:
        return 0
    if N == 1:
        return 0

    mu = N
    for p in factorize(N):
        mu = mu * (1 + 1/p)
    mu = mu / 12.0

    nu2 = 1
    facts = factorize(N)
    for p, e in facts.items():
        if p == 2:
            if e >= 2:
                nu2 = 0
                break
            else:
                nu2 = 0
        else:
            nu2 *= (1 + legendre_symbol(-1, p))
    if nu2 == 0:
        pass

    nu3 = 1
    for p, e in facts.items():
        if p == 3:
            if e >= 2:
                nu3 = 0
                break
            else:
                nu3 = 0
        else:
            nu3 *= (1 + legendre_symbol(-3, p))
    if nu3 == 0:
        pass

    divisors = [1]
    for p, e in facts.items():
        new_divs = []
        pk = 1
        for k in range(e + 1):
            for d in divisors:
                new_divs.append(d * pk)
            pk *= p
        divisors = new_divs

    nu_inf = 0
    for d in divisors:
        nu_inf += euler_phi(gcd(d, N // d))

    dim = 1 + mu - nu2/4.0 - nu3/3.0 - nu_inf/2.0
    return max(0, round(dim))


def analyze_level_lowering(a, b, label=""):
    c = a + b
    if gcd(a, b) != 1:
        return None

    abc_val = a * b * c
    N = rad(abc_val)

    facts_a = factorize(a)
    facts_b = factorize(b)
    facts_c = factorize(c)

    all_primes = sorted(set(list(facts_a.keys()) + list(facts_b.keys()) + list(facts_c.keys())))

    v_abc = {}
    for p in all_primes:
        v_abc[p] = facts_a.get(p, 0) + facts_b.get(p, 0) + facts_c.get(p, 0)

    v_delta = {}
    for p in all_primes:
        if p == 2:
            v_delta[p] = 4 + 2 * v_abc[p]
        else:
            v_delta[p] = 2 * v_abc[p]

    stuck_primes = []
    removable_primes = {}

    for p in all_primes:
        vd = v_delta[p]
        removed_by = []
        for l in range(3, max(vd + 1, 4)):
            if l > 1 and all(l % d != 0 for d in range(2, min(l, int(l**0.5) + 2))):
                pass
            else:
                continue
            if vd % l == 0:
                removed_by.append(l)

        for l in [3, 5, 7, 11, 13]:
            if vd % l == 0 and l not in removed_by:
                removed_by.append(l)

        if not removed_by:
            stuck_primes.append(p)
        else:
            removable_primes[p] = sorted(removed_by)

    N_stuck = 1
    for p in stuck_primes:
        N_stuck *= p

    dim_stuck = dim_S2_Gamma0(N_stuck) if N_stuck > 0 else 0

    return {
        'a': a, 'b': b, 'c': c, 'label': label,
        'N': N, 'abc_val': abc_val,
        'all_primes': all_primes,
        'v_abc': v_abc, 'v_delta': v_delta,
        'stuck_primes': stuck_primes,
        'removable_primes': removable_primes,
        'N_stuck': N_stuck,
        'dim_stuck': dim_stuck,
        'quality': math.log(c) / math.log(N) if N > 1 else 0,
    }


def main():
    print("=" * 95)
    print("WP4: LEVEL-LOWERING CASCADE ANALYSIS")
    print("Why does the FLT argument not generalize to abc?")
    print("=" * 95)

    print("\n--- FLT REFERENCE CASE ---")
    print("FLT: a^p + b^p = c^p => v_q(Delta) = 2p*v_q(abc), divisible by p for ALL q")
    print("=> Level drops to 2 at l=p. dim S_2(Gamma_0(2)) = 0. Contradiction.")
    print(f"dim S_2(Gamma_0(1)) = {dim_S2_Gamma0(1)}")
    print(f"dim S_2(Gamma_0(2)) = {dim_S2_Gamma0(2)}")
    print(f"dim S_2(Gamma_0(11)) = {dim_S2_Gamma0(11)}  [first nonzero]")
    print(f"dim S_2(Gamma_0(14)) = {dim_S2_Gamma0(14)}")
    print(f"dim S_2(Gamma_0(23)) = {dim_S2_Gamma0(23)}")
    print(f"dim S_2(Gamma_0(109)) = {dim_S2_Gamma0(109)}")

    test_triples = [
        (2, 3**10 * 109, "Reyssat"),
        (1, 8, "1+8=9"),
        (1, 63, "1+63=64"),
        (1, 80, "1+80=81"),
        (5, 27, "5+27=32"),
        (3, 125, "3+125=128"),
        (13, 243, "13+243=256"),
        (1, 2**12 - 1, "1+4095=4096"),
        (1, 4374, "1+4374=4375"),
        (32, 49, "32+49=81"),
        (625, 2048, "625+2048=2673"),
        (1, 2400, "1+2400=2401"),
        (1, 1023, "1+1023=1024"),
        (7**3, 2**11, "343+2048=2391"),
        (1, 5**7 - 1, "1+78124=78125"),
        (1, 14348906, "1+14348906=14348907"),
    ]

    print("\n" + "=" * 95)
    print("DETAILED LEVEL-LOWERING ANALYSIS")
    print("=" * 95)

    all_results = []
    for a, b, label in test_triples:
        r = analyze_level_lowering(a, b, label)
        if r is None:
            continue
        all_results.append(r)

        print(f"\n--- {label} ---")
        print(f"  a={a}, b={b}, c={r['c']}")
        print(f"  N = {r['N']}, quality = {r['quality']:.3f}")
        print(f"  Prime valuations v_p(abc) and v_p(Delta):")

        for p in r['all_primes']:
            va = r['v_abc'][p]
            vd = r['v_delta'][p]
            status = "STUCK" if p in r['stuck_primes'] else f"removable by l={r['removable_primes'][p]}"
            print(f"    p={p:>5d}: v_p(abc)={va:>3d}, v_p(Delta)={vd:>3d} => {status}")

        print(f"  Stuck primes: {r['stuck_primes'] if r['stuck_primes'] else 'NONE'}")
        print(f"  Minimal residual level N' = {r['N_stuck']}")
        print(f"  dim S_2(Gamma_0(N')) = {r['dim_stuck']}")
        contradiction = "YES => CONTRADICTION (like FLT)" if r['dim_stuck'] == 0 else "NO (newforms exist)"
        print(f"  Level-0 contradiction? {contradiction}")

    # Summary
    print("\n" + "=" * 95)
    print("SUMMARY: LEVEL-LOWERING CASCADE")
    print("=" * 95)

    print(f"\n{'Label':<25} {'N':>8} {'q':>6} {'#stuck':>6} {'N_stuck':>8} {'dim':>5} {'Contradiction?':<15}")
    print("-" * 80)
    for r in sorted(all_results, key=lambda x: -x['quality']):
        contr = "YES!" if r['dim_stuck'] == 0 else "no"
        n_stuck = len(r['stuck_primes'])
        print(f"{r['label']:<25} {r['N']:>8d} {r['quality']:>6.3f} {n_stuck:>6d} "
              f"{r['N_stuck']:>8d} {r['dim_stuck']:>5d} {contr:<15}")

    # Structural analysis
    print("\n" + "=" * 95)
    print("STRUCTURAL ANALYSIS: WHY FLT WORKS BUT abc DOESN'T")
    print("=" * 95)

    n_with_stuck = sum(1 for r in all_results if r['stuck_primes'])
    n_total = len(all_results)
    stuck_above_10 = sum(1 for r in all_results
                         if any(p >= 11 for p in r['stuck_primes']))

    print(f"\n  Triples with stuck primes: {n_with_stuck}/{n_total}")
    print(f"  Triples with stuck primes >= 11: {stuck_above_10}/{n_total}")
    print(f"  (For p >= 11: dim S_2(Gamma_0(p)) >= 1, so no contradiction possible)")

    print(f"\n  KEY OBSTRUCTION: A prime p with v_p(abc) = 1 satisfies v_p(Delta) = 2.")
    print(f"  No prime l >= 3 divides 2, so p is NEVER removable by level-lowering.")
    print(f"  In FLT: v_p(a^n*b^n*c^n) = n*v_p(abc), so v_p(Delta) = 2n*v_p(abc).")
    print(f"  For l = n: n | 2n*v_p(abc) always. ALL primes removable. Level -> 2.")

    print(f"\n  SQUAREFREE OBSTRUCTION:")
    print(f"  If abc is squarefree (v_p = 1 for all p|abc), NO level-lowering occurs.")
    print(f"  All primes stay stuck. N' = N. dim S_2(Gamma_0(N)) >> 0 for large N.")

    print(f"\n  MINIMUM EXPONENT FOR REMOVAL:")
    print(f"  To remove p at level l: need l | v_p(Delta) = 2*v_p(abc).")
    print(f"  For l >= 3: need l | 2*v, i.e., l | v (since gcd(l,2)=1 for l>=3).")
    print(f"  So v_p(abc) >= 3 needed to remove p at ANY l >= 3.")
    print(f"  v_p(abc) = 1: stuck forever. v_p(abc) = 2: stuck (no l>=3 divides 2).")
    print(f"  v_p(abc) = 3: removable at l=3. v_p(abc) = 5: removable at l=5.")


if __name__ == "__main__":
    main()
