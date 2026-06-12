"""Independent verification of dim Symb_2^+(Gamma_0(N)) formula."""
from math import gcd
from sympy import factorint, totient, divisors, legendre_symbol

def psi(N):
    result = N
    for p in factorint(N):
        result = result * (1 + 1/p)
    return int(result)

def cusps_correct(N):
    return int(sum(totient(gcd(d, N//d)) for d in divisors(N)))

def cusps_wrong(N):
    return int(sum(gcd(d, N//d) for d in divisors(N)))

def nu2(N):
    """Number of elliptic points of order 2 = solutions of x^2+1=0 mod N."""
    fN = factorint(N)
    result = 1
    for p, e in fN.items():
        if p == 2:
            if e >= 2:
                return 0
            # e=1: exactly 1 solution mod 2 (x=1, since -1=1 mod 2)
        else:
            ls = int(legendre_symbol(-1, p))
            if ls == -1:
                return 0
            result *= 2
    return result

def nu3(N):
    """Number of elliptic points of order 3 = solutions of x^2+x+1=0 mod N."""
    fN = factorint(N)
    if 2 in fN:
        return 0  # x^2+x+1 has no roots mod 2
    result = 1
    for p, e in fN.items():
        if p == 3:
            if e >= 2:
                return 0
            # e=1: exactly 1 solution mod 3 (x=1)
        else:
            ls = int(legendre_symbol(-3, p))
            if ls == -1:
                return 0
            result *= 2
    return result

def genus(N):
    p = psi(N)
    n2 = nu2(N)
    n3 = nu3(N)
    c = cusps_correct(N)
    g = 1 + p//12 - n2//4 - n3//3 - c//2
    return g, p, n2, n3, c

def star_splitting(N):
    f = 0
    p_sum = 0
    for d in divisors(N):
        gi = gcd(int(d), N // int(d))
        if gi <= 2:
            f += 1
        else:
            p_sum += int(totient(gi))
    p = p_sum // 2
    return f, p

def dim_symb(N):
    g, ps, n2, n3, c = genus(N)
    f, p = star_splitting(N)
    bp = f + p - 1
    bm = p
    return g + bp, g + bm, g, c, f, p, bp, bm

if __name__ == "__main__":
    expected = {
        23: (3, 2), 46: (8, 5), 92: (15, 10), 184: (28, 21),
        368: (52, 45), 736: (100, 93), 1472: (196, 189),
        2944: (388, 381), 5888: (772, 765),
    }
    all_ok = True

    print("=== 9 Test Levels (Sage-verified) ===")
    for N in [23, 46, 92, 184, 368, 736, 1472, 2944, 5888]:
        sp, sm, g, c, f, p, bp, bm = dim_symb(N)
        cw = cusps_wrong(N)
        ep, em = expected[N]
        ok = "OK" if sp == ep and sm == em else "FAIL"
        if ok == "FAIL":
            all_ok = False
        print("N=%5d: g=%d, c=%d, cwrong=%d, f=%d, p=%d, b+=%d, b-=%d -> S+=%d, S-=%d  [%s]"
              % (N, g, c, cw, f, p, bp, bm, sp, sm, ok))

    print()
    print("=== HCT Levels ===")
    comp_qdim = {60168: 10576, 80224: 10568, 120336: 21136}
    for N in [60168, 80224, 120336, 240672]:
        sp, sm, g, c, f, p, bp, bm = dim_symb(N)
        cw = cusps_wrong(N)
        cq = comp_qdim.get(N)
        if cq:
            match = "MATCH" if sp == cq else "MISMATCH"
            tag = "comp_qdim=%d %s" % (cq, match)
        else:
            tag = "Wiedemann running"
        print("N=%d: g=%d, c=%d, cwrong=%d, f=%d, p=%d, b+=%d, b-=%d -> S+=%d, S-=%d  [%s]"
              % (N, g, c, cw, f, p, bp, bm, sp, sm, tag))

    print()
    if all_ok:
        print("ALL 9 TEST LEVELS VERIFIED OK (against Sage ModularSymbols)")
    else:
        print("SOME LEVELS FAILED")
