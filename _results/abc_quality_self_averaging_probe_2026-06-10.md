# B3 Self-Averaging-Diagnostik der abc-Qualität (2026-06-10)

Alle Tripel a+b=c, gcd(a,b)=1, c ≤ 131071. q = log c / log rad(abc).
Blöcke pro Dyade: 16. Script: `_scripts/abc_quality_self_averaging_probe.py`.

| k | c-Fenster | n | ⟨q⟩ | R_q (Tripel) | R_q (Block) | max q | p(q>0.9) | M₀.₈/n | R_M0.8 (Block) | R_M0.9 (Block) |
|---|---|---:|---|---|---|---|---|---|---|---|
| 6 | [64, 127] | 1865 | 0.4570 | 0.037 | 0.00289 | 1.292 | 3.75e-03 | 1.08e-03 | 5.62 | 7.76 |
| 7 | [128, 255] | 7431 | 0.4374 | 0.0276 | 0.0011 | 1.427 | 1.35e-03 | 4.04e-04 | 4.56 | 5.5 |
| 8 | [256, 511] | 29888 | 0.4234 | 0.0214 | 0.000298 | 1.273 | 5.02e-04 | 1.35e-04 | 2.25 | 2.91 |
| 9 | [512, 1023] | 119428 | 0.4127 | 0.0176 | 0.000188 | 1.318 | 2.85e-04 | 7.37e-05 | 2 | 2.83 |
| 10 | [1024, 2047] | 478055 | 0.4040 | 0.0141 | 6.16e-05 | 1.297 | 6.48e-05 | 1.88e-05 | 1.27 | 2.86 |
| 11 | [2048, 4095] | 1911705 | 0.3969 | 0.0119 | 3.69e-05 | 1.456 | 4.39e-05 | 1.30e-05 | 1.06 | 1.39 |
| 12 | [4096, 8191] | 7649771 | 0.3910 | 0.0099 | 2.18e-05 | 1.568 | 1.39e-05 | 4.20e-06 | 0.732 | 1.17 |
| 13 | [8192, 16383] | 30596816 | 0.3861 | 0.00833 | 1.28e-05 | 1.285 | 5.33e-06 | 1.64e-06 | 0.449 | 0.793 |
| 14 | [16384, 32767] | 122389927 | 0.3819 | 0.0071 | 9.4e-06 | 1.282 | 2.12e-06 | 6.80e-07 | 0.817 | 1.53 |
| 15 | [32768, 65535] | 489555579 | 0.3782 | 0.00608 | 7.06e-06 | 1.547 | 6.80e-07 | 2.22e-07 | 0.365 | 0.717 |
| 16 | [65536, 131071] | 1958279015 | 0.3751 | 0.00527 | 5.46e-06 | 1.435 | 3.16e-07 | 1.01e-07 | 0.374 | 0.558 |

Laufzeit: 649.8s. JSON: `_results/abc_quality_self_averaging_probe_2026-06-10.json`.

## Befund (Interpretation siehe `_proof-notes/MG_b3_self_averaging_diagnostic_2026-06-10.md`)

1. **Bulk ist self-averaging:** R_q fällt monoton auf Tripel-Ebene
   (0.037 → 0.0053) und steil auf Block-Ebene (2.9e-3 → 5.5e-6).
2. **Tail-Masse ist im Messbereich NICHT self-averaging:** R der
   Block-Tail-Masse (θ=0.8/0.9) fällt von ~5–8 (k=6) nur bis ~0.4–0.8
   (k=13) und **stagniert dann auf O(1)** über die letzten 4 Dyaden
   (k=13–16: R_M0.9 = 0.79, 1.53, 0.72, 0.56) — während die
   Bulk-Block-R im selben Bereich um Größenordnungen weiter fällt.
   Einzelne Champions dominieren die Block-Masse (k=14-Ausreißer).
3. **CLT-Verletzungs-Kontrolle:** Bei k=16 wäre unter Unabhängigkeit
   R_q(Block) ≈ R_q(Tripel)/n_block ≈ 4e-11; beobachtet 5.5e-6
   (~10⁵ darüber) — dominiert vom deterministischen ⟨q⟩-Drift über das
   Fenster (Trend-Artefakt, kein Korrelations-Claim; Detrending offen).
4. max q pro Dyade trendlos in [1.27, 1.57]; absolute Anzahl q>0.9
   wächst pro Dyade (≈7 bei k=6, ≈619 bei k=16) bei steil fallendem Anteil.
