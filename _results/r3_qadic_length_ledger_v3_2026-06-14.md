# R3 v3 — q-adische Laengenebene (2026-06-14)

## (B) per-fixem-q Laengensumme (mit Tiefe) — erwartet blind fuer grosses q

| q | char_len_mean | char_len_max | tate_len_mean | tate_len_max |
|---|---:|---:|---:|---:|
| 101 | 0.0166 | 1 | 0.0 | 0 |
| 251 | 0.00415 | 1 | 0.0 | 0 |
| 1009 | 0.0 | 0 | 0.0 | 0 |
| 3863 | 0.0 | 0 | 0.0 | 0 |
| 5077 | 0.0 | 0 | 0.0 | 0 |

## (C) kurvenspezifische Tiefenverteilung + gewichtete Laengensumme

- **n_triples**: 241
- **mean_L_total**: 4.552
- **max_L_total**: 20
- **mean_L_char**: 4.137
- **mean_L_tate**: 0.415
- **global_max_depth_char**: 3
- **global_max_depth_tate**: 2
- **depth_hist_char**: {'1': 919, '2': 36, '3': 2}
- **depth_hist_tate**: {'1': 98, '2': 1}
- **corr(L_total, q_abc)**: -0.1654
- **corr(L_total, omega)**: 0.2316
- **frac_pairs_depth1_char**: 0.9603
- **frac_pairs_depth1_tate**: 0.9899

Lesart: ist die Tiefenverteilung dominiert von d=1 (frac_pairs_depth1 ~ 1) und max_depth klein,
UND corr(L_total, q_abc) schwach/negativ, dann haelt die qualitaets-flache Eigenschaft auf der
q-adischen LAENGENebene (nicht nur Indikatorebene) => Substanz von Glied 2b (R5.2) auf der
beweisrelevanten Ebene erhaertet. Starke Tiefen oder corr(L_total,q_abc)>0 => lebender Faden.