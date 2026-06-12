"""Loop 12: BSD-Diskrepanz-Diagnose.

Berechnet fuer jede Frey-Kurve E_{a,b}: y^2 = x(x-a)(x+b):
  - c4, c6, Delta (Modell-Diskriminante)
  - j-Invariante
  - Reduktionstyp bei jedem schlechten Prim p (via vereinfachtem Tate-Algo)
  - Tatsaechlichen Conductor N_cond (vs. angenommenem N_rad = rad(abc))
  - Korrekte a_p bei schlechten Primstellen

Zweck: Root Cause fuer 3/5 BSD-Diskrepanzen in ze_decomposition.py identifizieren.
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


def ord_p(n, p):
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1


# Weierstrass-Invarianten fuer y^2 = x^3 + a2*x^2 + a4*x
# (a1=0, a3=0, a6=0)
def weierstrass_invariants(a2, a4):
    b2 = 4 * a2
    b4 = 2 * a4
    b6 = 0
    b8 = -a4 * a4
    c4 = b2**2 - 24 * b4
    c6 = -b2**3 + 36 * b2 * b4 - 216 * b6
    delta = -b2**2 * b8 - 8 * b4**3 - 27 * b6**2 + 9 * b2 * b4 * b6
    return b2, b4, b6, b8, c4, c6, delta


def j_invariant(c4, delta):
    if delta == 0:
        return float('inf')
    return c4**3 / delta


def reduction_type_odd(a_val, b_val, p):
    """Reduktionstyp bei ungeradem p | abc.
    Returns: (type, a_p, f_p)
      type: 'good', 'split_mult', 'nonsplit_mult', 'additive'
      a_p: Koeffizient fuer L-Funktion
      f_p: Conductor-Exponent
    """
    c_val = a_val + b_val
    if p == 2:
        raise ValueError("Nur fuer ungerade p")

    # Pruefe ob p | abc
    divides_a = (a_val % p == 0)
    divides_b = (b_val % p == 0)
    divides_c = (c_val % p == 0)

    if not (divides_a or divides_b or divides_c):
        return ('good', None, 0)

    # Frey-Kurve y^2 = x(x-a)(x+b) bei p | abc:
    # Kurve hat multiplikative Reduktion (semistabil) bei ungeradem p | abc
    # Split/nonsplit haengt von Tangentialrichtungen am Knoten ab
    if divides_a:
        # Knoten bei x=0: y^2 = b*x^2, split gdw b ist QR mod p
        is_split = (legendre(b_val, p) == 1)
    elif divides_b:
        # Knoten bei x=0: y^2 = (-a)*x^2, split gdw -a ist QR mod p
        is_split = (legendre(-a_val, p) == 1)
    else:
        # p | c: Knoten bei x=a: y^2 = a*x^2 (nach Verschiebung), split gdw a QR
        is_split = (legendre(a_val, p) == 1)

    a_p = 1 if is_split else -1
    return ('split_mult' if is_split else 'nonsplit_mult', a_p, 1)


def reduction_at_2(a_val, b_val):
    """Reduktionstyp der Frey-Kurve bei p=2.

    Fuer y^2 = x(x-a)(x+b) mit genau einem geraden unter a, b, c=a+b.
    Bestimmt Kodaira-Typ via c4, Delta Bewertungen.

    Returns: (type_str, a_2, f_2)
    """
    c_val = a_val + b_val
    a2_coeff = b_val - a_val
    a4_coeff = -a_val * b_val
    _, _, _, _, c4, c6, delta = weierstrass_invariants(a2_coeff, a4_coeff)

    v_delta = ord_p(delta, 2) if delta != 0 else float('inf')
    v_c4 = ord_p(c4, 2) if c4 != 0 else float('inf')

    # Frey ist semistabil (multiplikativ) bei p=2 gdw:
    # v_2(c4) < 4 ODER (v_2(Delta) > 0 UND v_2(c4) >= 4 mit v_2(Delta) < 12)
    # Genauer: nach Minimierung und Tate-Algorithmus

    # Fuer das Modell y^2 = x^3 + A*x^2 + B*x (a1=a3=a6=0):
    # Minimalitaet bei 2: braucht v_2(a2) >= 0, v_2(a4) >= 0 (immer erfuellt fuer ganze a,b)
    # ABER: das Modell ist genau dann minimal bei 2, wenn es keine
    # Substitution x -> x + r, y -> y + sx + t gibt, die alle a_i ganzzahliger macht.
    # Fuer [0, A, 0, B, 0] mit A,B ganz: minimal gdw v_2(Delta) < 12
    # oder es gibt keine Substitution mit u=2 die alles verbessert.

    # Vereinfachter Test: Wenn wir x -> 4x, y -> 8y substituieren (u=2):
    # [0, A, 0, B, 0] -> [0, A/4, 0, B/16, 0] (fuer a1=a3=0)
    # Dies ist ganzzahlig gdw 4|A und 16|B.
    # Wenn ja, koennen wir minimieren: neues Modell hat Delta/2^12.

    # Iterativ minimieren
    A = a2_coeff
    B = a4_coeff
    u_total = 1
    while A % 4 == 0 and B % 16 == 0:
        A = A // 4
        B = B // 16
        u_total *= 2

    # Neues minimales(er) Modell: y^2 = x^3 + A*x^2 + B*x
    _, _, _, _, c4_min, c6_min, delta_min = weierstrass_invariants(A, B)

    v_delta_min = ord_p(delta_min, 2) if delta_min != 0 else float('inf')
    v_c4_min = ord_p(c4_min, 2) if c4_min != 0 else float('inf')

    # Kodaira-Typ aus Delta und c4:
    # Multiplikative Reduktion: v(Delta) > 0 und v(c4) = 0 -> I_n (n = v(Delta))
    # Additive: v(c4) > 0

    if v_delta_min == 0:
        return ('good', 0, 0, A, B)
    elif v_c4_min == 0:
        # Multiplikative Reduktion (I_n), n = v_2(delta_min)
        # Split/nonsplit: Bestimme ob Tangentialrichtungen rational ueber F_2
        # Fuer y^2 = x^3 + Ax^2 + Bx mod 2:
        roots_mod2 = []
        for x in range(2):
            val = (x**3 + A * x**2 + B * x) % 2
            if val == 0:
                roots_mod2.append(x)
        # Doppelwurzel bestimmen
        f_mod2 = [(x, (x**3 + A * x**2 + B * x) % 2) for x in range(2)]
        # Ableitung: 3x^2 + 2Ax + B mod 2
        df_mod2 = [(x, (3 * x**2 + 2 * A * x + B) % 2) for x in range(2)]

        # Singulaerer Punkt: f(x)=0 und f'(x)=0 mod 2
        sing_pts = [x for x in range(2)
                     if (x**3 + A * x**2 + B * x) % 2 == 0
                     and (3 * x**2 + 2 * A * x + B) % 2 == 0]

        if sing_pts:
            x0 = sing_pts[0]
            # Tangentialrichtungen: d^2f/dx^2 an x0
            # f(x) = x^3 + Ax^2 + Bx, verschiebe x -> x + x0
            # f(x+x0) = ... expandieren
            # Koeffizient von x^2 nach Verschiebung: 3x0 + A
            coeff_x2 = (3 * x0 + A) % 2
            # y^2 = coeff_x2 * x^2 + hoeheres -> split gdw coeff_x2 = 1 (Quadrat in F_2)
            # In F_2: 1 ist ein Quadrat, 0 nicht (Cusp)
            if coeff_x2 % 2 == 1:
                is_split = True  # y^2 = x^2 -> (y-x)(y+x) = 0 -> split in F_2
                a_2 = 1
            else:
                # coeff_x2 = 0 -> hoeherer Kontakt -> Cusp -> additiv
                a_2 = 0
                return ('additive', 0, 2 + _wild_part_2(delta_min, c4_min), A, B)
        else:
            # Kein singulaerer Punkt mod 2 -> gute Reduktion?
            return ('good_surprise', 0, 0, A, B)

        # Multiplikativ: f_2 = 1
        return ('split_mult' if is_split else 'nonsplit_mult', a_2, 1, A, B)
    else:
        # v(c4) > 0: additive Reduktion
        a_2 = 0
        wild = _wild_part_2(delta_min, c4_min)
        return ('additive', 0, 2 + wild, A, B)


def _wild_part_2(delta, c4):
    """Grobe Schaetzung des wilden Teils des Conductor-Exponenten bei p=2.
    Fuer additive Reduktion: f_2 = 2 + delta_wild, delta_wild in {0,...,4}.
    Exakte Berechnung braucht vollen Tate-Algo. Hier: Heuristik."""
    v_d = ord_p(delta, 2) if delta != 0 else 12
    v_c4 = ord_p(c4, 2) if c4 != 0 else 12
    # Grobe Schaetzung basierend auf Kodaira-Typ
    if v_c4 >= 4 and v_d >= 6:
        return 4  # Typ I*_n oder schlimmer
    elif v_c4 >= 4:
        return 2
    return 0


# === Tripel ===
triplets = [
    (1, 8, "1+2^3=3^2"),
    (3, 125, "3+5^3=2^7"),
    (1, 4374, "1+2*3^7=5^4*7"),
    (1, 2400, "1+2^5*3*5^2=7^4"),
    (6436341, 2, "Reyssat"),
]

print("=" * 120)
print("CONDUCTOR-DIAGNOSE: Frey-Kurven E_{a,b}: y^2 = x(x-a)(x+b)")
print("=" * 120)

for a_val, b_val, name in triplets:
    c_val = a_val + b_val
    abc = a_val * b_val * c_val
    rad_abc = 1
    for p in factorize(abc).keys():
        rad_abc *= p
    N_assumed = rad_abc

    a2_coeff = b_val - a_val
    a4_coeff = -a_val * b_val
    b2, b4, b6, b8, c4, c6, delta = weierstrass_invariants(a2_coeff, a4_coeff)
    j = j_invariant(c4, delta)

    print(f"\n{'='*80}")
    print(f"Tripel: {name}  (a={a_val}, b={b_val}, c={c_val})")
    print(f"  abc = {abc},  rad(abc) = {rad_abc}")
    print(f"  Modell: y^2 = x^3 + {a2_coeff}x^2 + ({a4_coeff})x")
    print(f"  c4 = {c4},  c6 = {c6}")
    print(f"  Delta(Modell) = {delta}")
    print(f"  v_2(Delta) = {ord_p(delta, 2)}")
    print(f"  j = {c4}^3 / {delta} = {j:.6f}")

    bad_primes = sorted(factorize(abc).keys())
    print(f"  Schlechte Primstellen: {bad_primes}")

    N_cond = 1
    correct_ap = {}

    # p=2 Analyse
    if 2 in bad_primes:
        result = reduction_at_2(a_val, b_val)
        rtype, a_2, f_2, A_min, B_min = result
        N_cond *= 2**f_2
        correct_ap[2] = a_2
        print(f"\n  p=2: Reduktionstyp = {rtype}")
        print(f"    a_2 = {a_2},  f_2 = {f_2}")
        if A_min != a2_coeff or B_min != a4_coeff:
            print(f"    Minimiertes Modell: y^2 = x^3 + {A_min}x^2 + ({B_min})x")
            _, _, _, _, c4m, c6m, dm = weierstrass_invariants(A_min, B_min)
            print(f"    c4_min = {c4m}, Delta_min = {dm}, v_2(Delta_min) = {ord_p(dm,2)}")

    # Ungerade Primstellen
    for p in bad_primes:
        if p == 2:
            continue
        rtype, a_p, f_p = reduction_type_odd(a_val, b_val, p)
        N_cond *= p**f_p
        correct_ap[p] = a_p
        print(f"  p={p}: {rtype}, a_{p} = {a_p}, f_{p} = {f_p}")

    print(f"\n  N_rad (angenommen) = {N_assumed}")
    print(f"  N_cond (berechnet) = {N_cond}")
    if N_cond != N_assumed:
        print(f"  *** DISKREPANZ: N_cond/N_rad = {N_cond/N_assumed:.1f} ***")
        print(f"  *** Script benutzt falschen Conductor! ***")
    else:
        print(f"  OK: N_cond = N_rad")

    # Vergleich a_p alt vs neu
    print(f"\n  a_p Vergleich (alt aus Script vs. korrekt):")
    for p in bad_primes:
        # Altes a_p aus dem Script
        if p == 2:
            if a_val % 2 != 0 or b_val % 2 != 0:
                # count_points_mod_p
                count = 1
                a_mod = a_val % 2
                b_mod = b_val % 2
                for x in range(2):
                    rhs = (x * ((x - a_mod) % 2) * ((x + b_mod) % 2)) % 2
                    if rhs == 0:
                        count += 1
                    else:
                        if legendre(rhs, 2) == 1:
                            count += 2
                old_ap = 2 + 1 - count
            else:
                old_ap = 0
        else:
            if a_val % p == 0:
                old_ap = 1 if legendre(b_val, p) == 1 else -1
            elif b_val % p == 0:
                old_ap = 1 if legendre(-a_val, p) == 1 else -1
            elif c_val % p == 0:
                old_ap = 1 if legendre(a_val, p) == 1 else -1
            else:
                old_ap = "N/A"

        new_ap = correct_ap.get(p, "?")
        match = "OK" if old_ap == new_ap else "FEHLER"
        print(f"    p={p}: alt={old_ap}, neu={new_ap}  [{match}]")

print("\n" + "=" * 120)
print("ZUSAMMENFASSUNG")
print("=" * 120)
print("""
Die Hauptfehlerquellen im ze_decomposition.py Script:
1. N = rad(abc) als Conductor angenommen -- bei p=2 oft FALSCH (additiv statt multiplikativ)
2. a_p bei p=2 via count_points_mod_p berechnet -- FALSCH fuer singulaere Kurven
3. Falscher Conductor -> falscher Normierungsfaktor sqrt(N) in L-Wert-Berechnung
4. Falsche a_p -> falsche Fourier-Koeffizienten -> falscher L-Wert
""")
