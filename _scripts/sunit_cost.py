# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""S-Unit Minimale Kosten: Exakte Berechnung fuer abc-Tripel.

Fuer p^e | c: Die Bedingung a+b=c erzwingt a*b^{-1} = -1 (mod p^e).
Die "Kosten" dieser Landung sind mu = min sum |n_q|*log(q) mit
prod q^{n_q} = -1 (mod p^e), wobei q in S_ab (ALLE Primteiler von a*b).

Die TRIVIALE Darstellung kommt direkt aus der Gleichung:
  a = prod q^{v_q(a)}, b = prod q^{v_q(b)},
  a*b^{-1} = prod q^{v_q(a)-v_q(b)} = -1 mod p^e.
  Kosten_trivial = sum |v_q(a) - v_q(b)| * log(q).

Frage: Gibt es eine BILLIGERE Darstellung?
Falls mu_min >= e*log(p) fuer alle stuck primes -> Obstruktion.
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
    (2, 6436341, 6436343),   # Reyssat
    (1, 2400, 2401),         # NICHT gedeckt durch LL
    (1, 242, 243),           # NICHT gedeckt durch LL
    (13, 243, 256),          # NICHT gedeckt durch LL
    (3, 125, 128),
    (1, 80, 81),
    (1, 4374, 4375),
    (5, 1024, 1029),
    (1, 512, 513),
    (1, 12167, 12168),
    (32, 49, 81),
]

print("=" * 120)
print("S-UNIT KOSTEN: Triviale Darstellung aus a+b=c")
print("=" * 120)
print()
print("Fuer p^e | c: a*b^{-1} = -1 (mod p^e)")
print("Triviale Kosten = sum |v_q(a) - v_q(b)| * log(q) fuer q in S_ab.")
print("Defekt-Beitrag = (e-1)*log(p) [Anteil am D_eff von dieser Primstelle]")
print()
print(f"{'Tripel':<28} {'p^e|c':>12} {'DefBeitr':>8} {'mu_triv':>8} {'mu/Def':>7} {'Darstellung'}")
print("-" * 110)

all_results = []
for a, b, c in triplets:
    if a+b != c or math.gcd(a,b) != 1:
        continue
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a*b*c)
    q_val = math.log(c) / math.log(N)

    # D_eff
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)
    D_eff = math.log(c) - math.log(N) - 2*log_u

    # Find stuck primes: p^e | c with e >= 2
    c_powers = [(p, e) for p, e in fc.items() if e >= 2]
    if not c_powers:
        continue

    # S_ab = all prime divisors of a*b (INCLUDING p=2!)
    S_ab = sorted(set(list(fa.keys()) + list(fb.keys())))

    label = f"({a},{b},{c})"
    for p_stuck, e_stuck in sorted(c_powers, key=lambda x: x[1]*math.log(x[0]), reverse=True):
        # Defect contribution from this prime to D_eff
        # D_eff contribution at p: (v_p(c) - 1 - neron_correction) * log(p)
        neron_p = (2*e_stuck) // 12  # Neron correction from v_p(Delta) = 2*v_p(abc)
        defect_p = (e_stuck - 1 - 2*neron_p) * math.log(p_stuck)

        # Trivial S-Unit cost: sum |v_q(a) - v_q(b)| * log(q) for q != p_stuck
        mu_trivial = 0
        repr_parts = []
        for q in S_ab:
            if q == p_stuck:
                continue
            vq_a = fa.get(q, 0)
            vq_b = fb.get(q, 0)
            diff = vq_a - vq_b
            if diff != 0:
                mu_trivial += abs(diff) * math.log(q)
                repr_parts.append(f"{q}^{diff:+d}")

        # Also include p_stuck itself if it divides a or b
        vp_a = fa.get(p_stuck, 0)
        vp_b = fb.get(p_stuck, 0)
        if vp_a > 0 or vp_b > 0:
            diff = vp_a - vp_b
            if diff != 0:
                mu_trivial += abs(diff) * math.log(p_stuck)
                repr_parts.append(f"{p_stuck}^{diff:+d}")

        ratio = mu_trivial / defect_p if defect_p > 0 else float('inf')
        repr_str = " * ".join(repr_parts[:5])

        print(f"{label:<28} {p_stuck}^{e_stuck}={p_stuck**e_stuck:>9} {defect_p:>8.3f} {mu_trivial:>8.3f} {ratio:>7.3f} {repr_str}")
        label = " " * 28

        all_results.append({
            'triplet': (a,b,c), 'p': p_stuck, 'e': e_stuck,
            'defect_p': defect_p, 'mu_trivial': mu_trivial, 'ratio': ratio,
            'D_eff': D_eff
        })

print()
print("=" * 120)
print("ANALYSE: Kann mu_trivial eine abc-Schranke liefern?")
print("=" * 120)
print()
print("Wenn mu_trivial >= defect_p fuer ALLE stuck primes => Potenzielle Obstruktion.")
print("Wenn mu_trivial < defect_p fuer manche => Billige Landung moeglich => Keine Obstruktion.")
print()

above = [r for r in all_results if r['ratio'] >= 1.0 and r['defect_p'] > 0]
below = [r for r in all_results if r['ratio'] < 1.0 and r['defect_p'] > 0]
print(f"  mu/Def >= 1 (Obstruktion):  {len(above)} Faelle")
print(f"  mu/Def < 1 (keine Obstr.):  {len(below)} Faelle")
print()

if above:
    print("  Obstruktions-Faelle:")
    for r in sorted(above, key=lambda x: x['ratio']):
        print(f"    ({r['triplet'][0]},{r['triplet'][1]},{r['triplet'][2]})"
              f" p={r['p']}^{r['e']}: mu/Def={r['ratio']:.3f}")
if below:
    print("  Keine-Obstruktion-Faelle:")
    for r in sorted(below, key=lambda x: x['ratio']):
        print(f"    ({r['triplet'][0]},{r['triplet'][1]},{r['triplet'][2]})"
              f" p={r['p']}^{r['e']}: mu/Def={r['ratio']:.3f}")

print()
print("=" * 120)
print("SCHLUESSELBEOBACHTUNG")
print("=" * 120)
print()
print("Die triviale Darstellung a*b^{-1} = -1 (mod p^e) hat Kosten:")
print("  mu_trivial = sum_{q in S_ab, q!=p} |v_q(a)-v_q(b)| * log(q)")
print()
print("Das ist im Wesentlichen: log(a) + log(b) = log(a*b) (ohne p-Anteil)")
print("Denn: sum |v_q(a)-v_q(b)|*log(q) <= sum (v_q(a)+v_q(b))*log(q) = log(a*b/p-Anteil)")
print()
print("Fuer abc-Tripel mit q > 1: log(c) > log(N), also log(a*b) ~ log(c) ~ q*log(N)")
print("Und: defect_p ~ (e-1)*log(p) ~ D_eff (ein Term)")
print()
print("Also: mu_trivial ~ log(a*b) und defect_p ~ (e-1)*log(p)")
print("Ratio ~ log(a*b)/((e-1)*log(p)) ~ log(c)/((e-1)*log(p))")
print()
print("Fuer Reyssat: log(c)=15.68, defect_23 = 4*log(23)=12.54")
print("  -> Ratio ~ 15.68/12.54 = 1.25 (grob)")
print("  -> Die triviale Darstellung ist TEURER als der Defekt")
print()
print("ABER: Gibt es BILLIGERE nicht-triviale Darstellungen?")
print("Wenn ja: mu_min < mu_trivial und die Obstruktion verschwindet.")
print("Wenn nein: mu_min = mu_trivial und die Obstruktion ist REAL.")
print()
print("Das ist die ENTSCHEIDENDE OFFENE FRAGE fuer die S-Unit-Capacity-Route.")
