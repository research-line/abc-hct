"""
CCM-Shimura Cancellation Test
==============================
Tests whether cross-correlations of Hecke eigenvalues show extra cancellation
beyond the random-walk prediction, as the CCM (Poisson-Rayleigh) mechanism
would predict.

CORE TEST:
  C(P) = sum_{p <= P, prime} a_p(f1) * a_p(f2)   [cross-correlation]
  S(P) = sum_{p <= P, prime} a_p(f1)^2             [self-correlation]

  Random-walk prediction: |C(P)| ~ P^{3/2}
  CCM prediction:         |C(P)| ~ P^{3/2 - delta} for some delta > 0
  Self-correlation:       S(P) ~ P^2 / 2           (always, pole at s=1)

If delta > 0: CCM cancellation present -> potential path to abc
If delta = 0: standard amplification tight -> no improvement

Also computes the Rankin-Selberg partial L-value:
  L_RS(f1 x f2, P) = sum_{p <= P} a_p(f1) a_p(f2) / p
"""

import math

def legendre_symbol(a, p):
    a = a % p
    if a == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [p for p in range(2, limit + 1) if is_prime[p]]

def compute_ap(curve_disc_fn, p):
    """Compute a_p by point counting.
    curve_disc_fn(x, p) returns the discriminant of the y-quadratic mod p."""
    s = 0
    for x in range(p):
        d = curve_disc_fn(x, p) % p
        s += legendre_symbol(d, p)
    return -s

# Curve definitions: each returns the discriminant of y^2 + y = f(x)
# i.e., disc = 1 + 4*f(x) for the equation y^2 + y - f(x) = 0

def curve_37a(x, p):
    """37a1: y^2 + y = x^3 - x"""
    return (1 + 4 * (pow(x, 3, p) - x)) % p

def curve_37b(x, p):
    """37b1: y^2 + y = x^3 + x^2 - 23x - 50"""
    return (1 + 4 * (pow(x, 3, p) + x * x - 23 * x - 50)) % p

def curve_43a(x, p):
    """43a1: y^2 + y = x^3 + x^2"""
    return (1 + 4 * (pow(x, 3, p) + x * x)) % p

def curve_53a(x, p):
    """53a1: y^2 + xy + y = x^3 - x^2
    disc = (x+1)^2 + 4*(x^3 - x^2) = x^2 + 2x + 1 + 4x^3 - 4x^2"""
    return (4 * pow(x, 3, p) - 3 * x * x + 2 * x + 1) % p

def curve_57a(x, p):
    """57a1: y^2 + y = x^3 - x^2 - 2x + 2"""
    return (1 + 4 * (pow(x, 3, p) - x * x - 2 * x + 2)) % p

def curve_57b(x, p):
    """57b1: y^2 + y = x^3 + x^2 - 20x - 32"""
    return (1 + 4 * (pow(x, 3, p) + x * x - 20 * x - 32)) % p

def curve_57c(x, p):
    """57c1: y^2 + xy = x^3 - x^2 - 2x + 2
    disc = x^2 + 4*(x^3 - x^2 - 2x + 2)"""
    return (4 * pow(x, 3, p) - 3 * x * x - 8 * x + 8) % p

# Level 61: dim S_2(Gamma_0(61)) = 4
def curve_61a(x, p):
    """61a1: y^2 + xy = x^3 - x^2 - x
    disc = x^2 + 4(x^3 - x^2 - x) = 4x^3 - 3x^2 - 4x"""
    return (4 * pow(x, 3, p) - 3 * x * x - 4 * x) % p


def run_test(curves, level, prime_limit=2000):
    """Run the CCM cancellation test for a set of curves at a given level."""
    primes = sieve_primes(prime_limit)
    good_primes = [p for p in primes if p > 2 and level % p != 0]

    n_curves = len(curves)
    labels = [c[0] for c in curves]
    fns = [c[1] for c in curves]

    # Compute all a_p
    ap_data = {label: [] for label in labels}
    for p in good_primes:
        for label, fn in zip(labels, fns):
            ap_data[label].append(compute_ap(fn, p))

    # Cross-correlation and self-correlation analysis
    print(f"\n{'='*90}")
    print(f"LEVEL N = {level}, {n_curves} Neuformen, {len(good_primes)} Primzahlen bis {prime_limit}")
    print(f"{'='*90}")

    # Checkpoints for measuring growth rate
    checkpoints = [50, 100, 200, 500, 1000, 1500, 2000]
    checkpoints = [c for c in checkpoints if c <= prime_limit]

    # Self-correlations
    print(f"\n--- SELF-KORRELATION S(P) = sum a_p^2 ---")
    print(f"Erwartung: S(P) ~ P^2 / 2 (Ramanujan, Sato-Tate)")
    print(f"{'Form':<8} {'P':>6} {'S(P)':>12} {'P^2/2':>12} {'Ratio':>8} {'log-Exp':>8}")
    print("-" * 60)

    for label in labels:
        prev_s = None
        prev_p = None
        for cp in checkpoints:
            idx = sum(1 for p in good_primes if p <= cp)
            if idx == 0:
                continue
            s = sum(ap_data[label][i]**2 for i in range(idx))
            p_max = good_primes[idx - 1]
            expected = p_max**2 / 2
            ratio = s / expected if expected > 0 else 0
            if prev_s is not None and prev_s > 0 and s > prev_s:
                log_exp = math.log(s / prev_s) / math.log(p_max / prev_p) if prev_p > 0 else 0
            else:
                log_exp = 0
            print(f"{label:<8} {p_max:>6d} {s:>12.1f} {expected:>12.1f} {ratio:>8.3f} {log_exp:>8.2f}")
            prev_s = s
            prev_p = p_max

    # Cross-correlations (all pairs)
    print(f"\n--- CROSS-KORRELATION C(P) = sum a_p(f1) * a_p(f2) ---")
    print(f"Random-Walk: |C(P)| ~ P^(3/2)")
    print(f"CCM-Hypothese: |C(P)| ~ P^(3/2 - delta) fuer delta > 0")

    pairs = []
    for i in range(n_curves):
        for j in range(i + 1, n_curves):
            pairs.append((i, j))

    for i, j in pairs:
        l1, l2 = labels[i], labels[j]
        print(f"\n  Paar ({l1}, {l2}):")
        print(f"  {'P':>6} {'C(P)':>12} {'|C|':>12} {'P^1.5':>12} {'|C|/P^1.5':>10} {'log-Exp':>8}")
        print("  " + "-" * 66)

        prev_c = None
        prev_p = None
        for cp in checkpoints:
            idx = sum(1 for p in good_primes if p <= cp)
            if idx == 0:
                continue
            c = sum(ap_data[l1][k] * ap_data[l2][k] for k in range(idx))
            p_max = good_primes[idx - 1]
            p15 = p_max**1.5
            ratio = abs(c) / p15 if p15 > 0 else 0
            if prev_c is not None and abs(prev_c) > 0 and abs(c) > 0:
                log_exp = math.log(abs(c) / abs(prev_c)) / math.log(p_max / prev_p) if prev_p > 0 and abs(prev_c) > 0 else 0
            else:
                log_exp = 0
            print(f"  {p_max:>6d} {c:>12.1f} {abs(c):>12.1f} {p15:>12.1f} {ratio:>10.4f} {log_exp:>8.2f}")
            prev_c = c
            prev_p = p_max

    # Rankin-Selberg L-values (partial sums at s=1)
    print(f"\n--- RANKIN-SELBERG PARTIAL L-WERTE L(f1 x f2, 1) ---")
    print(f"Self: L(f x f, 1) ~ log(P) (Pole bei s=1)")
    print(f"Cross: L(f1 x f2, 1) -> endlich (entire)")

    for i in range(n_curves):
        for j in range(i, n_curves):
            l1, l2 = labels[i], labels[j]
            print(f"\n  Paar ({l1}, {l2}){'  [SELF]' if i == j else '  [CROSS]'}:")
            print(f"  {'P':>6} {'L_RS(P)':>12} {'Konvergenz':>12}")
            print("  " + "-" * 36)

            prev_val = None
            for cp in checkpoints:
                idx = sum(1 for p in good_primes if p <= cp)
                if idx == 0:
                    continue
                val = sum(ap_data[l1][k] * ap_data[l2][k] / good_primes[k]
                          for k in range(idx))
                p_max = good_primes[idx - 1]
                delta = abs(val - prev_val) if prev_val is not None else 0
                print(f"  {p_max:>6d} {val:>12.6f} {delta:>12.6f}")
                prev_val = val

    # Growth rate analysis
    print(f"\n--- WACHSTUMSRATEN-ANALYSE ---")
    print(f"Frage: Waechst |C(P)| wie P^alpha? Messe alpha.")
    print(f"alpha = 1.5: Random Walk (keine Extra-Cancellation)")
    print(f"alpha < 1.5: CCM-Cancellation vorhanden!")
    print(f"alpha < 1.0: Starke Cancellation (wuerde abc-Gap verkleinern)")

    for i, j in pairs:
        l1, l2 = labels[i], labels[j]
        # Compute running exponent via linear regression on log-log
        log_p_list = []
        log_c_list = []
        for cp in range(20, prime_limit + 1, 20):
            idx = sum(1 for p in good_primes if p <= cp)
            if idx < 5:
                continue
            c = sum(ap_data[l1][k] * ap_data[l2][k] for k in range(idx))
            p_max = good_primes[idx - 1]
            if abs(c) > 0:
                log_p_list.append(math.log(p_max))
                log_c_list.append(math.log(abs(c)))

        if len(log_p_list) >= 10:
            # Linear regression: log|C| = alpha * log(P) + beta
            n = len(log_p_list)
            sx = sum(log_p_list)
            sy = sum(log_c_list)
            sxx = sum(x**2 for x in log_p_list)
            sxy = sum(x * y for x, y in zip(log_p_list, log_c_list))
            alpha = (n * sxy - sx * sy) / (n * sxx - sx**2)
            beta = (sy - alpha * sx) / n

            # Also compute for last half (asymptotic)
            half = n // 2
            lp2 = log_p_list[half:]
            lc2 = log_c_list[half:]
            n2 = len(lp2)
            sx2 = sum(lp2)
            sy2 = sum(lc2)
            sxx2 = sum(x**2 for x in lp2)
            sxy2 = sum(x * y for x, y in zip(lp2, lc2))
            alpha2 = (n2 * sxy2 - sx2 * sy2) / (n2 * sxx2 - sx2**2) if n2 * sxx2 - sx2**2 != 0 else 0

            print(f"\n  Paar ({l1}, {l2}):")
            print(f"    alpha (gesamt):     {alpha:.4f}  (Random Walk = 1.5)")
            print(f"    alpha (2. Haelfte): {alpha2:.4f}  (asymptotisch)")
            if alpha < 1.45:
                print(f"    >>> HINWEIS: alpha < 1.5 deutet auf Extra-Cancellation hin!")
            if alpha2 < 1.0:
                print(f"    >>> STARK: alpha_asym < 1.0 -- signifikante CCM-Signatur!")

    # Summary
    print(f"\n{'='*90}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*90}")
    print(f"Level N = {level}, {n_curves} Formen, Primzahlen bis {prime_limit}")
    print()
    print("INTERPRETATION:")
    print("  alpha ~ 1.5: Keine Extra-Cancellation. Standard-Amplifikation ist tight.")
    print("               Der sqrt(N)-Verlust ist intrinsisch -- CCM hilft NICHT.")
    print("  alpha ~ 1.0: Moderate Cancellation. CCM-Mechanismus moeglicherweise aktiv.")
    print("               Amplifikationsverlust reduziert sich auf N^{1/4}.")
    print("  alpha ~ 0.5: Starke Cancellation. Amplifikation fast verlustfrei.")
    print("               Wuerde abc stark einschraenken oder beweisen.")
    print()
    print("WARNUNG: Dieser Test auf X_0(N) (nicht-kompakt) ist ein PROXY fuer den")
    print("eigentlichen Test auf der kompakten Shimura-Kurve X_0^D(M). Auf der")
    print("kompakten Kurve koennte die Cancellation STAERKER sein (kein Eisenstein).")


def main():
    print("=" * 90)
    print("CCM-SHIMURA CANCELLATION TEST")
    print("Testet Poisson-Rayleigh-Cancellation in Hecke-Kreuzkorrelationen")
    print("=" * 90)

    # Test 1: Level 37 (2 rational newforms)
    curves_37 = [
        ("37a", curve_37a),
        ("37b", curve_37b),
    ]
    run_test(curves_37, level=37, prime_limit=2000)

    # Test 2: Level 57 = 3*19 (multiple newforms)
    curves_57 = [
        ("57a", curve_57a),
        ("57b", curve_57b),
        ("57c", curve_57c),
    ]
    run_test(curves_57, level=57, prime_limit=2000)

    # Test 3: Frey curve test
    # Triple (5, 27, 32): E: y^2 = x(x-5)(x+27) = x^3 + 22x^2 - 135x
    # N = rad(5*27*32) = rad(4320) = 30
    # Compare with other forms at level 30
    print(f"\n\n{'='*90}")
    print("FREY-KURVEN-TEST")
    print("Triple (5, 27, 32): E: y^2 = x(x-5)(x+27), N = 30")
    print("=" * 90)

    def curve_frey_5_27(x, p):
        """Frey curve y^2 = x^3 + 22x^2 - 135x, disc = 4*(x^3+22x^2-135x)"""
        return (4 * (pow(x, 3, p) + 22 * x * x - 135 * x)) % p

    # Level 30: need other forms too
    # 30a1: y^2 + xy + y = x^3 + x + 2 (conductor 30)
    def curve_30a(x, p):
        """30a1: y^2 + xy + y = x^3 + x + 2
        disc = (x+1)^2 + 4(x^3 + x + 2) = 4x^3 + x^2 + 6x + 9"""
        return (4 * pow(x, 3, p) + x * x + 6 * x + 9) % p

    # Test just the Frey curve's self-correlation to verify setup
    primes = sieve_primes(2000)
    good_primes = [p for p in primes if p > 2 and 30 % p != 0]

    print(f"\nFrey-Kurve a_p fuer kleine Primzahlen:")
    for p in good_primes[:15]:
        ap_frey = compute_ap(curve_frey_5_27, p)
        ap_30a = compute_ap(curve_30a, p)
        print(f"  p={p:>4d}: a_p(Frey)={ap_frey:>4d}, a_p(30a)={ap_30a:>4d}, "
              f"Ramanujan: |a_p| <= {2*math.sqrt(p):.1f}")

    # Run the full cross-correlation test
    curves_30 = [
        ("Frey", curve_frey_5_27),
        ("30a", curve_30a),
    ]
    run_test(curves_30, level=30, prime_limit=2000)


if __name__ == "__main__":
    main()
