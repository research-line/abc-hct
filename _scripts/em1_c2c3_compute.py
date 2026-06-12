"""
EM-1: C2/C3 Database for abc-Champions.

Computes Kodaira spectrum (C2) and residual Fuehrer-Drops (C3) for Frey curves
Y^2 = X(X-a)(X+b), a+b=c, gcd(a,b)=1.

C2: {v_p(Delta_min), Kodaira type, Tamagawa c_p, split/nonsplit} for all p | N
C3: D_ell = prod_{p|N, ell|v_p(Delta_min)} p  for ell in {2,3,5,7,11,13,17,19}

Pure arithmetic for odd primes (exact, no CAS needed).
p=2 flagged for PARI/Sage resolution (model may not be minimal there).

Output: JSON + human-readable summary to ~/compute/abc_em1/
"""

import json
import math
import os
import sys
from datetime import datetime


def factorize(n):
    n = abs(n)
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def rad(n):
    return math.prod(factorize(abs(n)).keys()) if n != 0 else 0


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def legendre_symbol(a, p):
    if p == 2:
        raise ValueError("Legendre symbol undefined for p=2")
    a = a % p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def compute_c2(a, b):
    """
    C2 (Kodaira spectrum) for Frey curve Y^2 = X(X-a)(X+b).

    At odd p: model is minimal. v_p(Delta_min) = 2*v_p(abc).
    Kodaira type I_n with n = v_p(Delta_min). Semistable.
    Split/nonsplit via Legendre symbols of tangent slopes at the node.
    Tamagawa: n (split), gcd(n,2) (nonsplit).

    At p=2: model Disc = 16*(abc)^2, may not be minimal. Flagged.
    """
    c = a + b
    facts_a = factorize(a)
    facts_b = factorize(b)
    facts_c = factorize(c)

    all_primes = sorted(set(list(facts_a) + list(facts_b) + list(facts_c)))

    c2 = {}
    for p in all_primes:
        v_abc_p = facts_a.get(p, 0) + facts_b.get(p, 0) + facts_c.get(p, 0)

        if p == 2:
            v_model = 4 + 2 * v_abc_p
            c2[p] = {
                "v_delta_min": v_model,
                "v_delta_model": v_model,
                "kodaira": f"I_{v_model}?",
                "tamagawa": None,
                "split": None,
                "minimal": False,
                "which_divides": (
                    "a" if facts_a.get(2, 0) > 0
                    else ("b" if facts_b.get(2, 0) > 0 else "c")
                ),
                "note": "p=2: model may not be minimal",
            }
            continue

        v_delta = 2 * v_abc_p
        if facts_a.get(p, 0) > 0:
            which = "a"
            split = legendre_symbol(b, p) == 1
        elif facts_b.get(p, 0) > 0:
            which = "b"
            split = legendre_symbol(-a, p) == 1
        else:
            which = "c"
            split = legendre_symbol(a, p) == 1

        tamagawa = v_delta if split else (2 if v_delta % 2 == 0 else 1)

        c2[p] = {
            "v_delta_min": v_delta,
            "kodaira": f"I_{v_delta}",
            "tamagawa": tamagawa,
            "split": split,
            "minimal": True,
            "which_divides": which,
        }

    return c2


def compute_c3(c2, N):
    """
    C3 (residual Fuehrer-Drops).
    D_ell = prod_{p|N, ell | v_p(Delta_min)} p.

    For semistable E: if ell | v_p(Delta_min) then rho-bar_{E,ell}
    is unramified at p (Ribet level-lowering).
    """
    test_ells = [2, 3, 5, 7, 11, 13, 17, 19]
    c3 = {}

    for ell in test_ells:
        drop_primes = []
        for p, data in c2.items():
            v = data["v_delta_min"]
            if v > 0 and v % ell == 0:
                drop_primes.append(p)

        D_ell = math.prod(drop_primes) if drop_primes else 1
        c3[ell] = {
            "D_ell": D_ell,
            "drop_primes": sorted(drop_primes),
            "log_ratio": (
                math.log(D_ell) / math.log(N)
                if D_ell > 1 and N > 1
                else 0.0
            ),
            "N_residual": N // D_ell if D_ell > 0 else N,
        }
    return c3


def root_number_odd(c2):
    """
    Root number contribution from odd primes only.
    w_p = -1 (split mult.) or +1 (nonsplit mult.).
    Full root number: w(E) = -1 * w_2 * w_odd.
    """
    w = 1
    for p, data in c2.items():
        if p == 2:
            continue
        if data["split"]:
            w *= -1
    return w


def analyze_triple(a, b, label=""):
    c = a + b
    if gcd(abs(a), abs(b)) != 1:
        return {"error": f"gcd(a,b) = {gcd(abs(a), abs(b))}", "label": label}

    abc_val = abs(a * b * c)
    N = rad(abc_val)
    quality = math.log(abs(c)) / math.log(N) if N > 1 else 0

    c2 = compute_c2(a, b)
    c3 = compute_c3(c2, N)
    w_odd = root_number_odd(c2)

    all_drop = set()
    for ell, d in c3.items():
        if ell >= 3:
            all_drop.update(d["drop_primes"])
    drop_union = math.prod(all_drop) if all_drop else 1

    tam_odd = 1
    for p, data in c2.items():
        if p != 2 and data["tamagawa"] is not None:
            tam_odd *= data["tamagawa"]

    defect = math.log(abs(c)) - math.log(N) if N > 1 else 0.0

    nontrivial_drop_mass = sum(
        d["log_ratio"] for ell, d in c3.items() if ell >= 3
    )

    return {
        "label": label,
        "a": a,
        "b": b,
        "c": c,
        "abc": abc_val,
        "N": N,
        "quality": round(quality, 6),
        "defect": round(defect, 6),
        "factorization": {
            "a": dict(factorize(abs(a))),
            "b": dict(factorize(abs(b))),
            "c": dict(factorize(abs(c))),
        },
        "C2": {str(p): data for p, data in sorted(c2.items())},
        "C3": {str(ell): data for ell, data in sorted(c3.items())},
        "drop_union": drop_union,
        "nontrivial_drop_mass": round(nontrivial_drop_mass, 6),
        "tamagawa_odd": tam_odd,
        "w_odd": w_odd,
        "w_2": "TBD",
        "n_primes": len(c2),
        "n_split": sum(1 for d in c2.values() if d.get("split") is True),
        "n_nonsplit": sum(1 for d in c2.values() if d.get("split") is False),
    }


ABC_CHAMPIONS = [
    # Reyssat (1987): q ~ 1.6299
    (2, 3**10 * 109, "Reyssat"),
    # ABC@Home record #2: q ~ 1.626
    (11**2, 3**2 * 5**6 * 7**3, "ABCHome_2"),
    # Classic: 1 + 2*3^7 = 5^4*7, q ~ 1.568
    (1, 2 * 3**7, "classic_4374"),
    # 1 + 2^5*3*5^2 = 7^4, q ~ 1.456
    (1, 2400, "classic_2401"),
]

COMPARISON_TRIPLES = [
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


def print_c2_table(result):
    print(f"\n  C2: Kodaira Spectrum")
    hdr = f"  {'p':>6} {'v_p(D)':>7} {'Type':>8} {'c_p':>5} {'Split':>7} {'div':>5}"
    print(hdr)
    print(f"  {'-' * len(hdr.strip())}")
    for p_str in sorted(result["C2"], key=lambda x: int(x)):
        d = result["C2"][p_str]
        sp = "?" if d.get("split") is None else ("yes" if d["split"] else "no")
        cp = "?" if d.get("tamagawa") is None else str(d["tamagawa"])
        dv = d.get("which_divides", "?")
        print(f"  {p_str:>6} {d['v_delta_min']:>7} {d['kodaira']:>8} {cp:>5} {sp:>7} {dv:>5}")


def print_c3_table(result):
    print(f"\n  C3: Residual Fuehrer-Drops  D_ell = N / N(rho-bar_{{E,ell}})")
    hdr = f"  {'ell':>4} {'D_ell':>10} {'lg/lgN':>8} {'N_res':>10} {'Drop primes'}"
    print(hdr)
    print(f"  {'-' * 65}")
    for ell_str in sorted(result["C3"], key=lambda x: int(x)):
        d = result["C3"][ell_str]
        dp = ", ".join(str(p) for p in d["drop_primes"]) if d["drop_primes"] else "-"
        print(
            f"  {ell_str:>4} {d['D_ell']:>10} {d['log_ratio']:>8.4f}"
            f" {d['N_residual']:>10} {dp}"
        )


def print_summary(result):
    if "error" in result:
        print(f"\n  {result['label']}: ERROR — {result['error']}")
        return

    print(f"\n{'=' * 80}")
    print(f"  {result['label']}")
    print(f"  a = {result['a']}, b = {result['b']}, c = {result['c']}")
    print(f"  N = {result['N']}, quality = {result['quality']:.4f}")
    print(f"{'=' * 80}")

    print_c2_table(result)
    print_c3_table(result)

    print(f"\n  Drop-Union = {result['drop_union']}, Defect = {result['defect']:.4f}")
    print(f"  Nontrivial Drop Mass (ℓ≥3) = {result['nontrivial_drop_mass']:.4f}")
    print(f"  Tamagawa (odd p only) = {result['tamagawa_odd']}")
    print(f"  w_odd = {result['w_odd']}, w_2 = {result['w_2']}")
    print(f"  Split: {result['n_split']}, Nonsplit: {result['n_nonsplit']}")


def print_comparison(all_results):
    print(f"\n{'=' * 80}")
    print("COMPARATIVE SUMMARY")
    print(f"{'=' * 80}")
    hdr = (
        f"{'Label':<20} {'q':>6} {'N':>8} {'Defect':>8}"
        f" {'DropU':>8} {'Tam_odd':>8} {'#spl':>5} {'#nsp':>5}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(all_results, key=lambda x: -x.get("quality", 0)):
        if "error" in r:
            continue
        print(
            f"{r['label']:<20} {r['quality']:>6.3f} {r['N']:>8}"
            f" {r['defect']:>8.4f} {r['drop_union']:>8} {r['tamagawa_odd']:>8}"
            f" {r['n_split']:>5} {r['n_nonsplit']:>5}"
        )


def main():
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data", "em1")
    os.makedirs(outdir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("EM-1: C2/C3 Database — Smoke Test")
    print(f"Output: {outdir}")
    print(f"Timestamp: {timestamp}")

    all_results = []

    print(f"\n{'=' * 80}")
    print("ABC CHAMPIONS")
    print(f"{'=' * 80}")
    for a, b, label in ABC_CHAMPIONS:
        result = analyze_triple(a, b, label)
        all_results.append(result)
        print_summary(result)

    print(f"\n{'=' * 80}")
    print("COMPARISON TRIPLES")
    print(f"{'=' * 80}")
    for a, b, label in COMPARISON_TRIPLES:
        result = analyze_triple(a, b, label)
        all_results.append(result)
        print_summary(result)

    print_comparison(all_results)

    json_path = os.path.join(outdir, f"c2c3_results_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)
    print(f"\nJSON saved: {json_path}")

    txt_path = os.path.join(outdir, f"c2c3_summary_{timestamp}.txt")
    old_stdout = sys.stdout
    with open(txt_path, "w", encoding="utf-8") as f:
        sys.stdout = f
        print(f"EM-1 C2/C3 Smoke Test — {timestamp}\n")
        for r in all_results:
            print_summary(r)
        print_comparison(all_results)
        sys.stdout = old_stdout
    print(f"Summary saved: {txt_path}")


if __name__ == "__main__":
    main()
