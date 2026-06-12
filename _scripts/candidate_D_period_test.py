"""
Kandidat D -- Periodenquotienten-Test fuer Frey-Kurven.
Berechnet Omega_E und Omega_{E'} fuer E' = E/<(0,0)>.

METHODE: Numerische Integration (mpmath.quad) fuer BEIDE Perioden.
KONVENTION (BSD/LMFDB): Omega = integral von |dx/(2y)| ueber E(R).
  disc > 0 (zwei Komp.): Omega = 2 * integral ueber Identitaetskomponente
  disc < 0 (eine Komp.): Omega = integral ueber einzige Komponente
"""
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

from mpmath import mp, mpf, sqrt, pi, agm, re, inf, quad
mp.dps = 50


def frey_real_period(a, b):
    """Reelle Periode Omega_E der Frey-Kurve y^2 = x(x-a)(x+b).
    Wurzeln: e1=-b < e2=0 < e3=a (drei reelle), disc > 0, zwei Komponenten.
    BSD-Konvention: Omega = 2 * (Integral ueber Identitaetskomponente [a, inf))."""
    a, b = mpf(a), mpf(b)
    def integrand(x):
        return 1 / sqrt(x * (x - a) * (x + b))
    identity = quad(integrand, [a, inf])
    return 2 * float(re(identity))


def isogenous_real_period(a, b):
    """Reelle Periode Omega_{E'} fuer E' = E/<(0,0)>.
    Velu: E' hat Gleichung y^2 = x(x^2 + 2(a-b)x + (a+b)^2).
    Einzige reelle Wurzel: x=0. disc < 0, eine Komponente.
    BSD-Konvention: Omega = Integral ueber einzige Komponente [0, inf)."""
    a, b = mpf(a), mpf(b)
    Ap = 2*(a - b)
    Bp = (a + b)**2
    def integrand(t):
        return 1 / sqrt(t * (t**2 + Ap*t + Bp))
    omega = quad(integrand, [0, inf])
    return float(re(omega))


def lmfdb_crosscheck():
    """Crosscheck: LMFDB 24.a3 hat y^2 = (x+3)(x+2)(x-6), Omega = 2.1565156..."""
    print("LMFDB CROSSCHECK: 24.a3")
    print("-" * 40)
    def integrand(x):
        return 1 / sqrt((x + 3) * (x + 2) * (x - 6))
    identity = quad(integrand, [mpf(6), inf])
    omega_lmfdb = 2 * float(re(identity))
    print(f"  2 * int_6^inf = {omega_lmfdb:.10f}")
    print(f"  LMFDB-Wert    = 2.1565156475")
    print(f"  Abweichung    = {abs(omega_lmfdb - 2.1565156475):.2e}")
    if abs(omega_lmfdb - 2.1565156475) < 1e-6:
        print("  -> MATCH. Integrationsmethode VERIFIZIERT.")
    else:
        print("  -> ABWEICHUNG. Methode pruefen!")
    print()
    return omega_lmfdb


def rad(n):
    n = abs(n)
    if n == 0:
        return 0
    r = 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            r *= d
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        r *= n
    return r


def run_test():
    triplets = [
        (1, 8),
        (3, 125),
        (13, 243),
        (1, 4374),
        (2, 6436341),
    ]

    print("KANDIDAT D -- PERIODENQUOTIENTEN-TEST (v2, num. Integration)")
    print("=" * 68)
    print()

    omega_ref = lmfdb_crosscheck()

    results = []

    for a_val, b_val in triplets:
        c_val = a_val + b_val
        N = rad(a_val * b_val * c_val)
        threshold = N ** (-0.5)

        omega_E = frey_real_period(a_val, b_val)
        omega_Ep = isogenous_real_period(a_val, b_val)
        ratio = omega_E / omega_Ep
        min_omega = min(omega_E, omega_Ep)

        print(f"=== Tripel ({a_val}, {b_val}, {c_val}) ===")
        print(f"  N (rad)        = {N}")
        print(f"  Omega_E        = {omega_E:.10f}  (disc>0, 2 Komp.)")
        print(f"  Omega_E'       = {omega_Ep:.10f}  (disc<0, 1 Komp.)")
        print(f"  Omega_E / Omega_E' = {ratio:.6f}")
        print(f"  min(Omega)     = {min_omega:.10f}")
        print(f"  N^{{-1/2}}       = {threshold:.10f}")
        print(f"  Omega_E / N^{{-1/2}}    = {omega_E / threshold:.4f}")
        print(f"  min(Omega) / N^{{-1/2}} = {min_omega / threshold:.4f}")
        print()

        results.append({
            'a': a_val, 'b': b_val, 'c': c_val,
            'N': N,
            'omega_E': omega_E,
            'omega_Ep': omega_Ep,
            'ratio': ratio,
            'min_omega': min_omega,
            'threshold': threshold,
        })

    print("=" * 68)
    print("ZUSAMMENFASSUNG")
    print("=" * 68)
    print(f"{'Tripel':<25} {'OmE/OmEp':>10} {'min/N^-1/2':>12} {'OmE/N^-1/2':>12} {'Gain':>8}")
    print("-" * 67)
    for r in results:
        gain = r['min_omega'] / r['omega_E']
        label = f"({r['a']},{r['b']},{r['c']})"
        print(f"{label:<25} {r['ratio']:>10.4f} {r['min_omega']/r['threshold']:>12.4f} {r['omega_E']/r['threshold']:>12.4f} {gain:>8.4f}")

    print()
    print("=" * 68)
    print("VERDIKT")
    print("=" * 68)

    ratios = [r['ratio'] for r in results]
    ratio_spread = max(ratios) - min(ratios)

    print(f"Verhaeltnis-Bereich: [{min(ratios):.4f}, {max(ratios):.4f}]")
    print(f"Spread: {ratio_spread:.4f}")

    if ratio_spread < 0.5:
        avg = sum(ratios) / len(ratios)
        print(f"-> KONSISTENT bei ~ {avg:.3f}")
        if avg > 1.5:
            print("-> Omega_E > Omega_E': min = Omega_E' (kleiner als Omega_E).")
            print("-> Isogenie VERSCHLECHTERT die Untergrenze.")
            print("-> KEIN ANC+-Gewinn. Kandidat D: FALSIFIZIERT.")
        elif avg < 0.7:
            print("-> Omega_E < Omega_E': min = Omega_E (unveraendert).")
            print("-> KEIN Gewinn. Kandidat D: FALSIFIZIERT.")
        else:
            print("-> Faktor ~ 1: Perioden vergleichbar. Kein systematischer Gain.")
            print("-> Kandidat D: FALSIFIZIERT (kein exploitbarer Unterschied).")
    else:
        print("-> VARIIERT: nicht-trivialer N-abhaengiger Quotient!")
        print("-> Weitere Analyse noetig.")

    gains = [r['min_omega'] / r['omega_E'] for r in results]
    print(f"\nmin(Omega)/Omega_E = {[f'{g:.4f}' for g in gains]}")
    if all(g < 1.01 for g in gains):
        print("-> min(Omega) <= Omega_E IMMER. KEIN Gewinn durch Isogenie-Klasse.")
    elif any(g > 1.01 for g in gains):
        print("-> SIGNAL: min(Omega) > Omega_E bei manchen Tripeln!")


if __name__ == "__main__":
    run_test()
