"""
Power-Index Beweis-Analyse v2 (effizient)
==========================================
Sieb-basierte Berechnung von powerful-number Paaren.
"""
import math, sys, time

def sieve_smallest_prime_factor(X):
    """Sieb für kleinsten Primfaktor. O(X log log X)."""
    spf = list(range(X + 1))
    for p in range(2, int(X**0.5) + 1):
        if spf[p] == p:
            for m in range(p * p, X + 1, p):
                if spf[m] == m:
                    spf[m] = p
    return spf

def factorize_with_spf(n, spf):
    factors = {}
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        factors[p] = e
    return factors

def rad_with_spf(n, spf):
    if n <= 1:
        return 1
    r = 1
    while n > 1:
        p = spf[n]
        r *= p
        while n % p == 0:
            n //= p
    return r

def power_index_with_spf(n, spf):
    if n <= 1:
        return float('inf')
    r = rad_with_spf(n, spf)
    if r <= 1:
        return float('inf')
    return math.log(n) / math.log(r)

def is_k_powerful_with_spf(n, k, spf):
    if n <= 1:
        return True
    m = n
    while m > 1:
        p = spf[m]
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e < k:
            return False
    return True

def fmt_factors(n, spf):
    if n <= 1:
        return str(n)
    f = factorize_with_spf(n, spf)
    parts = []
    for p in sorted(f.keys()):
        e = f[p]
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " · ".join(parts)

# ============================================================
print("Sieb wird aufgebaut...", flush=True)
t0 = time.time()
X_MAX = 2 * 10**6
spf = sieve_smallest_prime_factor(X_MAX + 10)
print(f"Sieb bis {X_MAX:.0e} fertig in {time.time()-t0:.1f}s\n", flush=True)

# ============================================================
# (A) KONSEKUTIVE POWERFUL-NUMBER PAARE
# ============================================================
print("=" * 90, flush=True)
print("(A) KONSEKUTIVE POWERFUL-NUMBER PAARE", flush=True)
print("=" * 90, flush=True)

# Markiere 2-powerful und 3-powerful
t1 = time.time()
is_2pow = [False] * (X_MAX + 2)
is_3pow = [False] * (X_MAX + 2)

for n in range(1, X_MAX + 2):
    pw = True
    pw3 = True
    m = n
    while m > 1:
        p = spf[min(m, X_MAX)]
        if p > m:
            break
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e < 2:
            pw = False
            pw3 = False
            break
        if e < 3:
            pw3 = False
    is_2pow[n] = pw
    is_3pow[n] = pw3

count_2pow = sum(is_2pow[1:X_MAX+1])
count_3pow = sum(is_3pow[1:X_MAX+1])
print(f"2-powerful bis {X_MAX:.0e}: {count_2pow}  (Dichte: {count_2pow/X_MAX:.6f}, ~√X={X_MAX**0.5:.0f})", flush=True)
print(f"3-powerful bis {X_MAX:.0e}: {count_3pow}  (Dichte: {count_3pow/X_MAX:.6f}, ~X^(1/3)={X_MAX**(1/3):.0f})", flush=True)
print(f"Markierung: {time.time()-t1:.1f}s\n", flush=True)

for k, is_kpow in [(2, is_2pow), (3, is_3pow)]:
    print(f"--- {k}-powerful Paare (n, n+a) ---", flush=True)
    for a in [1, 2, 3, 5, 7]:
        count = 0
        examples = []
        for n in range(1, X_MAX + 1):
            if n + a > X_MAX:
                break
            if is_kpow[n] and is_kpow[n + a]:
                count += 1
                if len(examples) < 3:
                    examples.append(n)
        print(f"  a={a}: {count} Paare", flush=True)
        for n in examples:
            pi1 = power_index_with_spf(n, spf)
            pi2 = power_index_with_spf(n + a, spf)
            print(f"    n={n} ({fmt_factors(n, spf)}, π={pi1:.2f}), "
                  f"n+{a}={n+a} ({fmt_factors(n+a, spf)}, π={pi2:.2f})", flush=True)
    print(flush=True)

# ============================================================
# (B) WACHSTUM P_k(X, a) — der entscheidende Exponent
# ============================================================
print("=" * 90, flush=True)
print("(B) WACHSTUM P_k(X, a) = #{n ≤ X : n und n+a beide k-powerful}", flush=True)
print("    abc braucht: P₂(X,1) = O(X^{1/2-δ}) für ein δ > 0", flush=True)
print("=" * 90, flush=True)

checkpoints = [10**3, 3*10**3, 10**4, 3*10**4, 10**5, 3*10**5, 10**6, 2*10**6]

for k, is_kpow in [(2, is_2pow), (3, is_3pow)]:
    for a in [1, 2]:
        print(f"\n  {k}-powerful, a = {a}:", flush=True)
        cum = 0
        prev_ratio = None
        for X in checkpoints:
            if X > X_MAX:
                break
            count_in_range = sum(1 for n in range(max(1, (checkpoints[checkpoints.index(X)-1]+1) if checkpoints.index(X)>0 else 1), X+1)
                                 if n + a <= X_MAX and is_kpow[n] and is_kpow[n + a])
            # Recalculate from scratch for accuracy
        cum = 0
        for X in checkpoints:
            if X > X_MAX:
                break
            cum = sum(1 for n in range(1, X + 1) if n + a <= len(is_kpow) - 1 and is_kpow[n] and is_kpow[n + a])
            if cum > 0:
                alpha = math.log(cum) / math.log(X)
                ratio_sqrt = cum / X**0.5
                print(f"    X={X:>10,.0f}: P={cum:>6d},  "
                      f"P/X^0.5={ratio_sqrt:.4f},  "
                      f"P ~ X^{alpha:.3f}", flush=True)
            else:
                print(f"    X={X:>10,.0f}: P={cum:>6d}", flush=True)

# ============================================================
# (C) COPRIME POWERFUL TRIPEL a + b = c
# ============================================================
print("\n" + "=" * 90, flush=True)
print("(C) COPRIME POWERFUL TRIPEL: a + b = c, gcd(a,b) = 1, alle k-powerful", flush=True)
print("=" * 90, flush=True)

X_trip = min(X_MAX // 2, 500000)

for k, is_kpow in [(2, is_2pow), (3, is_3pow)]:
    print(f"\n--- Alle drei {k}-powerful, c ≤ {X_trip:.0e} ---", flush=True)
    count = 0
    for c in range(3, X_trip + 1):
        if not is_kpow[c]:
            continue
        for a in range(1, c // 2 + 1):
            b = c - a
            if not is_kpow[a] or not is_kpow[b]:
                continue
            if math.gcd(a, b) != 1:
                continue
            count += 1
            r = rad_with_spf(a, spf) * rad_with_spf(b, spf) * rad_with_spf(c, spf)
            q = math.log(c) / math.log(r) if r > 1 else 0
            pi_a = power_index_with_spf(a, spf)
            pi_b = power_index_with_spf(b, spf)
            pi_c = power_index_with_spf(c, spf)
            inv_sum = sum(1/p for p in [pi_a, pi_b, pi_c] if p < 1e10)
            if count <= 30:
                print(f"  {fmt_factors(a, spf)} + {fmt_factors(b, spf)} = {fmt_factors(c, spf)}", flush=True)
                print(f"    q={q:.3f}, π=({pi_a:.2f},{pi_b:.2f},{pi_c:.2f}), "
                      f"Σ(1/π)={inv_sum:.3f}", flush=True)
    print(f"  GESAMT: {count} Tripel", flush=True)

# ============================================================
# (D) QUALITÄTS-VERTEILUNG aller abc-Tripel mit q > 1
# ============================================================
print("\n" + "=" * 90, flush=True)
print("(D) ALLE ABC-TRIPEL MIT q > 1.0, c ≤ 50000", flush=True)
print("=" * 90, flush=True)

X_q = 50000
high_q = []

for c in range(3, X_q + 1):
    for a in range(1, c // 2 + 1):
        b = c - a
        if math.gcd(a, b) != 1:
            continue
        r = rad_with_spf(a, spf) * rad_with_spf(b, spf) * rad_with_spf(c, spf)
        if r <= 1:
            continue
        q = math.log(c) / math.log(r)
        if q > 1.0:
            pi_a = power_index_with_spf(a, spf)
            pi_b = power_index_with_spf(b, spf)
            pi_c = power_index_with_spf(c, spf)
            inv_sum = sum(1/p for p in [pi_a, pi_b, pi_c] if p < 1e10)
            high_q.append((q, a, b, c, pi_a, pi_b, pi_c, inv_sum))

high_q.sort(reverse=True)
print(f"\n  Anzahl Tripel mit q > 1.0: {len(high_q)}", flush=True)
print(f"\n  Top-20:", flush=True)
print(f"  {'q':>6} {'a':>8} {'b':>10} {'c':>10} {'π(a)':>6} {'π(b)':>6} {'π(c)':>6} {'Σ1/π':>6}", flush=True)
print(f"  {'-'*70}", flush=True)
for q, a, b, c, pa, pb, pc, inv in high_q[:20]:
    def fp(p):
        return f"{p:.2f}" if p < 1e10 else "∞"
    print(f"  {q:>6.3f} {a:>8} {b:>10} {c:>10} {fp(pa):>6} {fp(pb):>6} {fp(pc):>6} {inv:>6.3f}", flush=True)

# Verteilungsstatistik
if high_q:
    inv_sums = [x[7] for x in high_q]
    print(f"\n  Σ(1/π) Statistik (nur q > 1 Tripel):", flush=True)
    print(f"    min:  {min(inv_sums):.4f}", flush=True)
    print(f"    max:  {max(inv_sums):.4f}", flush=True)
    print(f"    mean: {sum(inv_sums)/len(inv_sums):.4f}", flush=True)

    # Histogramm
    print(f"\n  Σ(1/π) Histogramm:", flush=True)
    bins = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8),
            (0.8, 0.9), (0.9, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 3.0)]
    for lo, hi in bins:
        n = sum(1 for s in inv_sums if lo <= s < hi)
        bar = "█" * (n * 2)
        print(f"    [{lo:.1f}, {hi:.1f}): {n:>4d}  {bar}", flush=True)

    # Korrelation q vs Σ(1/π)
    print(f"\n  Korrelation q ↔ 1/Σ(1/π):", flush=True)
    q_vals = [x[0] for x in high_q]
    approx_vals = [1/x[7] if x[7] > 0 else 0 for x in high_q]
    n = len(q_vals)
    if n > 2:
        mean_q = sum(q_vals)/n
        mean_a = sum(approx_vals)/n
        cov = sum((q-mean_q)*(a-mean_a) for q, a in zip(q_vals, approx_vals))/n
        var_q = sum((q-mean_q)**2 for q in q_vals)/n
        var_a = sum((a-mean_a)**2 for a in approx_vals)/n
        if var_q > 0 and var_a > 0:
            r = cov / (var_q**0.5 * var_a**0.5)
            print(f"    Pearson r(q, 1/Σ(1/π)) = {r:.4f}", flush=True)

# ============================================================
# (E) FAZIT
# ============================================================
print("\n" + "=" * 90, flush=True)
print("BEWEIS-DIAGNOSE", flush=True)
print("=" * 90, flush=True)
print("""
  Die Power-Index-Reformulierung abc ⟺ "Σ(1/π) ≥ 1-ε für fast alle"
  ist eine ÄQUIVALENTE Umformulierung. Sie liefert keinen neuen Beweis,
  aber eine klare STRUKTURDIAGNOSE:

  1. BARRIERE IST ADDITIV-MULTIPLIKATIV:
     n powerful UND n+a powerful gleichzeitig zu kontrollieren
     erfordert die Kopplung von Multiplikation (Faktorisierung)
     und Addition (Verschiebung) — DAS klassische Hindernis der
     analytischen Zahlentheorie.

  2. SIEB-METHODEN REICHEN NICHT:
     Das große Sieb kontrolliert Charaktersummen, aber powerful-number
     Indikatoren sind KEINE glatten Funktionen in Charakteren.
     Man bräuchte ein "multiplikatives Sieb" — das existiert nicht.

  3. DIE GLEICHE BARRIERE WIE IM HAUPTPAPER:
     abc ⟺ Ω_E ≥ N^{-1/2-ε} ⟹ |L(f,1)| ≥ N^{-1/2-ε}  [Rückrichtung: Sha-Lücke]
     Das ist eine INDIVIDUELLE untere Schranke aus FAMILIEN-Statistik.
     Power-Index-Sprache: "Σ(1/π) INDIVIDUELL beschränkt, nicht nur
     im Mittel." Genau derselbe Statistisch→Individuell-Gap.

  4. PARTIELLES RESULTAT MÖGLICH:
     abc mit Exponent 2/3 statt 1+ε (d.h. c < rad(abc)^{2/3+ε})
     IST beweisbar mit aktuellen Methoden (Stewart-Yu 2001 geben
     c < rad(abc)^{1.7+ε} — noch weit von 1+ε entfernt).
""", flush=True)
