# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""Stuck-Prime Census: Isoliert die Primstellen die Route 11d/11e treffen muessen.

Fuer jedes p^e | c:
  single_prime_defect_p = (e - 1 - 2*floor(e/6)) * log(p)
  LL_cover_p = log(p) falls es ein ell>=3, ell∤N mit ell|v_p(abc) gibt
  stuck_p = single_prime_defect_p - LL_cover_p

stuck_p > 0 => Diese Primstelle braucht ein NEUES Werkzeug (11d/11e).
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
print("STUCK-PRIME CENSUS: Welche Primstellen brauchen Route 11d/11e?")
print("=" * 130)
print()
print("Fuer p^e | abc mit e>=2:")
print("  defect_p = (e - 1 - 2*floor(e/6)) * log(p)   [Neron-korrigierter Beitrag zu D_eff]")
print("  LL_cover = log(p) falls ∃ ell>=3, ell∤N: ell|v_p(abc)  [Level-Lowering-Deckung]")
print("  stuck_p  = defect_p - LL_cover   [Restdefekt: braucht 11d/11e]")
print()
print(f"{'Tripel':<25} {'q':>5} {'D_eff':>7} | {'p^e':>8} {'defect_p':>9} {'LL_ell':>7} {'LL_cov':>7} {'stuck_p':>8} {'Status'}")
print("-" * 120)

all_stuck = []
for a, b, c in clean:
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a * b * c)
    logN = math.log(N)
    q_val = math.log(c) / logN

    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    v_abc = {}
    for p in all_primes:
        v_abc[p] = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)

    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = v_abc[p]
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)
    D_eff = math.log(c) - logN - 2*log_u

    if D_eff <= 0:
        continue

    label = f"({a},{b},{c})"
    triplet_stuck_total = 0

    for p in sorted(all_primes):
        e = v_abc[p]
        if e < 2 or p == 2:
            continue

        neron_corr = (2*e) // 12
        defect_p = (e - 1 - 2*neron_corr) * math.log(p)
        if defect_p <= 0:
            continue

        # LL coverage: exists PRIME ell>=3, ell∤N, ell|v_p(abc)?
        ll_ell = 0
        for ell in [3, 5, 7, 11, 13, 17, 19, 23, 29]:
            if ell > e:
                break
            if e % ell == 0 and N % ell != 0:
                ll_ell = ell
                break

        ll_cover = math.log(p) if ll_ell > 0 else 0
        stuck_p = defect_p - ll_cover
        status = "STUCK" if stuck_p > 0 else "gedeckt"

        print(f"{label:<25} {q_val:>5.3f} {D_eff:>7.3f} | {p}^{e:>2}={p**e:>7} {defect_p:>9.3f} {ll_ell if ll_ell else '-':>7} {ll_cover:>7.3f} {stuck_p:>8.3f} {status}")
        label = " " * 25

        if stuck_p > 0:
            all_stuck.append({
                'triplet': (a,b,c), 'p': p, 'e': e,
                'defect_p': defect_p, 'll_ell': ll_ell,
                'll_cover': ll_cover, 'stuck_p': stuck_p,
                'q': q_val, 'D_eff': D_eff
            })
            triplet_stuck_total += stuck_p

print()
print("=" * 130)
print("ZUSAMMENFASSUNG: Stuck Primes")
print("=" * 130)
print()
print(f"Anzahl Stuck-Primstellen: {len(all_stuck)}")
print()
if all_stuck:
    print(f"{'Tripel':<25} {'p^e':>10} {'stuck_p':>8} {'% of D_eff':>10} {'Diagnose'}")
    print("-" * 80)
    for s in sorted(all_stuck, key=lambda x: x['stuck_p'], reverse=True):
        pct = 100 * s['stuck_p'] / s['D_eff'] if s['D_eff'] > 0 else 0
        diag = f"Kein ell>=3 mit ell|{s['e']}, ell∤N" if s['ll_ell'] == 0 else f"LL({s['ll_ell']}) deckt nur log({s['p']})={math.log(s['p']):.3f}"
        print(f"({s['triplet'][0]},{s['triplet'][1]},{s['triplet'][2]}){'':>10} {s['p']}^{s['e']:>2}={s['p']**s['e']:>7} {s['stuck_p']:>8.3f} {pct:>9.1f}% {diag}")

print()
print("=" * 130)
print("SCHLUSSFOLGERUNG")
print("=" * 130)
print()
print("Stuck primes sind GENAU die Stellen, die Route 11d/11e treffen muessen.")
print("Fuer diese gilt: p^e | c (oder a,b), kein ell>=3 teilt e mit ell∤N,")
print("oder LL deckt nur log(p) statt (e-1)*log(p).")
print()
print("Das gesuchte Objekt muss an genau diesen Stellen 'stuck_p' Kapazitaet liefern:")
print("  - metrisch linear in e*log(p)")
print("  - nicht identisch mit log|Delta| (sonst Szpiro-zirkulaer)")
print("  - nicht identisch mit Baker-Schranken (sonst 11b-blockiert)")
print("  - Kandidaten: Theta-Divisor-Pullback, Arakelov-Green am Cusp, Neron-Vertikaldivisor")
