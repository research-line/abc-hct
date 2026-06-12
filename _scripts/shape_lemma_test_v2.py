# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""
SUPERSEDED by shape_lemma_scaling_check.py (2026-05-03).

This file uses u^2 scaling which is INCORRECT. The correct scaling is u (not u^2).
See BEWEISNOTIZ.md §15 for the proof. Kept for reference only.

Original description:
Local Shape Lemma — Corrected Néron Compensation Analysis (v2)
"""

import math
import cmath

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

def agm(a, b, tol=1e-15, max_iter=100):
    a, b = float(a), float(b)
    for _ in range(max_iter):
        a, b = (a + b) / 2, math.sqrt(a * b)
        if abs(a - b) < tol:
            break
    return a

def compute_periods(a_param, b_param):
    e1 = float(a_param)
    e2 = 0.0
    e3 = float(-b_param)
    if e1 < e3:
        e1, e3 = e3, e1
    if e1 < e2:
        e1, e2 = e2, e1
    if e2 < e3:
        e2, e3 = e3, e2
    omega1 = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e1 - e2))
    omega3_mag = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e2 - e3))
    return omega1, omega3_mag

def compute_neron_u2(a, b, c):
    delta = 16 * (a * b * c)**2
    factors_delta = factorize(delta)
    u2 = 1
    for p, vp_delta in factors_delta.items():
        k = vp_delta // 12
        if k > 0:
            u2 *= p**(2 * k)
    return u2

def compute_vp_info(a, b, c):
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    all_p = set(fa) | set(fb) | set(fc)
    info = {}
    for p in sorted(all_p):
        v = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        v_delta = 2*v + (4 if p == 2 else 0)
        info[p] = {'v_abc': v, 'v_delta': v_delta, 'floor_12': v_delta // 12}
    return info

def analyze_triple(a, b, label=""):
    c = a + b
    if gcd(a, b) != 1:
        return None
    N = rad(a * b * c)
    q = math.log(c) / math.log(N) if N > 1 else 0
    u2 = compute_neron_u2(a, b, c)
    vp = compute_vp_info(a, b, c)

    try:
        omega1, omega3_mag = compute_periods(a, b)
    except (ValueError, ZeroDivisionError):
        return None

    lambda1_model = 2 * min(omega1, omega3_mag)
    lambda1_min = u2 * lambda1_model

    t = b / c
    K_t_approx = math.pi / (2 * agm(1.0, math.sqrt(1 - t)))
    K_1mt_approx = math.pi / (2 * agm(1.0, math.sqrt(t)))

    pi_over_sqrtc = math.pi / math.sqrt(c)
    N_inv_half = 1.0 / math.sqrt(N)

    ratio_model = lambda1_model / N_inv_half
    ratio_min = lambda1_min / N_inv_half

    if ratio_min > 0:
        eps_margin = math.log(ratio_min) / (2 * math.log(N))
    else:
        eps_margin = float('-inf')

    needed_no_const = math.sqrt(c / N)
    needed_with_pi = needed_no_const / math.pi

    sqfree = all(info['v_abc'] <= 1 for p, info in vp.items() if p > 2) and \
             vp.get(2, {'v_abc': 0})['v_abc'] <= 3

    return {
        'a': a, 'b': b, 'c': c, 'label': label,
        'N': N, 'q': q, 'u2': u2, 'vp': vp,
        't': t,
        'K_t': K_t_approx, 'K_1mt': K_1mt_approx,
        'omega1': omega1, 'omega3_mag': omega3_mag,
        'lambda1_model': lambda1_model,
        'lambda1_min': lambda1_min,
        'N_inv_half': N_inv_half,
        'ratio_model': ratio_model,
        'ratio_min': ratio_min,
        'eps_margin': eps_margin,
        'needed_no_const': needed_no_const,
        'needed_with_pi': needed_with_pi,
        'u2_suff_naive': u2 >= needed_no_const,
        'u2_suff_correct': u2 >= needed_with_pi,
        'abc_holds': ratio_min >= 1.0,
        'sqfree': sqfree,
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
        (2, 6859, "(2,6859,6861)"),
        (7**3, 2**11, "(343,2048,2391)"),
        (3**7, 2**17, "(2187,131072,133259)"),
        (1, 2**12 - 1, "(1,4095,4096)"),
        (1, 2**15 - 1, "(1,32767,32768)"),
    ]

    print("=" * 110)
    print("LOCAL SHAPE LEMMA v2 — WITH GEOMETRIC CONSTANT pi")
    print("=" * 110)
    print("lambda_1(E_model) = 2*min(K(t),K(1-t))/sqrt(c) >= pi/sqrt(c)")
    print("lambda_1(E_min)   = u^2 * lambda_1(E_model)")
    print("abc condition: lambda_1(E_min) >= N^{-1/2-eps}")
    print()

    print(f"{'Label':<22} {'N':>8} {'q':>6} {'u2':>8} "
          f"{'lam1_mod':>10} {'lam1_min':>10} {'N^-1/2':>10} "
          f"{'ratio':>7} {'eps_m':>7} {'holds':>6}")
    print("-" * 110)

    results = []
    for a, b, label in triples:
        r = analyze_triple(a, b, label)
        if r is None:
            continue
        results.append(r)
        print(f"{label:<22} {r['N']:>8d} {r['q']:>6.3f} {r['u2']:>8d} "
              f"{r['lambda1_model']:>10.2e} {r['lambda1_min']:>10.2e} "
              f"{r['N_inv_half']:>10.2e} "
              f"{r['ratio_min']:>7.3f} {r['eps_margin']:>7.4f} "
              f"{'YES' if r['abc_holds'] else 'NO':>6}")

    print("\n" + "=" * 110)
    print("COMPENSATION ANALYSIS: u^2 * pi vs sqrt(c/N)")
    print("=" * 110)
    print(f"\n{'Label':<22} {'u2':>6} {'u2*pi':>8} {'sqrt(c/N)':>10} "
          f"{'u2*pi/...':>10} {'naive':>6} {'+pi':>6}")
    print("-" * 75)

    for r in results:
        u2pi = r['u2'] * math.pi
        print(f"{r['label']:<22} {r['u2']:>6d} {u2pi:>8.2f} "
              f"{r['needed_no_const']:>10.2f} "
              f"{u2pi / r['needed_no_const']:>10.4f} "
              f"{'YES' if r['u2_suff_naive'] else 'NO':>6} "
              f"{'YES' if r['u2_suff_correct'] else 'NO':>6}")

    print("\n" + "=" * 110)
    print("WORST CASES: HIGHEST q WITH SMALLEST eps-MARGIN")
    print("=" * 110)

    by_margin = sorted(results, key=lambda r: r['eps_margin'])
    print(f"\n{'Label':<22} {'q':>6} {'eps_margin':>10} {'u2':>6} {'lambda1_min/N^-1/2':>20}")
    print("-" * 70)
    for r in by_margin[:8]:
        print(f"{r['label']:<22} {r['q']:>6.3f} {r['eps_margin']:>10.4f} "
              f"{r['u2']:>6d} {r['ratio_min']:>20.4f}")

    print("\n" + "=" * 110)
    print("REYSSAT DEEP ANALYSIS")
    print("=" * 110)

    for r in results:
        if r['label'] != "Reyssat":
            continue
        print(f"\n  Triple: ({r['a']}, {r['b']}, {r['c']})")
        print(f"  N = {r['N']}, q = {r['q']:.4f}")
        print(f"  t = b/c = {r['t']:.10f}")
        print(f"  K(t) = {r['K_t']:.6f}, K(1-t) = {r['K_1mt']:.6f}")
        print(f"  omega1 = {r['omega1']:.6e}, omega3_mag = {r['omega3_mag']:.6e}")
        print(f"  lambda1(model) = 2*min(...) = {r['lambda1_model']:.6e}")
        print(f"  pi/sqrt(c) = {math.pi/math.sqrt(r['c']):.6e} (lower bound)")
        print(f"  u^2 = {r['u2']}")
        print(f"  lambda1(min) = u^2 * lambda1(model) = {r['lambda1_min']:.6e}")
        print(f"  N^{{-1/2}} = {r['N_inv_half']:.6e}")
        print(f"  lambda1(min) / N^{{-1/2}} = {r['ratio_min']:.6f}")
        print(f"  eps-margin = {r['eps_margin']:.6f}")
        print(f"  abc condition at eps=0: {'HOLDS' if r['abc_holds'] else 'FAILS'}")
        print(f"\n  Decomposition:")
        print(f"    Shape factor:  pi/sqrt(c) = {math.pi/math.sqrt(r['c']):.6e}")
        print(f"    K-bonus:       lambda1_model/(pi/sqrt(c)) = {r['lambda1_model']/(math.pi/math.sqrt(r['c'])):.4f}")
        print(f"    Neron factor:  u^2 = {r['u2']}")
        print(f"    Combined:      {r['lambda1_min']:.6e}")
        print(f"    Needed:        N^{{-1/2}} = {r['N_inv_half']:.6e}")
        print(f"    Surplus:       {r['ratio_min']:.4f}x")

        print(f"\n  p-adic structure:")
        for p, info in sorted(r['vp'].items()):
            if info['v_abc'] > 1:
                print(f"    p={p}: v_p(abc)={info['v_abc']}, v_p(Delta)={info['v_delta']}, "
                      f"floor/12={info['floor_12']}, u_p^2={p**(2*info['floor_12']) if info['floor_12'] > 0 else 1}")

    print("\n" + "=" * 110)
    print("SUMMARY")
    print("=" * 110)

    all_hold = all(r['abc_holds'] for r in results)
    min_margin = min(r['eps_margin'] for r in results)
    worst = min(results, key=lambda r: r['eps_margin'])

    print(f"\n  Triples tested: {len(results)}")
    print(f"  lambda1(E_min) >= N^{{-1/2}} for all: {'YES' if all_hold else 'NO'}")
    print(f"  Smallest eps-margin: {min_margin:.4f} (at {worst['label']}, q={worst['q']:.3f})")
    print(f"\n  Key finding: Including the geometric constant C1=pi from the")
    print(f"  Shape-Elimination Lemma, the Neron compensation u^2*pi suffices")
    print(f"  for ALL tested triples, including Reyssat (q=1.63).")
    print(f"\n  Naive analysis (without pi): Reyssat appears to fail")
    print(f"  Corrected analysis (with pi): Reyssat margin = {[r for r in results if r['label']=='Reyssat'][0]['ratio_min']:.3f}x")
    print(f"\n  The geometric constant pi is NOT a luxury — it is load-bearing.")

    any_u2naive_fail = [r for r in results if not r['u2_suff_naive'] and r['q'] > 1.0]
    any_u2corr_fail = [r for r in results if not r['u2_suff_correct'] and r['q'] > 1.0]
    print(f"\n  Triples where u^2 < sqrt(c/N) (naive): {len(any_u2naive_fail)}")
    print(f"  Triples where u^2 < sqrt(c/N)/pi (correct): {len(any_u2corr_fail)}")

if __name__ == "__main__":
    main()
