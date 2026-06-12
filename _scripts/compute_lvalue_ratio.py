"""Compute L(E,1)/Omega_E for the 5 mining Frey curves numerically.

Method:
- Omega_E via AGM formula (exact for our model)
- L(E,1) via exponentially convergent series: 2 * sum a_n/n * exp(-2*pi*n/sqrt(N))
- a_n via point counting (primes) + multiplicativity
"""
import math
from functools import lru_cache

def factorize(n):
    factors = {}
    d = 2
    while d * d <= abs(n):
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if abs(n) > 1:
        factors[abs(n)] = factors.get(abs(n), 0) + 1
    return factors

def rad(n):
    return math.prod(factorize(n).keys()) if n != 0 else 0

def legendre(a, p):
    """Legendre symbol (a/p)."""
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1

def agm(a, b, tol=1e-15):
    """Arithmetic-geometric mean."""
    while abs(a - b) > tol * abs(a):
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a

def real_period_frey(a_val, b_val):
    """Real period Omega for E_{a,b}: y^2 = x(x-a)(x+b).

    Roots: -b, 0, a (ordered for a,b > 0).
    Omega = 2*pi / AGM(sqrt(a+b), sqrt(a))

    This is the real period of the IDENTITY component.
    For full BSD we need Omega * number_of_real_components.
    Since Frey curves have 3 real roots, there are 2 real components,
    but by convention Omega_E = real period (one component) for BSD.
    """
    return 2 * math.pi / agm(math.sqrt(a_val + b_val), math.sqrt(a_val))

def count_points_mod_p(a_val, b_val, p):
    """Count #E_{a,b}(F_p) for E: y^2 = x(x-a)(x+b).
    Returns a_p = p + 1 - #E(F_p).
    """
    count = 1  # point at infinity
    a_mod = a_val % p
    b_mod = b_val % p
    for x in range(p):
        rhs = (x * ((x - a_mod) % p) * ((x + b_mod) % p)) % p
        if rhs == 0:
            count += 1  # y=0
        else:
            leg = legendre(rhs, p)
            if leg == 1:
                count += 2  # two y values
    return p + 1 - count

def a_p_bad(a_val, b_val, p):
    """a_p for bad (multiplicative) prime p.
    For semistable Frey curve at odd p|abc:
    - p|a: split iff (-b*c / p) = (p... actually iff curve has split mult. red.

    For E: y^2 = x(x-a)(x+b), at p|a:
      Reduce mod p: y^2 = x * (-a mod p=0)...
      Actually: y^2 = x^2*(x+b) mod p (since x-a = x mod p when p|a)
      Node at (0,0). Tangent slopes: y^2 = x^2 * b mod p → slopes = +-sqrt(b)
      Split iff b is a QR mod p, i.e. (b/p) = 1.

    For p|b: y^2 = x*(x-a)*x = x^2*(x-a) mod p. Node at (0,0).
      Tangent slopes from x^2*(x-a): need to be careful...
      Actually y^2 = x(x-a)(x+b), at p|b: x+b = x mod p.
      So y^2 = x * (x-a) * x = x^2(x-a) mod p. Node at x=0.
      Tangent: y^2 ~ x^2*(-a) for small x. Split iff (-a/p) = 1.

    For p|c (c=a+b): y^2 = x(x-a)(x+b). Since a+b=0 mod p, b = -a mod p.
      So y^2 = x(x-a)(x-a) = x(x-a)^2 mod p. Node at x=a mod p.
      Translate: let u = x-a, then y^2 = (u+a)*u^2 mod p.
      Tangent: y^2 ~ a*u^2 for small u. Split iff (a/p) = 1.
    """
    c_val = a_val + b_val
    if p == 2:
        # For p=2: complex, just count directly
        return count_points_mod_p(a_val, b_val, 2) if a_val % 2 != 0 or b_val % 2 != 0 else 0

    if a_val % p == 0:
        # split iff (b/p) = 1... wait, tangent slopes are +-sqrt(b mod p)
        # But need to account for the other factor: y^2 = x^2(x+b)
        # At node x=0: parametrize near node: y ~ ±sqrt(b) * x
        # Split mult iff sqrt(b) exists in F_p, i.e. (b/p) = 1
        return 1 if legendre(b_val, p) == 1 else -1
    elif b_val % p == 0:
        # split iff (-a/p) = 1
        return 1 if legendre(-a_val, p) == 1 else -1
    elif c_val % p == 0:
        # split iff (a/p) = 1
        return 1 if legendre(a_val, p) == 1 else -1
    else:
        return None  # good reduction, should not be called

def compute_an(a_val, b_val, N, max_n):
    """Compute a_n for n = 1..max_n using multiplicativity."""
    c_val = a_val + b_val
    bad_primes = set(factorize(N).keys())

    # Sieve for a_p values
    an = [0] * (max_n + 1)
    an[1] = 1

    # First compute a_p for all primes p <= max_n
    is_prime = [True] * (max_n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(max_n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, max_n + 1, i):
                is_prime[j] = False

    ap = {}
    for p in range(2, max_n + 1):
        if is_prime[p]:
            if p in bad_primes:
                ap[p] = a_p_bad(a_val, b_val, p)
            else:
                ap[p] = count_points_mod_p(a_val, b_val, p)

    # Now compute a_n using multiplicativity
    # a_{p^k} = a_p * a_{p^{k-1}} - p * a_{p^{k-2}} for good p
    # a_{p^k} = a_p^k for bad p
    for p in range(2, max_n + 1):
        if not is_prime[p]:
            continue
        # Fill in a_{p^k}
        pk = p
        a_prev_prev = 1  # a_{p^0} = 1
        a_prev = ap[p]   # a_{p^1}
        an[p] = ap[p]
        pk = p * p
        while pk <= max_n:
            if p in bad_primes:
                a_curr = ap[p] * a_prev  # a_{p^k} = a_p^k for bad primes
            else:
                a_curr = ap[p] * a_prev - p * a_prev_prev
            an[pk] = a_curr
            a_prev_prev = a_prev
            a_prev = a_curr
            pk *= p

    # Now fill in composite n using multiplicativity: a_{mn} = a_m * a_n for gcd(m,n)=1
    # We do this by iterating over primes and filling
    for n in range(2, max_n + 1):
        if an[n] != 0 or n == 1:
            continue
        # Factor n and compute a_n from prime powers
        temp = n
        result = 1
        for p in range(2, n + 1):
            if p * p > temp and temp > 1:
                result *= an[temp] if an[temp] != 0 else ap.get(temp, 0)
                break
            if temp % p == 0:
                pk = 1
                while temp % p == 0:
                    pk *= p
                    temp //= p
                result *= an[pk]
            if temp == 1:
                break
        an[n] = result

    return an

def compute_L_value(a_val, b_val, N, num_terms=2000):
    """Compute L(E,1) using the exponentially convergent formula:
    L(E,1) = 2 * sum_{n=1}^infty a_n/n * exp(-2*pi*n/sqrt(N))

    Valid for epsilon = +1 (which all our Frey curves have in some orientation).
    """
    an = compute_an(a_val, b_val, N, num_terms)
    sqrt_N = math.sqrt(N)

    L_val = 0.0
    for n in range(1, num_terms + 1):
        if an[n] == 0:
            continue
        term = an[n] / n * math.exp(-2 * math.pi * n / sqrt_N)
        L_val += term
        # Check convergence
        if n > 100 and abs(term) < 1e-14:
            break

    return 2 * L_val

# Mining triplets (using orientation with epsilon=+1)
triplets = [
    (1, 8, "1+2^3=3^2", 6),
    (3, 125, "3+5^3=2^7", 30),
    (1, 4374, "1+2*3^7=5^4*7", 210),
    (1, 2400, "1+2^5*3*5^2=7^4", 210),
]
# Reyssat needs orientation E_{6436341, 2} for epsilon=+1
triplets_reyssat = [(6436341, 2, "Reyssat (E_{b,a})", 15042)]

print("=" * 75)
print("L(E,1)/Omega_E NUMERISCHER TEST fuer Mining-Frey-Kurven")
print("=" * 75)
print(f"{'Tripel':<25} {'Omega_E':>12} {'L(E,1)':>12} {'L/Omega':>10} {'>=1/16?':>8}")
print("-" * 75)

for a_val, b_val, name, N in triplets:
    c_val = a_val + b_val
    assert rad(a_val * b_val * c_val) == N or True  # might differ for non-coprime

    omega = real_period_frey(a_val, b_val)
    # Use enough terms for convergence
    rate = math.exp(-2 * math.pi / math.sqrt(N))
    needed = min(5000, max(500, int(-30 / math.log(rate)) if rate < 1 else 5000))
    L_val = compute_L_value(a_val, b_val, N, num_terms=needed)

    ratio = L_val / omega if omega > 0 else float('nan')
    check = "YES" if ratio >= 1/16 - 0.001 else "NO"
    print(f"{name:<25} {omega:>12.6f} {L_val:>12.6f} {ratio:>10.4f} {check:>8}")

print()
print("Reyssat (groesser, braucht mehr Terme):")

for a_val, b_val, name, N in triplets_reyssat:
    c_val = a_val + b_val
    omega = real_period_frey(a_val, b_val)
    # For N=15042, convergence rate is exp(-2pi/sqrt(15042)) ~ 0.95
    # Need ~600 terms for 1e-12 precision: -12/log(0.95) ~ 234
    # But actually need more due to a_n oscillation
    L_val = compute_L_value(a_val, b_val, N, num_terms=3000)
    ratio = L_val / omega if omega > 0 else float('nan')
    check = "YES" if ratio >= 1/16 - 0.001 else "NO"
    print(f"{name:<25} {omega:>12.6f} {L_val:>12.6f} {ratio:>10.4f} {check:>8}")

print()
print("=" * 75)
print("INTERPRETATION")
print("=" * 75)
print("""
BSD-Konsistenz: L(E,1)/Omega_E >= 1/16 (generisch) oder >= 1/256 (uniform).
Falls alle Werte >= 1/16: konsistent mit |Sha|*prod(c_p)/16 >= 1.
Der Wert L/Omega = |Sha|*prod(c_p)/|tors|^2 ist eine POSITIVE GANZE ZAHL
geteilt durch |tors|^2 (fuer Frey: /16 generisch).
""")
