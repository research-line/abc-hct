# OBSOLETE: u-vs-u²-Frage settled (Loop 37/38, lineares u). Falsche u-Werte (u₃=3, u=18).
# Aktive Verifikation: compute_eta_bound.py (Shape-Elimination Diagnostic).
# Korrekte u-Berechnung: _scripts/d_eff_ledger_corrected.py (Loop 39).
"""
Scaling Check: u vs u^2 in Néron minimization.

§14 claims lambda_1(E_min) = u^2 * lambda_1(E_model).
Differential analysis suggests lambda_1(E_min) = u * lambda_1(E_model).

Test: compute periods for the Frey model and the u-scaled model
directly via AGM, compare the ratio.
"""
import math

def agm(a, b, tol=1e-15, max_iter=100):
    a, b = float(a), float(b)
    for _ in range(max_iter):
        a, b = (a + b) / 2, math.sqrt(a * b)
        if abs(a - b) < tol:
            break
    return a

def compute_model_periods(a_param, b_param):
    e1, e2, e3 = sorted([float(a_param), 0.0, float(-b_param)], reverse=True)
    omega1 = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e1 - e2))
    omega3 = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e2 - e3))
    return omega1, omega3

def compute_scaled_periods(a_param, b_param, u):
    a_s = a_param / u**2
    b_s = b_param / u**2
    e1, e2, e3 = sorted([float(a_s), 0.0, float(-b_s)], reverse=True)
    omega1 = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e1 - e2))
    omega3 = math.pi / agm(math.sqrt(e1 - e3), math.sqrt(e2 - e3))
    return omega1, omega3

triples = [
    (1, 8, 1, "(1,8,9) sqfree"),
    (3, 125, 2, "(3,125,128) u_2=2"),
    (13, 243, 2, "(13,243,256) u_2=2"),
    (1, 4374, 3, "(1,4374,4375) u_3=3"),
    (2, 6436341, 3, "Reyssat u_3=3"),
    (1, 531440, 18, "(1,531440,531441) u=18"),
]

print("=" * 90)
print("NÉRON SCALING CHECK: u vs u^2")
print("Compute periods for model and u-scaled model, compare ratios.")
print("=" * 90)
print()
print(f"{'Triple':<30} {'u':>3} {'om1_model':>12} {'om1_scaled':>12} "
      f"{'ratio':>8} {'u':>4} {'u^2':>4}")
print("-" * 85)

for a, b, u, label in triples:
    o1m, o3m = compute_model_periods(a, b)
    o1s, o3s = compute_scaled_periods(a, b, u)
    r1 = o1s / o1m
    r3 = o3s / o3m
    print(f"{label:<30} {u:>3} {o1m:>12.6e} {o1s:>12.6e} "
          f"{r1:>8.4f} {u:>4d} {u**2:>4d}")
    print(f"{'':30} {'':>3} {o3m:>12.6e} {o3s:>12.6e} "
          f"{r3:>8.4f}")

print()
print("=" * 90)
print("RESULT: If ratio ≈ u → scaling is u. If ratio ≈ u^2 → scaling is u^2.")
print("=" * 90)

print("\n\nDIRECT COMPUTATION FOR REYSSAT:")
a, b, u = 2, 6436341, 3
c = a + b
N = 2 * 3 * 23 * 109

o1m, o3m = compute_model_periods(a, b)
lambda1_model = min(o1m, o3m)

print(f"  Model: omega1={o1m:.6e}, omega3={o3m:.6e}")
print(f"  lambda1(model) = min = {lambda1_model:.6e}")
print(f"  pi/sqrt(c) = {math.pi/math.sqrt(c):.6e}")
print(f"  lambda1(model) / (pi/sqrt(c)) = {lambda1_model / (math.pi/math.sqrt(c)):.4f}")

print(f"\n  With u-scaling (u={u}):")
lambda1_min_u = u * lambda1_model
print(f"  lambda1(min) = u * lambda1(model) = {lambda1_min_u:.6e}")
print(f"  N^{{-1/2}} = {1/math.sqrt(N):.6e}")
print(f"  ratio = {lambda1_min_u / (1/math.sqrt(N)):.6f}")

print(f"\n  With u^2-scaling (u^2={u**2}):")
lambda1_min_u2 = u**2 * lambda1_model
print(f"  lambda1(min) = u^2 * lambda1(model) = {lambda1_min_u2:.6e}")
print(f"  ratio = {lambda1_min_u2 / (1/math.sqrt(N)):.6f}")

print(f"\n  Direct AGM for scaled model (u={u}):")
o1s, o3s = compute_scaled_periods(a, b, u)
lambda1_direct = min(o1s, o3s)
print(f"  lambda1(scaled) = {lambda1_direct:.6e}")
print(f"  lambda1(scaled)/lambda1(model) = {lambda1_direct/lambda1_model:.4f}")
print(f"  This matches u={u}: {'YES' if abs(lambda1_direct/lambda1_model - u) < 0.01 else 'NO'}")
print(f"  This matches u^2={u**2}: {'YES' if abs(lambda1_direct/lambda1_model - u**2) < 0.01 else 'NO'}")

print(f"\n  EFFECTIVE QUALITY ANALYSIS:")
q = math.log(c) / math.log(N)
log_upi = math.log(u * math.pi)
bonus = 2 * log_upi / math.log(N)
q_eff = q - bonus
print(f"  q(abc) = {q:.4f}")
print(f"  Néron+shape bonus: 2*log(u*pi)/log(N) = {bonus:.4f}")
print(f"  q_eff = q - bonus = {q_eff:.4f}")
print(f"  q_eff < 1: {'YES → abc holds with C_eps=1' if q_eff < 1 else 'NO → still needs C_eps'}")
