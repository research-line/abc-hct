# OBSOLETE: alte u-Formel (u_odd != 1), siehe _scripts/d_eff_ledger_corrected.py (Loop 39).
"""Level-Lowering Capacity: NUR ell >= 3 (ell=2 ist trivial fuer Frey-Kurven!)

Fuer Frey-Kurven: v_p(Delta) = 2*v_p(abc) fuer p ungerade,
                  v_2(Delta) = 4 + 2*v_2(abc).
Damit ist v_p(Delta) IMMER GERADE => ell=2 laesst ALLE Primen fallen.
C_LL(2) = log(N) ist trivial!

Nicht-triviales Level-Lowering: ell >= 3, d.h. ell | 2*v_p(abc).
Da ell ungerade: ell | 2*v_p(abc) <=> ell | v_p(abc).
Also: S_ell = {p : ell | v_p(abc)}.

Zusaetzlich: minimale gewichtete S-Unit-Laenge mu_{p,e}(S_ab).
"""
import math
from itertools import product as iterproduct

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
    (1, 8, 9), (3, 125, 128), (1, 80, 81), (32, 49, 81),
    (5, 27, 32), (13, 243, 256), (1, 4374, 4375),
    (2, 6436341, 6436343),
    (1, 2, 3), (1, 63, 64), (7, 18, 25), (1, 242, 243),
    (3, 253, 256), (1, 2400, 2401), (1, 4913, 4914),
    (2, 6561, 6563), (1, 12167, 12168), (1, 512, 513),
    (1, 48, 49), (5, 1024, 1029),
]

clean = [(a,b,c) for a,b,c in triplets if a+b==c and math.gcd(a,b)==1]
clean.sort(key=lambda t: math.log(t[2])/math.log(rad(t[0]*t[1]*t[2])), reverse=True)

print("=" * 120)
print("LEVEL-LOWERING CAPACITY: NUR ell >= 3 (nicht-trivial)")
print("=" * 120)
print()
print("Erklaerung: Fuer Frey-Kurven ist v_p(Delta) = 2*v_p(abc) stets gerade.")
print("ell=2 faellt TRIVIAL alle Primen -> C_LL(2) = log(N). Nutzlos!")
print("Nicht-trivial: ell >= 3, d.h. ell | v_p(abc) (da ell ungerade, 2 kuerzt sich).")
print()
print(f"{'Tripel':<28} {'q':>5} {'D_eff':>7} {'C_LL3+':>7} {'ell*':>4} {'Primes':>15} {'Deckt?':>8} {'Gap':>7}")
print("-" * 95)

results = []
for a, b, c in clean:
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a * b * c)
    logN = math.log(N)
    q_val = math.log(c) / logN

    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)
    D_eff = math.log(c) - logN - 2*log_u

    # v_p(abc) for each prime
    v_abc = {}
    for p in all_primes:
        v_abc[p] = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)

    # For each PRIME ell >= 3, ell ∤ N: S_ell = {p | N : ell | v_p(abc)}
    best_ell = 0
    best_c_ll = 0
    best_primes = []

    primes_list = [3, 5, 7, 11, 13, 17, 19, 23, 29]
    for ell in primes_list:
        if N % ell == 0:
            continue
        dropped = [p for p in all_primes if v_abc.get(p, 0) >= ell and v_abc[p] % ell == 0]
        if dropped:
            c_ll = sum(math.log(p) for p in dropped)
            if c_ll > best_c_ll:
                best_c_ll = c_ll
                best_ell = ell
                best_primes = sorted(dropped)

    gap = best_c_ll - D_eff
    covers = "JA" if best_c_ll > max(0, D_eff) else "NEIN"

    label = f"({a},{b},{c})"
    primes_str = str(best_primes) if best_primes else "KEINE"
    print(f"{label:<28} {q_val:>5.3f} {D_eff:>7.3f} {best_c_ll:>7.3f} {best_ell:>4} {primes_str:>15} {covers:>8} {gap:>+7.3f}")

    results.append({'a':a,'b':b,'c':c,'q':q_val,'D_eff':D_eff,
                    'C_LL':best_c_ll,'ell':best_ell,'primes':best_primes,'gap':gap})

print()
covered = sum(1 for r in results if r['D_eff'] > 0 and r['gap'] > 0)
total = sum(1 for r in results if r['D_eff'] > 0)
print(f"Nicht-triviales LL deckt: {covered}/{total} Tripel mit D_eff > 0")
not_covered = [r for r in results if r['D_eff'] > 0 and r['gap'] <= 0]
if not_covered:
    print("\nNICHT GEDECKT:")
    for r in not_covered:
        print(f"  ({r['a']},{r['b']},{r['c']}): D_eff={r['D_eff']:.3f}, C_LL(ell>={3})={r['C_LL']:.3f}")

# ===== PART 2: Minimal weighted S-Unit representation =====
print()
print("=" * 120)
print("S-UNIT MINIMALE GEWICHTETE LAENGE: mu_{p,e}(S_ab)")
print("=" * 120)
print()
print("Fuer p^e | c (p>2, e>=2): Finde minimales sum |n_q|*log(q) mit prod q^{n_q} = -1 mod p^e")
print("wobei q in S_ab = {Primteiler von a*b}.")
print("Vergleiche mu mit e*log(p) = Defekt-Beitrag dieser Prim.")
print()

def find_min_representation(target_mod, generators, modulus, max_exp=20):
    """Find minimal weighted representation of target_mod in (Z/modulus)^x
    using generators with weights log(g).
    Uses BFS on weighted exponent vectors."""
    if modulus <= 1:
        return 0, []

    # For small cases, BFS
    # target: we want prod g_i^{n_i} = target mod modulus
    # minimize: sum |n_i| * log(g_i)
    # Strategy: iterative deepening on total weight

    n_gens = len(generators)
    if n_gens == 0:
        return float('inf'), []

    # Precompute generator powers mod modulus
    gen_powers = []  # gen_powers[i][k] = generators[i]^k mod modulus
    gen_inv_powers = []  # gen_powers[i][-k] = generators[i]^{-k} mod modulus
    for g in generators:
        if math.gcd(g, modulus) != 1:
            gen_powers.append({0: 1})
            gen_inv_powers.append({0: 1})
            continue
        powers = {0: 1}
        inv_powers = {0: 1}
        g_inv = pow(g, -1, modulus)
        val = 1
        inv_val = 1
        for k in range(1, max_exp + 1):
            val = (val * g) % modulus
            inv_val = (inv_val * g_inv) % modulus
            powers[k] = val
            inv_powers[k] = inv_val
        gen_powers.append(powers)
        gen_inv_powers.append(inv_powers)

    # BFS: find minimal cost path to target
    best_cost = float('inf')
    best_exps = []

    # For small number of generators, try exhaustive
    if n_gens <= 3 and max_exp <= 15:
        ranges = [range(-min(max_exp, 12), min(max_exp, 12)+1) for _ in range(n_gens)]
        for exps in iterproduct(*ranges):
            if all(e == 0 for e in exps):
                continue
            val = 1
            valid = True
            for i, e in enumerate(exps):
                if e > 0 and e in gen_powers[i]:
                    val = (val * gen_powers[i][e]) % modulus
                elif e < 0 and (-e) in gen_inv_powers[i]:
                    val = (val * gen_inv_powers[i][-e]) % modulus
                elif e == 0:
                    pass
                else:
                    valid = False
                    break
            if not valid:
                continue
            if val == target_mod % modulus:
                cost = sum(abs(e) * math.log(generators[i]) for i, e in enumerate(exps))
                if cost < best_cost:
                    best_cost = cost
                    best_exps = list(exps)

    return best_cost, best_exps


print(f"{'Tripel':<25} {'p^e|c':>10} {'e*logp':>7} {'mu':>8} {'mu/e*logp':>10} {'Exponents':>25}")
print("-" * 100)

for a, b, c in clean:
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    N = rad(a * b * c)
    q_val = math.log(c) / math.log(N)

    # Only D_eff > 0 triplets
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    log_u = 0
    for p in all_primes:
        if p == 2: continue
        vp = fa.get(p,0) + fb.get(p,0) + fc.get(p,0)
        u_p = (2*vp) // 12
        if u_p > 0:
            log_u += u_p * math.log(p)
    D_eff = math.log(c) - math.log(N) - 2*log_u
    if D_eff < 0.5:
        continue

    c_powers = [(p, e) for p, e in fc.items() if p > 2 and e >= 2]
    if not c_powers:
        # Check if defect comes from a or b side
        continue

    S_ab = sorted(set(list(fa.keys()) + list(fb.keys())) - {2})

    label = f"({a},{b},{c})"
    for p_stuck, e_stuck in sorted(c_powers, key=lambda x: x[1]*math.log(x[0]), reverse=True):
        modulus = p_stuck ** e_stuck
        # Target: -1 mod p^e (since a+b=c, p^e|c => a = -b mod p^e => a*b^{-1} = -1 mod p^e)
        target = modulus - 1  # = -1 mod modulus

        # Generators: primes in S_ab coprime to p_stuck
        gens = [q for q in S_ab if q != p_stuck and math.gcd(q, modulus) == 1]
        if not gens:
            print(f"{label:<25} {p_stuck}^{e_stuck}={modulus:>8} {e_stuck*math.log(p_stuck):>7.3f} {'N/A':>8} {'N/A':>10} (no generators)")
            label = " " * 25
            continue

        # Limit search for large moduli
        max_e = min(15, e_stuck * 3)
        mu, exps = find_min_representation(target, gens, modulus, max_exp=max_e)

        if mu == float('inf'):
            mu_str = "INF"
            ratio_str = "INF"
            exp_str = "(not found)"
        else:
            mu_str = f"{mu:.3f}"
            ratio = mu / (e_stuck * math.log(p_stuck))
            ratio_str = f"{ratio:.4f}"
            exp_str = str(dict(zip(gens, exps)))

        print(f"{label:<25} {p_stuck}^{e_stuck}={modulus:>8} {e_stuck*math.log(p_stuck):>7.3f} {mu_str:>8} {ratio_str:>10} {exp_str:>25}")
        label = " " * 25

print()
print("=" * 120)
print("INTERPRETATION")
print("=" * 120)
print()
print("mu/(e*log p) = Verhaeltnis der minimalen S-Unit-Kosten zum Defekt-Beitrag.")
print()
print("Falls mu >= e*log(p) fuer alle stuck primes:")
print("  -> S-Unit-Landung ist MINDESTENS so teuer wie der Defekt")
print("  -> Potentielle Obstruktion!")
print()
print("Falls mu < e*log(p):")
print("  -> Tiefe Landung ist BILLIGER als der Defekt")
print("  -> Keine Obstruktion durch S-Unit-Kosten allein")
