# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""Vergleich: Tate-Parameter-Summe (= log|Delta|) vs D_eff
Strukturelle Frage: Wo sitzt der "stuck" Anteil pro Prim?"""
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

triplets = [
    (1,8,9),(3,125,128),(1,80,81),(32,49,81),(5,27,32),
    (13,243,256),(1,4374,4375),(2,6436341,6436343),
    (1,2,3),(1,63,64),(7,18,25),(1,242,243),(3,253,256),
    (1,2400,2401),(1,4913,4914),(2,6561,6563),
    (1,12167,12168),(1,512,513),(1,48,49),(5,1024,1029),
]

print("=" * 110)
print("Tate-Parameter-Summe: S_Tate = sum c_p*log(p) = log|Delta_min| (bis auf 2-Korrektur)")
print("=" * 110)
print()
print(f"{'Tripel':<28} {'q':>5} {'D_eff':>7} {'S_Tate':>7} {'S/logN':>6} {'S/6lnN':>6} {'D/S':>6}")
print("-" * 80)

for a, b, c in sorted(triplets, key=lambda t: math.log(t[2])/math.log(rad(t[0]*t[1]*t[2])), reverse=True):
    if a+b != c or math.gcd(a,b) != 1:
        continue
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a*b*c)
    logN = math.log(N)
    q_val = math.log(c) / logN
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))

    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = fa.get(p,0)+fb.get(p,0)+fc.get(p,0)
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)

    D_eff = math.log(c) - logN - 2*log_u

    S_tate = 0
    for p in all_primes:
        vp = fa.get(p,0)+fb.get(p,0)+fc.get(p,0)
        S_tate += 2*vp * math.log(p)

    s_over_6 = S_tate / (6 * logN)
    d_over_s = D_eff / S_tate if S_tate > 0 else 0

    label = f"({a},{b},{c})"
    print(f"{label:<28} {q_val:>5.3f} {D_eff:>7.3f} {S_tate:>7.3f} "
          f"{S_tate/logN:>6.3f} {s_over_6:>6.3f} {d_over_s:>6.4f}")

print()
print("=" * 110)
print("Per-Prim Stuck-Analyse (nur Tripel mit D_eff > 1.0)")
print("=" * 110)
print()

for a, b, c in sorted(triplets, key=lambda t: math.log(t[2])/math.log(rad(t[0]*t[1]*t[2])), reverse=True):
    if a+b != c or math.gcd(a,b) != 1:
        continue
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a*b*c)
    logN = math.log(N)
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))

    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = fa.get(p,0)+fb.get(p,0)+fc.get(p,0)
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)

    D_eff = math.log(c) - logN - 2*log_u
    if D_eff < 1.0:
        continue

    print(f"({a},{b},{c}): q={math.log(c)/logN:.3f}, D_eff={D_eff:.3f}")
    print(f"  {'p':>5} {'v_p(c)':>6} {'c_p':>4} {'Tate_p':>7} {'Defect_p':>8} {'Neron_p':>7} {'Stuck?':>6}")

    for p in sorted(all_primes):
        vp_a = fa.get(p,0)
        vp_b = fb.get(p,0)
        vp_c = fc.get(p,0)
        vp_abc = vp_a + vp_b + vp_c
        c_p = 2 * vp_abc
        tate_p = c_p * math.log(p)

        # Defect contribution from c-side only
        if p == 2:
            neron_p = 0  # simplified for p=2
        else:
            neron_p = (2*vp_abc) // 12

        # D_eff contribution at this prime
        if vp_c >= 2:
            defect_p = (vp_c - 1 - neron_p) * math.log(p)
        elif vp_c == 1:
            defect_p = 0  # rad already accounts for this
        else:
            # p divides a or b but not c
            defect_p = -(1 + 2*neron_p) * math.log(p)  # protective

        stuck = "STUCK" if vp_c >= 2 and neron_p == 0 else ""
        if vp_c >= 2 or (vp_abc > 0 and abs(defect_p) > 0.5):
            print(f"  {p:>5} {vp_c:>6} {c_p:>4} {tate_p:>7.3f} {defect_p:>8.3f} {neron_p:>7} {stuck:>6}")
    print()

# The KEY structural insight
print("=" * 110)
print("STRUKTURELLE EINSICHT")
print("=" * 110)
print()
print("Vergleich der SKALIERUNGEN (fuer D_eff > 0 Tripel):")
print()
print("1. D_eff = sum_p (v_p(c) - 1 - neron_p) * log(p)")
print("   --> Waechst LINEAR in v_p(c) mal log(p)")
print()
print("2. log(prod c_p) = sum_p log(2*v_p(abc))")
print("   --> Waechst LOGARITHMISCH in v_p (!!!)")
print()
print("3. S_Tate = sum c_p * log(p) = sum 2*v_p(abc)*log(p) = log|Delta|")
print("   --> Waechst LINEAR in v_p(abc) mal log(p)")
print()
print("ERGEBNIS:")
print("  - log(prod c_p) << D_eff bei extremalen Tripeln (ANTI-KORRELATION)")
print("    Grund: log(2*v_p) vs (v_p - 1)*log(p). Fuer v_p=5,p=23:")
print("      log(10) = 2.30  vs  4*log(23) = 12.54  --> Faktor 5.5x")
print()
print("  - S_Tate ~ D_eff + 6*logN (lineare Beziehung!)")
print("    Grund: Beide wachsen linear in v_p*log(p)")
print("    S_Tate/6*logN ist der Szpiro-Quotient. D_eff misst den UEBERSCHUSS.")
print()
print("  - Route 11 (naive Tamagawa-Capacity 1/prod(c_p)) ist STRUKTURELL SCHWAECHER")
print("    als Route 12 (D_eff). Sie kann die extremalen Faelle NICHT erreichen.")
print()
print("  - Die RICHTIGE Capacity-Groesse muesste p^{-f(v_p)} mit f ~ v_p sein,")
print("    nicht bloss 1/c_p = 1/(2*v_p).")
print()
print("  - Kandidat: Tate-Periode |q_E|_p = p^{-c_p} = p^{-2*v_p(abc)}")
print("    Das gibt: -sum c_p*log(p) = -log|Delta| (die DISKRIMINANTE)")
print("    --> Aber Szpiro (log|Delta| < (6+eps)*logN) IST abc. Zirkulaer!")
