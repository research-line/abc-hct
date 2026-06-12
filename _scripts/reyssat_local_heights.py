"""
Q1/Q2 Analysis: Local height structure at CD-inert primes for Reyssat.

Complements the PARI/GP L-value computation with:
- Detailed Kodaira/Tamagawa analysis (from gp output)
- Component group structure at each bad prime
- Heegner hypothesis verification for multiple D
- Theoretical analysis of r_p at CD primes
"""
import math
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

def kronecker(D, n):
    if n == 0:
        return 1 if abs(D) == 1 else 0
    if n == 1:
        return 1
    if n == 2:
        d8 = D % 8
        if d8 in (1, 7):
            return 1
        elif d8 in (3, 5):
            return -1
        else:
            return 0
    if n < 0:
        return kronecker(D, -n) * (-1 if D < 0 else 1)
    result = 1
    temp = n
    while temp % 2 == 0:
        result *= kronecker(D, 2)
        temp //= 2
    if temp == 1:
        return result
    d = 3
    while d * d <= temp:
        while temp % d == 0:
            result *= legendre(D, d)
            temp //= d
        d += 2
    if temp > 1:
        result *= legendre(D, temp)
    return result

def legendre(a, p):
    a = a % p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r

def is_fundamental_discriminant(D):
    if D == 0:
        return False
    if D == 1:
        return False
    absD = abs(D)
    if absD % 4 == 0:
        m = absD // 4
        if m % 4 in (2, 3):
            d = 2
            while d * d <= m:
                if m % (d * d) == 0:
                    return False
                d += 1
            return True
        return False
    elif absD % 4 == 3:
        d = 2
        while d * d <= absD:
            if absD % (d * d) == 0:
                return False
            d += 1
        return True
    return False

def class_number_naive(D):
    """Naive class number computation for negative fundamental discriminant."""
    if D >= 0:
        return 0
    absD = abs(D)
    h = 0
    limit = int(math.sqrt(absD / 3)) + 1
    for b in range(0, limit + 1):
        b2 = b * b
        if (absD - b2) % 4 != 0 if absD % 4 == 3 else (absD - b2) % 4 != 0:
            if b == 0:
                rem = absD
            else:
                rem = absD - b2
            if rem < 0:
                break
        for a in range(max(1, b), int(math.sqrt(absD)) + 1):
            c_val = (b * b + absD)
            if c_val % (4 * a) != 0:
                continue
            c_val = c_val // (4 * a)
            if c_val < a:
                continue
            if a == b or a == c_val:
                h += 1
            elif b == 0:
                h += 1 if a == c_val else 2
            else:
                h += 2
    return h

a, b = 2, 6436341
c = a + b
N = 15042

print("=" * 70)
print("Q1/Q2: LOCAL HEIGHT STRUCTURE FOR REYSSAT")
print("=" * 70)

print(f"\nTriple: ({a}, {b}, {c})")
print(f"  b = 3^10 * 109 = {3**10 * 109}")
print(f"  c = 23^5 = {23**5}")
print(f"  N = rad(abc) = 2 * 3 * 23 * 109 = {2*3*23*109}")

print("\n--- HEEGNER HYPOTHESIS SCAN ---")
print("Finding fundamental discriminants D < 0 where all p|N split in Q(sqrt(D)).")
print("Condition: (D/p) = +1 for p in {2, 3, 23, 109}")
print()

bad_primes = [2, 3, 23, 109]
candidates = []

for absD in range(3, 500):
    D = -absD
    if not is_fundamental_discriminant(D):
        continue
    ok = True
    for p in bad_primes:
        if kronecker(D, p) != 1:
            ok = False
            break
    if not ok:
        continue
    h = class_number_naive(D)
    candidates.append((D, h))

print(f"Found {len(candidates)} candidates with |D| < 500:")
print(f"{'D':>6} {'h_K':>4} {'(D/2)':>6} {'(D/3)':>6} {'(D/23)':>6} {'(D/109)':>7}")
print("-" * 45)
for D, h in candidates[:30]:
    print(f"{D:>6} {h:>4} {kronecker(D,2):>6} {kronecker(D,3):>6} "
          f"{kronecker(D,23):>6} {kronecker(D,109):>7}")

print(f"\n  Total candidates: {len(candidates)}")
print(f"  Smallest |D|: {candidates[0][0] if candidates else 'none'}")
print(f"  Smallest h=1: ", end="")
h1 = [d for d, h in candidates if h == 1]
print(f"{h1[0] if h1 else 'none'} ({len(h1)} total)")

print("\n--- CD-INERT ANALYSIS FOR D=-31 ---")
D = -31
print(f"\nD = {D}, h_K = {class_number_naive(D)}")
print(f"Q(sqrt({D})) = Q(sqrt(-31))")

print("\nKronecker symbols at bad primes:")
for p in bad_primes:
    kr = kronecker(D, p)
    status = "SPLIT" if kr == 1 else ("INERT" if kr == -1 else "RAMIFIED")
    print(f"  (D/{p}) = {kr:+d}  =>  {p} is {status} in Q(sqrt({D}))")

print("\n  Primes 3, 23 are INERT => they go into quaternion discriminant")
print("  Primes 2, 109 SPLIT => they go into the level")
print("  Shimura curve: X_0^{3*23}(2*109) = X_0^69(218)")

print("\n--- THEORETICAL COMPONENT ANALYSIS ---")
print()
print("At CD-inert primes (p=3, p=23):")
print("  The Cerednik-Drinfeld uniformization applies.")
print("  The special fiber is a quotient of the Bruhat-Tits tree of PGL_2(Q_p).")
print()
print("  Key theorem (Zhang 2001, Thm 6.1):")
print("  For O_K -> R an optimal embedding (R = Eichler order),")
print("  the Heegner point P_K reduces to the vertex/edge of the BT tree")
print("  determined by the embedding. At an INERT prime p, the CM point")
print("  maps to a SPECIAL vertex (not a generic edge), typically in")
print("  the identity component of the Neron model.")
print()
print("  Standard result: If p is inert in K and p | disc(quaternion),")
print("  then the standard Heegner point reduces to the IDENTITY COMPONENT")
print("  of the special fiber. This means r_p = 0 and lambda_p(P) = 0.")
print()
print("  HOWEVER: This applies to the STANDARD construction. Alternatives:")
print("  (a) Higher conductor c > 1: O_c = Z + c*O_K with p | c")
print("      can shift the component. But this changes the GZ formula.")
print("  (b) Different D: Choose D where 3, 23 SPLIT (not inert).")
print("      Then these primes go into the level, not the quaternion disc.")
print("  (c) Stark-Heegner points: p-adic construction that may land")
print("      on non-identity components. Not covered by classical GZ.")

print("\n--- ALTERNATIVE D: PRIMES 3, 23 SPLIT ---")
print("Looking for D where ALL of {2, 3, 23, 109} split (including 3, 23):")
print("This avoids CD-inert issues by putting all primes in the level.")
print()

alt_candidates = []
for D_val, h in candidates:
    if kronecker(D_val, 3) == 1 and kronecker(D_val, 23) == 1:
        alt_candidates.append((D_val, h))

if alt_candidates:
    print(f"{'D':>6} {'h_K':>4}  Note")
    print("-" * 30)
    for D_val, h in alt_candidates[:15]:
        note = ""
        if h == 1:
            note = "  <-- class number 1"
        print(f"{D_val:>6} {h:>4}{note}")
    print(f"\n  {len(alt_candidates)} candidates found.")
    print("  For these D, the Shimura curve is X_0^1(N) = X_0(N),")
    print("  the classical modular curve. No CD-uniformization issues.")
    print("  Standard Heegner point construction applies with")
    print("  local heights from the Neron model cycle graph.")
else:
    print("  No candidates found in range!")

print("\n--- LOCAL NERON-TATE HEIGHT ESTIMATE (CLASSICAL CASE) ---")
print("For D where all p|N split, the classical GZ formula applies.")
print("The local height at p|N with multiplicative reduction (Kodaira I_n):")
print("  lambda_p(P) = (r/c_p)(1 - r/c_p) * v_p(Delta) * log(p)")
print("  where c_p = Tamagawa number, r = component index of P mod p")
print()

Delta = 16 * (a * b * c) ** 2
print(f"Discriminant Delta = 16*(abc)^2 = {Delta}")
print(f"log(Delta) = {math.log(Delta):.4f}")
print()

for p in bad_primes:
    vp = 0
    temp = Delta
    while temp % p == 0:
        vp += 1
        temp //= p
    print(f"  p={p}: v_p(Delta) = {vp}")

print("\nNOTE: Actual Kodaira types, Tamagawa numbers, and minimal")
print("discriminant exponents come from the gp computation.")
print("The above v_p(Delta) is for the NON-MINIMAL model.")

print("\n--- NAIVE LOCAL HEIGHT BUDGET (IF ALL r_p OPTIMAL) ---")
print("Maximum possible local heights (r = c_p/2 approximation):")
print("(Requires actual c_p from gp output to be precise)")
print()

for p in bad_primes:
    vp = 0
    temp = Delta
    while temp % p == 0:
        vp += 1
        temp //= p
    lam_max = vp * math.log(p) / 4
    print(f"  p={p}: lambda_max = v_p(Delta)*log(p)/4 = {vp}*{math.log(p):.4f}/4 = {lam_max:.4f}")

total_max = sum(
    (lambda p: (sum(1 for _ in iter(lambda: Delta % p == 0, False)) if False else
     (lambda: (v := 0, d := Delta, [(v := v + 1, d := d // p) for _ in range(100) if d % p == 0], v)[-1])()))(p)
    for p in bad_primes
)

print("\n--- DEFECT THAT HEEGNER ROUTE MUST PAY ---")
q = math.log(c) / math.log(2 * 3 * 23 * 109)
print(f"  q = log(c)/log(N) = {q:.4f}")
print(f"  q - 1 = {q - 1:.4f} (raw quality excess)")

u = 3
q_eff = q - 2 * math.log(u * math.pi) / math.log(N)
print(f"  u = {u} (Neron scaling factor)")
print(f"  q_eff = q - 2*log(u*pi)/log(N) = {q_eff:.4f}")
print(f"  q_eff - 1 = {q_eff - 1:.4f} (residual excess for Heegner)")
print(f"  Required log-height: (q_eff - 1)*log(N)/2 = {(q_eff - 1)*math.log(N)/2:.4f}")
print(f"  Required linear factor: N^{{(q_eff-1)/2}} = {N**((q_eff-1)/2):.4f}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Key findings:
1. D=-31 causes CD-inert issues at p=3,23 (as documented in BEWEISNOTIZ).
2. Alternative discriminants where all p|N SPLIT avoid this entirely.
3. For split-everywhere D, the classical modular curve X_0(N) is used,
   with standard Neron model local heights (cycle graph formula applies).
4. The actual viability depends on L(E, chi_D, 1) != 0,
   which is computed by the PARI/GP script.
""")
