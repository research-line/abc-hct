#!/usr/bin/env sage -python
"""
Phase 2 of Frey-Watkins-Saturation test (FWS):
Compute Frey conductor and modular degree for a list of abc triples,
output log(m)/log(N) per triple.
"""

from sage.all import EllipticCurve, RR
import json
import sys
from math import log

# Classical abc triples used in the 2026-05-17 Phase-2 PARI run
# (a, b, c=a+b, gcd(a,b)=1, b >= a >= 1)
# Frey curve: y^2 = x(x-a)(x+b)  in Weierstrass [0, b-a, 0, -a*b, 0]
TRIPLES = [
    (1, 8, 9),
    (1, 80, 81),
    (3, 125, 128),
    (32, 49, 81),
    (13, 243, 256),
    (5, 27, 32),
    (1, 48, 49),
    (1, 99, 100),
    (1, 288, 289),
    (1, 728, 729),
    (625, 2048, 2673),
    (1, 2400, 2401),
    (1, 5831, 5832),
    (3, 1024, 1027),    # 3+2^10
    (2, 6436341, 6436343),  # Reyssat
]

# Use set of canonical-ordered triples (b >= a)
seen = set()
triples_unique = []
for (a, b, c) in TRIPLES:
    if a > b:
        a, b = b, a
    key = (a, b, c)
    if key in seen:
        continue
    seen.add(key)
    triples_unique.append(key)

results = []
for (a, b, c) in triples_unique:
    if a + b != c:
        results.append({"triple": [a, b, c], "error": "a+b != c"})
        continue
    from math import gcd
    if gcd(a, b) != 1:
        results.append({"triple": [a, b, c], "error": "gcd(a,b) != 1"})
        continue
    try:
        E = EllipticCurve([0, b - a, 0, -a * b, 0])
        E = E.minimal_model()
        N = E.conductor()
        m = E.modular_degree()
        rank = E.rank()
        disc = E.discriminant()
        log_ratio = float(RR(log(float(m)) / log(float(N)))) if N > 1 else None
        # rad(abc)
        from math import gcd as g
        n = abs(a * b * c)
        rad = 1
        d = 2
        while d * d <= n:
            if n % d == 0:
                rad *= d
                while n % d == 0:
                    n //= d
            d += 1
        if n > 1:
            rad *= n
        quality = float(RR(log(c) / log(rad)))
        results.append({
            "triple": [a, b, c],
            "rad_abc": rad,
            "quality": round(quality, 4),
            "N": int(N),
            "m": int(m),
            "rank": int(rank),
            "log_m_over_log_N": round(log_ratio, 4) if log_ratio is not None else None,
            "saturates_N_to_1": (log_ratio is not None and log_ratio >= 1.0),
        })
    except Exception as e:
        results.append({"triple": [a, b, c], "error": str(e)[:200]})

print(json.dumps({"results": results}, indent=2))
