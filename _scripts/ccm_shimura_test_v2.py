"""
CCM-Shimura Cancellation Test v2
=================================
Extended test on SHIMURA CURVE LEVELS vs standard levels.

Key insight: For D = product of even number of primes, ALL newforms at
level D correspond (via Jacquet-Langlands) to forms on the compact
Shimura curve X_0^D(1). Their Hecke eigenvalues a_p (p nmid D) are
identical. So computing cross-correlations of a_p on X_0(D) IS the
compact Shimura curve test.

SHIMURA LEVELS (all newforms live on compact curve):
  D = 26 = 2*13: genus(X_0^26(1)) = 2, 2 rational newforms
  D = 58 = 2*29: genus(X_0^58(1)) = 2, 2 rational newforms

COMPARISON LEVELS (standard, non-compact):
  N = 37 (prime): dim S_2^new = 2
  N = 57 = 3*19: dim S_2^new = 3

MEASUREMENT:
  C(P) = sum_{p<=P} a_p(f1) * a_p(f2)
  Random walk: |C(P)| ~ P^{3/2}
  CCM signal:  |C(P)| ~ P^{alpha} with alpha < 3/2
"""

import math
import sys
import time

PRIME_LIMIT = 10000

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

def compute_ap(disc_fn, p):
    s = 0
    for x in range(p):
        d = disc_fn(x, p) % p
        s += legendre_symbol(d, p)
    return -s

def make_weierstrass_disc(a1, a2, a3, a4, a6):
    """Return discriminant function for y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6.
    Disc of quadratic in y: (a1*x + a3)^2 + 4*(x^3 + a2*x^2 + a4*x + a6)."""
    c2 = a1*a1 + 4*a2
    c1 = 2*a1*a3 + 4*a4
    c0 = a3*a3 + 4*a6
    def disc(x, p):
        return (4*pow(x, 3, p) + c2*x*x + c1*x + c0) % p
    return disc

# =========================================================================
# CURVE DEFINITIONS (one per isogeny class, from LMFDB/Cremona)
# =========================================================================

# --- SHIMURA LEVEL D = 26 = 2*13 (genus 2, ALL new) ---
CURVES_26 = [
    ("26a", make_weierstrass_disc(1, 0, 1, -5, -8)),   # y^2+xy+y = x^3-5x-8
    ("26b", make_weierstrass_disc(1, -1, 1, -3, 3)),    # y^2+xy+y = x^3-x^2-3x+3
]

# --- SHIMURA LEVEL D = 58 = 2*29 (genus 2 new among 6 total, ALL new) ---
CURVES_58 = [
    ("58a", make_weierstrass_disc(1, -1, 0, -1, 1)),    # y^2+xy = x^3-x^2-x+1
    ("58b", make_weierstrass_disc(1, 1, 1, -455, -3951)),# y^2+xy+y = x^3+x^2-455x-3951
]

# --- COMPARISON: N = 37 (prime, not Shimura disc) ---
CURVES_37 = [
    ("37a", make_weierstrass_disc(0, 0, 1, -1, 0)),     # y^2+y = x^3-x
    ("37b", make_weierstrass_disc(0, 1, 1, -23, -50)),   # y^2+y = x^3+x^2-23x-50
]

# --- COMPARISON: N = 57 = 3*19 (not Shimura, 3 is odd # of primes) ---
CURVES_57 = [
    ("57a", make_weierstrass_disc(0, -1, 1, -2, 2)),    # y^2+y = x^3-x^2-2x+2
    ("57b", make_weierstrass_disc(0, 1, 1, -20, -32)),   # y^2+y = x^3+x^2-20x-32
    ("57c", make_weierstrass_disc(1, -1, 0, -2, 2)),    # y^2+xy = x^3-x^2-2x+2
]

ALL_LEVELS = [
    (26, CURVES_26, True,  "D=2*13, kompakte Shimura-Kurve X_0^26(1), genus 2"),
    (58, CURVES_58, True,  "D=2*29, kompakte Shimura-Kurve X_0^58(1), genus 2"),
    (37, CURVES_37, False, "Prim, X_0(37), genus 2"),
    (57, CURVES_57, False, "3*19, X_0(57), genus 3"),
]

def linear_regression(xs, ys):
    """Least-squares fit y = a*x + b. Returns (a, b, r^2)."""
    n = len(xs)
    if n < 2:
        return (0, 0, 0)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x*x for x in xs)
    sxy = sum(x*y for x, y in zip(xs, ys))
    denom = n*sxx - sx*sx
    if abs(denom) < 1e-15:
        return (0, 0, 0)
    a = (n*sxy - sx*sy) / denom
    b = (sy - a*sx) / n
    ss_tot = sum((y - sy/n)**2 for y in ys)
    ss_res = sum((y - a*x - b)**2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    return (a, b, r2)

def compute_alpha(primes_used, cumulative_abs, label=""):
    """Compute growth exponent alpha from log-log regression of |C(P)| vs P.
    Uses multiple windows for stability assessment."""
    log_p = []
    log_c = []
    for p, c in zip(primes_used, cumulative_abs):
        if c > 0 and p > 10:
            log_p.append(math.log(p))
            log_c.append(math.log(c))

    if len(log_p) < 5:
        return None

    n = len(log_p)
    full_a, full_b, full_r2 = linear_regression(log_p, log_c)

    # Second half
    h = n // 2
    half_a, half_b, half_r2 = linear_regression(log_p[h:], log_c[h:])

    # Last quarter
    q = 3 * n // 4
    quarter_a, quarter_b, quarter_r2 = linear_regression(log_p[q:], log_c[q:])

    return {
        "full": (full_a, full_r2),
        "half": (half_a, half_r2),
        "quarter": (quarter_a, quarter_r2),
    }

def run_level(level, curves, is_shimura, description, prime_limit):
    """Run the full CCM test for one level."""
    primes = sieve_primes(prime_limit)
    good_primes = [p for p in primes if p > 2 and level % p != 0]

    labels = [c[0] for c in curves]
    fns = [c[1] for c in curves]
    n_curves = len(curves)

    shimura_tag = "SHIMURA" if is_shimura else "STANDARD"

    print(f"\n{'='*90}")
    print(f"LEVEL N = {level} [{shimura_tag}] -- {description}")
    print(f"{n_curves} Neuformen, {len(good_primes)} Primzahlen bis {prime_limit}")
    print(f"{'='*90}")

    t0 = time.time()
    ap_data = {label: [] for label in labels}
    for idx, p in enumerate(good_primes):
        for label, fn in zip(labels, fns):
            ap_data[label].append(compute_ap(fn, p))
        if (idx + 1) % 200 == 0:
            elapsed = time.time() - t0
            print(f"  ... {idx+1}/{len(good_primes)} Primzahlen berechnet ({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Berechnung abgeschlossen in {elapsed:.1f}s")

    # Checkpoints
    checkpoints = [100, 200, 500, 1000, 2000, 3000, 5000, 7000, 10000, 15000, 20000]
    checkpoints = [c for c in checkpoints if c <= prime_limit]

    # Cross-correlations
    pairs = [(i, j) for i in range(n_curves) for j in range(i+1, n_curves)]
    results = []

    for i, j in pairs:
        l1, l2 = labels[i], labels[j]
        ap1 = ap_data[l1]
        ap2 = ap_data[l2]

        # Build cumulative cross-correlation at each prime
        cum_cross = []
        running = 0
        for k in range(len(good_primes)):
            running += ap1[k] * ap2[k]
            cum_cross.append(running)

        # Rankin-Selberg partial L-value
        cum_rs = []
        running_rs = 0.0
        for k in range(len(good_primes)):
            running_rs += ap1[k] * ap2[k] / good_primes[k]
            cum_rs.append(running_rs)

        print(f"\n  --- Paar ({l1}, {l2}) ---")
        print(f"  {'P':>6} {'#primes':>7} {'C(P)':>12} {'|C|':>10} {'P^1.5':>10} {'Ratio':>8} {'L_RS':>10}")
        print("  " + "-" * 72)

        for cp in checkpoints:
            idx = sum(1 for p in good_primes if p <= cp) - 1
            if idx < 0:
                continue
            p_max = good_primes[idx]
            c_val = cum_cross[idx]
            abs_c = abs(c_val)
            p15 = p_max ** 1.5
            ratio = abs_c / p15 if p15 > 0 else 0
            n_primes = idx + 1
            rs_val = cum_rs[idx]
            print(f"  {p_max:>6d} {n_primes:>7d} {c_val:>12.0f} {abs_c:>10.0f} {p15:>10.0f} {ratio:>8.4f} {rs_val:>10.3f}")

        # Growth exponent analysis
        sample_primes = []
        sample_abs = []
        for k in range(len(good_primes)):
            if good_primes[k] >= 50:
                sample_primes.append(good_primes[k])
                sample_abs.append(abs(cum_cross[k]))

        alpha = compute_alpha(sample_primes, sample_abs, f"({l1},{l2})")

        if alpha:
            a_full, r2_full = alpha["full"]
            a_half, r2_half = alpha["half"]
            a_quarter, r2_quarter = alpha["quarter"]

            verdict = "KEINE Cancellation"
            if a_full < 1.35 and r2_full > 0.8:
                verdict = "MODERATE Cancellation"
            if a_full < 1.0 and r2_full > 0.8:
                verdict = "STARKE Cancellation"
            if r2_full < 0.5:
                verdict = "INSTABIL (schlechter Fit)"

            print(f"\n  WACHSTUMSEXPONENT alpha (|C(P)| ~ P^alpha):")
            print(f"    Gesamt:       alpha = {a_full:.4f}  (R² = {r2_full:.4f})")
            print(f"    2. Hälfte:    alpha = {a_half:.4f}  (R² = {r2_half:.4f})")
            print(f"    Letztes 1/4:  alpha = {a_quarter:.4f}  (R² = {r2_quarter:.4f})")
            print(f"    Random Walk = 1.5000")
            print(f"    --> {verdict}")

            results.append({
                "pair": f"({l1},{l2})",
                "alpha_full": a_full,
                "r2_full": r2_full,
                "alpha_half": a_half,
                "r2_half": r2_half,
                "alpha_quarter": a_quarter,
                "verdict": verdict,
                "rs_final": cum_rs[-1],
            })

    return results

def main():
    prime_limit = PRIME_LIMIT
    if len(sys.argv) > 1:
        prime_limit = int(sys.argv[1])

    print("=" * 90)
    print("CCM-SHIMURA CANCELLATION TEST v2")
    print("Vergleich: Kompakte Shimura-Kurven vs. Standard-Modulkurven")
    print(f"Primbereich: bis {prime_limit}")
    print("=" * 90)
    print()
    print("THEORIE:")
    print("  Auf X_0^D(M) (kompakt): Kreuzterme = abc-Gap = sqrt(N)-Verlust")
    print("  CCM-Hypothese: Poisson-Rayleigh-Cancellation reduziert Kreuzterme")
    print("  Test: Waechst |C(P)| = |sum a_p(f1)*a_p(f2)| wie P^alpha?")
    print("    alpha = 1.5: Random Walk (keine Cancellation)")
    print("    alpha < 1.5: Extra-Cancellation (CCM-Signal)")
    print("    alpha < 1.0: Starke Cancellation")
    print()
    print("SHIMURA-LEVEL-EIGENSCHAFT:")
    print("  Bei D = 2*13 = 26 und D = 2*29 = 58 sind ALLE Neuformen")
    print("  JL-Transfers von der kompakten Shimura-Kurve X_0^D(1).")
    print("  Die Kreuzkorrelation ihrer a_p IST der Shimura-Kurven-Test.")

    all_results = {}
    t_total = time.time()

    for level, curves, is_shimura, desc in ALL_LEVELS:
        results = run_level(level, curves, is_shimura, desc, prime_limit)
        all_results[level] = (is_shimura, results)

    # =====================================================================
    # GRAND SUMMARY
    # =====================================================================
    print(f"\n{'='*90}")
    print("GESAMTÜBERSICHT")
    print(f"{'='*90}")
    print()
    print(f"{'Level':>5} {'Typ':>8} {'Paar':>12} {'alpha_full':>11} {'R²':>6} "
          f"{'alpha_half':>11} {'R²':>6} {'alpha_1/4':>10} {'Verdict':>25}")
    print("-" * 105)

    shimura_alphas = []
    standard_alphas = []

    for level, (is_shimura, results) in sorted(all_results.items()):
        typ = "SHIMURA" if is_shimura else "STANDARD"
        for r in results:
            alpha_f = r["alpha_full"]
            r2_f = r["r2_full"]
            alpha_h = r["alpha_half"]
            r2_h = r["r2_half"]
            alpha_q = r["alpha_quarter"]
            v = r["verdict"]
            print(f"{level:>5d} {typ:>8} {r['pair']:>12} {alpha_f:>11.4f} {r2_f:>6.3f} "
                  f"{alpha_h:>11.4f} {r2_h:>6.3f} {alpha_q:>10.4f} {v:>25}")
            if is_shimura and r2_f > 0.5:
                shimura_alphas.append(alpha_f)
            elif not is_shimura and r2_f > 0.5:
                standard_alphas.append(alpha_f)

    print()
    if shimura_alphas:
        avg_s = sum(shimura_alphas) / len(shimura_alphas)
        print(f"  Shimura-Levels:  mittleres alpha = {avg_s:.4f}  (n={len(shimura_alphas)})")
    if standard_alphas:
        avg_st = sum(standard_alphas) / len(standard_alphas)
        print(f"  Standard-Levels: mittleres alpha = {avg_st:.4f}  (n={len(standard_alphas)})")
    print(f"  Random Walk (Nullhypothese): alpha = 1.5000")

    print(f"\n  Gesamtlaufzeit: {time.time() - t_total:.1f}s")

    print()
    print("INTERPRETATION:")
    print("  Falls Shimura-alpha < Standard-alpha: Kompakte Geometrie hilft")
    print("  Falls Shimura-alpha ~ 1.5: CCM-Cancellation nicht sichtbar")
    print("  Falls BEIDE < 1.5: Universelle Cancellation (nicht Shimura-spezifisch)")
    print()
    print("CAVEAT: alpha-Messung ist empfindlich auf Primbereich.")
    print("Stabilitaet pruefen via R^2 und Konsistenz full/half/quarter.")

if __name__ == "__main__":
    main()
