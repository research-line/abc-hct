"""Pasten-Gap-Analyse: Warum Exponent 8/3 statt 1?

Ribet-Takahashi (vereinfacht): Fuer Frey-Kurve E mit N = rad(abc), D | N:
  delta_{1,N} / delta_{D,N/D} = gamma * prod_{p|D} c_p(E)

wobei c_p = Tamagawa-Zahl = v_p(Delta_min) fuer split mult.

Fuer Frey bei p^e||c: c_p = 2e.

abc sagt:  SUM e_p * log(p) <= (1+eps) * log(N)
Pasten:    PROD v_p(abc) <= K_eps * rad^{8/3+eps}
           d.h. SUM log(v_p(abc)) <= (8/3+eps) * log(rad)

GAP: Shimura-Grade sind MULTIPLIKATIV (Produkte),
     abc ist ADDITIV (Summe von Hoehen).
     Produkt -> Summe gibt log(), daher: log(e) statt e*log(p).
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

print("=" * 130)
print("PASTEN-GAP ANALYSE: Multiplikativ vs. Additiv")
print("=" * 130)
print()
print("abc-Vermutung:  log(c) <= (1+eps) * log(rad(abc))")
print("aequivalent:    SUM_{p|abc} (v_p(abc)-1) * log(p) <= eps * log(rad)")
print()
print("Pasten (JNT 2024): PROD_{p|abc} v_p(abc) <= K_eps * rad(abc)^{8/3+eps}")
print("aequivalent:       SUM log(v_p) <= (8/3+eps) * log(rad) + C")
print()
print("Shimura-Methode:   prod c_p <= delta_{1,N} <= N^{1+eps}")
print("wobei c_p = 2*v_p(abc) fuer Frey-Kurven (split mult.)")
print()
print("STRUKTURELLER GAP:")
print("  abc:    sum e_p * log(p) <= ... (ADDITIV in e_p)")
print("  Pasten: sum log(e_p) <= ... (MULTIPLIKATIV -> LOGARITHMISCH in e_p)")
print("  Verlust: e*log(p) -> log(e) pro Primstelle")
print()

print("=" * 130)
print("NUMERISCHE ILLUSTRATION: Multiplikativer vs. Additiver Defekt")
print("=" * 130)
print()
print(f"{'Tripel':<22} {'q':>5} | {'abc_defect':>11} {'pasten_lhs':>11} {'ratio_abc':>10} {'ratio_past':>11} | {'gap_factor':>10}")
print(f"{'':22} {'':>5} | {'sum e*logp':>11} {'sum log(v)':>11} {'/ log(rad)':>10} {'/ log(rad)':>11} | {'abc/past':>10}")
print("-" * 110)

for a, b, c in clean:
    fa = factorize(a)
    fb = factorize(b)
    fc = factorize(c)
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))

    N = rad(a * b * c)
    logN = math.log(N)
    q_val = math.log(c) / logN

    # abc-Defekt: sum (v_p - 1) * log(p)
    abc_defect = 0
    pasten_lhs = 0  # sum log(v_p)
    for p in all_primes:
        v = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        if v >= 2:
            abc_defect += (v - 1) * math.log(p)
            pasten_lhs += math.log(v)

    ratio_abc = abc_defect / logN if logN > 0 else 0
    ratio_past = pasten_lhs / logN if logN > 0 else 0
    gap_factor = abc_defect / pasten_lhs if pasten_lhs > 0 else float('inf')

    label = f"({a},{b},{c})"
    print(f"{label:<22} {q_val:>5.3f} | {abc_defect:>11.4f} {pasten_lhs:>11.4f} {ratio_abc:>10.4f} {ratio_past:>11.4f} | {gap_factor:>10.2f}")

print()
print("=" * 130)
print("INTERPRETATION")
print("=" * 130)
print()
print("gap_factor = (abc-Defekt) / (Pasten-LHS) = (sum e*log(p)) / (sum log(v_p))")
print()
print("Dieser Faktor zeigt, wie viel STAERKER abc gegenueber Pasten ist:")
print("  - gap_factor ~ e*log(p)/log(e) pro dominantem stuck prime")
print("  - Fuer e=10, p=3: gap ~ 10*1.1/2.3 = 4.8")
print("  - Fuer e=5, p=7: gap ~ 5*1.9/1.6 = 5.9")
print()
print("=" * 130)
print("WO ENTSTEHT DER VERLUST?")
print("=" * 130)
print()
print("Ribet-Takahashi: delta_{1,N}/delta_{D,M} = gamma * PROD_{p|D} c_p")
print()
print("Schritte und Verluste:")
print("1. Modularity degree: delta_{1,N} <= dim(S_2(Gamma_0(N))) * ||f||")
print("   -> delta_{1,N} ~ N^{1+eps} (Conrey-Duke-Farmer: delta_{1,N} ~ N^{7/4+eps})")
print("   VERLUST A: delta_{1,N} koennte groesser sein als noetig")
print()
print("2. Shimura-Grad-Ratio: delta_{1,N}/delta_{D,M} = gamma * prod c_p")
print("   Diese Gleichung ist EXAKT (Ribet-Takahashi). Kein Verlust hier.")
print()
print("3. Produkt -> Summe: PROD c_p <= delta_{1,N} <= N^{alpha}")
print("   Also: SUM log(c_p) <= alpha * log(N)")
print("   VERLUST B: Produkt-zu-Summe-Konversion gibt LOGARITHMEN.")
print("   abc braeuchte: SUM c_p * log(p) / c_p ... nein:")
print("   abc braeuchte: SUM (c_p/2) * log(p) <= (1+eps) * log(N)")
print("   Pasten liefert: SUM log(c_p/2) <= alpha * log(N)")
print("   Differenz: e*log(p) vs. log(e). Das IST der strukturelle Gap.")
print()
print("4. Optimierung ueber D: Pasten waehlt D optimal.")
print("   VERLUST C: Nicht alle primes koennen gleichzeitig in D sein")
print("   (D muss gerade viele Primfaktoren haben fuer Shimura-Def.).")
print("   Aber fuer Frey: N = rad(abc), alle p||N, daher ist diese")
print("   Einschraenkung mild (Paritaets-Flip mit Hilfs-p).")
print()
print("5. Der Exponent 8/3:")
print("   Pasten's Optimierung ueber die admissible factorization D|N")
print("   und die Schranken fuer delta_{D,M} fuehren zum Exponenten 8/3.")
print("   Conrey-Duke-Farmer: delta_{1,N} ~ N^{7/4}. Pasten: 8/3 > 7/4.")
print("   Der Extra-Verlust (8/3 - 7/4 = 11/12) kommt von:")
print("   - Shimura-Kurven-Genus-Abschaetzung (g ~ D*M/12)")
print("   - Division durch D bei der Grad-Ratio")
print("   - Manin-Konstanten-Bounding")
print()
print("=" * 130)
print("FAZIT: Ist 8/3 -> 1 moeglich?")
print("=" * 130)
print()
print("NEIN mit der Shimura-Grad-Methode allein.")
print("Der Verlust ist STRUKTURELL:")
print("  Shimura-Grade sind MULTIPLIKATIV (Grad einer Abbildung)")
print("  -> Sie messen PRODUKTE von Tamagawa-Zahlen")
print("  -> Umwandlung Produkt -> Summe gibt LOGARITHMEN")
print("  -> log(e) statt e*log(p)")
print()
print("Um von 8/3 nach 1+eps zu kommen, braeuchte man:")
print("  (a) Eine ADDITIVE Eigenschaft von Shimura-Kurven, oder")
print("  (b) Iteration: Nicht nur einen Grad, sondern VIELE Grade")
print("      verknuepfen (e-mal?), oder")
print("  (c) Ein gaenzlich anderes Werkzeug das linear in e ist.")
print()
print("Kandidat (b): L-Funktionen von Shimura-Kurven in FAMILIEN,")
print("  d.h. die analytische Fortsetzung ueber D hinweg.")
print("  Aber: Das ist im Wesentlichen die Langlands-Transferring-Idee")
print("  und fuehrt zurueck auf die ANC-Route (Route 1).")
print()
print("SCHLUSSFOLGERUNG:")
print("  Pasten-Gap ist INHAERENT in der Shimura-Grad-Methode.")
print("  8/3 -> 1 erfordert einen Paradigmenwechsel, nicht nur")
print("  eine Verfeinerung innerhalb der Shimura-Architektur.")
