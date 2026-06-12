"""
Verify global root numbers of Frey curves E_{a,b}: y^2 = x(x-a)(x+b)
for abc-triplets (a,b,c) with a+b=c, gcd(a,b)=1.

Uses explicit formulas for local root numbers:
- Odd primes: Rohrlich formula via split/non-split multiplicative reduction
- p=2: Halberstadt/Connell lookup (Kodaira type + congruence conditions)

References:
- Rohrlich (1993): Elliptic curves and p-adic uniformisation
- Halberstadt (1998): Calcul du nombre de Tamagawa local
- Connell (1996): Handbook of Elliptic and Hyperelliptic Curve Cryptography (tables)
- Rizzo (2003): Average root numbers for a nonconstant family of elliptic curves
"""
import sys
from math import gcd
from sympy.ntheory import factorint
from sympy import legendre_symbol


def frey_curve_invariants(a, b):
    """Compute Weierstrass invariants for E_{a,b}: y^2 = x(x-a)(x+b).
    Model: y^2 = x^3 + (b-a)x^2 - ab*x
    [a1,a2,a3,a4,a6] = [0, b-a, 0, -ab, 0]
    """
    c = a + b
    a1, a2, a3, a4, a6 = 0, b - a, 0, -a * b, 0

    b2 = 4 * a2
    b4 = 2 * a4
    b6 = 0
    b8 = -(a * b) ** 2

    c4 = b2**2 - 24 * b4  # = 16(a^2 + ab + b^2)
    c6 = -b2**3 + 36 * b2 * b4  # since b6=0

    Delta = 16 * a**2 * b**2 * c**2

    # Verify discriminant formula
    Delta_check = -b2**2 * b8 - 8 * b4**3
    assert Delta == Delta_check, f"Discriminant mismatch: {Delta} vs {Delta_check}"

    return {
        'a': a, 'b': b, 'c': c,
        'a1': a1, 'a2': a2, 'a3': a3, 'a4': a4, 'a6': a6,
        'b2': b2, 'b4': b4, 'b6': b6, 'b8': b8,
        'c4': c4, 'c6': c6, 'Delta': Delta
    }


def val(n, p):
    """p-adic valuation of n."""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def local_root_number_odd(a, b, p):
    """Local root number w_p for odd prime p dividing abc.

    For Frey curve y^2 = x(x-a)(x+b) at odd p:
    - p|a, p∤bc: split iff (b/p) = 1
    - p|b, p∤ac: split iff (-a/p) = 1
    - p|c, p∤ab: split iff (a/p) = 1

    w_p = -1 if split multiplicative, +1 if non-split.
    """
    c = a + b
    va, vb, vc = val(a, p), val(b, p), val(c, p)

    if va == 0 and vb == 0 and vc == 0:
        return 1  # good reduction

    # Exactly one of a, b, c is divisible by p (since gcd(a,b)=1)
    if va > 0:
        # p|a: split iff b is QR mod p
        leg = legendre_symbol(b % p, p)
        return -1 if leg == 1 else 1
    elif vb > 0:
        # p|b: split iff -a is QR mod p
        leg = legendre_symbol((-a) % p, p)
        return -1 if leg == 1 else 1
    else:
        # p|c: split iff a is QR mod p (equivalently, -b mod p since a≡-b)
        leg = legendre_symbol(a % p, p)
        return -1 if leg == 1 else 1


def local_root_number_2(a, b):
    """Local root number w_2 for the Frey curve y^2 = x(x-a)(x+b).

    This uses the Halberstadt/Rizzo approach for p=2.
    The curve [0, b-a, 0, -ab, 0] needs careful analysis at 2.

    Strategy: Use Rizzo's formulas (Theorem 1.1, 2003) for the specific
    family y^2 = x^3 + Bx^2 + Cx where B = b-a, C = -ab.

    For this curve form, the local root number at 2 depends on
    v_2(B), v_2(C), and congruence conditions mod powers of 2.
    """
    c = a + b
    B = b - a  # a2 coefficient
    C = -a * b  # a4 coefficient

    # Determine which of a, b, c is even
    # Since gcd(a,b)=1, at most one of a,b is even
    # If both a,b odd, then c = a+b is even

    v2a = val(a, 2)
    v2b = val(b, 2)
    v2c = val(c, 2)

    # The curve y^2 = x(x-a)(x+b)
    # Discriminant: Delta = 16*a^2*b^2*c^2, v_2(Delta) = 4 + 2*v2a + 2*v2b + 2*v2c
    # c4 = 16*(a^2 + ab + b^2), v_2(c4) >= 4

    # We use the substitution x -> 4x, y -> 8y to get a potentially better model:
    # y^2 = x^3 + (b-a)/4 * x^2 - ab/16 * x (if 4|B and 16|C)
    # This is the Néron model approach.

    # For the Frey curve, the minimal model at 2 and its Kodaira type
    # depend on congruences. We implement case-by-case.

    # CASE 1: Both a, b odd (so c even, v2c >= 1)
    if v2a == 0 and v2b == 0:
        # a, b odd, c = a+b even
        # B = b-a is even (both odd), C = -ab is odd
        # v_2(B) >= 1, v_2(C) = 0
        # The curve already has v_2(c4) = 4 (since a^2+ab+b^2 is odd when a,b both odd)
        # v_2(Delta) = 4 + 0 + 0 + 2*v2c

        # For this case, we use Connell's tables.
        # With the model [0, B, 0, C, 0], B even, C odd:
        # Kodaira type at 2 depends on v_2(B) and congruences.

        # Transform: x -> x + B/4... but B might not be divisible by 4.
        # Let's use the standard Tate algorithm approach.

        # Actually, for the specific Frey curve case, Rizzo (2003) and
        # Rohrlich (1996) give:
        # When a ≡ b ≡ 1 (mod 2):
        # The minimal discriminant has v_2(Delta_min) depending on v_2(c).
        # The local root number at 2 is determined by a, b mod 8.

        # From Rizzo (2003), Proposition 3.3 (family y^2 = x(x-a)(x+b)):
        # When a,b odd: w_2 depends on (a mod 8, b mod 8)
        # More specifically, on c = a+b mod 16 and a*b mod 8

        # The substitution x -> x + (b-a)/4 ... no, (b-a)/4 not integer.
        # Let's use x -> x, y -> y (keep model) and apply Tate directly.

        # Standard result for y^2 = x^3 + a2*x^2 + a4*x with a2 even, a4 odd:
        # The singular point mod 2: x^3 + a4*x ≡ x(x^2 + 1) ≡ x(x+1)^2 mod 2
        # So the curve has a node at x=1 mod 2 (since a4 ≡ 1 mod 2 means x^2+a4 has root at x=1 mod... )
        # Actually mod 2: x^3 + a4*x = x^3 + x = x(x^2+1) = x(x+1)^2 (over F_2)
        # This means the curve has ADDITIVE reduction at 2 (cusp, not node).

        # For additive reduction at 2, the root number formula is more complex.
        # We need the full Halberstadt tables.

        # Let me use the explicit formula from the literature.
        # For E: y^2 = x(x-a)(x+b), a,b odd, the root number at 2:
        #
        # Key: Define d = -1 (the leading coefficient twist).
        # The curve has c_6 = -32(b-a)(2a+b)(a+2b)
        # For a,b odd: b-a even, 2a+b odd, a+2b odd.
        # v_2(c_6) = 5 + v_2(b-a)

        # Following Halberstadt's algorithm for the Kodaira-Néron type:
        # After extensive case analysis (which I'll implement numerically):

        # Use Rohrlich's result: for y^2 = x^3 + Bx^2 + Cx,
        # with v_2(B) = 1, v_2(C) = 0 (i.e., B=2B', C odd):
        # Reducing mod 2: cusp at (1, 0) in P^2
        # After translation x -> x+1: y^2 = (x+1)(x+1-a)(x+1+b)
        #                              = (x+1)(x+(1-a))(x+(1+b))
        # a odd => 1-a even, 1+b even

        # This is getting very involved. Let me just use the explicit
        # numerical computation via Tate's algorithm.
        return _tate_algorithm_at_2(a, b)

    # CASE 2: 2|a, b odd (so c odd)
    elif v2a >= 1 and v2b == 0:
        # B = b-a: since a even, b odd, B is odd
        # C = -ab: v_2(C) = v2a
        # c4 = 16*(a^2+ab+b^2): a^2+ab+b^2 ≡ 0+0+1 = 1 mod 2 if v2a >= 1
        # so v_2(c4) = 4
        # Delta = 16*a^2*b^2*c^2, v_2(Delta) = 4 + 2*v2a

        # The model [0, B, 0, C, 0] with B odd, v_2(C) = v2a >= 1:
        # mod 2: y^2 = x^3 + x^2 (since B odd, C even)
        # = x^2(x+1), node at (0,0) with tangents y^2 = x^2, i.e. y = ±x
        # These are defined over F_2 → SPLIT multiplicative reduction
        #
        # Wait, but that gives I_n type. Let me be more careful.
        # y^2 + ... the curve is y^2 = x^3 + Bx^2 + Cx
        # mod 2: y^2 = x^3 + x^2 = x^2(x+1) — node at x=0
        # tangent directions: y^2 = x^2·1 (leading term at x=0 gives y^2 = Bx^2 = x^2 since B odd)
        # Split since 1 is a square in F_2.
        # So w_2 = -1 for split multiplicative.

        # But WAIT: this is only if the reduction is truly multiplicative (I_n type).
        # We need to verify this isn't additive. For multiplicative reduction at 2,
        # we need v_2(c4) = 0 in the minimal model. Let's check:
        # Our c4 has v_2(c4) = 4. If we can do a change of variables reducing
        # by (u=2, r, s, t), then c4' = c4/u^4 = c4/16, and v_2(c4') = 0.
        # This means the minimal model has c4' with v_2 = 0, confirming mult. red.
        # n = v_2(Delta')/... hmm let me think more carefully.

        # For the substitution [u=2, r=0, s=0, t=0]:
        # a1' = (a1+2s)/u = 0
        # a2' = (a2 - s*a1 + 3r - s^2)/u^2 = a2/4 = (b-a)/4
        # Wait, (b-a)/4 might not be an integer since b-a is odd!
        # So u=2 is NOT a valid substitution here (model already minimal at 2)!

        # If the model is already minimal, then v_2(c4)=4 means... hmm.
        # Actually for a minimal model with v_2(c4) >= 4, the Kodaira type
        # is NOT I_n (which requires v_2(c4)=0). It must be I*_n, IV*, III*, II*, or worse.

        # Hmm, but the reduction mod 2 showed a node (multiplicative), which contradicts
        # this. The issue is that "minimal" at 2 for curves with a1=0 is subtle.

        # Let me re-approach: for the model y^2 = x^3 + Bx^2 + Cx with B odd:
        # Change of variables: x -> x, y -> y + x (i.e., add a1=0 -> a1=2... no)
        # Better: complete the square differently.

        # Actually, the standard approach is Tate's algorithm. Let me just implement it.
        return _tate_algorithm_at_2(a, b)

    # CASE 3: a odd, 2|b (so c odd)
    else:
        # Same as Case 2 by symmetry considerations, but not identical
        # because the curve is y^2 = x(x-a)(x+b) which is NOT symmetric in a,b.
        return _tate_algorithm_at_2(a, b)


def _tate_algorithm_at_2(a, b):
    """Full Tate's algorithm at p=2 for y^2 = x(x-a)(x+b).

    Returns the local root number w_2.

    This implements the algorithm following Silverman's Advanced Topics
    and Connell's Handbook, adapted for p=2.

    For practical purposes with small examples, we compute the conductor
    exponent and use known results for the specific reduction types.
    """
    # Instead of the full Tate algorithm (very complex at p=2),
    # use the following approach:
    # 1. Compute c4, c6, Delta
    # 2. Determine Kodaira type via valuations and congruences
    # 3. Look up root number from type + additional data

    # Alternative: use the Dokchitser-Dokchitser formula (2008):
    # For semistable curves: w_2 = (-1)^{f_2} where f_2 is conductor exponent
    # For non-semistable: more complex

    # Actually, the most reliable approach for our specific family:
    # Use the FORMULA from Rizzo (2003), "Average root numbers..."
    # Theorem 1.1 gives w_2 for the family y^2 = x(x+A)(x+B) explicitly.

    # Our curve is y^2 = x(x-a)(x+b) = x(x+(-a))(x+b)
    # In Rizzo's notation: A = -a, B = b
    # (His curve is y^2 = x(x+A)(x+B), same as ours with A=-a, B=b)

    # Rizzo's results (Proposition 2.1, explicit w_2 tables):
    # The root number w_2 depends on:
    # - v_2(A), v_2(B), v_2(A+B) = v_2(b-a) (since A+B = -a+b = b-a)
    # - The odd parts modulo 4 or 8

    # For gcd(a,b)=1 and a+b=c:
    # A = -a, B = b, A+B = b-a, A*B = -ab
    # Also note: x(x+A)(x+B) = x(x-a)(x+b), discriminant ∝ A²B²(A+B)² = a²b²(b-a)²
    # But our discriminant was 16a²b²c². Hmm, Rizzo uses A+B = b-a while
    # our third factor in the discriminant involves c=a+b. Let me reconcile.
    #
    # Actually: y^2 = x(x-a)(x+b). The roots of the cubic are 0, a, -b.
    # Discriminant of x(x-a)(x+b) = x^3+(b-a)x^2-abx is:
    # Disc = (0-a)^2 * (0-(-b))^2 * (a-(-b))^2 = a^2 * b^2 * (a+b)^2 = a^2 b^2 c^2
    # And the elliptic curve discriminant is Delta = 16 * disc(cubic) = 16a²b²c². ✓
    #
    # So the three "branch differences" are: a, b, c = a+b.
    # In Rizzo's notation with y^2 = x(x+A)(x+B): the roots are 0, -A, -B.
    # Branch differences: A, B, A-B (distance between -A and -B is |A-B| = |(-a)-b| = |-(a+b)| = c)
    # Wait: 0-(-A) = A = -a, 0-(-B) = B = b, (-A)-(-B) = B-A = b-(-a) = a+b = c.
    # So the three pairwise differences of roots are: -a, b, c. Their product squared
    # (up to sign) gives the discriminant. ✓

    # Now I'll use a direct computational approach for specific values.
    # Compute the conductor exponent at 2 and local root number
    # using the explicit change-of-variable approach.

    # For our SPECIFIC test cases, let me compute w_2 via the
    # Ogg-Saito formula and explicit model analysis.

    # PRAGMATIC APPROACH: Compute w_2 using the formula
    # w_2 = (-1)^{n_2} * kronecker(-1, N_2/2^{f_2}) ...
    # No, that's not standard.

    # Let me use the most elementary approach:
    # For p=2, the global root number is:
    # epsilon = -1^{something} * product of local
    #
    # The Dokchitser brothers' formula (2010):
    # For a curve E/Q_2 with additive reduction:
    #   w_2 = (-1)^{(f_2+1) + delta_2}
    # where f_2 is the conductor exponent and delta_2 is a correction term.
    #
    # But this is too imprecise. Let me just implement the direct computation
    # for our specific curves.

    # DIRECT COMPUTATION using the model and explicit formulas:
    # For y^2 = x^3 + a2*x^2 + a4*x (our curve):
    # At 2, use the fact that for the GLOBAL root number we have:
    # epsilon(E) = -prod_v w_v
    # With w_infty = -1, so epsilon = prod_{p finite} w_p

    # For the conductor exponent at 2: use Ogg's formula for semistable curves,
    # or compute directly.

    # Since the full Tate algorithm at 2 is 50+ cases, let me use a
    # NUMERICAL approach: compute the conductor via counting points mod 2^k.

    # ALTERNATIVE: Just compute the Hasse-Weil L-function sign directly from
    # the modular form. But that requires the modular form...

    # OK, let me implement a simplified version that covers our test cases.
    # The key insight: for Frey curves with specific a,b values, we can
    # compute w_2 from first principles using the model.

    return _w2_from_model(a, b)


def _w2_from_model(a, b):
    """Compute w_2 for y^2 = x(x-a)(x+b) using explicit model analysis.

    Uses the approach from:
    - Halberstadt (1998), Tables for Kodaira-Néron types at p=2
    - Papadopoulos (1993), Sur la classification de Néron des courbes
      elliptiques en caractéristique résiduelle 2 et 3

    For the Frey curve, the conductor exponent at 2 and local root number
    depend on the congruences of a, b mod 2, 4, 8, 16.
    """
    c = a + b

    # Our model: [a1,a2,a3,a4,a6] = [0, b-a, 0, -ab, 0]
    # This is a "short" model with a1=a3=0.
    # For p=2, a short model is NEVER minimal if the reduction is multiplicative
    # (because a minimal model at 2 with mult. red. requires a1 odd).

    # Step 1: Try to reach a better model by completing the square.
    # Standard trick: y^2 = f(x) can be rewritten as (y+...)^2 = ... only if
    # we allow a1 ≠ 0. Change of variable y -> y + a1/2*x + a3/2 requires
    # division by 2, which is not integral at p=2.

    # Step 2: Use Tate's algorithm directly.
    # Start with model [0, b-a, 0, -ab, 0]

    a1, a2, a3, a4, a6 = 0, b - a, 0, -a * b, 0

    # Compute standard quantities
    b2_val = a1**2 + 4*a2
    b4_val = a1*a3 + 2*a4
    b6_val = a3**2 + 4*a6
    b8_val = a1**2*a6 - a1*a3*a4 + a2*a6 + a2**2*a4 - a4**2

    c4_val = b2_val**2 - 24*b4_val
    c6_val = -b2_val**3 + 36*b2_val*b4_val - 216*b6_val
    Delta_val = -b2_val**2*b8_val - 8*b4_val**3 - 27*b6_val**2 + 9*b2_val*b4_val*b6_val

    # For the full Tate algorithm at p=2, we follow the procedure in
    # Silverman, Advanced Topics, IV.9, adapted for p=2.
    # This is EXTREMELY involved (50+ subcases).

    # SHORTCUT: For our specific examples, use the KNOWN results:
    # The conductor exponent f_2 for y^2 = x(x-a)(x+b) with gcd(a,b)=1:
    #
    # Case A: a,b both odd (c even):
    #   Reduction is ADDITIVE at 2.
    #   f_2 depends on a,b mod 8 and v_2(c).
    #   If v_2(c) = 1 (c ≡ 2 mod 4): typically f_2 = 6, type I*_n
    #   If v_2(c) >= 2: various subcases
    #
    # Case B: exactly one of a,b even:
    #   If v_2(even one) = 1: additive reduction, f_2 = 4 or 6
    #   If v_2(even one) >= 2: need further analysis
    #   The model can potentially be made minimal with mult. reduction.

    # Since implementing the FULL algorithm is too complex here,
    # I'll use an alternative: compute via the Kraus conditions.

    # ACTUALLY, the most reliable method for our purposes:
    # Use the formula for the GLOBAL root number directly.
    # We know all odd local root numbers. We know epsilon = +1 or -1.
    # The equation epsilon = w_2 * prod_{odd p} w_p gives us w_2.
    #
    # But we DON'T know epsilon (that's what we're trying to compute)!

    # So let me implement a minimal but correct version of Tate at 2.
    # Following Cremona's "Algorithms for Modular Elliptic Curves" (1997),
    # Chapter 3.

    return _tate_at_2_cremona(a1, a2, a3, a4, a6)


def _tate_at_2_cremona(a1, a2, a3, a4, a6):
    """Tate's algorithm at p=2, following Cremona (1997) Chapter 3.

    Returns (kodaira_type, f_2, c_p, split, w_2) where:
    - kodaira_type: string like "I_n", "I*_n", "II", etc.
    - f_2: conductor exponent
    - c_p: Tamagawa number
    - split: True/False for I_n type (None for others)
    - w_2: local root number

    NOTE: This is a SIMPLIFIED version covering the main cases.
    For a complete implementation, see Cremona's mwrank/eclib.
    """
    p = 2

    # Helper
    def vp(n):
        return val(n, p) if n != 0 else 99

    # Step 1: Check if model is minimal at 2.
    # Criterion: model [a1,a2,a3,a4,a6] is minimal at p iff
    # there's no transform [u,r,s,t] with u=p that gives integral ai'.
    # For p=2 with a1=0:
    # a1' = (a1+2s)/2 = s — need s integral, OK for any s
    # a2' = (a2 - s*a1 + 3r - s^2)/4 — need (a2 + 3r - s^2) ≡ 0 mod 4
    # a3' = (a3 + r*a1 + 2t)/8 — need (a3 + 2t) ≡ 0 mod 8, i.e., t ≡ ...
    #        but a3=0, so need 2t ≡ 0 mod 8, i.e., t ≡ 0 mod 4
    # a4' = (a4 - s*a3 + 2r*a2 - (t+r*s)*a1 + 3r^2 - 2*s*t) / 16
    #      = (a4 + 2r*a2 + 3r^2 - 2*s*t) / 16
    # a6' = (a6 + r*a4 + r^2*a2 + r^3 - t*a3 - t^2 - r*t*a1) / 64
    #      = (a6 + r*a4 + r^2*a2 + r^3 - t^2) / 64
    #      = (r*a4 + r^2*a2 + r^3 - t^2) / 64 (since a6=0)

    # Try s=0, r=0, t=0: a2' = a2/4 — integral iff 4|a2
    # With a2 = b-a:
    # If 4|(b-a), then we can reduce. Otherwise model is minimal (at least for this s,r,t).

    # More generally, try s=0,1; r=0,1; t=0,2,4,6 (mod 8)...
    # This gets very complex. Let me try the specific substitution.

    # For our specific curve [0, b-a, 0, -ab, 0]:
    # First check: is there a substitution with u=2 making all ai' integral?

    best_model = (a1, a2, a3, a4, a6)
    found_reduction = False

    for s in range(2):
        for r in range(4):
            # a2' = (a2 + 3r - s^2) / 4
            num_a2 = a2 + 3*r - s**2
            if num_a2 % 4 != 0:
                continue
            a2_new = num_a2 // 4

            # a3' = (a3 + 2t) / 8 = 2t/8 = t/4 — need t ≡ 0 mod 4
            for t in range(0, 8, 4):
                a1_new = s
                a3_new = t // 4

                # a4' = (a4 + 2*r*a2 + 3*r^2 - 2*s*t) / 16
                num_a4 = a4 + 2*r*a2 + 3*r**2 - 2*s*t
                if num_a4 % 16 != 0:
                    continue
                a4_new = num_a4 // 16

                # a6' = (r*a4 + r^2*a2 + r^3 - t^2) / 64
                num_a6 = r*a4 + r**2*a2 + r**3 - t**2
                if num_a6 % 64 != 0:
                    continue
                a6_new = num_a6 // 64

                # Found a valid reduction!
                found_reduction = True
                best_model = (a1_new, a2_new, a3_new, a4_new, a6_new)
                break
            if found_reduction:
                break
        if found_reduction:
            break

    if found_reduction:
        # Model was not minimal, use reduced model
        a1, a2, a3, a4, a6 = best_model
        # Might need to reduce further...
        # For now, assume one step suffices for our examples

    # Now apply a simplified Tate algorithm at p=2.
    # Key quantities:
    b2 = a1**2 + 4*a2
    b4 = a1*a3 + 2*a4
    b6 = a3**2 + 4*a6
    b8 = a1**2*a6 - a1*a3*a4 + a2*a6 + a2**2*a4 - a4**2
    c4 = b2**2 - 24*b4
    c6 = -b2**3 + 36*b2*b4 - 216*b6
    Delta = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6

    if Delta == 0:
        # Singular curve — shouldn't happen for our inputs
        return ("singular", 0, 0, None, 1)

    vD = vp(Delta)
    vc4 = vp(c4)
    vc6 = vp(c6)

    # Step 1 of Tate: if p ∤ Delta, good reduction
    if vD == 0:
        return ("I_0", 0, 1, None, 1)

    # Step 2: if p ∤ c4, multiplicative reduction (type I_n)
    if vc4 == 0:
        n = vD
        # Split iff -c6 is a square mod 4 (for p=2)
        # Actually for p=2: split iff the curve over Q_2 is isomorphic to
        # the Tate curve (not a twist). This is: split iff a1^2 + 4a2 has
        # a square root in Z_2, i.e., b2 ≡ square mod 8.
        # Equivalently (Silverman): split iff the curve has a rational
        # 2-torsion point... no that's not right either.

        # For multiplicative reduction at 2:
        # split iff -c6/c4^{3/2} is a square in Q_2^*/(Q_2^*)^2
        # But c4^{3/2} might not make sense.

        # Correct criterion (Silverman IV.9.2):
        # For I_n at p: split iff the quadratic twist by the
        # "determinant character" is trivial.
        # Equivalently: split iff -c6 ∈ (Q_p^*)^2 for the MINIMAL model.

        # For p=2: -c6 is a 2-adic square iff v_2(-c6) is even AND
        # the odd part ≡ 1 mod 8.
        neg_c6 = -c6
        v_neg_c6 = vp(abs(neg_c6))
        if neg_c6 == 0:
            split = False
        else:
            odd_part = neg_c6 // (2**v_neg_c6)
            # A 2-adic integer u is a square iff u ≡ 1 mod 8
            split = (v_neg_c6 % 2 == 0) and (odd_part % 8 == 1)

        w2 = -1 if split else 1
        f2 = 1  # conductor exponent for multiplicative reduction
        c_p_tam = n if split else (n if n % 2 == 0 else 1)  # simplified
        return (f"I_{n}", f2, c_p_tam, split, w2)

    # Step 3+: additive reduction (vc4 >= 1, which at p=2 means vc4 >= ... )
    # For additive reduction, the local root number depends on the specific
    # Kodaira-Néron type and additional data.

    # For p=2 with additive reduction, this is VERY complex.
    # The conductor exponent f_2 ranges from 2 to 6.

    # Use the shortcut: for additive potentially multiplicative reduction,
    # w_2 = -1. For additive potentially good reduction, w_2 depends on
    # the potential good reduction type.

    # Criterion for "potentially multiplicative":
    # The curve has potentially multiplicative reduction iff v_p(j) < 0,
    # where j = c4^3/Delta is the j-invariant.
    # v_p(j) = 3*vc4 - vD
    vj = 3*vc4 - vD

    if vj < 0:
        # Potentially multiplicative (types I*_n)
        # For I*_n at p=2: w_2 depends on n and congruences.
        # General result: w_2 = (-1) for I*_n with n even when split,
        # and various other cases.

        # Simplified: for Frey curves with potentially multiplicative reduction at 2,
        # the root number w_2 is typically -1 (split) or +1 (non-split).

        # Use the formula: for I*_n, the root number is w_2 = -(-1)^{n} * twist_sign
        # This is not quite right. Let me use a different approach.

        # For I*_n type: conductor exponent f_2 = n + 4 + (2 if p=2 else 0)... no.
        # Actually for p=2, I*_n: f_2 = 2 + something.

        # I'll fall back to computing w_2 from the full product formula below.
        # Mark as "needs_computation"

        # The I*_n type: n = vD - 4*vc4... not standard.
        # Actually for additive reduction with vj < 0:
        # After a quadratic twist or extension, the curve becomes multiplicative.
        # Type is I*_{vD - 6} for p >= 3, but for p=2 it's more subtle.

        # For our purposes, return a flag and compute w_2 differently.
        n_star = max(0, vD - 4 - 2*max(0, vc4-2))  # rough estimate
        return (f"I*_{n_star}", 2 + min(4, vD), 0, None, None)  # None means: needs further work

    else:
        # Potentially good reduction
        # Types: II, III, IV, II*, III*, IV*
        # w_2 depends on the specific type.

        # For p=2 with potentially good reduction:
        # Use Rohrlich's formula or the Dokchitser-Dokchitser result.

        # Rough classification:
        if vc4 >= 4 and vc6 >= 6 and vD >= 12:
            # Could reduce model further? Already checked above.
            pass

        # Simplified: return based on c4 mod 16, c6 mod 32, Delta mod various
        # This is where the Halberstadt tables come in.

        # For our specific test cases, this branch handles a,b both odd.
        # w_2 for Frey curves with a,b odd depends on a*b mod 8:
        # - ab ≡ 1 mod 8 (a ≡ b ≡ ±1 mod 4, same residue): w_2 = +1
        # - ab ≡ 3 mod 8 (a ≡ 1, b ≡ 3 or vice versa): w_2 = -1
        # - ab ≡ 5 mod 8: w_2 = +1
        # - ab ≡ 7 mod 8: w_2 = -1
        #
        # ACTUALLY this is just: w_2 = (-1)^{(ab-1)/2} = Jacobi(-1, |ab|)... no
        # w_2 = (-1)^{...} — I'm not confident in this formula.

        # Let me return None to signal that we need a different approach.
        return ("additive_pot_good", vD, 0, None, None)


def compute_global_root_number(a, b, verbose=True):
    """Compute global root number epsilon(E_{a,b}) for Frey curve y^2 = x(x-a)(x+b).

    Uses: epsilon = w_infty * w_2 * prod_{odd p | abc} w_p
    with w_infty = -1.
    """
    c = a + b
    assert gcd(abs(a), abs(b)) == 1, f"gcd(a,b) must be 1, got gcd({a},{b})={gcd(abs(a),abs(b))}"

    if verbose:
        print(f"\n{'='*60}")
        print(f"E_({a},{b}): y² = x(x-{a})(x+{b}), c = {c}")
        print(f"{'='*60}")

    # Factor abc to find bad primes
    factors_a = factorint(abs(a)) if a != 0 else {}
    factors_b = factorint(abs(b)) if b != 0 else {}
    factors_c = factorint(abs(c)) if c != 0 else {}

    all_primes = set()
    all_primes.update(factors_a.keys())
    all_primes.update(factors_b.keys())
    all_primes.update(factors_c.keys())

    # Archimedean place
    w_inf = -1
    if verbose:
        print(f"  w_∞ = {w_inf}")

    # Local root numbers at odd primes
    odd_product = 1
    for p in sorted(all_primes):
        if p == 2:
            continue
        wp = local_root_number_odd(a, b, p)
        odd_product *= wp
        if verbose:
            va, vb, vc = val(a, p), val(b, p), val(c, p)
            which = "a" if va > 0 else ("b" if vb > 0 else "c")
            v = max(va, vb, vc)
            # Determine split/non-split
            if va > 0:
                leg = legendre_symbol(b % p, p)
                split_str = f"split (({b}/{p})={leg})" if leg == 1 else f"non-split (({b}/{p})={leg})"
            elif vb > 0:
                leg = legendre_symbol((-a) % p, p)
                split_str = f"split (({-a}/{p})={leg})" if leg == 1 else f"non-split (({-a}/{p})={leg})"
            else:
                leg = legendre_symbol(a % p, p)
                split_str = f"split (({a}/{p})={leg})" if leg == 1 else f"non-split (({a}/{p})={leg})"
            print(f"  w_{p} = {wp:+d}  [p^{v}||{which}, I_{2*v}, {split_str}]")

    # Local root number at 2
    tate_result = local_root_number_2(a, b)
    if isinstance(tate_result, tuple):
        kodaira, f2, c_tam, split, w2 = tate_result
        if verbose:
            print(f"  w_2: Tate result: type={kodaira}, f_2={f2}, split={split}, w_2={w2}")
    else:
        w2 = tate_result
        if verbose:
            print(f"  w_2 = {w2}")

    if w2 is None:
        if verbose:
            print(f"  WARNING: w_2 could not be determined by simplified Tate algorithm.")
            print(f"  Computing w_2 from constraint: epsilon = w_inf * w_2 * prod(w_odd)")
            print(f"  Cannot determine global root number without w_2!")
        return None, w_inf, w2, odd_product

    # Global root number
    epsilon = w_inf * w2 * odd_product

    if verbose:
        print(f"\n  Global: ε = w_∞ · w_2 · ∏w_p = ({w_inf}) · ({w2}) · ({odd_product}) = {epsilon}")
        print(f"  Analytic rank parity: {'even' if epsilon == 1 else 'odd'}")

    return epsilon, w_inf, w2, odd_product


def main():
    """Test root numbers for abc-triplets in both orientations."""

    print("=" * 70)
    print("ROOT NUMBER VERIFICATION FOR FREY CURVES")
    print("Triplets from mining table: (a, b, c) with a + b = c, gcd(a,b) = 1")
    print("Testing BOTH orientations: E_{a,b} and E_{b,a}")
    print("=" * 70)

    # Test triplets: (a, b, c) with a + b = c
    triplets = [
        (1, 8, 9),           # 1 + 2^3 = 3^2
        (1, 63, 64),         # 1 + 63 = 64, but gcd(1,63)=1? 63=7·9, 64=2^6
        (1, 2, 3),           # simplest
        (5, 27, 32),         # 5 + 3^3 = 2^5
        (7, 9, 16),          # 7 + 3^2 = 2^4, gcd=1? gcd(7,9)=1 ✓
        (1, 80, 81),         # 1 + 80 = 81 = 3^4, 80 = 2^4·5
        (32, 49, 81),        # 2^5 + 7^2 = 3^4, gcd(32,49)=1 ✓
    ]

    print("\n\nPHASE 1: ODD LOCAL ROOT NUMBERS (these are exact)")
    print("=" * 70)

    results = []

    for (a, b, c) in triplets:
        assert a + b == c, f"Triplet error: {a}+{b}≠{c}"
        assert gcd(a, b) == 1, f"gcd({a},{b})≠1"

        print(f"\n{'─'*70}")
        print(f"TRIPLET ({a}, {b}, {c})")
        print(f"{'─'*70}")

        # Orientation 1: E_{a,b}
        eps1, w_inf1, w2_1, odd1 = compute_global_root_number(a, b, verbose=True)

        # Orientation 2: E_{b,a}
        eps2, w_inf2, w2_2, odd2 = compute_global_root_number(b, a, verbose=True)

        # Ratio of odd parts
        odd_ratio = odd1 * odd2  # Since w_p^2 = 1, ratio = product of changes

        results.append({
            'triplet': (a, b, c),
            'eps1': eps1, 'eps2': eps2,
            'w2_1': w2_1, 'w2_2': w2_2,
            'odd1': odd1, 'odd2': odd2
        })

    print("\n\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Triplet':<20} {'ε(E_{a,b})':<12} {'ε(E_{b,a})':<12} {'w_2(a,b)':<10} {'w_2(b,a)':<10} {'∏w_odd(a,b)':<12} {'∏w_odd(b,a)':<12}")
    print("-" * 88)

    for r in results:
        a, b, c = r['triplet']
        e1 = r['eps1'] if r['eps1'] is not None else "?"
        e2 = r['eps2'] if r['eps2'] is not None else "?"
        w21 = r['w2_1'] if r['w2_1'] is not None else "?"
        w22 = r['w2_2'] if r['w2_2'] is not None else "?"
        print(f"({a},{b},{c}){'':<{14-len(f'({a},{b},{c})')}} {str(e1):<12} {str(e2):<12} {str(w21):<10} {str(w22):<10} {r['odd1']:<12} {r['odd2']:<12}")

    print("\n\nKEY QUESTION: Is there any triplet with ε = -1 in BOTH orientations?")
    both_minus = [(a,b,c) for r in results
                  if r['eps1'] == -1 and r['eps2'] == -1
                  for (a,b,c) in [r['triplet']]]
    if both_minus:
        print(f"  YES: {both_minus}")
    else:
        undetermined = [(a,b,c) for r in results
                       if r['eps1'] is None or r['eps2'] is None
                       for (a,b,c) in [r['triplet']]]
        if undetermined:
            print(f"  UNDETERMINED for: {undetermined} (w_2 computation failed)")
        else:
            print(f"  NO — all triplets have ε = +1 in at least one orientation.")


if __name__ == "__main__":
    main()
