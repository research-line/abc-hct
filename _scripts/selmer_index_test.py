"""Phase 1b Priority A: Lokaler Selmer-Index [H¹(G_p, E[ℓⁿ]) : H¹_f] an stuck primes.

Kernfrage: Sieht der lokale Selmer-Index e·log(p) oder nur log(e)?

Für E/Q_p mit split multiplikativer Reduktion, Tate-Parameter q mit v_p(q) = c_p:
  - |E[ℓⁿ](Q_p)| = gcd(ℓⁿ, p-1) · gcd(ℓⁿ, c_p)   [Tate-Kurve]
  - |H¹(G_p, E[ℓⁿ])| = p^{2n·δ_{ℓ,p}} · |E[ℓⁿ](Q_p)|²  [Euler-Char.]
  - |H¹_f(G_p, E[ℓⁿ])| = |E(Q_p)/ℓⁿ| = gcd(ℓⁿ, p-1) · gcd(ℓⁿ, c_p) · (ℓⁿ/...)

Für Frey bei p^e||c: c_p = v_p(Δ_min) = 2e.
"""
import math

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

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

print("=" * 130)
print("PHASE 1b — LOKALER SELMER-INDEX AN STUCK PRIMES")
print("=" * 130)
print()
print("Formel fuer split mult. Red., Tate-Parameter q mit v_p(q) = c_p = 2e:")
print("  |E[ell^n](Q_p)| = gcd(ell^n, p-1) * gcd(ell^n, c_p)")
print("  |E(Q_p)/ell^n|  = (ell^n * gcd(ell^n, p-1) * gcd(ell^n, c_p)) / ord(q in Q_p*/(Q_p*)^{ell^n})")
print("                  ≈ gcd(ell^n, p-1) * gcd(ell^n, c_p)   [wenn u = q/p^{c_p} ell^n-te Potenz]")
print("  [H¹ : H¹_f]    = |E[ell^n](Q_p)| = gcd(ell^n, p-1) * gcd(ell^n, c_p)")
print()
print("FRAGE: Sieht [H¹:H¹_f] den vollen Wert e*log(p), oder nur gcd-Information?")
print()

# Sammle stuck primes
stuck_primes = []
clean = [(a,b,c) for a,b,c in triplets if a+b==c and math.gcd(a,b)==1]
clean.sort(key=lambda t: math.log(t[2])/math.log(rad(t[0]*t[1]*t[2])), reverse=True)

for a, b, c in clean:
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    v_abc = {}
    for p in all_primes:
        v_abc[p] = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)
    for p in sorted(all_primes):
        if p == 2:
            continue
        e = v_abc[p]
        if e >= 2:
            stuck_primes.append({'triplet': (a,b,c), 'p': p, 'e': e, 'c_p': 2*e})

print(f"{'Tripel':<22} {'p':>3} {'e':>3} {'c_p=2e':>6} | ", end="")
print(f"{'ell=2':>8} {'ell=3':>8} {'ell=5':>8} {'ell=7':>8} {'ell=p':>8} | {'e*log(p)':>9} {'Diagnose'}")
print("-" * 130)

for sp in stuck_primes:
    a, b, c = sp['triplet']
    p = sp['p']
    e = sp['e']
    c_p = sp['c_p']  # = 2e

    label = f"({a},{b},{c})"
    target = e * math.log(p)  # das was wir sehen WOLLEN

    indices = {}
    for ell in [2, 3, 5, 7]:
        if ell == p:
            continue
        n = 1
        # [H¹:H¹_f] = gcd(ell^n, p-1) * gcd(ell^n, c_p)
        idx = gcd(ell**n, p-1) * gcd(ell**n, c_p)
        indices[f"ell={ell}"] = idx

    # ell = p Fall (p-primaer)
    # Fuer p ungerade, p teilt e nicht: gcd(p^n, p-1)=1, gcd(p^n, 2e)=gcd(p^n, 2e)
    n = 1
    idx_p_primary = gcd(p**n, p-1) * gcd(p**n, c_p)
    # Aber: fuer ell=p ist die Euler-Char anders!
    # |H¹(G_p, E[p^n])| = p^{2n} * |E[p^n](Q_p)|² (der Faktor p^{2n} kommt von |p^n|_p^{-2})
    # |H¹_f| = |E(Q_p)/p^n|
    # Also [H¹:H¹_f] = p^{2n} * |E[p^n](Q_p)|² / |E(Q_p)/p^n|
    # = p^{2n} * (gcd(p^n,p-1)*gcd(p^n,c_p))² / (gcd(p^n,p-1)*gcd(p^n,c_p) ??? )
    # Vereinfacht fuer p ungerade, n=1:
    # |E[p](Q_p)| = gcd(p, p-1) * gcd(p, 2e) = 1 * gcd(p, 2e) [p∤(p-1)]
    e_p_tors = gcd(p, 2*e)  # 1 wenn p∤e (meistens), p wenn p|e
    # |E(Q_p)/p| = ... analog: gcd(p, p-1) * gcd(p, 2e) = gcd(p, 2e)
    # [H¹:H¹_f] fuer ell=p: p² * (gcd(p,2e))² / gcd(p,2e) = p² * gcd(p,2e)
    idx_p_primary = p**2 * gcd(p, 2*e)  # fuer n=1

    # Log des Index als "Kapazitaet"
    log_indices = {}
    for key, val in indices.items():
        log_indices[key] = math.log(val) if val > 1 else 0
    log_idx_p = math.log(idx_p_primary)

    # Maximaler Index ueber alle ell
    max_log = max(list(log_indices.values()) + [log_idx_p])

    # Diagnose
    ratio = max_log / target if target > 0 else 0
    if ratio < 0.3:
        diag = "BLIND (sieht <30% von e*log(p))"
    elif ratio < 0.7:
        diag = f"PARTIELL ({ratio:.0%})"
    else:
        diag = f"SIEHT {ratio:.0%} — ABER: = log(c_p) nicht e*log(p)!"

    print(f"{label:<22} {p:>3} {e:>3} {c_p:>6} | ", end="")
    for key in ["ell=2", "ell=3", "ell=5", "ell=7"]:
        val = indices.get(key, "-")
        if val == "-":
            print(f"{'(=p)':>8}", end=" ")
        else:
            print(f"{val:>8}", end=" ")
    print(f"{idx_p_primary:>8} | {target:>9.3f} {diag}")

print()
print("=" * 130)
print("ANALYSE: Was sieht der lokale Selmer-Index?")
print("=" * 130)
print()
print("1. Fuer ell ≠ p, n=1:")
print("   [H¹:H¹_f] = gcd(ell, p-1) * gcd(ell, 2e)")
print("   → Sieht HOECHSTENS ob ell | 2e (ja/nein). Das ist O(1), nicht e*log(p)!")
print("   → Fuer grosse ell^n: gcd(ell^n, 2e) = ell^{v_ell(2e)} ≈ log(e)/log(ell)")
print("   → LOGARITHMISCH in e, nicht linear.")
print()
print("2. Fuer ell = p, n=1:")
print("   [H¹:H¹_f] = p² * gcd(p, 2e)")
print("   → Fuer p teilt e nicht: Index = p² (KONSTANT, unabhaengig von e!)")
print("   → Fuer p | e: Index = p³ (sieht nur ob p|e, nicht wie oft)")
print()
print("3. FAZIT: Der lokale Selmer-Index ist TATE-ZIRKULAER.")
print("   Er haengt ausschliesslich von c_p = v_p(q_E) = 2e ab,")
print("   und zwar nur ueber gcd-Relationen — d.h. er sieht die")
print("   TEILBARKEITSSTRUKTUR von e, nicht den WERT e*log(p).")
print()
print("4. MAXIMALER Informationsgehalt: v_ell(2e) * log(ell) fuer optimales ell.")
print("   Das ist O(log(e)), NICHT O(e*log(p)).")
print()

# Berechne den maximalen log-Index vs. Target
print("QUANTITATIV: max(log[H¹:H¹_f]) / (e*log(p)) fuer jeden stuck prime:")
print(f"{'Tripel':<22} {'p^e':>8} {'max_log_idx':>12} {'e*log(p)':>10} {'Ratio':>8} {'Verdict'}")
print("-" * 80)

for sp in stuck_primes:
    a, b, c = sp['triplet']
    p, e, c_p = sp['p'], sp['e'], sp['c_p']
    target = e * math.log(p)

    # Maximiere ueber alle ell und n
    max_log_idx = 0
    best_ell_n = ""

    for ell in [2, 3, 5, 7, 11, 13]:
        for n in range(1, 10):
            if ell == p:
                # p-primary: [H¹:H¹_f] = p^{2n} * gcd(p^n, 2e)
                idx = p**(2*n) * gcd(p**n, 2*e)
            else:
                # ell ≠ p: [H¹:H¹_f] = gcd(ell^n, p-1) * gcd(ell^n, 2e)
                idx = gcd(ell**n, p-1) * gcd(ell**n, 2*e)

            log_idx = math.log(idx) if idx > 1 else 0

            # Aber: n waechst kuenstlich! Die INFORMATION ueber e ist nur gcd(ell^n, 2e).
            # Der p^{2n}-Faktor ist "gratis" (haengt nicht von e ab).
            # Relevantes Signal: nur gcd(ell^n, 2e)
            signal = gcd(ell**n, 2*e) if ell != p else gcd(p**n, 2*e)
            log_signal = math.log(signal) if signal > 1 else 0

            if log_signal > max_log_idx:
                max_log_idx = log_signal
                best_ell_n = f"ell={ell},n={n}"

    ratio = max_log_idx / target if target > 0 else 0
    verdict = "UNZUREICHEND" if ratio < 0.5 else "PARTIELL"

    print(f"({a},{b},{c}){'':>8} {p}^{e}={p**e:>6} {max_log_idx:>12.4f} {target:>10.4f} {ratio:>8.2%} {verdict} [{best_ell_n}]")

print()
print("=" * 130)
print("SCHLUSSFOLGERUNG Phase 1b Priority A")
print("=" * 130)
print()
print("Der lokale Selmer-Index [H¹(G_p, E[ell^n]) : H¹_f(G_p, E[ell^n])]")
print("ist VOLLSTAENDIG durch den Tate-Parameter q_E (d.h. c_p = 2e) bestimmt.")
print()
print("Er sieht:")
print("  - Die ell-adische Bewertung v_ell(2e) — O(log e)")
print("  - Die Kongruenz p ≡ 1 mod ell — unabhaengig von e")
print("  - Den Faktor p^{2n} fuer ell=p — unabhaengig von e")
print()
print("Er sieht NICHT:")
print("  - Den vollen Wert e * log(p) (die 'Cusp Depth')")
print("  - Globale Kopplung zwischen verschiedenen stuck primes")
print()
print("ERGEBNIS: Priority A (lokaler Selmer-Index) ist TATE-ZIRKULAR.")
print("          Nicht geeignet als Cap_p-Kandidat fuer Route 11d.")
print()
print("ABER: Die GLOBALE Selmer-Gruppe (= Kern der Lokalisierungsabbildung)")
print("      ist ein globales Objekt. Ihr Rang / Korang haengt von ALLEN Stellen")
print("      gleichzeitig ab. Allerdings misst der Rang ω(N) ~ log(N)/log(log(N)),")
print("      nicht individuelle Exponenten e_p.")
print()
print("→ Priority B (Euler-Systeme) und Priority C (ueberkonvergente Formen)")
print("  muessen als NAECHSTES geprueft werden.")
