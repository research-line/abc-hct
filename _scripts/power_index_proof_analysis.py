"""
Power-Index Beweis-Analyse
===========================
Untersucht drei mögliche Hebelansätze aus der 1/π-Reformulierung:
(A) Sieb-Schranken für powerful-number Paare
(B) Strukturelle Constraints aus a+b=c + Coprimality
(C) Verbindung zu L-Funktionen (Rückkopplung an Hauptpaper)
"""

import math
from collections import defaultdict

def factorize(n):
    if n <= 1:
        return {}
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
    if n <= 1:
        return 1
    return math.prod(factorize(n).keys())

def power_index(n):
    if n <= 1:
        return float('inf')
    r = rad(n)
    if r <= 1:
        return float('inf')
    return math.log(n) / math.log(r)

def is_k_powerful(n, k):
    """Ist n k-powerful (jeder Primfaktor mit Exponent >= k)?"""
    if n <= 1:
        return True
    for p, e in factorize(n).items():
        if e < k:
            return False
    return True

# ============================================================
# (A) EMPIRISCH: Paare (n, n+a) beide k-powerful
# ============================================================
print("=" * 90)
print("(A) KONSEKUTIVE POWERFUL-NUMBER PAARE")
print("    Frage: Wie viele n <= X haben n UND n+a beide k-powerful?")
print("=" * 90)

X_max = 10**7

for k in [2, 3]:
    print(f"\n--- {k}-powerful Paare ---")
    for a in [1, 2, 3, 5]:
        count = 0
        examples = []
        for n in range(1, X_max + 1):
            if is_k_powerful(n, k) and is_k_powerful(n + a, k):
                count += 1
                if count <= 5:
                    examples.append((n, n + a))
        # Theoretische Erwartung
        single_count = sum(1 for n in range(1, X_max + 1) if is_k_powerful(n, k))
        density = single_count / X_max
        pair_expected_indep = density**2 * X_max
        print(f"  a={a}: {count} Paare bis {X_max:.0e}  "
              f"(einzeln: {single_count}, Dichte: {density:.6f}, "
              f"erwartet unabhängig: {pair_expected_indep:.1f})")
        if examples:
            for n1, n2 in examples[:3]:
                f1 = " · ".join(f"{p}^{e}" if e > 1 else str(p)
                               for p, e in sorted(factorize(n1).items()))
                f2 = " · ".join(f"{p}^{e}" if e > 1 else str(p)
                               for p, e in sorted(factorize(n2).items()))
                pi1 = power_index(n1)
                pi2 = power_index(n2)
                print(f"        n={n1} ({f1}, π={pi1:.2f}), "
                      f"n+{a}={n2} ({f2}, π={pi2:.2f})")

# ============================================================
# (B) STRUKTURELLE CONSTRAINTS: a + b = c, gcd(a,b)=1, alle powerful
# ============================================================
print("\n" + "=" * 90)
print("(B) COPRIME POWERFUL TRIPEL: a + b = c, gcd(a,b) = 1, alle k-powerful")
print("=" * 90)

X_search = 10**5

for k in [2, 3]:
    print(f"\n--- Alle drei {k}-powerful ---")
    count = 0
    for a in range(1, X_search):
        if not is_k_powerful(a, k):
            continue
        for b in range(a + 1, X_search):
            c = a + b
            if c > 2 * X_search:
                break
            if math.gcd(a, b) != 1:
                continue
            if not is_k_powerful(b, k):
                continue
            if not is_k_powerful(c, k):
                continue
            count += 1
            q = math.log(c) / math.log(rad(a * b * c))
            pi_a = power_index(a)
            pi_b = power_index(b)
            pi_c = power_index(c)
            inv_sum = sum(1/p for p in [pi_a, pi_b, pi_c] if p < 1e10)

            def fmt(n):
                f = factorize(n)
                return " · ".join(f"{p}^{e}" if e > 1 else str(p)
                                 for p, e in sorted(f.items()))

            if count <= 20:
                print(f"  {fmt(a)} + {fmt(b)} = {fmt(c)}")
                print(f"    q={q:.3f}, π=({pi_a:.1f},{pi_b:.1f},{pi_c:.1f}), "
                      f"Σ(1/π)={inv_sum:.3f}")
    print(f"  GESAMT: {count} Tripel bis {X_search:.0e}")

# ============================================================
# (C) CONSTRAINT-ANALYSE: Was erzwingt gcd(a,b)=1 + a+b=c?
# ============================================================
print("\n" + "=" * 90)
print("(C) COPRIMALITY-CONSTRAINT BEI POWERFUL NUMBERS")
print("    Wenn a = p₁^α₁···pᵣ^αᵣ (αᵢ ≥ 2) und b = q₁^β₁···qₛ^βₛ (βⱼ ≥ 2)")
print("    mit {pᵢ} ∩ {qⱼ} = ∅, wie oft ist a+b auch powerful?")
print("=" * 90)

# Für 2-powerful: a = s²t³ parametrisieren
# Zähle Tripel mit Coprimality und prüfe ob c = a+b powerful
print("\n--- 2-powerful Tripel mit Qualität q > 1.0 bis 10^6 ---")
high_q_count = 0
X_hq = 10**6
for a in range(1, min(X_hq, 10**4)):
    if not is_k_powerful(a, 2):
        continue
    for b in range(a, X_hq):
        if not is_k_powerful(b, 2):
            continue
        c = a + b
        if math.gcd(a, b) != 1:
            continue
        if not is_k_powerful(c, 2):
            continue
        q = math.log(c) / math.log(rad(a * b * c))
        if q > 1.0:
            high_q_count += 1
            if high_q_count <= 15:
                def fmt2(n):
                    f = factorize(n)
                    return " · ".join(f"{p}^{e}" if e > 1 else str(p)
                                     for p, e in sorted(f.items()))
                print(f"  {fmt2(a)} + {fmt2(b)} = {fmt2(c)}, q = {q:.4f}")
print(f"  GESAMT mit q > 1.0: {high_q_count}")

# ============================================================
# (D) WACHSTUM DER POWERFUL-PAIR ZÄHLFUNKTION
# ============================================================
print("\n" + "=" * 90)
print("(D) WACHSTUM: P₂(X,a) = #{n ≤ X : n und n+a beide 2-powerful}")
print("    abc ⟹ P₂(X,a) = O(X^{1/2}) (trivial), aber gilt P₂ = o(X^{1/2})?")
print("=" * 90)

checkpoints = [10**k for k in range(3, 8)]

for a in [1, 2]:
    print(f"\n  a = {a}:")
    prev_count = 0
    prev_X = 0
    for X in checkpoints:
        count = 0
        for n in range(max(1, prev_X + 1) if prev_X else 1, X + 1):
            if is_k_powerful(n, 2) and is_k_powerful(n + a, 2):
                count += 1
        count += prev_count
        ratio = count / X**0.5 if X > 0 else 0
        log_ratio = math.log(count) / math.log(X) if count > 0 else 0
        print(f"    X = {X:.0e}: P₂ = {count:>6d},  "
              f"P₂/√X = {ratio:.4f},  "
              f"P₂ ~ X^{log_ratio:.3f}")
        prev_count = count
        prev_X = X

# ============================================================
# (E) DER ENTSCHEIDENDE PUNKT: POWERFUL + ADDITIVITÄT
# ============================================================
print("\n" + "=" * 90)
print("(E) KERN-ANALYSE: Warum ist abc ÄQUIVALENT zu powerful-pair Schranken?")
print("=" * 90)
print("""
  THEOREM (bekannt, Granville 1998):
    abc-Vermutung ⟺ Für jedes ε > 0 und festes a ≥ 1:
    #{n ≤ X : rad(n) ≤ n^{1/2-ε} UND rad(n+a) ≤ (n+a)^{1/2-ε}} < ∞

  D.h.: Es gibt nur ENDLICH viele n, wo n und n+a GLEICHZEITIG
  "mehr als 2-powerful" sind (π > 2+δ für beide).

  WAS FEHLT FÜR EINEN BEWEIS:

  1. SIEB-BARRIERE: Das große Sieb gibt
       Σ_{n≤X} μ²(n)·μ²(n+a) ~ c_a · X
     (quadratfreie Paare). Für powerful-Paare fehlt das Analogon:
       Σ_{n≤X} 1_{powerful}(n) · 1_{powerful}(n+a) ~ ???
     Die Korrelation ist nicht durch Siebmethoden kontrollierbar,
     weil powerful-numbers eine MULTIPLIKATIVE Eigenschaft sind
     und die Kopplung n → n+a ADDITIV ist.

  2. L-FUNKTIONS-BARRIERE: Die Dichte der k-powerful numbers
     hängt mit ζ(k) zusammen. Die PAAR-Dichte braucht
     Korrelationen von Dirichlet-Reihen, die auf Vermutungen
     wie GRH und Chowla hinauslaufen.

  3. INDIVIDUELL-VS-STATISTISCH: Selbst wenn wir die Paar-Dichte
     im Durchschnitt kontrollieren (was teilweise gelingt),
     braucht abc eine PUNKTWEISE Aussage für JEDES n.
     Das ist genau die Barriere "Statistisch → Individuell"
     aus dem Hauptpaper.

  FAZIT: Die Power-Index-Reformulierung ist eine ÄQUIVALENTE
  Umformulierung. Sie bietet keine neue Beweisroute, aber eine
  klare DIAGNOSTIK: abc scheitert exakt an der Unfähigkeit,
  multiplikative Eigenschaften (powerful) unter additiver
  Verschiebung (n → n+a) individuell zu kontrollieren.
""")
