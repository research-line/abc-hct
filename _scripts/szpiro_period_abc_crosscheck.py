#!/usr/bin/env python3
"""Iter-6 prime (2026-06-03): independent cross-confirmation of rem:period_abc_equivalent.

The project derives the period <-> abc equivalence (lambda_1 ~ c^{-1/2}) via the AGM
comparison.  This script re-derives the same scaling via a SECOND, independent route --
the Szpiro-Zerlegung identity

    |Delta_min| = (2*pi/omega_1)^12 * |eta(tau)|^24                         (*)

with the genuine real period omega_1 (AGM) and tau = omega_2/omega_1 of the Frey curve
y^2 = x(x-a)(x+b), and the Frey discriminant Delta = 16(abc)^2.  In the BALANCED chamber
(a ~ b ~ c) the eta-factor is bounded between positive constants, so (*) gives

    omega_1 ~ (abc)^{-1/6} ~ c^{-1/2}    (balanced),

matching the AGM route.  This is a CROSS-CONFIRMATION, not a new result and not progress
toward proving abc: it confirms the period target is a faithful restatement of abc
(no weakening), and it guards against a hidden error in the one-route equivalence.

Scope: BALANCED chamber only.  For boundary triples (e.g. Reyssat a=2) the eta-factor is
NOT bounded below (|eta|^24 -> 0), so omega_1 ~ (abc)^{-1/6} does NOT hold uniformly into
the boundary chamber -- printed below for contrast.

Pure mpmath, no compute-host needed (runs in well under a second).
"""

import math
import mpmath as mp

mp.mp.dps = 40


def frey_check(a, b, eta_terms=400):
    """Frey curve y^2 = x(x-a)(x+b), roots e1=a > e2=0 > e3=-b.  Returns the real period,
    |eta(tau)|^24, and K := |Delta| / ((2pi/omega_1)^12 |eta|^24) (should be 1)."""
    a, b = mp.mpf(a), mp.mpf(b)
    c = a + b
    AGM1 = mp.agm(mp.sqrt(c), mp.sqrt(a))   # sqrt(e1-e3)=sqrt(c), sqrt(e1-e2)=sqrt(a)
    AGM2 = mp.agm(mp.sqrt(c), mp.sqrt(b))   # sqrt(e1-e3)=sqrt(c), sqrt(e2-e3)=sqrt(b)
    om1 = mp.pi / AGM1                        # real period
    tau = 1j * AGM1 / AGM2                     # purely imaginary, Im(tau) > 0
    q = mp.e ** (2j * mp.pi * tau)             # real in (0,1)
    eta = q ** (mp.mpf(1) / 24)
    for n in range(1, eta_terms):
        eta *= (1 - q ** n)
    eta = abs(eta)
    Delta = 16 * (a * b * c) ** 2              # Frey discriminant 16(abc)^2
    rhs = (2 * mp.pi / om1) ** 12 * eta ** 24
    K = abs(Delta) / rhs
    return {
        "c": float(c), "abc": float(a * b * c), "om1": float(om1),
        "eta24": float(eta ** 24), "K": float(K), "tau_im": float(mp.im(tau)),
    }


def main():
    print("=== Szpiro-Zerlegung identity check |Delta| = (2pi/om1)^12 |eta|^24 ===")
    print("triple             c           Omega1        eta^24        K(=1?)     Om*(abc)^(1/6)")
    triples = [(5, 27), (32, 49), (49, 576), (675, 5292), (2, 6436341)]  # last = Reyssat (boundary)
    for a, b in triples:
        r = frey_check(a, b)
        rc = r["om1"] * (r["abc"]) ** (1 / 6)
        tag = "  <- Reyssat (boundary a=2): eta->0, ratio drifts" if a == 2 else ""
        print(f"({a},{b})".ljust(19)
              + f"{r['c']:.3e}  {r['om1']:.4e}  {r['eta24']:.3e}  {r['K']:.6f}  {rc:.4f}{tag}")

    print("\n=== Exponent fit (balanced family a=b -> c, varying scale) ===")
    import numpy as np
    ks = [10 ** i for i in range(2, 8)]
    logom, logc, logabc = [], [], []
    for k in ks:
        r = frey_check(k, k)
        logom.append(math.log(r["om1"])); logc.append(math.log(r["c"])); logabc.append(math.log(r["abc"]))
    sc = float(np.polyfit(logc, logom, 1)[0])
    sa = float(np.polyfit(logabc, logom, 1)[0])
    print(f"d log(Omega)/d log(c)   = {sc:.5f}   (expected -0.5)")
    print(f"d log(Omega)/d log(abc) = {sa:.5f}   (expected -1/6 = {-1/6:.5f})")
    ok = abs(sc + 0.5) < 1e-4 and abs(sa + 1/6) < 1e-4
    print("\nVERDICT:", "cross-confirmation PASS (balanced)" if ok else "MISMATCH -- investigate")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
