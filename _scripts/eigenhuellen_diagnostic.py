"""Compute Phi(T) overflow diagnostic for all 5 mining triplets.
Also compute Stern-Brocot parents for Reyssat lambda = a/c.
"""
import math
from fractions import Fraction

def factorize(n):
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
    return math.prod(factorize(n).keys())

def compute_u(abc_product):
    factors = factorize(abc_product)
    u = 1
    for p, e in factors.items():
        u *= p ** (e // 6)
    return u

def phi_overflow(a, b, c):
    N = rad(a * b * c)
    u = compute_u(a * b * c)
    phi = math.log(c) - math.log(N) - 2 * math.log(u) if u > 0 else math.log(c) - math.log(N)
    return phi, N, u

def stern_brocot_parents(a, c):
    frac = Fraction(a, c)
    num, den = frac.numerator, frac.denominator
    cf = []
    n, d = num, den
    while d != 0:
        cf.append(n // d)
        n, d = d, n % d
    h = [0, 1]
    k = [1, 0]
    for ai in cf:
        h.append(ai * h[-1] + h[-2])
        k.append(ai * k[-1] + k[-2])
    if len(cf) >= 2:
        left_num = h[-3]
        left_den = k[-3]
        right_num = h[-2] - h[-3] if cf[-1] > 1 else h[-4]
        right_den = k[-2] - k[-3] if cf[-1] > 1 else k[-4]
    else:
        left_num, left_den = 0, 1
        right_num, right_den = 1, 0
    return (left_num, left_den), (right_num, right_den), cf

triplets = [
    (1, 8, 9, "1+2^3=3^2"),
    (3, 125, 128, "3+5^3=2^7"),
    (1, 4374, 4375, "1+2*3^7=5^4*7"),
    (2, 6436341, 6436343, "2+3^10*109=23^5 (Reyssat)"),
    (1, 2400, 2401, "1+2^5*3*5^2=7^4"),
]

print("=" * 70)
print("EIGENHUELLEN-DIAGNOSTIK: Phi(T) fuer Mining-Tripel")
print("=" * 70)
print(f"{'Tripel':<30} {'Phi':>8} {'N':>8} {'u':>6} {'Status':<15}")
print("-" * 70)

for a, b, c, name in triplets:
    assert a + b == c, f"Not a valid triplet: {a}+{b}!={c}"
    phi, N, u = phi_overflow(a, b, c)
    q = math.log(c) / math.log(N) if N > 1 else 0
    status = "OVERFLOW" if phi > 0 else "STABLE"
    print(f"{name:<30} {phi:>8.3f} {N:>8} {u:>6} {status:<15} q={q:.4f}")

print()
print("=" * 70)
print("STERN-BROCOT-ANALYSE: Reyssat lambda = 2/6436343")
print("=" * 70)

a_r, c_r = 2, 6436343
parents_l, parents_r, cf = stern_brocot_parents(a_r, c_r)
print(f"lambda = {a_r}/{c_r}")
print(f"Continued fraction: {cf[:10]}{'...' if len(cf) > 10 else ''}")
print(f"Left parent:  {parents_l[0]}/{parents_l[1]}")
print(f"Right parent: {parents_r[0]}/{parents_r[1]}")
print()

med_num = parents_l[0] + parents_r[0]
med_den = parents_l[1] + parents_r[1]
print(f"Mediant check: ({parents_l[0]}+{parents_r[0]})/({parents_l[1]}+{parents_r[1]}) = {med_num}/{med_den}")
print(f"Expected: {a_r}/{c_r}")
print(f"Match: {Fraction(med_num, med_den) == Fraction(a_r, c_r)}")
print()

if parents_l[1] > 0:
    a_L, c_L = parents_l[0], parents_l[1]
    b_L = c_L - a_L
    if b_L > 0 and a_L > 0:
        phi_L, N_L, u_L = phi_overflow(a_L, b_L, c_L)
        print(f"Left parent triplet: ({a_L}, {b_L}, {c_L})")
        print(f"  Phi_L = {phi_L:.3f}, N_L = {N_L}, u_L = {u_L}")
    else:
        print(f"Left parent triplet: ({a_L}, {b_L}, {c_L}) -- DEGENERATE")

if parents_r[1] > 0:
    a_R, c_R = parents_r[0], parents_r[1]
    b_R = c_R - a_R
    if b_R > 0 and a_R > 0:
        phi_R, N_R, u_R = phi_overflow(a_R, b_R, c_R)
        print(f"Right parent triplet: ({a_R}, {b_R}, {c_R})")
        print(f"  Phi_R = {phi_R:.3f}, N_R = {N_R}, u_R = {u_R}")
    else:
        print(f"Right parent triplet: ({a_R}, {b_R}, {c_R}) -- DEGENERATE or trivial")

print()
print("=" * 70)
print("KRITISCHE BEWERTUNG")
print("=" * 70)
print("""
1. Phi(T) ist eine REFORMULIERUNG von abc, nicht ein neuer Beweisansatz.
   abc <=> Phi(T) <= eps*log(N) + C_eps fuer alle T.

2. Stern-Brocot-Eltern eines abc-Tripels sind i.A. KEINE abc-Tripel.
   Die Elternbrueche a_L/c_L haben keinen Grund, a_L + b_L = c_L mit
   besonderer arithmetischer Struktur zu erfuellen.

3. Das Discharging ist als HEURISTIK nuetzlich (Diagnostik), aber der
   induktive Schluss scheitert, weil E_new (neue Radical-Entropie)
   nicht kontrollierbar ist ohne abc vorauszusetzen.

4. POSITIV: Die Phi-Diagnostik ist ein schneller Gesundheitscheck
   fuer neue Tripel und klassifiziert den Schwierigkeitsgrad.
""")
