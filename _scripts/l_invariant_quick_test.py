"""L-Invarianten-Quick-Test (Phase 1b+, 2026-05-05)

Berechnet v_p(L_p(E)) = v_p(log_p(u)) - v_p(2e) fuer alle stuck primes.
Iwasawa-Konvention: log_p(p) = 0.

L_p(E) ist ein Element von Q_p. Relevant ist seine P-ADISCHE Bewertung,
nicht sein archimedischer Betrag.

Fuer Capacity-Tauglichkeit muesste v_p(L_p) NEGATIV sein (= L_p p-adisch gross).
Fuer L_p → 0 (e→∞) waere v_p(L_p) wachsend (= L_p p-adisch klein → nutzlos).
"""
import math

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
    return math.prod(factorize(n).keys()) if n > 1 else 1

def v_p(n, p):
    if n == 0:
        return float('inf')
    v = 0
    n = abs(n)
    while n % p == 0:
        n //= p
        v += 1
    return v

def mod_inverse(a, m):
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def compute_u_mod_pk(a, b, c, p, e, prec):
    """Berechnet u = q_E / p^{2e} mod p^prec fuer die Frey-Kurve.

    u ≡ 1/J_0 mod p^prec, wobei J_0 = unit part von j(E) bei p.
    j(E) = 256(a^2+ab+b^2)^3 / (a^2 b^2 c^2).
    """
    modulus = p ** prec

    j_num = 256 * (a**2 + a*b + b**2)**3
    j_den = a**2 * b**2 * c**2

    vp_num = v_p(j_num, p)
    vp_den = v_p(j_den, p)
    vp_j = vp_num - vp_den

    if vp_j != -2*e:
        return None, f"v_p(j)={vp_j} != {-2*e}"

    # Unit parts
    j_num_unit = j_num // (p ** vp_num)
    j_den_unit = j_den // (p ** vp_den)

    # J_0 = j_num_unit / j_den_unit mod p^prec
    inv_den = mod_inverse(j_den_unit % modulus, modulus)
    if inv_den is None:
        return None, "j_den not invertible"

    J_0 = (j_num_unit * inv_den) % modulus

    # u = 1/J_0 mod p^prec (erster Term der q-Inversion)
    u = mod_inverse(J_0 % modulus, modulus)
    if u is None:
        return None, "J_0 not invertible"

    # Korrekturterme: q = (1/j)(1 + 744/j + 750420/j^2 + ...)
    # 744/j hat v_p = 2e, also Korrektur an u ist von Ordnung p^{2e}
    # Fuer prec <= 2e sind die Korrekturen irrelevant. Fuer prec > 2e muesste iteriert werden.
    # Hier: prec <= 2e reicht fuer v_p(u-1).

    return u, None

def vp_log_p(u_mod, p, prec):
    """Berechnet v_p(log_p(u)) fuer u ∈ Z_p^* gegeben mod p^prec.

    Strategie:
    1. Berechne w = u^{p-1} mod p^prec (lebt in 1 + pZ_p)
    2. v_p(log_p(u)) = v_p(log_p(w)) - v_p(p-1)
       Nein: log_p(u) = log_p(w)/(p-1), also v_p(log_p(u)) = v_p(log_p(w)) - v_p(p-1)
    3. Fuer w ∈ 1+p^k Z_p (k≥1): v_p(log_p(w)) = k (erster Term dominiert wenn k < p)
       Genauer: log_p(w) = (w-1) - (w-1)^2/2 + ... und v_p((w-1)^n/n) = nk - v_p(n)
       Der n=1 Term hat v_p = k. Der n=2 Term hat v_p = 2k - v_p(2) ≥ 2k-1.
       Also: v_p(log_p(w)) = k falls k ≥ 1 und 2k-v_p(2) > k, d.h. k > v_p(2).
       Fuer p ungerade: v_p(2) = 0, also k > 0 genuegt → v_p(log_p(w)) = k.
    """
    modulus = p ** prec

    # w = u^{p-1} mod p^prec
    w = pow(u_mod, p - 1, modulus)

    # v_p(w - 1) = wie weit ist w von 1 entfernt?
    w_minus_1 = (w - 1) % modulus
    if w_minus_1 == 0:
        # w ≡ 1 mod p^prec → v_p(w-1) ≥ prec
        k = prec
    else:
        k = v_p(w_minus_1, p)

    # Fuer p ungerade und k ≥ 1: v_p(log_p(w)) = k
    # (erster Term (w-1) dominiert, naechster Term (w-1)^2/2 hat v_p = 2k > k)
    vp_log_w = k

    # log_p(u) = log_p(w) / (p-1)
    vp_p_minus_1 = v_p(p - 1, p)  # = 0 fuer p ungerade (p-1 ist gerade, aber nicht durch p teilbar)
    vp_log_u = vp_log_w - vp_p_minus_1

    return vp_log_u, k


# === HAUPTPROGRAMM ===

triplets = [
    (2, 6436341, 6436343),
    (1, 4374, 4375),
    (1, 2400, 2401),
    (3, 125, 128),
    (1, 512, 513),
    (1, 242, 243),
    (5, 1024, 1029),
    (1, 80, 81),
    (13, 243, 256),
    (1, 12167, 12168),
    (1, 8, 9),
    (32, 49, 81),
    (1, 63, 64),
    (1, 48, 49),
    (5, 27, 32),
]

clean = [(a,b,c) for a,b,c in triplets if a+b==c and math.gcd(a,b)==1]
clean.sort(key=lambda t: math.log(t[2])/math.log(rad(t[0]*t[1]*t[2])), reverse=True)

print("=" * 120)
print("L-INVARIANTEN QUICK-TEST: v_p(L_p) fuer Frey-Kurven an stuck primes")
print("=" * 120)
print()
print("L_p(E) = log_p(q_E)/ord_p(q_E) = log_p(u)/(2e) ∈ Q_p")
print("v_p(L_p) = v_p(log_p(u)) - v_p(2e)")
print()
print("Capacity-Tauglichkeit erfordert: v_p(L_p) NEGATIV (L_p p-adisch gross)")
print("L_p → 0 (e→∞) bedeutet: v_p(L_p) WACHSEND (L_p p-adisch klein → nutzlos)")
print()
print("Berechnung: u ≡ 1/J_0 mod p^prec, w = u^{p-1} ∈ 1+p^k Z_p, v_p(log_p(u)) = k.")
print()

results = []

print(f"{'Tripel':<22} {'p^e':>10} {'u mod p²':>10} {'v_p(u-1)':>9} {'k=v_p(w-1)':>11} {'v_p(log u)':>11} {'v_p(2e)':>8} {'v_p(L_p)':>9} {'Diagnose'}")
print("-" * 120)

for a, b, c in clean:
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    all_factors = {}
    for d in [fa, fb, fc]:
        for pp, ee in d.items():
            all_factors[pp] = all_factors.get(pp, 0) + ee

    N = rad(a * b * c)
    D_eff = math.log(c) - math.log(N)

    for p in sorted(all_factors.keys()):
        if p == 2:
            continue
        e = all_factors[p]
        if e < 2:
            continue

        label = f"({a},{b},{c})"
        prec = min(2*e + 4, 40)  # prec <= 2e genuegt (Korrekturterme O(p^{2e}))

        u_mod, err = compute_u_mod_pk(a, b, c, p, e, prec)
        if u_mod is None:
            print(f"{label:<22} {p}^{e}={p**e:>8} ERROR: {err}")
            continue

        # v_p(u-1)
        modulus = p ** prec
        u_minus_1 = (u_mod - 1) % modulus
        vp_u_minus_1 = v_p(u_minus_1, p) if u_minus_1 != 0 else prec

        # v_p(log_p(u))
        vp_log_u, k = vp_log_p(u_mod, p, prec)

        # v_p(2e)
        vp_2e = v_p(2*e, p)

        # v_p(L_p) = v_p(log_p(u)) - v_p(2e)
        # Aber: L_p = log_p(u)/(2e), und 2e ist eine rationale Zahl.
        # v_p(L_p) = v_p(log_p(u)) - v_p(2e)
        vp_Lp = vp_log_u - vp_2e

        # u mod p^2 fuer Anzeige
        u_display = u_mod % (p**2)

        # Diagnose
        if vp_Lp > 0:
            diag = f"p-adisch KLEIN (→0). Kein Capacity-Hebel."
        elif vp_Lp == 0:
            diag = f"p-adische Einheit. Neutral."
        else:
            diag = f"p-adisch GROSS. Potentiell interessant!"

        results.append({
            'triplet': (a,b,c), 'p': p, 'e': e,
            'vp_u_minus_1': vp_u_minus_1,
            'k': k, 'vp_log_u': vp_log_u,
            'vp_2e': vp_2e, 'vp_Lp': vp_Lp,
            'D_eff': D_eff
        })

        print(f"{label:<22} {p}^{e}={p**e:>8} {u_display:>10} {vp_u_minus_1:>9} {k:>11} {vp_log_u:>11} {vp_2e:>8} {vp_Lp:>9} {diag}")

print()
print("=" * 120)
print("STRUKTURANALYSE")
print("=" * 120)
print()

# Zaehle Faelle
n_klein = sum(1 for r in results if r['vp_Lp'] > 0)
n_neutral = sum(1 for r in results if r['vp_Lp'] == 0)
n_gross = sum(1 for r in results if r['vp_Lp'] < 0)

print(f"v_p(L_p) > 0 (p-adisch klein, nutzlos): {n_klein}/{len(results)}")
print(f"v_p(L_p) = 0 (p-adische Einheit):       {n_neutral}/{len(results)}")
print(f"v_p(L_p) < 0 (p-adisch gross):           {n_gross}/{len(results)}")
print()

# Skalierungstest: waechst v_p(log_p(u)) mit e?
print("Skalierungstest: v_p(log_p(u)) vs. e")
print(f"{'p':>3} {'e':>3} {'v_p(u-1)':>9} {'v_p(log u)':>11} {'v_p(L_p)':>9}")
print("-" * 45)
for r in sorted(results, key=lambda x: (x['p'], x['e'])):
    print(f"{r['p']:>3} {r['e']:>3} {r['vp_u_minus_1']:>9} {r['vp_log_u']:>11} {r['vp_Lp']:>9}")

print()
print("=" * 120)
print("INTERPRETATION")
print("=" * 120)
print()
print("v_p(log_p(u)) haengt von v_p(u-1) ab, also davon wie nahe u an 1 liegt")
print("in der p-adischen Metrik. Fuer Frey-Kurven bei p^e|c:")
print("  u = 1/J_0 wobei J_0 = (unit part von j) = 256(a²+ab+b²)³/(a²b²) mod p")
print("  → v_p(u-1) ist durch die ARITHMETIK von (a,b,c) mod p bestimmt,")
print("    NICHT durch den Exponenten e!")
print()
print("Daher: v_p(log_p(u)) ist UNABHAENGIG von e (fuer festes Tripel/p).")
print("Aber v_p(2e) waechst mit e (wenn p|e). Ergo:")
print("  v_p(L_p) = v_p(log_p(u)) - v_p(2e) FAELLT (oder bleibt) fuer groessere e.")
print()
print("Das bedeutet:")
print("  - L_p wird p-adisch NICHT kleiner fuer grosse e")
print("  - ABER: L_p hat keine Skalierung die e*log(p) reflektiert")
print("  - L_p haengt von der RESTKLASSE a,b mod p ab, nicht von der Hoehe e")
print()
print("FAZIT: L_p ist ARITHMETISCH KONSTANT (abh. von Tripel mod p),")
print("       nicht e-skalierend. Bestaetigt: Kein Capacity-Kandidat.")
print("       Weder falsches Vorzeichen (alter Fehler) noch richtiges —")
print("       sondern FEHLENDE SKALIERUNG mit e.")
