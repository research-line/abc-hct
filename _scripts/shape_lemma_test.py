# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""
Local Shape Lemma Test — Néron Compensation Analysis

For each abc triple, compute:
  u^2 = Prod_{p|abc} p^{2*floor(v_p(Delta)/12)}
  Compensation ratio: log(u^2) / log(c/N)
  Residual deficit: log(c/N) - log(u^2)

Question: Can u^2 close the gap between c^{-1/2} and N^{-1/2-eps}?
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
    result = 1
    for p in factorize(n):
        result *= p
    return result

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def compute_neron_u2(a, b, c):
    abc = a * b * c
    delta = 16 * abc**2
    factors_delta = factorize(delta)

    u2 = 1
    details = {}
    for p, vp_delta in factors_delta.items():
        k = vp_delta // 12
        if k > 0:
            u2 *= p**(2 * k)
            details[p] = {'v_p_delta': vp_delta, 'floor_div_12': k, 'u_p^2': p**(2*k)}

    return u2, details

def compute_vp_abc(a, b, c):
    factors_a = factorize(a)
    factors_b = factorize(b)
    factors_c = factorize(c)

    all_primes = set(factors_a) | set(factors_b) | set(factors_c)
    result = {}
    for p in sorted(all_primes):
        va = factors_a.get(p, 0)
        vb = factors_b.get(p, 0)
        vc = factors_c.get(p, 0)
        total = va + vb + vc
        result[p] = {'v_a': va, 'v_b': vb, 'v_c': vc, 'v_abc': total,
                      'v_delta': 2*total + (4 if p == 2 else 0)}
    return result

def analyze_triple(a, b, label=""):
    c = a + b
    if gcd(a, b) != 1:
        return None

    N = rad(a * b * c)
    q = math.log(c) / math.log(N) if N > 1 else 0

    u2, u_details = compute_neron_u2(a, b, c)
    vp_info = compute_vp_abc(a, b, c)

    log_c_over_N = math.log(c / N) if c > N else 0
    log_u2 = math.log(u2) if u2 > 1 else 0

    compensation_ratio = log_u2 / log_c_over_N if log_c_over_N > 0 else 0
    residual = log_c_over_N - log_u2

    needed_factor = math.sqrt(c / N) if c > N else 1.0

    return {
        'a': a, 'b': b, 'c': c, 'label': label,
        'N': N, 'q': q,
        'u2': u2, 'u_details': u_details,
        'vp_info': vp_info,
        'log_c_over_N': log_c_over_N,
        'log_u2': log_u2,
        'compensation_ratio': compensation_ratio,
        'residual': residual,
        'needed_factor': needed_factor,
        'u2_sufficient': u2 >= needed_factor,
        'squarefree': all(info['v_abc'] <= 1 for p, info in vp_info.items() if p > 2),
    }

def main():
    triples = [
        (1, 8, "(1,8,9)"),
        (1, 48, "(1,48,49)"),
        (1, 63, "(1,63,64)"),
        (1, 80, "(1,80,81)"),
        (3, 125, "(3,125,128)"),
        (5, 27, "(5,27,32)"),
        (13, 243, "(13,243,256)"),
        (32, 49, "(32,49,81)"),
        (1, 4374, "(1,4374,4375)"),
        (1, 1023, "(1,1023,1024)"),
        (2, 6436341, "Reyssat"),
        (1, 2400, "(1,2400,2401)"),
        (1, 6560, "(1,6560,6561)"),
        (7, 2187, "(7,2187,2194)"),
        (1, 531440, "(1,531440,531441)"),
        (1, 14348906, "(1,..,14348907)"),
    ]

    print("=" * 100)
    print("LOCAL SHAPE LEMMA — NÉRON COMPENSATION ANALYSIS")
    print("Question: Does u^2 from Néron minimization compensate c/N gap?")
    print("lambda_1(E_min) = u^2 * lambda_1(E_model) >= u^2 * C * c^{-1/2}")
    print("Need: u^2 * c^{-1/2} >= N^{-1/2-eps}, i.e., u^2 >= sqrt(c/N)")
    print("=" * 100)

    print(f"\n{'Label':<22} {'N':>10} {'q':>6} {'u^2':>10} "
          f"{'sqrt(c/N)':>10} {'comp%':>6} {'suffic':>7} {'sqfree':>7}")
    print("-" * 85)

    results = []
    for a, b, label in triples:
        r = analyze_triple(a, b, label)
        if r is None:
            continue
        results.append(r)
        print(f"{label:<22} {r['N']:>10d} {r['q']:>6.3f} {r['u2']:>10d} "
              f"{r['needed_factor']:>10.2f} "
              f"{r['compensation_ratio']*100:>5.1f}% "
              f"{'YES' if r['u2_sufficient'] else 'NO':>7} "
              f"{'yes' if r['squarefree'] else 'NO':>7}")

    print("\n" + "=" * 100)
    print("DETAILED p-ADIC ANALYSIS FOR HIGH-QUALITY NON-SQUAREFREE TRIPLES")
    print("=" * 100)

    for r in results:
        if r['squarefree'] or r['q'] < 1.1:
            continue
        print(f"\n  {r['label']}: a={r['a']}, b={r['b']}, c={r['c']}")
        print(f"    N={r['N']}, q={r['q']:.4f}, u^2={r['u2']}")
        print(f"    sqrt(c/N)={r['needed_factor']:.4f}, u^2/sqrt(c/N)={r['u2']/r['needed_factor']:.4f}")
        print(f"    Compensation: {r['compensation_ratio']*100:.1f}% of log(c/N)")
        print(f"    Residual deficit: {r['residual']:.4f}")
        for p, info in sorted(r['vp_info'].items()):
            if info['v_abc'] > 1:
                v_delta = info['v_delta']
                k = v_delta // 12
                u_p2 = p**(2*k) if k > 0 else 1
                captured = 2*k*math.log(p) / ((info['v_abc']-1)*math.log(p)) if info['v_abc'] > 1 else 0
                print(f"      p={p}: v_p(abc)={info['v_abc']}, v_p(Δ)={v_delta}, "
                      f"floor/12={k}, u_p^2={u_p2}, "
                      f"captured={(captured*100):.0f}% of (v_p-1)")

    print("\n" + "=" * 100)
    print("THEORETICAL ANALYSIS: ASYMPTOTIC CAPTURE RATE")
    print("For v_p -> infinity: 2*floor(v_p/6)/(v_p-1) -> 1/3")
    print("=" * 100)

    print(f"\n  {'v_p':>5} {'2*floor(v_p/6)':>15} {'v_p-1':>8} {'ratio':>8}")
    print("  " + "-" * 40)
    for vp in [2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 18, 20, 24, 30, 50, 100]:
        numer = 2 * (vp // 6)
        denom = vp - 1
        ratio = numer / denom if denom > 0 else 0
        print(f"  {vp:>5d} {numer:>15d} {denom:>8d} {ratio:>8.3f}")

    print("\n" + "=" * 100)
    print("CONCLUSION")
    print("=" * 100)

    nonsqfree_high = [r for r in results if not r['squarefree'] and r['q'] > 1.1]
    if nonsqfree_high:
        comp_rates = [r['compensation_ratio'] for r in nonsqfree_high]
        print(f"\n  Non-squarefree high-quality triples: {len(nonsqfree_high)}")
        print(f"  Compensation range: {min(comp_rates)*100:.1f}% - {max(comp_rates)*100:.1f}%")
        print(f"  u^2 sufficient for any: {any(r['u2_sufficient'] for r in nonsqfree_high)}")

    any_sufficient = any(r['u2_sufficient'] and r['q'] > 1.0 for r in results)
    print(f"\n  LOCAL SHAPE LEMMA (strong form): {'HOLDS' if any_sufficient else 'FALSIFIED'}")
    print(f"  u^2 captures ~1/3 of quality deficit asymptotically")
    print(f"  Residual ~2/3 remains: this is the irreducible abc content")
    print(f"  Shape-Elimination + Néron = necessary but not sufficient")

if __name__ == "__main__":
    main()
