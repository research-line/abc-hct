"""
WP1: Period-conductor census for Frey curves.

For each abc triple (a, b, c=a+b) with gcd(a,b)=1:
  - Frey curve: y^2 = x(x-a)(x+b)
  - Compute period ratio tau via AGM
  - Compute real period Omega_E
  - Evaluate |eta(tau)|^24
  - Szpiro decomposition: log|Delta| = 12*log(2pi/omega1) + log|eta|^24
  - Period exponent: alpha = log(Omega_E)/log(N)

The abc conjecture is equivalent to:
  alpha >= -1/2 - epsilon  (period lower bound)

Known (GRH): alpha >= -1 - epsilon.
"""

import math
import cmath
import time

def rad(n):
    n = abs(n)
    if n <= 1:
        return max(n, 1)
    result = 1
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            result *= d
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        result *= temp
    return result

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

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

def v2(n):
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        c += 1
        n //= 2
    return c

def check_u2_brute_force(a, b, c):
    """Laska-Kraus bei p=2: prüfe ob Frey-Kurve nicht-minimal ist.
    Korrektur Loop 37/38: u_odd=1 immer, u₂ ∈ {1,2}."""
    abc_prod = a * b * c
    if v2(abc_prod) < 4:
        return 1
    a2 = b - a
    a4 = -(a * b)
    for r in range(64):
        for s in range(2):
            for t0 in range(16):
                t = 4 * t0
                if (a2 + 3 * r - s * s) % 4 != 0:
                    continue
                if (a4 + 2 * r * a2 + 3 * r * r - 2 * s * t) % 16 != 0:
                    continue
                if (r**3 + r**2 * a2 + r * a4 - t**2) % 64 != 0:
                    continue
                return 2
    return 1

def compute_neron_u(a, b, c):
    """Korrigiert (Loop 41): u_odd=1 für alle Frey-Kurven, u₂ via Laska-Kraus."""
    return check_u2_brute_force(a, b, c)

def compute_defect_ledger(a, b, c):
    """Korrigiert (Loop 41): u_odd=1, u₂ via Laska-Kraus. Néron-Exponent nur bei p=2."""
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    all_primes = sorted(set(fa) | set(fb) | set(fc))
    u2 = check_u2_brute_force(a, b, c)
    entries = []
    for p in all_primes:
        ea, eb, ec = fa.get(p, 0), fb.get(p, 0), fc.get(p, 0)
        e_total = ea + eb + ec
        if ec > 0:
            side = 'c'
        elif ea > 0:
            side = 'a'
        else:
            side = 'b'
        vp_delta = 2 * e_total + (4 if p == 2 else 0)
        u_p_exp = (1 if u2 == 2 else 0) if p == 2 else 0
        if side == 'c':
            net_coeff = ec - 1 - 2 * u_p_exp
        else:
            net_coeff = -(1 + 2 * u_p_exp)
        contribution = net_coeff * math.log(p)
        entries.append({
            'p': p, 'side': side, 'e': e_total,
            'vp_delta': vp_delta, 'u_p_exp': u_p_exp,
            'net_coeff': net_coeff, 'contribution': contribution,
        })
    total = sum(e['contribution'] for e in entries)
    return entries, total


def agm(a, b, tol=1e-15, max_iter=100):
    a, b = float(a), float(b)
    for _ in range(max_iter):
        a, b = (a + b) / 2, math.sqrt(a * b)
        if abs(a - b) < tol:
            break
    return a

def eta_product(tau, num_terms=300):
    q = cmath.exp(2j * math.pi * tau)
    q_24th = cmath.exp(2j * math.pi * tau / 24)
    product = 1.0
    qn = 1.0
    for n in range(1, num_terms + 1):
        qn *= q
        product *= (1 - qn)
    return q_24th * product

def compute_tau_and_periods(a_param, b_param):
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
    tau = complex(0, omega3_mag / omega1)
    return tau, omega1

def reduce_tau(tau):
    y = tau.imag
    if y <= 0:
        return tau, 1.0
    if y >= 1.0:
        return tau, 1.0
    tau_red = complex(0, 1.0 / y)
    scale = y ** 12
    return tau_red, scale

def analyze_frey_curve(a, b):
    c = a + b
    if gcd(a, b) != 1:
        return None

    N = rad(a * b * c)
    delta_min = 16 * (a * b * c) ** 2

    try:
        tau, omega1 = compute_tau_and_periods(a, b)
    except (ValueError, ZeroDivisionError):
        return None
    if tau.imag <= 0:
        return None

    eta_val = eta_product(tau, num_terms=300)
    eta_24 = abs(eta_val) ** 24

    tau_red, scale = reduce_tau(tau)
    eta_24_red = scale * eta_24

    log_delta = math.log(delta_min)
    log_N = math.log(N)
    szpiro_ratio = log_delta / log_N if log_N > 0 else float('inf')

    log_eta24 = math.log(eta_24) if eta_24 > 0 else float('-inf')
    eta_exponent = log_eta24 / log_N if log_N > 0 else 0

    omega_E = 2 * omega1
    log_omega = math.log(omega_E)
    period_exponent = log_omega / log_N if log_N > 0 else 0

    szpiro_period = 12 * math.log(2 * math.pi / omega1)
    szpiro_eta = log_eta24
    szpiro_check = szpiro_period + szpiro_eta
    szpiro_residual = log_delta - szpiro_check

    period_share = szpiro_period / log_N if log_N > 0 else 0
    eta_share = szpiro_eta / log_N if log_N > 0 else 0

    q = math.log(c) / math.log(N) if N > 1 else 0

    h_falt = -math.log(omega1) - 0.5 * math.log(tau.imag)
    h_falt_exponent = h_falt / log_N if log_N > 0 else 0

    e1 = float(a)
    e2 = 0.0
    e3 = float(-b)
    if e1 < e3:
        e1, e3 = e3, e1
    if e1 < e2:
        e1, e2 = e2, e1
    if e2 < e3:
        e2, e3 = e3, e2
    omega3_mag = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e2 - e3))
    lambda1_model = min(omega1, omega3_mag)
    u_neron = compute_neron_u(a, b, c)
    lambda1_min = u_neron * lambda1_model
    N_inv_half = 1.0 / math.sqrt(N)
    lambda1_ratio = lambda1_min / N_inv_half if N_inv_half > 0 else 0
    q_eff = q - 2 * math.log(u_neron * math.pi) / log_N if log_N > 0 and u_neron > 0 else q
    defect_entries, defect_total = compute_defect_ledger(a, b, c)

    theta = math.asin(math.sqrt(a / c))
    shape_balance = 2 * math.sqrt(a * b) / c
    cusp_shape_depth = -math.log(min(a / c, b / c))
    lam1_residual = math.log(lambda1_model) + 0.5 * math.log(c)
    lam1_residual_norm = lam1_residual / log_N if log_N > 0 else 0

    return {
        'a': a, 'b': b, 'c': c,
        'N': N, 'delta_min': delta_min,
        'quality': q,
        'tau': tau, 'im_tau': tau.imag,
        'tau_red': tau_red, 'im_tau_red': tau_red.imag,
        'omega1': omega1, 'omega_E': omega_E,
        'eta_24': eta_24,
        'eta_24_red': eta_24_red,
        'log_delta': log_delta, 'log_N': log_N,
        'szpiro_ratio': szpiro_ratio,
        'log_eta24': log_eta24,
        'eta_exponent': eta_exponent,
        'log_omega': log_omega,
        'period_exponent': period_exponent,
        'szpiro_period': szpiro_period,
        'szpiro_eta': szpiro_eta,
        'szpiro_residual': szpiro_residual,
        'period_share': period_share,
        'eta_share': eta_share,
        'h_falt': h_falt,
        'h_falt_exponent': h_falt_exponent,
        'omega3_mag': omega3_mag,
        'lambda1_model': lambda1_model,
        'u_neron': u_neron,
        'lambda1_min': lambda1_min,
        'lambda1_ratio': lambda1_ratio,
        'q_eff': q_eff,
        'defect_entries': defect_entries,
        'defect_total': defect_total,
        'theta': theta,
        'shape_balance': shape_balance,
        'cusp_shape_depth': cusp_shape_depth,
        'lam1_residual': lam1_residual,
        'lam1_residual_norm': lam1_residual_norm,
    }

def sieve_radical(max_n):
    rad_arr = [1] * (max_n + 1)
    for p in range(2, max_n + 1):
        if rad_arr[p] == 1:
            for m in range(p, max_n + 1, p):
                rad_arr[m] *= p
    return rad_arr

def find_high_quality_triples_sieve(max_c=10000, min_quality=1.2):
    print(f"  Precomputing radical sieve up to {max_c}...")
    rad_arr = sieve_radical(max_c)
    found = []
    for c in range(3, max_c + 1):
        if rad_arr[c] == c:
            continue
        log_c = math.log(c)
        max_rad = c ** (1.0 / min_quality)
        for a in range(1, c // 2 + 1):
            b = c - a
            if gcd(a, b) != 1:
                continue
            r = rad_arr[a] * rad_arr[b] * rad_arr[c]
            if r <= max_rad:
                q = log_c / math.log(r)
                found.append((a, b, q))
    found.sort(key=lambda x: -x[2])
    return found

def main():
    print("=" * 90)
    print("WP1: PERIOD-CONDUCTOR CENSUS FOR FREY CURVES")
    print("abc <=> Omega_E >= c * N^{-1/2-eps}")
    print("Known (GRH): alpha = log(Omega)/log(N) >= -1-eps")
    print("Conjectured: alpha >= -1/2-eps")
    print("=" * 90)

    test_triples = [
        (1, 2, "1+2=3"),
        (1, 8, "1+8=9"),
        (1, 48, "1+48=49"),
        (1, 63, "1+63=64"),
        (1, 80, "1+80=81"),
        (1, 1023, "1+1023=1024"),
        (1, 2400, "1+2400=2401"),
        (1, 4374, "1+4374=4375"),
        (1, 6560, "1+6560=6561"),
        (2, 109, "2+109=111"),
        (3, 125, "3+125=128"),
        (5, 27, "5+27=32"),
        (7, 2187, "7+2187=2194"),
        (13, 243, "13+243=256"),
        (32, 49, "32+49=81"),
        (2, 6859, "2+6859=6861"),
        (1, 2**6 * 3 - 1, "1+191=192"),
        (2, 3**10 * 109, "Reyssat"),
        (1, 2**12 - 1, "1+4095=4096"),
        (11, 2**5, "11+32=43"),
        (1, 2**10 * 3 - 1, "1+3071=3072"),
        (7**3, 2**11, "343+2048=2391"),
        (1, 2**15 - 1, "1+32767=32768"),
        (1, 5**7 - 1, "1+78124=78125"),
        (3**7, 2**17, "2187+131072=133259"),
        (1, 3**15 - 1, "1+14348906=14348907"),
        (2**4, 3**7 - 16, "16+2171=2187"),
        (1, 3**12 - 1, "1+531440=531441"),
    ]

    print(f"\n{'Triple':<22} {'N':>10} {'q(abc)':>7} {'sigma':>7} "
          f"{'alpha':>7} {'eta_sh':>7} {'prd_sh':>7} "
          f"{'|eta|^24':>10} {'Im(tau)':>7}")
    print("-" * 90)

    results = []
    for a, b, label in test_triples:
        r = analyze_frey_curve(a, b)
        if r is None:
            print(f"{label:<22} {'SKIP':>10}")
            continue
        results.append(r)
        print(f"{label:<22} {r['N']:>10d} {r['quality']:>7.3f} "
              f"{r['szpiro_ratio']:>7.3f} {r['period_exponent']:>7.4f} "
              f"{r['eta_share']:>7.3f} {r['period_share']:>7.3f} "
              f"{r['eta_24']:>10.2e} {r['im_tau']:>7.4f}")

    if not results:
        return

    # -- Szpiro decomposition verification --
    print("\n" + "=" * 90)
    print("SZPIRO DECOMPOSITION VERIFICATION")
    print("log|Delta| = 12*log(2pi/omega1) + log|eta|^24 + residual")
    print("=" * 90)

    max_residual = 0
    for r in results:
        res = abs(r['szpiro_residual'])
        max_residual = max(max_residual, res)
    print(f"Max |residual| = {max_residual:.6f} "
          f"({'OK' if max_residual < 0.01 else 'CHECK'})")

    # -- Period exponent analysis --
    print("\n" + "=" * 90)
    print("PERIOD EXPONENT ANALYSIS")
    print("alpha = log(Omega_E)/log(N)")
    print("abc requires: alpha >= -0.5")
    print("GRH gives:    alpha >= -1.0")
    print("=" * 90)

    alphas = [r['period_exponent'] for r in results]
    print(f"\n  min alpha = {min(alphas):.4f}")
    print(f"  max alpha = {max(alphas):.4f}")
    print(f"  mean alpha = {sum(alphas)/len(alphas):.4f}")
    print(f"  All alpha > -0.5: {'YES' if min(alphas) > -0.5 else 'NO'}")
    print(f"  All alpha > -1.0: {'YES' if min(alphas) > -1.0 else 'NO'}")

    worst = min(results, key=lambda r: r['period_exponent'])
    print(f"\n  Worst case: a={worst['a']}, b={worst['b']}, c={worst['c']}")
    print(f"    N = {worst['N']}, alpha = {worst['period_exponent']:.4f}")
    print(f"    Omega_E = {worst['omega_E']:.6e}")
    print(f"    Szpiro ratio = {worst['szpiro_ratio']:.3f}")

    # -- Szpiro decomposition --
    print("\n" + "=" * 90)
    print("SZPIRO RATIO DECOMPOSITION")
    print("sigma = period_share + eta_share")
    print("=" * 90)

    for r in sorted(results, key=lambda x: -x['szpiro_ratio'])[:10]:
        print(f"  sigma={r['szpiro_ratio']:.3f} = "
              f"{r['period_share']:.3f}(period) + "
              f"{r['eta_share']:.3f}(eta)  "
              f"[q={r['quality']:.3f}] "
              f"a={r['a']}, b={r['b']}")

    # -- Eta bound check --
    print("\n" + "=" * 90)
    print("ETA BOUND CHECK")
    print("|eta(tau_red)|^24 < 0.005 for all E/Q (Theorem 8.10)")
    print("tau_red = SL_2(Z)-reduced period ratio (Im >= 1)")
    print("=" * 90)

    eta_vals = [r['eta_24'] for r in results]
    eta_red_vals = [r['eta_24_red'] for r in results]
    print(f"\n  Unreduced (raw AGM):")
    print(f"    max |eta|^24 = {max(eta_vals):.6e}")
    print(f"    min |eta|^24 = {min(eta_vals):.6e}")
    print(f"\n  SL_2(Z)-reduced:")
    print(f"    max |eta_red|^24 = {max(eta_red_vals):.6e}")
    print(f"    min |eta_red|^24 = {min(eta_red_vals):.6e}")
    print(f"    All < 0.005: {'YES' if max(eta_red_vals) < 0.005 else 'NO'}")

    eta_exps = [r['eta_exponent'] for r in results]
    print(f"\n  Eta exponents (unreduced, basis-dependent):")
    print(f"    max = {max(eta_exps):.4f}")
    print(f"    All < 0: {'YES' if max(eta_exps) < 0 else 'NO'}")

    # -- Systematic search with sieve --
    print("\n" + "=" * 90)
    print("SYSTEMATIC SEARCH: HIGH-QUALITY TRIPLES (c <= 10000, q >= 1.2)")
    print("=" * 90)

    t0 = time.time()
    hq = find_high_quality_triples_sieve(10000, 1.2)
    dt = time.time() - t0
    print(f"  Found {len(hq)} high-quality triples in {dt:.1f}s")

    if hq:
        print(f"\n{'a':>8} {'b':>8} {'c':>8} {'N':>10} {'q(abc)':>7} "
              f"{'sigma':>7} {'alpha':>7} {'|eta|^24':>10}")
        print("-" * 75)
        for a, b, q in hq[:30]:
            r = analyze_frey_curve(a, b)
            if r is None:
                continue
            results.append(r)
            print(f"{a:>8d} {b:>8d} {a+b:>8d} {r['N']:>10d} "
                  f"{q:>7.3f} {r['szpiro_ratio']:>7.3f} "
                  f"{r['period_exponent']:>7.4f} {r['eta_24']:>10.2e}")

    # -- Effective quality (q_eff) analysis --
    print("\n" + "=" * 90)
    print("EFFECTIVE QUALITY ANALYSIS (§15)")
    print("q_eff = q - 2*log(u*pi)/log(N)")
    print("u = Neron minimization factor (scaling is u, NOT u^2)")
    print("Shape+Neron eliminate geometric quality; q_eff = irreducible arithmetic content")
    print("=" * 90)

    print(f"\n  {'Triple':<22} {'q':>6} {'u':>6} {'q_eff':>7} "
          f"{'lam1_mod':>10} {'lam1_min':>10} {'N^-1/2':>10} {'ratio':>7}")
    print("  " + "-" * 85)
    for r in sorted(results, key=lambda x: -x['q_eff']):
        label = f"({r['a']},{r['b']},{r['c']})"
        if len(label) > 22:
            label = label[:19] + "..."
        print(f"  {label:<22} {r['quality']:>6.3f} {r['u_neron']:>6d} {r['q_eff']:>7.4f} "
              f"{r['lambda1_model']:>10.2e} {r['lambda1_min']:>10.2e} "
              f"{1/math.sqrt(r['N']):>10.2e} {r['lambda1_ratio']:>7.4f}")

    all_qeff = [r['q_eff'] for r in results]
    high_q = [r for r in results if r['quality'] > 1.0]
    high_q_eff = [r['q_eff'] for r in high_q] if high_q else [0]

    print(f"\n  All {len(results)} curves:")
    print(f"    q_eff range: [{min(all_qeff):.4f}, {max(all_qeff):.4f}]")
    print(f"    q_eff < 1 for all: {'YES' if max(all_qeff) < 1 else 'NO'}")
    if high_q:
        worst_qeff = max(high_q, key=lambda r: r['q_eff'])
        print(f"\n  High-quality triples (q > 1): {len(high_q)}")
        print(f"    max q_eff: {max(high_q_eff):.4f} at ({worst_qeff['a']},{worst_qeff['b']},{worst_qeff['c']})")
        print(f"    q_eff < 1+eps for all: {'YES — geometric tools suffice' if max(high_q_eff) < 1.0 else 'NO — arithmetic residual remains'}")

    # lambda1_min vs N^{-1/2} check
    all_ratios = [r['lambda1_ratio'] for r in results]
    print(f"\n  lambda1(E_min) / N^{{-1/2}}:")
    print(f"    min ratio: {min(all_ratios):.4f}")
    print(f"    All >= 1 (abc at eps=0): {'YES' if min(all_ratios) >= 1.0 else 'NO'}")

    # -- Defect Ledger analysis --
    print("\n" + "=" * 90)
    print("DEFECT LEDGER (§15 / GPT Review)")
    print("D_eff = sum over p: net_coeff(p) * log(p)")
    print("  p|c:  net = (e_p - 1 - 2*floor(v_p(Delta)/12))  [DEFECT if > 0]")
    print("  p|ab: net = -(1 + 2*floor(v_p(Delta)/12))       [INSURANCE, always < 0]")
    print("q_eff ~ 1 + (D_eff - 2*log(pi)) / log(N)")
    print("=" * 90)

    for r in sorted(results, key=lambda x: -x['quality'])[:15]:
        label = f"({r['a']},{r['b']},{r['c']})"
        if len(label) > 25:
            label = label[:22] + "..."
        print(f"\n  {label}  q={r['quality']:.3f}  q_eff={r['q_eff']:.4f}  D_eff={r['defect_total']:.4f}")
        print(f"    {'p':>5} {'side':>4} {'e_p':>4} {'v_p(D)':>6} {'u_p':>4} {'net':>5} {'contrib':>8}")
        print(f"    {'-'*40}")
        for e in sorted(r['defect_entries'], key=lambda x: -x['contribution']):
            tag = '+DEF' if e['contribution'] > 0.01 else '-INS' if e['contribution'] < -0.01 else '  ~0'
            print(f"    {e['p']:>5} {e['side']:>4} {e['e']:>4} {e['vp_delta']:>6} "
                  f"{e['u_p_exp']:>4} {e['net_coeff']:>5} {e['contribution']:>+8.3f} {tag}")

    print(f"\n  {'--- DEFECT BUDGET SUMMARY ---':^60}")
    print(f"  {'Triple':<25} {'D_eff':>7} {'q_eff':>7} {'top defect prime':>20}")
    print(f"  {'-'*60}")
    for r in sorted(results, key=lambda x: -x['defect_total'])[:10]:
        label = f"({r['a']},{r['b']},{r['c']})"
        if len(label) > 25:
            label = label[:22] + "..."
        worst_p = max(r['defect_entries'], key=lambda x: x['contribution'])
        if worst_p['contribution'] > 0:
            ptag = f"p={worst_p['p']}({worst_p['side']}) {worst_p['contribution']:+.3f}"
        else:
            ptag = "none (all insured)"
        print(f"  {label:<25} {r['defect_total']:>+7.3f} {r['q_eff']:>7.4f} {ptag:>20}")

    # -- Shape-Elimination Diagnostic --
    log_C1 = math.log(math.pi)
    log_C2 = math.log(3.7081493546027438)
    print("\n" + "=" * 90)
    print("SHAPE-ELIMINATION DIAGNOSTIC (Frostlinsen-Lemma)")
    print("lambda1_residual = log(lambda1_model) + 0.5*log(c)")
    print(f"Expected range: [log(pi), log(2K(1/2))] = [{log_C1:.4f}, {log_C2:.4f}]")
    print("theta = arcsin(sqrt(a/c)),  shape_balance = sin(2*theta) = 2*sqrt(ab)/c")
    print("cusp_shape_depth = -log(min(a/c, b/c))  [large => extreme shape]")
    print("=" * 90)

    print(f"\n  {'Triple':<22} {'q':>6} {'theta':>7} {'sin2th':>7} "
          f"{'cusp_d':>7} {'lam1_res':>9} {'norm':>7} {'in_band':>8}")
    print("  " + "-" * 80)
    sorted_by_q = sorted(results, key=lambda x: -x['quality'])
    all_in_band = True
    for r in sorted_by_q:
        label = f"({r['a']},{r['b']},{r['c']})"
        if len(label) > 22:
            label = label[:19] + "..."
        in_band = log_C1 - 0.001 <= r['lam1_residual'] <= log_C2 + 0.001
        if not in_band:
            all_in_band = False
        tag = "OK" if in_band else "FAIL"
        print(f"  {label:<22} {r['quality']:>6.3f} {math.degrees(r['theta']):>7.2f} "
              f"{r['shape_balance']:>7.4f} {r['cusp_shape_depth']:>7.3f} "
              f"{r['lam1_residual']:>9.5f} {r['lam1_residual_norm']:>7.4f} {tag:>8}")

    all_res = [r['lam1_residual'] for r in results]
    all_sb = [r['shape_balance'] for r in results]
    all_cd = [r['cusp_shape_depth'] for r in results]
    print(f"\n  lambda1_residual range: [{min(all_res):.5f}, {max(all_res):.5f}]")
    print(f"  Theoretical band:      [{log_C1:.5f}, {log_C2:.5f}]")
    print(f"  All in band: {'YES — Shape-Elimination confirmed' if all_in_band else 'NO — check outliers'}")
    print(f"  shape_balance range: [{min(all_sb):.4f}, {max(all_sb):.4f}]  (1.0 = symmetric)")
    print(f"  cusp_shape_depth range: [{min(all_cd):.3f}, {max(all_cd):.3f}]  (0 = symmetric)")

    # -- Final summary --
    print("\n" + "=" * 90)
    print("FINAL SUMMARY")
    print("=" * 90)

    all_alphas = [r['period_exponent'] for r in results]
    all_sigmas = [r['szpiro_ratio'] for r in results]
    all_etas = [r['eta_24'] for r in results]

    print(f"\nTotal curves analyzed: {len(results)}")
    print(f"\nPeriod exponent alpha = log(Omega_E)/log(N):")
    print(f"  Range: [{min(all_alphas):.4f}, {max(all_alphas):.4f}]")
    print(f"  abc threshold (-0.5): {'ALL ABOVE' if min(all_alphas) > -0.5 else 'VIOLATED'}")
    print(f"\nSzpiro ratio sigma = log|Delta|/log N:")
    print(f"  Range: [{min(all_sigmas):.3f}, {max(all_sigmas):.3f}]")
    print(f"  Szpiro bound (6): {'ALL BELOW' if max(all_sigmas) < 6 else 'some above 6'}")
    all_etas_red = [r['eta_24_red'] for r in results]
    print(f"\nEta bound |eta_red|^24 (SL_2(Z)-reduced):")
    print(f"  Max: {max(all_etas_red):.6e}")
    print(f"  Theorem 8.10 bound (0.005): {'CONFIRMED' if max(all_etas_red) < 0.005 else 'VIOLATED'}")

    # -- Faltings height analysis (WP3) --
    print("\n" + "=" * 90)
    print("FALTINGS HEIGHT ANALYSIS (WP3)")
    print("h_Falt = -log(omega1) - (1/2)*log(Im tau)  [omega1 = half-period from AGM]")
    print("abc requires: h_Falt/log(N) <= 1/2 + epsilon")
    print("GRH gives:    h_Falt/log(N) <= 1 + epsilon")
    print("=" * 90)

    all_hf = [r['h_falt_exponent'] for r in results]
    print(f"\n  Faltings height exponent beta = h_Falt/log(N):")
    print(f"    Range: [{min(all_hf):.4f}, {max(all_hf):.4f}]")
    print(f"    abc threshold (0.5): {'ALL BELOW' if max(all_hf) < 0.5 else 'some above 0.5'}")
    print(f"    GRH threshold (1.0): {'ALL BELOW' if max(all_hf) < 1.0 else 'some above 1.0'}")

    worst_hf = max(results, key=lambda r: r['h_falt_exponent'])
    print(f"\n  Worst case: a={worst_hf['a']}, b={worst_hf['b']}, c={worst_hf['c']}")
    print(f"    N = {worst_hf['N']}, beta = {worst_hf['h_falt_exponent']:.4f}")
    print(f"    h_Falt = {worst_hf['h_falt']:.4f}")
    print(f"    Omega_E = {worst_hf['omega_E']:.6e}, Im(tau) = {worst_hf['im_tau']:.4f}")
    print(f"    alpha = {worst_hf['period_exponent']:.4f}, quality = {worst_hf['quality']:.3f}")

    print(f"\n  Equivalence chain (all {len(results)} curves):")
    print(f"    abc (q<1+eps):       max q = {max(r['quality'] for r in results):.3f}")
    print(f"    Szpiro (sigma<6+eps): max sigma = {max(all_sigmas):.3f}")
    print(f"    Period (alpha>-0.5): min alpha = {min(all_alphas):.4f}")
    print(f"    Faltings (beta<0.5): max beta = {max(all_hf):.4f}")
    print(f"    Eta (|eta_red|<0.005): max = {max(all_etas_red):.6e}")

    print(f"\n  Top 10 by Faltings exponent:")
    print(f"  {'a':>8} {'b':>8} {'c':>8} {'N':>8} {'q':>6} {'sigma':>6} "
          f"{'alpha':>7} {'beta':>7} {'h_Falt':>8}")
    print("  " + "-" * 78)
    for r in sorted(results, key=lambda x: -x['h_falt_exponent'])[:10]:
        print(f"  {r['a']:>8d} {r['b']:>8d} {r['c']:>8d} {r['N']:>8d} "
              f"{r['quality']:>6.3f} {r['szpiro_ratio']:>6.3f} "
              f"{r['period_exponent']:>7.4f} {r['h_falt_exponent']:>7.4f} "
              f"{r['h_falt']:>8.3f}")

if __name__ == "__main__":
    main()
