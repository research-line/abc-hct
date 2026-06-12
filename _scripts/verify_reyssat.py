"""Verify Reyssat root numbers for both Frey curve orientations."""
from sympy import legendre_symbol

a, b, c = 2, 6436341, 6436343
print("=== Reyssat: 2 + 3^10*109 = 23^5 ===")
print()

# Orientation 1: E_{a,b} = E_{2, 6436341}
# Odd primes: 3|b, 109|b, 23|c
print("--- Orientation 1: E_{2, 6436341} ---")
# p|b: split iff (-a/p)=1
w3_1 = legendre_symbol(-a, 3)
w109_1 = legendre_symbol(-a, 109)
# p|c: split iff (a/p)=1
w23_1 = legendre_symbol(a, 23)

lw3_1 = -1 if w3_1 == 1 else 1
lw109_1 = -1 if w109_1 == 1 else 1
lw23_1 = -1 if w23_1 == 1 else 1

print(f"  p=3: (-2/3)={w3_1}, w_3={lw3_1}")
print(f"  p=109: (-2/109)={w109_1}, w_109={lw109_1}")
print(f"  p=23: (2/23)={w23_1}, w_23={lw23_1}")

prod1 = lw3_1 * lw109_1 * lw23_1
print(f"  prod_odd = {prod1}")
print(f"  => eps = w_inf * w_2 * prod_odd = (-1)*w_2*({prod1}) = {-prod1}*w_2")
print()

# Orientation 2: E_{b,a} = E_{6436341, 2}
# Odd primes: 3|a(=6436341), 109|a(=6436341), 23|c(=6436343)
print("--- Orientation 2: E_{6436341, 2} ---")
# p|a: split iff (b/p)=1, here b=2
w3_2 = legendre_symbol(2, 3)
w109_2 = legendre_symbol(2, 109)
# p|c: split iff (a/p)=1, a=6436341
w23_2 = legendre_symbol(6436341, 23)

lw3_2 = -1 if w3_2 == 1 else 1
lw109_2 = -1 if w109_2 == 1 else 1
lw23_2 = -1 if w23_2 == 1 else 1

print(f"  p=3: (2/3)={w3_2}, w_3={lw3_2}")
print(f"  p=109: (2/109)={w109_2}, w_109={lw109_2}")
print(f"  p=23: (6436341/23)={w23_2}, w_23={lw23_2}")

prod2 = lw3_2 * lw109_2 * lw23_2
print(f"  prod_odd = {prod2}")
print(f"  => eps = w_inf * w_2 * prod_odd = (-1)*w_2*({prod2}) = {-prod2}*w_2")
print()

# Additional: 6436341 mod 23
print(f"  (Check: 6436341 mod 23 = {6436341 % 23})")
print()

print("=== RESULT ===")
print(f"BOTH orientations: eps = {-prod1}*w_2  (since prod_odd={prod1})")
print()
print("PARI data (TODO line 174-175): eps=-1 ONLY for E_{2, 6436341}.")
print("=> w_2(E_{2, 6436341}) = +1  (from -w_2=-1)")
print("=> w_2(E_{6436341, 2}) = -1  (w_2 flips on a<->b swap)")
print("=> eps(E_{6436341, 2}) = (-1)*(-1)*(+1) = +1")
print()
print("CONCLUSION: Reyssat is NOT a blocker. ANC+ applies to E_{6436341, 2}.")
