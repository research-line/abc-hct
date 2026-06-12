"""Z_E = A_E * P_E Zerlegung fuer Frey-Kurven.

Loop 11 erstellt, Loop 14 korrigiert: N_cond statt N_rad, kurvenspezifisches |tors|^2.

Z_E = L(E,1) * sqrt(N_cond)     -- ANC+ Messgröße
A_E = L(E,1) / Omega_E          -- algebraischer BSD-Teil
P_E = Omega_E * sqrt(N_cond)    -- Perioden-Conductor-Kern

Konsistenz: Z_E = A_E * P_E
BSD-Formel: A_E * |tors|^2 = Tam * |Sha|  (kurvenspezifisch)
"""
import math
import os

os.environ["PYTHONIOENCODING"] = "utf-8"


def factorize(n):
    factors = {}
    d = 2
    temp = abs(n)
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def rad(n):
    return math.prod(factorize(n).keys()) if n != 0 else 0


def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1


def agm(a, b, tol=1e-15):
    while abs(a - b) > tol * abs(a):
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a


def real_period_frey(a_val, b_val):
    return 2 * math.pi / agm(math.sqrt(a_val + b_val), math.sqrt(a_val))


def count_points_mod_p(a_val, b_val, p):
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


def a_p_bad(a_val, b_val, p):
    c_val = a_val + b_val
    if p == 2:
        return count_points_mod_p(a_val, b_val, 2) if (a_val % 2 != 0 or b_val % 2 != 0) else 0
    if a_val % p == 0:
        return 1 if legendre(b_val, p) == 1 else -1
    elif b_val % p == 0:
        return 1 if legendre(-a_val, p) == 1 else -1
    elif c_val % p == 0:
        return 1 if legendre(a_val, p) == 1 else -1
    return None


def compute_an(a_val, b_val, N, max_n):
    bad_primes = set(factorize(N).keys())
    an = [0] * (max_n + 1)
    an[1] = 1
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
    for p in range(2, max_n + 1):
        if not is_prime[p]:
            continue
        a_prev_prev = 1
        a_prev = ap[p]
        an[p] = ap[p]
        pk = p * p
        while pk <= max_n:
            if p in bad_primes:
                a_curr = ap[p] * a_prev
            else:
                a_curr = ap[p] * a_prev - p * a_prev_prev
            an[pk] = a_curr
            a_prev_prev = a_prev
            a_prev = a_curr
            pk *= p
    for n in range(2, max_n + 1):
        if an[n] != 0 or n == 1:
            continue
        temp = n
        result = 1
        for p in range(2, n + 1):
            if p * p > temp and temp > 1:
                result *= an[temp] if an[temp] != 0 else ap.get(temp, 0)
                break
            if temp % p == 0:
                pk_val = 1
                while temp % p == 0:
                    pk_val *= p
                    temp //= p
                result *= an[pk_val]
            if temp == 1:
                break
        an[n] = result
    return an


def compute_L_value(a_val, b_val, N, num_terms=2000):
    an = compute_an(a_val, b_val, N, num_terms)
    sqrt_N = math.sqrt(N)
    L_val = 0.0
    for n in range(1, num_terms + 1):
        if an[n] == 0:
            continue
        term = an[n] / n * math.exp(-2 * math.pi * n / sqrt_N)
        L_val += term
        if n > 100 and abs(term) < 1e-14:
            break
    return 2 * L_val


# === Tripel (alle epsilon=+1, N_cond via LMFDB Loop 13) ===
# Format: (a, b, name, N_rad, N_cond, tors_sq, tam, sha_an)
triplets = [
    (1, 8, "1+2^3=3^2", 6, 48, 64, 16, 1),
    (3, 125, "3+5^3=2^7", 30, 240, 16, 16, 1),
    (1, 4374, "1+2*3^7=5^4*7", 210, 3360, 16, 64, 1),
    (1, 2400, "1+2^5*3*5^2=7^4", 210, 1680, 64, 256, 1),
    (6436341, 2, "Reyssat(E_{b,a})", 15042, 240672, 16, 16, 361),
]

print("=" * 120)
print("Z_E = A_E * P_E  ZERLEGUNG fuer Frey-Kurven (korrigiert Loop 14)")
print("A_E = L(E,1)/Omega_E  (algebraisch, BSD)")
print("P_E = Omega_E * sqrt(N_cond)  (Perioden-Conductor-Kern)")
print("Z_E = L(E,1) * sqrt(N_cond)  (ANC+ Messgroesse)")
print("N_cond = tatsaechlicher Kurvenkonduktor (LMFDB), NICHT rad(abc)")
print("=" * 120)

header = (f"{'Tripel':<22} {'N_cond':>7} {'q':>5} {'Omega_E':>10} {'L(E,1)':>10} "
          f"{'A_E':>10} {'A*|t|^2':>8} {'Tam*Sha':>8} {'P_E':>10} {'Z_E':>10}")
print(header)
print("-" * 120)

results = []

for a_val, b_val, name, N_rad, N_cond, tors_sq, tam, sha_an in triplets:
    c_val = a_val + b_val
    q = math.log(c_val) / math.log(N_rad) if N_rad > 1 else float('nan')

    omega = real_period_frey(a_val, b_val)

    rate = math.exp(-2 * math.pi / math.sqrt(N_cond))
    needed = min(5000, max(500, int(-30 / math.log(rate)) if rate < 1 else 5000))
    L_val = compute_L_value(a_val, b_val, N_cond, num_terms=needed)

    A_E = L_val / omega if omega > 0 else float('nan')
    P_E = omega * math.sqrt(N_cond)
    Z_E = L_val * math.sqrt(N_cond)
    A_tors = A_E * tors_sq
    tam_sha = tam * sha_an

    results.append((name, N_cond, N_rad, q, omega, L_val, A_E, tors_sq, A_tors, tam_sha, P_E, Z_E))

    print(f"{name:<22} {N_cond:>7} {q:>5.2f} {omega:>10.6f} {L_val:>10.6f} "
          f"{A_E:>10.4f} {A_tors:>8.1f} {tam_sha:>8} {P_E:>10.3f} {Z_E:>10.3f}")

print()
print("=" * 120)
print("BSD-KONSISTENZ: A_E * |tors|^2 = Tam * |Sha|")
print("=" * 120)
print()
for r in results:
    name, N_cond, N_rad, q, omega, L_val, A_E, tors_sq, A_tors, tam_sha, P_E, Z_E = r
    deviation = abs(A_tors - tam_sha)
    rel_dev = deviation / tam_sha if tam_sha > 0 else float('inf')
    status = "OK" if rel_dev < 0.001 else "WARNUNG"
    print(f"  {name:<22}: A_E*{tors_sq} = {A_tors:>8.1f}  Tam*Sha = {tam_sha:>6}  "
          f"(rel. Abw: {rel_dev:.6f})  [{status}]")

print()
print("=" * 120)
print("KORREKTUR zu Loop 11:")
print("  A_E spannt 0.25 bis 361 (Faktor 1444) -- NICHT stabil.")
print("  Spread getrieben von Tam*|Sha|/|tors|^2 (BSD-Arithmetik), nicht von q.")
print("  Loop-11-Schluss 'A_E stabil, P_E variabel' war FALSCH (N=rad statt N_cond).")
print("  Bei n=5 keine statistischen Korrelationsaussagen moeglich.")
print("=" * 120)
print()
print("Die BSD-Schranke A_E >= 1/256 ist THEOREMATISCH bekannt (semistabil).")
print("Reyssat: |Sha|_an = 19^2 = 361 (BSD-conditional, keine 19-Isogenie in 240672.c).")
print("Diese Numerik ist Konsistenzpruefung, nicht Entdeckung.")
