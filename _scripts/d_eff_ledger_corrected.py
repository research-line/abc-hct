"""D_eff-Ledger Neuberechnung (Loop 39, 2026-05-06)
Korrektur: u_odd = 1 IMMER (Loop 37); u_2 in {1,2} (Loop 38).
Exakte u_2-Bestimmung via Brute-Force Laska-Kraus bei p=2.
"""
import math
import sys
import os

TRIPLETS = [
    (1, 8, 9), (3, 125, 128), (1, 80, 81), (32, 49, 81), (5, 27, 32),
    (13, 243, 256), (1, 4374, 4375), (2, 6436341, 6436343),
    (1, 2, 3), (1, 63, 64), (7, 18, 25), (1, 242, 243), (3, 253, 256),
    (1, 2400, 2401), (1, 4913, 4914), (2, 6561, 6563),
    (1, 12167, 12168), (1, 512, 513), (1, 48, 49), (5, 1024, 1029),
]

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

def v2(n):
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        c += 1
        n //= 2
    return c

def u_old_formula(a, b, c):
    """Alte (FALSCHE) Formel: u = prod_p p^{floor(v_p(Delta)/12)} fuer ungerade p."""
    fa, fb, fc = factorize(a), factorize(b), factorize(c)
    all_primes = set(list(fa.keys()) + list(fb.keys()) + list(fc.keys()))
    log_u = 0
    for p in all_primes:
        if p == 2:
            continue
        vp_abc = fa.get(p, 0) + fb.get(p, 0) + fc.get(p, 0)
        vp_delta = 2 * vp_abc  # Delta = 16(abc)^2
        u_p = vp_delta // 12
        if u_p > 0:
            log_u += u_p * math.log(p)
    return math.exp(log_u)

def check_u2_brute_force(a, b, c):
    """Pruefe ob Frey-Kurve E_{a,b}: y^2 = x(x-a)(x+b) bei p=2 nicht-minimal ist.
    Weierstrass-Koeffizienten: a1=0, a2=b-a, a3=0, a4=-ab, a6=0.
    Substitution [u,r,s,t] = [2,r,s,t]: Pruefe ob ganzzahlige a_i' existieren.
    """
    abc_prod = a * b * c
    v2_abc = v2(abc_prod)
    if v2_abc < 4:
        return 1  # 16 nmid abc => v2(Delta) < 12 => u2 = 1

    a2 = b - a
    a4 = -(a * b)

    for r in range(64):
        for s in range(2):
            for t0 in range(16):
                t = 4 * t0
                # a2' = (a2 + 3r - s^2) / 4
                num_a2 = a2 + 3 * r - s * s
                if num_a2 % 4 != 0:
                    continue
                # a4' = (a4 + 2*r*a2 + 3*r^2 - 2*s*t) / 16
                num_a4 = a4 + 2 * r * a2 + 3 * r * r - 2 * s * t
                if num_a4 % 16 != 0:
                    continue
                # a6' = (r^3 + r^2*a2 + r*a4 - t^2) / 64
                # Note: a6=0, a3=0, a1=0 => a6' = (r*a4 + r^2*a2 + r^3 - t^2) / 64
                num_a6 = r * r * r + r * r * a2 + r * a4 - t * t
                if num_a6 % 64 != 0:
                    continue
                return 2  # Nicht-minimal bei p=2

    return 1  # Kein gueltiger Substitutionsvektor gefunden => minimal bei p=2

def compute_ledger():
    results = []
    for a, b, c in TRIPLETS:
        assert a + b == c and math.gcd(a, b) == 1, f"Kein primitives Tripel: ({a},{b},{c})"
        N = rad(a * b * c)
        logc = math.log(c)
        logN = math.log(N)
        q = logc / logN

        u_old = u_old_formula(a, b, c)
        u2 = check_u2_brute_force(a, b, c)
        u_new = u2  # u_odd = 1, also u = u2

        D_eff_old = logc - logN - 2 * math.log(u_old)
        D_eff_new = logc - logN - 2 * math.log(u_new)

        v2_abc = v2(a * b * c)
        results.append({
            'a': a, 'b': b, 'c': c,
            'q': q, 'N': N, 'logc': logc, 'logN': logN,
            'u_old': u_old, 'u_new': u_new, 'u2': u2,
            'v2_abc': v2_abc,
            'D_eff_old': D_eff_old, 'D_eff_new': D_eff_new,
            'D_over_logN_old': D_eff_old / logN if logN > 0 else 0,
            'D_over_logN_new': D_eff_new / logN if logN > 0 else 0,
        })

    results.sort(key=lambda r: r['N'])
    return results

def format_output(results):
    lines = []
    lines.append("=" * 130)
    lines.append("D_eff-LEDGER NEUBERECHNUNG (Loop 39, 2026-05-06)")
    lines.append("Korrektur: u_odd = 1 IMMER (Loop 37); u_2 exakt via Laska-Kraus Brute-Force (Loop 38/39)")
    lines.append("=" * 130)
    lines.append("")

    hdr = (f"{'Tripel':<28} {'q':>5} {'N':>10} {'log(c)':>7} {'log(N)':>7} "
           f"{'u_alt':>5} {'u_neu':>5} {'D_old':>7} {'D_new':>7} "
           f"{'D/lnN_o':>7} {'D/lnN_n':>7} {'Delta':>7} {'v2abc':>5}")
    lines.append(hdr)
    lines.append("-" * 130)

    n_changed = 0
    n_deff_pos = 0
    max_d_over_logN = 0
    max_triple = ""

    for r in results:
        label = f"({r['a']},{r['b']},{r['c']})"
        delta = r['D_eff_new'] - r['D_eff_old']
        changed = "*" if abs(delta) > 0.001 else " "
        if abs(delta) > 0.001:
            n_changed += 1
        if r['D_eff_new'] > 0:
            n_deff_pos += 1
        if r['D_over_logN_new'] > max_d_over_logN:
            max_d_over_logN = r['D_over_logN_new']
            max_triple = label

        lines.append(
            f"{label:<28} {r['q']:>5.3f} {r['N']:>10} {r['logc']:>7.3f} {r['logN']:>7.3f} "
            f"{r['u_old']:>5.1f} {r['u_new']:>5} {r['D_eff_old']:>7.3f} {r['D_eff_new']:>7.3f} "
            f"{r['D_over_logN_old']:>7.4f} {r['D_over_logN_new']:>7.4f} {delta:>+7.3f}{changed} {r['v2_abc']:>5}"
        )

    lines.append("-" * 130)
    lines.append("")
    lines.append("LEGENDE:")
    lines.append("  u_alt  = alte Formel prod_p p^{floor(v_p(Delta)/12)} (ungerade p; FALSCH)")
    lines.append("  u_neu  = korrekte Formel: u_odd=1 immer, u_2 via Laska-Kraus (Loop 37+38)")
    lines.append("  D_old  = D_eff mit u_alt")
    lines.append("  D_new  = D_eff mit u_neu = log(c) - log(rad(abc)) - 2*log(u_neu)")
    lines.append("  Delta  = D_new - D_old (*  = geaendert)")
    lines.append("  v2abc  = v_2(abc); 16|abc erfordert v2abc >= 4")
    lines.append("")
    lines.append("ZUSAMMENFASSUNG:")
    lines.append(f"  Geaenderte Tripel:       {n_changed}/20")
    lines.append(f"  Tripel mit D_eff > 0:    {n_deff_pos}/20")
    lines.append(f"  Max D_eff/log(N):        {max_d_over_logN:.4f}  bei {max_triple}")
    lines.append("")

    # u2-Analyse
    lines.append("U2-ANALYSE (nur Tripel mit 16|abc):")
    lines.append(f"{'Tripel':<28} {'v2(abc)':>7} {'u2':>3} {'Bemerkung'}")
    lines.append("-" * 70)
    for r in results:
        if r['v2_abc'] >= 4:
            label = f"({r['a']},{r['b']},{r['c']})"
            note = "u2=2: nicht-minimal" if r['u2'] == 2 else "u2=1: trotz 16|abc, Kraus-Bedingung nicht erfuellt"
            lines.append(f"{label:<28} {r['v2_abc']:>7} {r['u2']:>3}   {note}")
    lines.append("")

    # Sortiert nach D_eff/log(N) (absteigend)
    lines.append("TOP-TRIPEL nach D_eff/log(N) (neu, absteigend):")
    by_ratio = sorted(results, key=lambda r: r['D_over_logN_new'], reverse=True)
    lines.append(f"{'#':>2} {'Tripel':<28} {'q':>5} {'D_new':>7} {'D/lnN':>7}")
    lines.append("-" * 55)
    for i, r in enumerate(by_ratio[:10], 1):
        label = f"({r['a']},{r['b']},{r['c']})"
        lines.append(f"{i:>2} {label:<28} {r['q']:>5.3f} {r['D_eff_new']:>7.3f} {r['D_over_logN_new']:>7.4f}")
    lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    results = compute_ledger()
    output = format_output(results)

    print(output)

    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_results")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, "d_eff_ledger_2026-05-06.txt")
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\nGespeichert: {outfile}")
