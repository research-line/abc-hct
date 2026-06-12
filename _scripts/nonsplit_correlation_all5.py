"""Test correlation: Does eps=+1 orientation systematically give nonsplit reduction?

For each mining triplet, compute split/nonsplit at all odd bad primes
for BOTH orientations, and check which orientation has eps=+1.
"""
import math

def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1

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

def analyze_orientation(a, b, name):
    """Analyze split/nonsplit at all odd primes for E_{a,b}."""
    c = a + b
    abc = a * b * c
    odd_primes = [p for p in factorize(abc).keys() if p > 2]

    results = []
    prod_wp = 1  # product of local root numbers at odd primes

    for p in sorted(odd_primes):
        if a % p == 0:
            who = 'a'
            is_split = legendre(b, p) == 1
        elif b % p == 0:
            who = 'b'
            is_split = legendre(-a, p) == 1
        else:
            who = 'c'
            is_split = legendre(a, p) == 1

        wp = -1 if is_split else 1
        prod_wp *= wp
        vp = factorize(abc)[p]
        cp = 2 * vp if is_split else (2 if (2*vp) % 2 == 0 else 1)
        results.append((p, who, is_split, wp, cp, vp))

    # eps = w_inf * w_2 * prod_wp = (-1) * w_2 * prod_wp
    # We know eps from PARI data, but we can infer w_2 from:
    # If eps=+1: w_2 = -1/prod_wp (needs prod_wp = -1 for w_2=+1, or prod_wp=+1 for w_2=-1)
    return results, prod_wp

# Mining triplets - both orientations
# Format: (a, b, triplet_name, known_eps_for_E_ab)
triplets = [
    # (1,8,9): PARI says eps=+1 for BOTH orientations
    (1, 8, "(1,8,9)", +1),
    (8, 1, "(8,1,9)", +1),

    # (3,125,128): PARI says eps=+1 for BOTH
    (3, 125, "(3,125,128)", +1),
    (125, 3, "(125,3,128)", +1),

    # (1,4374,4375): PARI says eps=+1 for BOTH
    (1, 4374, "(1,4374,4375)", +1),
    (4374, 1, "(4374,1,4375)", +1),

    # (1,2400,2401): PARI says eps=+1 for BOTH
    (1, 2400, "(1,2400,2401)", +1),
    (2400, 1, "(2400,1,2401)", +1),

    # Reyssat: eps=-1 for E_{2,6436341}, eps=+1 for E_{6436341,2}
    (2, 6436341, "Reyssat(2,b)", -1),
    (6436341, 2, "Reyssat(b,2)", +1),
]

print("=" * 85)
print("NONSPLIT-KORRELATION: Ist eps=+1 systematisch mit nonsplit korreliert?")
print("=" * 85)
print()
print(f"{'Orientierung':<22} {'eps':>4} {'#split':>7} {'#nonsplit':>9} {'prod_cp':>8} {'Muster':<15}")
print("-" * 85)

for a, b, name, known_eps in triplets:
    results, prod_wp = analyze_orientation(a, b, name)
    n_split = sum(1 for r in results if r[2])
    n_nonsplit = sum(1 for r in results if not r[2])
    prod_cp = math.prod(r[4] for r in results)

    # Determine pattern
    if n_split == 0:
        pattern = "ALL NONSPLIT"
    elif n_nonsplit == 0:
        pattern = "ALL SPLIT"
    else:
        pattern = "MIXED"

    eps_str = "+1" if known_eps == 1 else "-1"
    label = f"E_{{{name}}}"
    print(f"{label:<22} {eps_str:>4} {n_split:>7} {n_nonsplit:>9} {prod_cp:>8} {pattern:<15}")

    # Detail
    for p, who, is_split, wp, cp, vp in results:
        status = "SPLIT" if is_split else "nonsplit"
        print(f"    p={p:<5} ({who}|{p}, e={vp}): {status:>8}, c_p={cp}, w_p={wp:+d}")
    print()

print("=" * 85)
print("AUSWERTUNG")
print("=" * 85)
print()

# Count correlation
eps_plus_all_nonsplit = 0
eps_plus_not_all_nonsplit = 0
eps_plus_total = 0

for a, b, name, known_eps in triplets:
    if known_eps != +1:
        continue
    eps_plus_total += 1
    results, _ = analyze_orientation(a, b, name)
    n_split = sum(1 for r in results if r[2])
    if n_split == 0:
        eps_plus_all_nonsplit += 1
    else:
        eps_plus_not_all_nonsplit += 1

print(f"Von {eps_plus_total} Orientierungen mit eps=+1:")
print(f"  ALL NONSPLIT: {eps_plus_all_nonsplit}")
print(f"  NICHT all nonsplit: {eps_plus_not_all_nonsplit}")
print()
print("FAZIT: ", end="")
if eps_plus_all_nonsplit == eps_plus_total:
    print("PERFEKTE KORRELATION! eps=+1 => alle odd primes nonsplit.")
elif eps_plus_all_nonsplit > eps_plus_total / 2:
    print("STARKE KORRELATION, aber nicht perfekt.")
else:
    print("KEINE systematische Korrelation. Reyssat war Zufall.")
