"""
SUPERSEDED — Use pari_p2_results.jsonl (PARI/GP ground truth) instead.

The (c4, c6, Delta) test below is NECESSARY but NOT SUFFICIENT at p=2.
4 of 15 triples are misclassified (classic_2401, 1+80=81, 3+125=128, 625+2048=2673).
The claim "multiplicative iff v2(abc)>=4" is FALSE. See em1b_pari_p2.gp for correct analysis.

Original docstring (for reference):
Minimality and reduction type at p=2 for Frey curves Y^2 = X(X-a)(X+b).

Uses the (c4, c6, Delta) minimality criterion:
  Non-minimal at p iff v_p(c4) >= 4 AND v_p(c6) >= 6 AND v_p(Delta) >= 12.

Key structural result for Frey curves with gcd(a,b)=1:
  c4 = 16*(a^2 + ab + b^2), and a^2+ab+b^2 is ALWAYS odd for coprime a,b.
  Therefore v2(c4) = 4 exactly, so at most ONE u=2 substitution is possible.

  c6 = -32*(b-a)*(2a+b)*(a+2b), and v2(c6) >= 6 always for coprime a,b.

  Delta = 16*(abc)^2, so v2(Delta) = 4 + 2*v2(abc).

Partition:
  - v2(abc) >= 4: model non-minimal, after u=2 get v2(c4_min)=0 -> MULTIPLICATIVE, f2=1
  - v2(abc) <= 3: model IS minimal, v2(c4)=4>0 -> ADDITIVE, f2 >= 2
"""

import json
import os


def val(n, p):
    if n == 0:
        return float('inf')
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def analyze_frey_p2(a, b, label=""):
    c = a + b
    assert c > 0 and a > 0 and b > 0
    from math import gcd
    assert gcd(a, b) == 1, f"gcd({a},{b})={gcd(a,b)}, must be 1"

    a2_coeff = b - a
    a4_coeff = -a * b

    # Weierstrass invariants for [0, b-a, 0, -ab, 0]
    b2 = 4 * a2_coeff
    b4 = 2 * a4_coeff
    c4 = 16 * (a**2 + a*b + b**2)
    c6 = -32 * (b - a) * (2*a + b) * (a + 2*b)
    Delta = 16 * (a * b * c)**2

    v2_c4 = val(c4, 2)
    v2_c6 = val(c6, 2)
    v2_Delta = val(Delta, 2)
    v2_abc = val(a * b * c, 2)

    # Verify structural claims
    inner = a**2 + a*b + b**2
    assert inner % 2 == 1, f"a^2+ab+b^2={inner} should be odd for coprime a,b"
    assert v2_c4 == 4, f"v2(c4)={v2_c4}, expected 4"
    assert v2_Delta == 4 + 2*v2_abc, f"v2(Delta)={v2_Delta}, expected {4+2*v2_abc}"

    # Minimality test: non-minimal iff v2(c4)>=4 AND v2(c6)>=6 AND v2(Delta)>=12
    can_reduce = (v2_c4 >= 4) and (v2_c6 >= 6) and (v2_Delta >= 12)

    # k_max = min(floor(v2(c4)/4), floor(v2(c6)/6), floor(v2(Delta)/12))
    k_max = min(v2_c4 // 4, v2_c6 // 6, v2_Delta // 12)

    # After k_max applications of u=2:
    v2_c4_min = v2_c4 - 4 * k_max
    v2_c6_min = v2_c6 - 6 * k_max
    v2_Delta_min = v2_Delta - 12 * k_max

    if v2_Delta_min == 0:
        reduction = "good"
        f2 = 0
        kodaira = "I_0"
    elif v2_c4_min == 0:
        reduction = "multiplicative"
        f2 = 1
        n = v2_Delta_min
        kodaira = f"I_{n}"
    else:
        reduction = "additive"
        f2 = ">=2 (exact needs full Tate)"
        kodaira = "additive (exact type needs full Tate at p=2)"

    # For multiplicative: N = rad(abc) since f2=1
    # For additive: N = 2^f2 * rad_odd(abc), f2 >= 2
    rad_abc = 1
    for x in [a, b, c]:
        temp = abs(x)
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                rad_abc *= d
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            rad_abc *= temp
    # Remove duplicate primes (product of distinct primes dividing abc)
    primes_abc = set()
    for x in [a, b, c]:
        temp = abs(x)
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                primes_abc.add(d)
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            primes_abc.add(temp)
    rad_abc = 1
    for p in primes_abc:
        rad_abc *= p

    rad_odd = rad_abc // 2 if 2 in primes_abc else rad_abc

    if reduction == "good":
        N_equals_rad = False
        conductor_note = f"N = rad_odd(abc) = {rad_odd} (good at 2, no factor of 2 in N)"
    elif reduction == "multiplicative":
        N_equals_rad = True
        conductor_note = f"N = rad(abc) = {rad_abc}"
    else:
        N_equals_rad = False
        conductor_note = f"N = 2^f2 * rad_odd(abc), f2>=2, N > rad(abc)"

    return {
        "label": label,
        "a": a,
        "b": b,
        "c": c,
        "v2_abc": v2_abc,
        "v2_c4": v2_c4,
        "v2_c6": v2_c6,
        "v2_Delta": v2_Delta,
        "k_max": k_max,
        "v2_c4_min": v2_c4_min,
        "v2_Delta_min": v2_Delta_min,
        "reduction_at_2": reduction,
        "kodaira_p2": kodaira,
        "f2": f2,
        "N_equals_rad_abc": N_equals_rad,
        "rad_abc": rad_abc,
        "conductor_note": conductor_note,
    }


TRIPLES = [
    (2, 3**10 * 109, "Reyssat"),
    (11**2, 3**2 * 5**6 * 7**3, "ABCHome_2"),
    (1, 2 * 3**7, "classic_4374"),
    (1, 2400, "classic_2401"),
    (1, 8, "1+8=9"),
    (1, 63, "1+63=64"),
    (1, 80, "1+80=81"),
    (5, 27, "5+27=32"),
    (3, 125, "3+125=128"),
    (13, 243, "13+243=256"),
    (32, 49, "32+49=81"),
    (1, 4374, "1+4374=4375_dup"),
    (1, 2**12 - 1, "1+4095=4096"),
    (625, 2048, "625+2048=2673"),
    (1, 1023, "1+1023=1024"),
]


if __name__ == "__main__":
    results = []
    additive_triples = []
    multiplicative_triples = []

    for a, b, label in TRIPLES:
        r = analyze_frey_p2(a, b, label)
        results.append(r)

        if r["reduction_at_2"] == "multiplicative":
            multiplicative_triples.append(label)
        elif r["reduction_at_2"] == "additive":
            additive_triples.append(label)

        print(f"\n{'='*70}")
        print(f"  {label}: a={a}, b={b}, c={a+b}")
        print(f"  v2(abc)={r['v2_abc']}, v2(c4)={r['v2_c4']}, "
              f"v2(c6)={r['v2_c6']}, v2(Delta)={r['v2_Delta']}")
        print(f"  k_max={r['k_max']} -> v2(c4_min)={r['v2_c4_min']}, "
              f"v2(Delta_min)={r['v2_Delta_min']}")
        print(f"  REDUCTION at p=2: {r['reduction_at_2'].upper()}")
        print(f"  Kodaira: {r['kodaira_p2']}, f2={r['f2']}")
        print(f"  N = rad(abc)? {r['N_equals_rad_abc']}")
        print(f"  {r['conductor_note']}")

    print(f"\n{'='*70}")
    good_triples = [r["label"] for r in results if r["reduction_at_2"] == "good"]

    print(f"\nSUMMARY: {len(good_triples)} good, {len(multiplicative_triples)} multiplicative, "
          f"{len(additive_triples)} additive")
    if good_triples:
        print(f"\nGOOD at p=2 (f2=0, N = rad_odd(abc) < rad(abc)):")
        for t in good_triples:
            print(f"  - {t}")
    print(f"\nMULTIPLICATIVE (semistable at 2, N=rad(abc)):")
    for t in multiplicative_triples:
        print(f"  - {t}")
    print(f"\nADDITIVE (non-semistable at 2, N > rad(abc)):")
    for t in additive_triples:
        print(f"  - {t}")

    print(f"\nCRITERION: multiplicative iff v2(abc) >= 4")
    print(f"           additive iff v2(abc) in {{1,2,3}}")

    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "_data", "em1")
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "tate_p2_analysis.json")

    output = {
        "method": "(c4, c6, Delta) minimality test",
        "structural_result": (
            "For Frey curves Y^2=X(X-a)(X+b) with gcd(a,b)=1: "
            "v2(c4)=4 always; multiplicative at 2 iff v2(abc)>=4; "
            "additive iff v2(abc) in {1,2,3}."
        ),
        "partition": {
            "good": [r["label"] for r in results if r["reduction_at_2"] == "good"],
            "multiplicative": multiplicative_triples,
            "additive": additive_triples,
        },
        "triples": results,
    }

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str, ensure_ascii=False)
    print(f"\nJSON saved: {outpath}")
