# No-Magma Sparse Hecke Quotient: Größenabschätzung

Datum: 2026-05-10

| Level | Faktorisierung | Manin-Symbole = [SL2:Gamma0] | Rows bis T5 | nnz-bound bis T5 | Rows alle 4 | nnz-bound alle 4 |
|---:|---|---:|---:|---:|---:|---:|
| 109 | `109` | 110 | 220 | 1100 | 550 | 5170 |
| 218 | `2 * 109` | 330 | 660 | 3300 | 1650 | 15510 |
| 60168 | `2^3 * 3 * 23 * 109` | 126720 | 253440 | 1267200 | 633600 | 5955840 |
| 80224 | `2^5 * 23 * 109` | 126720 | 253440 | 1267200 | 633600 | 5955840 |
| 120336 | `2^4 * 3 * 23 * 109` | 253440 | 506880 | 2534400 | 1267200 | 11911680 |
| 240672 | `2^5 * 3 * 23 * 109` | 506880 | 1013760 | 5068800 | 2534400 | 23823360 |

Interpretation: Der erste echte Restlevel `60168` liegt in der Größenordnung von ca. 126720 Manin-Symbolen, 253440 Zeilen bis inklusive `T_5-a_5`, und konservativ ca. 1.27 Mio. dünnen Nichtnull-Einträgen im Standard-Hecke-Modell. Das ist kein Kleinstlauf, aber deutlich konkreter als ein voller Newspace-/Newform-Materialisierungsversuch.
