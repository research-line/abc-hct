"""Loop 13: Conductor-Scan fuer Frey-Kurven.

Testet L(E,1) mit verschiedenen Kandidaten-Conductoren.
BSD-Kriterium: L/Omega * |tors|^2 muss nahe positiver ganzer Zahl sein.
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
            for j in range(i * i, max_n + 1, i):
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


# === VERIFICATION: E_{3,125} with N=240 ===
print("=" * 80)
print("VERIFIKATION: E_{3,125} mit N_cond=240 (LMFDB 240.b3)")
print("=" * 80)
a, b = 3, 125
omega = real_period_frey(a, b)
L_240 = compute_L_value(a, b, 240, num_terms=3000)
A_E = L_240 / omega
print(f"Omega = {omega:.6f}")
print(f"L(E,1) mit N=240: {L_240:.6f}")
print(f"LMFDB erwartet:   1.158392")
print(f"A_E = L/Omega = {A_E:.6f}")
print(f"A_E * 16 (|tors|^2=[2,2]) = {A_E * 16:.3f}")
print(f"BSD-Match: {'JA' if abs(A_E * 16 - round(A_E * 16)) < 0.05 else 'NEIN'}")
print()


# === CONDUCTOR SCAN ===
curves = [
    (1, 4374, "E_{1,4374}", 210),
    (1, 2400, "E_{1,2400}", 210),
]

for a_val, b_val, name, N_rad in curves:
    c_val = a_val + b_val
    omega = real_period_frey(a_val, b_val)

    odd_part = 1
    for p in set(factorize(N_rad).keys()):
        if p > 2:
            odd_part *= p

    print("=" * 80)
    print(f"CONDUCTOR-SCAN: {name}  (a={a_val}, b={b_val}, c={c_val})")
    print(f"  rad(abc) = {N_rad}, odd_part = {odd_part}")
    print(f"  Omega = {omega:.6f}")
    print(f"  Kandidaten: N = {odd_part} * 2^k fuer k=1..8")
    print("-" * 80)
    print(f"  {'N':>8} {'2^k':>5} {'L(E,1)':>12} {'A_E':>10} {'A*16':>8} {'A*64':>8} {'naechste_int':>5} {'Abw':>8} {'Status'}")
    print("-" * 80)

    best_N = None
    best_dev = 999

    for k in range(1, 9):
        N_cand = odd_part * (2 ** k)
        rate = math.exp(-2 * math.pi / math.sqrt(N_cand))
        needed = min(5000, max(500, int(-30 / math.log(rate)) if rate < 1 else 5000))
        L_val = compute_L_value(a_val, b_val, N_cand, num_terms=needed)

        A_E = L_val / omega if omega > 0 else float('nan')
        A16 = A_E * 16
        A64 = A_E * 64

        # Check both |tors|^2 = 16 and 64
        dev16 = abs(A16 - round(A16))
        dev64 = abs(A64 - round(A64))

        if dev16 < dev64:
            near = round(A16)
            dev = dev16
            tors_label = "*16"
        else:
            near = round(A64)
            dev = dev64
            tors_label = "*64"

        status = ""
        if dev < 0.02 and near > 0:
            status = f"<-- BSD CLEAN ({tors_label}={near})"
            if dev < best_dev:
                best_dev = dev
                best_N = N_cand

        print(f"  {N_cand:>8} {2**k:>5} {L_val:>12.6f} {A_E:>10.6f} {A16:>8.3f} {A64:>8.3f} {near:>5} {dev:>8.4f} {status}")

    print()
    if best_N:
        print(f"  BESTER KANDIDAT: N = {best_N} (= {factorize(best_N)})")
    else:
        print(f"  KEIN BSD-CLEAN KANDIDAT gefunden")
    print()
