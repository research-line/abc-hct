"""Compute L(E,1)/Omega_E for mining Frey curves — v2 with correct conductors.

Key fix: (1,8,9) has conductor 36 (additive at 2,3), NOT 6.
For additive primes: a_p = 0.
For multiplicative primes: a_p = +1 (split) or -1 (nonsplit).
"""
import math

def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1

def agm_val(a, b, tol=1e-15):
    while abs(a - b) > tol * abs(a):
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a

def real_period_frey(a_val, b_val):
    """Real period for E_{a,b}: y^2 = x(x-a)(x+b), a,b > 0.
    Omega = 2*pi / AGM(sqrt(a+b), sqrt(a)).
    Note: for curves with 2 real components (3 real roots, which is always
    the case here), the BSD period is Omega_+ (the real period of the
    identity component). Some references use 2*Omega for the full real locus.
    We use Omega = 2*pi/AGM(sqrt(c), sqrt(a)) which gives one component.
    """
    return 2 * math.pi / agm_val(math.sqrt(a_val + b_val), math.sqrt(a_val))

def count_points_mod_p(a_val, b_val, p):
    """Count #E(F_p) for E: y^2 = x(x-a)(x+b). Returns a_p = p+1-#E."""
    count = 1
    a_mod = a_val % p
    b_mod = b_val % p
    for x in range(p):
        rhs = (x * ((x - a_mod) % p) * ((x + b_mod) % p)) % p
        if rhs == 0:
            count += 1
        else:
            if legendre(rhs, p) == 1:
                count += 2
    return p + 1 - count

def get_reduction_type(a_val, b_val, p, conductor_exp):
    """Determine a_p at a bad prime.
    conductor_exp = 1: multiplicative; conductor_exp >= 2: additive (a_p=0).
    For multiplicative: determine split/nonsplit.
    """
    if conductor_exp >= 2:
        return 0  # additive

    c_val = a_val + b_val
    if a_val % p == 0:
        return 1 if legendre(b_val, p) == 1 else -1
    elif b_val % p == 0:
        return 1 if legendre(-a_val, p) == 1 else -1
    elif c_val % p == 0:
        return 1 if legendre(a_val, p) == 1 else -1
    return 0

def compute_an_array(a_val, b_val, bad_primes_dict, max_n):
    """Compute a_n for n=1..max_n.
    bad_primes_dict: {p: conductor_exponent} for bad primes.
    """
    # Sieve primes
    is_prime = [True] * (max_n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(max_n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, max_n + 1, i):
                is_prime[j] = False

    # Compute a_p for all primes
    ap = {}
    for p in range(2, max_n + 1):
        if not is_prime[p]:
            continue
        if p in bad_primes_dict:
            ap[p] = get_reduction_type(a_val, b_val, p, bad_primes_dict[p])
        else:
            ap[p] = count_points_mod_p(a_val, b_val, p)

    # Build a_n via prime powers then multiplicativity
    # a_{p^k}: good p: a_{p^k} = a_p*a_{p^{k-1}} - p*a_{p^{k-2}}
    #          bad p (mult, f_p=1): a_{p^k} = (a_p)^k
    #          bad p (add, f_p>=2): a_{p^k} = 0 for k>=1
    an = [0] * (max_n + 1)
    an[1] = 1

    # Store a_{p^k} for each prime
    apk = {}  # apk[(p,k)] = a_{p^k}
    for p in range(2, max_n + 1):
        if not is_prime[p]:
            continue
        apk[(p, 0)] = 1
        apk[(p, 1)] = ap[p]
        an[p] = ap[p]

        pk = p * p
        k = 2
        while pk <= max_n:
            if p in bad_primes_dict:
                if bad_primes_dict[p] >= 2:
                    apk[(p, k)] = 0
                else:
                    apk[(p, k)] = ap[p] ** k
            else:
                apk[(p, k)] = ap[p] * apk[(p, k-1)] - p * apk[(p, k-2)]
            an[pk] = apk[(p, k)]
            pk *= p
            k += 1

    # Fill composite n by multiplicativity
    for n in range(2, max_n + 1):
        if an[n] != 0:
            continue
        # Factor n into prime powers
        temp = n
        result = 1
        for p in range(2, max_n + 1):
            if not is_prime[p]:
                continue
            if p * p > temp:
                if temp > 1:
                    result *= ap.get(temp, 0)
                break
            if temp % p == 0:
                k = 0
                pk = 1
                while temp % p == 0:
                    temp //= p
                    k += 1
                    pk *= p
                result *= apk.get((p, k), 0)
            if temp == 1:
                break
        an[n] = result

    return an

def compute_L_at_1(a_val, b_val, bad_primes_dict, N, num_terms=2000):
    """L(E,1) = 2 * sum a_n/n * exp(-2*pi*n/sqrt(N)) for epsilon=+1."""
    an = compute_an_array(a_val, b_val, bad_primes_dict, num_terms)
    sqrt_N = math.sqrt(N)
    decay = 2 * math.pi / sqrt_N

    L_val = 0.0
    for n in range(1, num_terms + 1):
        if an[n] == 0:
            continue
        term = an[n] / n * math.exp(-decay * n)
        L_val += term

    return 2 * L_val

# === Mining triplets with CORRECT conductors ===
# Format: (a, b, name, conductor, bad_primes_dict)
curves = [
    # (1,8,9): E_{1,8}, conductor 36 = 2^2 * 3^2. Additive at 2 AND 3.
    (1, 8, "1+2^3=3^2", 36, {2: 2, 3: 2}),

    # (3,125,128): E_{3,125}, conductor 30 = 2*3*5. Semistable (mult at 2,3,5).
    (3, 125, "3+5^3=2^7", 30, {2: 1, 3: 1, 5: 1}),

    # (1,4374,4375): E_{1,4374}, conductor 210 = 2*3*5*7. Semistable.
    # 4374 = 2*3^7, 4375 = 5^4*7. Bad primes: 2,3,5,7.
    (1, 4374, "1+2*3^7=5^4*7", 210, {2: 1, 3: 1, 5: 1, 7: 1}),

    # (1,2400,2401): E_{1,2400}, conductor 210. 2400=2^5*3*5^2, 2401=7^4.
    (1, 2400, "1+2^5*3*5^2=7^4", 210, {2: 1, 3: 1, 5: 1, 7: 1}),

    # Reyssat E_{6436341,2}: conductor 15042 = 2*3*109*23. Semistable.
    (6436341, 2, "Reyssat(E_{b,a})", 15042, {2: 1, 3: 1, 23: 1, 109: 1}),
]

print("=" * 78)
print("L(E,1)/Omega_E — KORRIGIERTE Berechnung (korrekte Konduktoren)")
print("=" * 78)
print(f"{'Tripel':<22} {'N':>6} {'Omega':>10} {'L(E,1)':>10} {'L/Omega':>9} {'BSD?':>5}")
print("-" * 78)

results = []
for a_val, b_val, name, N, bad_dict in curves:
    omega = real_period_frey(a_val, b_val)

    # Determine number of terms needed
    rate = math.exp(-2 * math.pi / math.sqrt(N))
    if rate < 0.99:
        needed = min(5000, max(500, int(-30 / math.log(rate))))
    else:
        needed = 5000  # slow convergence (Reyssat)

    L_val = compute_L_at_1(a_val, b_val, bad_dict, N, num_terms=needed)
    ratio = L_val / omega if omega > 0 else float('nan')

    # BSD predicts: L/Omega = |Sha|*prod(c_p)/|tors|^2 which should be rational
    # For Frey: |tors| = 4 generically, so L/Omega should be k/16 for integer k
    bsd_check = "OK" if ratio > 1/256 else "FAIL"
    results.append((name, N, omega, L_val, ratio))
    print(f"{name:<22} {N:>6} {omega:>10.6f} {L_val:>10.6f} {ratio:>9.4f} {bsd_check:>5}")

print()
print("=" * 78)
print("ANALYSE")
print("=" * 78)
for name, N, omega, L_val, ratio in results:
    # Check if ratio is close to k/16 for some integer k
    approx_k = ratio * 16
    nearest_k = round(approx_k)
    err = abs(approx_k - nearest_k)
    rational_note = f"  ~ {nearest_k}/16" if err < 0.05 else f"  ({approx_k:.2f}/16, nicht ganzzahlig)"
    print(f"  {name}: L/Omega = {ratio:.6f}{rational_note}")

print()
print("LEGENDE:")
print("  BSD OK = L/Omega >= 1/256 (uniforme Untergrenze aus Audit)")
print("  Rational ~ k/16 deutet auf |Sha|*prod(c_p) = k (fuer |tors|=4)")
print("  Fuer |tors|=2*4=8 waere es k/64, etc.")
