"""Keating-Snaith z-Score fuer Frey-Kurven L-Werte.

Loop 10 erstellt, Loop 14 korrigiert: N_cond statt N_rad.

Frage: Korreliert abc-Qualitaet q mit anomal kleinem L-Wert (z<<0)?
KS-Vorhersage: log|L(f,1)| ~ N(-(1/2) log log N, log log N)
z-Score: z = (log|L(f,1)| + (1/2) log log N) / sqrt(log log N)
"""
import math
import os
import sys

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


# === Tripel-Datensatz (alle mit epsilon=+1, N_cond via LMFDB Loop 13) ===
# Format: (a, b, name, N_rad, N_cond)
triplets = [
    (1, 8, "1+2^3=3^2", 6, 48),
    (3, 125, "3+5^3=2^7", 30, 240),
    (1, 4374, "1+2*3^7=5^4*7", 210, 3360),
    (1, 2400, "1+2^5*3*5^2=7^4", 210, 1680),
    (6436341, 2, "Reyssat(E_{b,a})", 15042, 240672),
]

print("=" * 100)
print("KEATING-SNAITH z-SCORE ANALYSE fuer Frey-Kurven (korrigiert Loop 14)")
print("KS-Vorhersage: log|L(f,1)| ~ N(-(1/2) log log N, log log N)")
print("z = (log|L| + 0.5*log(log N_cond)) / sqrt(log(log N_cond))")
print("N_cond = tatsaechlicher Kurvenkonduktor (LMFDB), NICHT rad(abc)")
print("=" * 100)

header = f"{'Tripel':<22} {'N_cond':>7} {'q':>5} {'L(E,1)':>12} {'log|L|':>8} {'KS_mu':>8} {'KS_sig':>7} {'z':>7}"
print(header)
print("-" * 100)

results = []

for a_val, b_val, name, N_rad, N_cond in triplets:
    c_val = a_val + b_val
    q = math.log(c_val) / math.log(N_rad) if N_rad > 1 else float('nan')

    rate = math.exp(-2 * math.pi / math.sqrt(N_cond))
    needed = min(5000, max(500, int(-30 / math.log(rate)) if rate < 1 else 5000))
    L_val = compute_L_value(a_val, b_val, N_cond, num_terms=needed)

    log_L = math.log(abs(L_val)) if abs(L_val) > 1e-50 else -999

    log_log_N = math.log(math.log(N_cond)) if N_cond > 1 else 0
    ks_mu = -0.5 * log_log_N
    ks_sigma = math.sqrt(abs(log_log_N)) if log_log_N > 0 else 0.01
    z_score = (log_L - ks_mu) / ks_sigma if ks_sigma > 0.01 else float('nan')

    results.append((name, N_cond, q, L_val, log_L, ks_mu, ks_sigma, z_score))

    print(f"{name:<22} {N_cond:>7} {q:>5.2f} {L_val:>12.6f} {log_L:>8.3f} {ks_mu:>8.3f} {ks_sigma:>7.3f} {z_score:>7.2f}")

print()
print("=" * 100)
print("INTERPRETATION")
print("=" * 100)
print()
print("z ~ 0:  L-Wert nahe KS-Mittelwert (generisch)")
print("z << 0: L-Wert anomal klein (Anomalie-Hinweis)")
print("z >> 0: L-Wert anomal gross")
print()
print("ACHTUNG: Reyssat hat |Sha|_an = 361, d.h. L(E,1) ist 361x groesser als")
print("bei Sha=1. z-Score wird dadurch stark nach oben verschoben (contra Anomalie).")
print()

qs = [r[2] for r in results if not math.isnan(r[7])]
zs = [r[7] for r in results if not math.isnan(r[7])]
if len(qs) >= 3:
    q_mean = sum(qs) / len(qs)
    z_mean = sum(zs) / len(zs)
    cov = sum((q - q_mean) * (z - z_mean) for q, z in zip(qs, zs)) / len(qs)
    q_std = math.sqrt(sum((q - q_mean)**2 for q in qs) / len(qs))
    z_std = math.sqrt(sum((z - z_mean)**2 for z in zs) / len(zs))
    corr = cov / (q_std * z_std) if q_std > 0 and z_std > 0 else 0
    print(f"Pearson-Korrelation q vs z: r = {corr:.4f}  (n={len(qs)})")
    print(f"  q-Bereich: [{min(qs):.3f}, {max(qs):.3f}]")
    print(f"  z-Bereich: [{min(zs):.2f}, {max(zs):.2f}]")
    print("  WARNUNG: n=5 ist zu klein fuer statistisch signifikante Korrelation.")
else:
    print("Zu wenige Datenpunkte fuer Korrelationstest")

print()
print("Caveat: n=5 reicht NICHT fuer Hypothesentests. Dies ist Konsistenzpruefung.")
print("Reyssat (N_cond=240672, q=1.63): z-Score durch |Sha|=361 dominiert, nicht durch q.")
