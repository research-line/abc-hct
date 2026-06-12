# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""Capacity-Census: Route 11 (Adelic Spike-Capacity) vs Route 12 (D_eff)
Berechnet fuer 20 abc-Tripel:
  1. D_eff = log(c) - log(N) - 2*log(u)  [Route 12]
  2. log(prod c_p)  [Tamagawa-Produkt]
  3. Saturierungs-Defizit = log(abc) - log(rad(abc))
Kernfrage: Skaliert log(prod c_p) ANDERS als D_eff?
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

def compute_metrics(a, b, c):
    assert a + b == c and math.gcd(a, b) == 1
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a * b * c)
    q = math.log(c) / math.log(N) if N > 1 else 0

    # Neron correction
    log_u = 0
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    for p in all_primes:
        if p == 2:
            continue
        vp_abc = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        vp_delta = 2 * vp_abc
        u_p = vp_delta // 12
        if u_p > 0:
            log_u += u_p * math.log(p)

    D_eff = math.log(c) - math.log(N) - 2 * log_u

    # Tamagawa product
    log_tam = 0
    tam_detail = {}
    for p in all_primes:
        vp = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        if vp > 0:
            c_p = 2 * vp  # Tamagawa for I_{2v} type
            log_tam += math.log(c_p)
            tam_detail[p] = c_p

    # Tamagawa margin
    tam_margin = log_tam - max(0, D_eff)

    # Saturation deficit = sum (v_p(abc) - 1) * log(p) for v_p >= 2
    sat_deficit = 0
    for p in all_primes:
        vp_total = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        if vp_total > 1:
            sat_deficit += (vp_total - 1) * math.log(p)

    # Route 11 "Capacity Quotient":
    # Q_cap = log(prod c_p) / log(c)
    # If Q_cap > 1: Tamagawa "overcovers" the height -> route works
    # If Q_cap < 1: Tamagawa alone insufficient
    q_cap = log_tam / math.log(c) if c > 1 else 0

    # "Tamagawa excess over radical":
    # E_tam = log(prod c_p) - log(N)
    # Positive = Tamagawa sees more than just the radical primes
    e_tam = log_tam - math.log(N)

    return {
        'a': a, 'b': b, 'c': c,
        'N': N, 'q': q,
        'D_eff': D_eff,
        'D_eff_over_logN': D_eff / math.log(N) if N > 1 else 0,
        'log_tam': log_tam,
        'log_tam_over_logN': log_tam / math.log(N) if N > 1 else 0,
        'tam_margin': tam_margin,
        'q_cap': q_cap,
        'e_tam': e_tam,
        'e_tam_over_logN': e_tam / math.log(N) if N > 1 else 0,
        'sat_deficit': sat_deficit,
        'sat_deficit_over_logN': sat_deficit / math.log(N) if N > 1 else 0,
        'tam_detail': tam_detail,
    }

# 20 abc-Tripel (kanonisch: a+b=c, gcd(a,b)=1)
triplets = [
    (1, 8, 9),
    (3, 125, 128),
    (1, 80, 81),
    (32, 49, 81),
    (5, 27, 32),
    (13, 243, 256),
    (1, 4374, 4375),
    (2, 6436341, 6436343),   # Reyssat: 2 + 3^10*109 = 23^5
    (1, 2, 3),
    (1, 63, 64),
    (7, 18, 25),
    (1, 242, 243),
    (3, 253, 256),
    (1, 2400, 2401),
    (1, 4913, 4914),
    (2, 6561, 6563),
    (1, 12167, 12168),
    (1, 512, 513),
    (1, 48, 49),
    (5, 1024, 1029),
]

# Validate and deduplicate
clean = []
seen = set()
for a, b, c in triplets:
    if a + b == c and math.gcd(a, b) == 1 and (a, b, c) not in seen:
        clean.append((a, b, c))
        seen.add((a, b, c))

# Sort by q (descending)
clean.sort(key=lambda t: math.log(t[2]) / math.log(rad(t[0]*t[1]*t[2])), reverse=True)

print("=" * 130)
print(f"{'Tripel':<28} {'q':>5} {'D_eff':>7} {'D/lnN':>6} {'ln(Pc_p)':>8} {'Tc/lnN':>6} {'E_tam':>7} {'Et/lnN':>6} {'Q_cap':>5} {'SatDef':>7} {'SD/lnN':>6}")
print("=" * 130)

results = []
for a, b, c in clean:
    m = compute_metrics(a, b, c)
    results.append(m)
    label = f"({a},{b},{c})"
    print(f"{label:<28} {m['q']:>5.3f} {m['D_eff']:>7.3f} {m['D_eff_over_logN']:>6.3f} "
          f"{m['log_tam']:>8.3f} {m['log_tam_over_logN']:>6.3f} "
          f"{m['e_tam']:>7.3f} {m['e_tam_over_logN']:>6.3f} "
          f"{m['q_cap']:>5.3f} {m['sat_deficit']:>7.3f} {m['sat_deficit_over_logN']:>6.3f}")

print("\n" + "=" * 130)
print("\n## ANALYSE: Skalierung der drei Groessen relativ zu log(N)")
print()

# Separate by D_eff sign
pos = [r for r in results if r['D_eff'] > 0]
neg = [r for r in results if r['D_eff'] <= 0]

print(f"Tripel mit D_eff > 0: {len(pos)}")
print(f"Tripel mit D_eff <= 0: {len(neg)}")
print()

if pos:
    print("## Detailanalyse D_eff > 0 Tripel:")
    print(f"{'Tripel':<28} {'D_eff':>7} {'ln(Pc_p)':>8} {'Ratio':>6} {'E_tam':>7} {'E/D':>6} Tamagawa")
    for r in pos:
        ratio = r['log_tam'] / r['D_eff']
        e_ratio = r['e_tam'] / r['D_eff'] if r['D_eff'] > 0 else 0
        tam_str = str({p: v for p, v in sorted(r['tam_detail'].items())})
        print(f"  ({r['a']},{r['b']},{r['c']})".ljust(28) +
              f" {r['D_eff']:>7.3f} {r['log_tam']:>8.3f} {ratio:>6.2f} "
              f"{r['e_tam']:>7.3f} {e_ratio:>6.2f}  {tam_str}")

print()
print("## KERNTEST: Korrelation und Proportionalitaet")
print()

if len(pos) > 2:
    d_vals = [r['D_eff'] for r in pos]
    t_vals = [r['log_tam'] for r in pos]
    e_vals = [r['e_tam'] for r in pos]
    s_vals = [r['sat_deficit'] for r in pos]

    def corr(x, y):
        n = len(x)
        mx, my = sum(x)/n, sum(y)/n
        cov = sum((a-mx)*(b-my) for a, b in zip(x, y)) / n
        sx = (sum((a-mx)**2 for a in x) / n) ** 0.5
        sy = (sum((b-my)**2 for b in y) / n) ** 0.5
        return cov / (sx * sy) if sx > 0 and sy > 0 else 0

    print(f"  r(D_eff, log(Pc_p)) = {corr(d_vals, t_vals):.4f}")
    print(f"  r(D_eff, E_tam)     = {corr(d_vals, e_vals):.4f}")
    print(f"  r(D_eff, SatDef)    = {corr(d_vals, s_vals):.4f}")
    print()

    # Ratio stability
    ratios_t = [t/d for t, d in zip(t_vals, d_vals)]
    ratios_e = [e/d for e, d in zip(e_vals, d_vals)]
    print(f"  log(Pc_p)/D_eff: mean={sum(ratios_t)/len(ratios_t):.3f}, "
          f"std={( sum((r - sum(ratios_t)/len(ratios_t))**2 for r in ratios_t)/len(ratios_t) )**0.5:.3f}")
    print(f"  E_tam/D_eff:     mean={sum(ratios_e)/len(ratios_e):.3f}, "
          f"std={( sum((r - sum(ratios_e)/len(ratios_e))**2 for r in ratios_e)/len(ratios_e) )**0.5:.3f}")

print()
print("## ENTSCHEIDENDE FRAGE: Ist E_tam (= log(Pc_p) - log(N)) proportional zu D_eff?")
print("   Falls JA: Route 11 = Route 12 in Verkleidung (GLEICHE Skalierung)")
print("   Falls NEIN: Route 11 hat EIGENE Information (verschiedene Skalierung)")
print()

# Check if Tamagawa grows with N independently of D_eff
print("## Tamagawa-Skalierung fuer ALLE Tripel (auch D_eff <= 0):")
print(f"{'Tripel':<28} {'logN':>5} {'ln(Pc_p)':>8} {'E_tam':>7} {'E/lnN':>6}")
for r in results:
    print(f"  ({r['a']},{r['b']},{r['c']})".ljust(28) +
          f" {math.log(r['N']):>5.2f} {r['log_tam']:>8.3f} {r['e_tam']:>7.3f} {r['e_tam_over_logN']:>6.3f}")

# Final verdict
print()
print("=" * 80)
print("## VERDICT")
print("=" * 80)
all_e_over_logN = [r['e_tam_over_logN'] for r in results]
pos_e_over_logN = [r['e_tam_over_logN'] for r in pos]
print(f"  E_tam/logN (alle):   mean={sum(all_e_over_logN)/len(all_e_over_logN):.4f}, "
      f"max={max(all_e_over_logN):.4f}, min={min(all_e_over_logN):.4f}")
if pos_e_over_logN:
    print(f"  E_tam/logN (D>0):    mean={sum(pos_e_over_logN)/len(pos_e_over_logN):.4f}, "
          f"max={max(pos_e_over_logN):.4f}")
    pos_d_over_logN = [r['D_eff_over_logN'] for r in pos]
    print(f"  D_eff/logN (D>0):    mean={sum(pos_d_over_logN)/len(pos_d_over_logN):.4f}, "
          f"max={max(pos_d_over_logN):.4f}")
    print()
    # Key comparison
    for r in pos:
        gap = r['e_tam_over_logN'] - r['D_eff_over_logN']
        print(f"  ({r['a']},{r['b']},{r['c']}): E_tam/logN - D_eff/logN = {gap:+.4f} "
              f"{'<-- Tam DECKT D_eff' if gap > 0 else '<-- Tam DECKT NICHT'}")
