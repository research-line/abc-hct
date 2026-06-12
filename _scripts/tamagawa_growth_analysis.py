"""Analyze Tamagawa product growth vs N^{1/2} for mining Frey curves.

Key question: Does prod(c_p) grow faster than sqrt(N)?
If yes: A_E = Sha*prod(c_p)/16 > N^{1/2} even for Sha=1,
which means Omega_E = L/A_E < L/sqrt(N) — confirming that the period
shrinks below N^{-1/2} for high-quality triplets BECAUSE of Tamagawa growth.
"""
import math

def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1

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

def tamagawa_at_p(a, b, p):
    """Compute Tamagawa number c_p for E_{a,b} at multiplicative prime p.
    For split multiplicative: c_p = v_p(Delta_min).
    For nonsplit: c_p = 1 if v_p(Delta) odd, 2 if even.
    Delta = 16*a^2*b^2*c^2, so v_p(Delta) = 2*v_p(a) or 2*v_p(b) or 2*v_p(c).
    """
    c = a + b
    if p == 2:
        # Approximate: v_2(Delta) for non-minimal model
        v2 = 4 + 2*factorize(a).get(2,0) + 2*factorize(b).get(2,0) + 2*factorize(c).get(2,0)
        return min(v2, 12)  # rough upper bound, actual value needs Tate algorithm

    if a % p == 0:
        vp = 2 * factorize(a)[p]
        is_split = legendre(b, p) == 1
    elif b % p == 0:
        vp = 2 * factorize(b)[p]
        is_split = legendre(-a, p) == 1
    elif c % p == 0:
        vp = 2 * factorize(c)[p]
        is_split = legendre(a, p) == 1
    else:
        return 1  # good reduction

    if is_split:
        return vp
    else:
        return 2 if vp % 2 == 0 else 1

# Mining triplets
triplets = [
    (1, 8, 9, "1+2^3=3^2"),
    (3, 125, 128, "3+5^3=2^7"),
    (1, 4374, 4375, "1+2*3^7=5^4*7"),
    (1, 2400, 2401, "1+2^5*3*5^2=7^4"),
    (6436341, 2, 6436343, "Reyssat(E_{b,a})"),
]

print("=" * 80)
print("TAMAGAWA-PRODUKT vs sqrt(N): Wachstumsanalyse")
print("=" * 80)
print()
print(f"{'Tripel':<22} {'N':>7} {'sqrt(N)':>8} {'prod_cp':>8} {'ratio':>7} {'A_E_min':>8}")
print("-" * 80)

for item in triplets:
    if len(item) == 4:
        a, b, c, name = item
    else:
        a, b = item[0], item[1]
        c = a + b
        name = item[3]

    N = 1
    for p in factorize(a*b*c).keys():
        N *= p

    # Compute Tamagawa product at all bad primes
    bad_primes = set(factorize(a*b*c).keys())
    prod_cp = 1
    details = []
    for p in sorted(bad_primes):
        cp = tamagawa_at_p(a, b, p)
        prod_cp *= cp
        if cp > 1:
            details.append(f"c_{p}={cp}")

    sqrt_N = math.sqrt(N)
    ratio = prod_cp / sqrt_N
    A_E_min = prod_cp / 16  # minimum A_E assuming Sha=1, |tors|=4

    print(f"{name:<22} {N:>7} {sqrt_N:>8.1f} {prod_cp:>8} {ratio:>7.2f} {A_E_min:>8.1f}")
    print(f"  Detail: {', '.join(details)}")

print()
print("=" * 80)
print("INTERPRETATION")
print("=" * 80)
print("""
Wenn ratio = prod(c_p)/sqrt(N) > 1, dann ueberschreitet das Tamagawa-Produkt
bereits sqrt(N). Das bedeutet:

  A_E = |Sha| * prod(c_p) / |tors|^2 >= prod(c_p)/16 >= sqrt(N)/16

Und damit:
  Omega_E = L(E,1) / A_E <= L(E,1) * 16 / prod(c_p)

Fuer "typischen" L-Wert ~ O(1) (Iwaniec-Sarnak):
  Omega_E <= C / prod(c_p) << 1/sqrt(N)

Das ist GENAU der abc-Defekt: Die Periode ist kleiner als N^{-1/2} weil
das Tamagawa-Produkt groesser als sqrt(N) ist.

ANC+ (L >= c*N^{-1/2-eps}) zusammen mit Omega = L/A sagt:
  c*N^{-1/2-eps} <= L = Omega * A
  => Omega >= c*N^{-1/2-eps}/A >= c*N^{-1/2-eps} * 16/prod(c_p)

Das ist NUR dann >= c'/N^{-1/2-eps} (Periodenuntergrenze) wenn
  prod(c_p) <= C * N^{eps}

Also: abc <=> Tamagawa-Produkt waechst hoechstens polynomial in N^eps!
      (Aequivalent: Summe der Exponenten waechst sublinear in log N)
""")

# Verify: for Reyssat, does prod(c_p) ~ N^{0.5+something}?
print("REYSSAT-DETAIL:")
a, b, c = 6436341, 2, 6436343
N = 2*3*23*109
prod_cp_reyssat = tamagawa_at_p(a,b,3) * tamagawa_at_p(a,b,23) * tamagawa_at_p(a,b,109) * tamagawa_at_p(a,b,2)
print(f"  log(prod_cp)/log(N) = {math.log(prod_cp_reyssat)/math.log(N):.4f}")
print(f"  Zum Vergleich: 1/2 = 0.5000")
print(f"  quality q = log(c)/log(N) = {math.log(c)/math.log(N):.4f}")
print(f"  => Tamagawa-Exponent ~ {math.log(prod_cp_reyssat)/math.log(N):.3f} vs q/2-Erwartung ~ {math.log(c)/(2*math.log(N)):.3f}")
