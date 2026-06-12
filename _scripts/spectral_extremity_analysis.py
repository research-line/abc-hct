import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

data = [
    ("1+2=3", 0.613147, 1, 1.1714200841, 0.3742353925),
    ("1+8=9", 1.226294, 1, 0.8428751774, 0.3202233192),
    ("1+48=49", 1.041242, -1, 1.4261701612, 0.3331091225),
    ("1+63=64", 1.112694, 1, 0.8688618644, 0.3413016699),
    ("1+80=81", 1.292030, 1, 1.5962422221, 0.4055514735),
    ("1+1023=1024", 0.909207, 1, 1.8198641983, 0.2705905180),
    ("1+2400=2401", 1.455673, 1, 1.7236114974, 0.2692229396),
    ("1+4374=4375", 1.567887, 1, 1.3493965216, 0.1772371537),
    ("1+6560=6561", 1.235303, -1, 5.4845362519, 0.5506696446),
    ("2+109=111", 0.466566, -1, 2.9320274460, 0.1175420248),
    ("3+125=128", 1.426565, 1, 1.1583921113, 0.2943084835),
    ("5+27=32", 1.018975, 1, 0.5586580432, 0.2387073229),
    ("7+2187=2194", 0.716472, -1, 7.0498481523, 0.2405945512),
    ("13+243=256", 1.272790, 1, 0.7252179631, 0.2440309452),
    ("32+49=81", 1.175719, 1, 0.8688618644, 0.3413016699),
    ("2+6859=6861", 0.708321, -1, 6.3455663559, 0.1404098710),
    ("1+191=192", 0.746376, -1, 3.4984969533, 0.6012918891),
    ("Reyssat", 1.629912, -1, 11.1803795338, 0.5047776934),
    ("1+4095=4096", 1.051277, 1, 2.7727274484, 0.3835893315),
    ("11+32=43", 0.548901, 1, 1.3091852930, 0.2360632238),
    ("1+3071=3072", 0.817601, 1, 4.6780047930, 0.4015160366),
    ("343+2048=2391", 0.746696, 1, 8.2788936366, 0.6120619760),
    ("1+32767=32768", 0.937503, 1, 3.2011762141, 0.2000750398),
    ("1+78124=78125", 0.924786, 1, 3.1642602811, 0.0894990825),
    ("2187+131072=133259", 0.868174, -1, 4.2553036646, 0.1423044914),
    ("1+14348906=14348907", 1.085592, 1, 0.0, 0.0),
    ("16+2171=2187", 0.811665, 1, 4.6106882957, 0.2566199982),
    ("1+531440=531441", 1.080379, 1, 4.2023882144, 0.1182639271),
]

sorted_data = sorted(data, key=lambda x: x[1])

print("=" * 90)
print("SPECTRAL EXTREMITY TEST: L-value / N^{1/4} vs quality q")
print("=" * 90)
print(f"{'Triple':<26} {'q':>8} {'w':>3} {'L-val':>12} {'L/N^{1/4}':>12}")
print("-" * 90)

ratios = []
for label, q, w, lval, ratio in sorted_data:
    if lval == 0.0:
        note = " <-- rank>=2?"
    else:
        note = ""
    deriv = "'" if w == -1 else ""
    print(f"{label:<26} {q:>8.4f} {w:>+3d} {lval:>12.6f} {ratio:>12.6f}{note}")
    ratios.append((q, ratio, w))

print("\n" + "=" * 90)
print("MONOTONICITY CHECK")
print("=" * 90)

non_zero = [(q, r, w) for q, r, w in ratios if r > 0]
up = 0
down = 0
for i in range(1, len(non_zero)):
    if non_zero[i][1] > non_zero[i-1][1]:
        up += 1
    elif non_zero[i][1] < non_zero[i-1][1]:
        down += 1

print(f"Transitions (excl. L=0): {up} up, {down} down")
print(f"Monotone? {'YES' if down == 0 else 'NO'}")

rank1 = [(q, r) for q, r, w in ratios if w == -1]
rank1_sorted = sorted(rank1, key=lambda x: x[0])
print(f"\nRank-1 only (w=-1, {len(rank1)} curves):")
r1_up = 0
r1_down = 0
for i in range(1, len(rank1_sorted)):
    direction = "UP" if rank1_sorted[i][1] > rank1_sorted[i-1][1] else "DOWN"
    print(f"  q={rank1_sorted[i-1][0]:.4f}->{rank1_sorted[i][0]:.4f}: "
          f"{rank1_sorted[i-1][1]:.4f}->{rank1_sorted[i][1]:.4f} ({direction})")
    if direction == "UP":
        r1_up += 1
    else:
        r1_down += 1
print(f"  Transitions: {r1_up} up, {r1_down} down")
print(f"  Monotone? {'YES' if r1_down == 0 else 'NO'}")

import statistics
qs = [q for q, r, w in non_zero]
rs = [r for q, r, w in non_zero]
if len(qs) > 1:
    mean_q = statistics.mean(qs)
    mean_r = statistics.mean(rs)
    cov = sum((qs[i] - mean_q) * (rs[i] - mean_r) for i in range(len(qs)))
    var_q = sum((q - mean_q)**2 for q in qs)
    var_r = sum((r - mean_r)**2 for r in rs)
    if var_q > 0 and var_r > 0:
        corr = cov / (var_q * var_r) ** 0.5
        print(f"\nPearson correlation (all, excl L=0): r = {corr:.4f}")

    rank1_qs = [q for q, r in rank1_sorted]
    rank1_rs = [r for q, r in rank1_sorted]
    mean_q1 = statistics.mean(rank1_qs)
    mean_r1 = statistics.mean(rank1_rs)
    cov1 = sum((rank1_qs[i] - mean_q1) * (rank1_rs[i] - mean_r1) for i in range(len(rank1_qs)))
    var_q1 = sum((q - mean_q1)**2 for q in rank1_qs)
    var_r1 = sum((r - mean_r1)**2 for r in rank1_rs)
    if var_q1 > 0 and var_r1 > 0:
        corr1 = cov1 / (var_q1 * var_r1) ** 0.5
        print(f"Pearson correlation (rank-1 only): r = {corr1:.4f}")

print("\n" + "=" * 90)
print("VERDICT")
print("=" * 90)
