# FWS-h Phase 3b: Diskriminantenhöhe versus Faltings-Höhe

Datum: 2026-05-17
Input: `_results/frey_watkins_saturation_phase3b_2026-05-17.json`
Skript: `_scripts/frey_faltings_sandwich_phase3b.py`

## Wichtige Korrektur

Die proof-relevante Szpiro-Wand ist nicht die normalisierte Sage-Faltings-Höhe allein,
sondern die Diskriminantenhöhe

```text
H_delta(E) = log |Delta_min(E)| / 12.
```

Die echte Faltings-Höhe enthält archimedische Terme. Sie ist eng verwandt,
aber darf in Beweisnotizen nicht still mit `H_delta` identifiziert werden.

## Kurzbefund

- `n = 60` Frey-Datenpunkte.
- `corr(H_delta/logN, q) = 0.7355`.
- `corr(h_F/logN, q) = 0.5330`.
- `corr(rho, q) = 0.3948`.
- `H_delta/logN` liegt in `0.1969 .. 0.4937`.
- `h_F/logN` liegt in `-0.0975 .. 0.4703`.

## Hochqualitätszone `q >= 1.5`

| Tripel | q | H_delta/logN | h_F/logN | rho |
|---|---:|---:|---:|---:|
| Reyssat (2, 6436341, 6436343) | 1.630 | 0.450 | 0.470 | 1.793 |
| (1, 4374, 4375) | 1.568 | 0.373 | 0.297 | 1.427 |

## Höchste Diskriminantenhöhe

| Rang | Tripel | q | H_delta/logN | h_F/logN | rho |
|---:|---|---:|---:|---:|---:|
| 1 | (625, 2048, 2673) | 1.361 | 0.494 | 0.330 | 1.471 |
| 2 | (1024, 1377, 2401) | 1.185 | 0.486 | 0.287 | 1.362 |
| 3 | (125, 2187, 2312) | 1.242 | 0.474 | 0.318 | 1.429 |
| 4 | (169, 343, 512) | 1.199 | 0.462 | 0.212 | 1.131 |
| 5 | Reyssat (2, 6436341, 6436343) | 1.630 | 0.450 | 0.470 | 1.793 |
| 6 | (243, 1805, 2048) | 1.202 | 0.435 | 0.287 | 1.375 |
| 7 | (139, 2048, 2187) | 1.143 | 0.433 | 0.254 | 1.257 |
| 8 | (128, 2997, 3125) | 1.148 | 0.431 | 0.265 | 1.334 |
| 9 | (13, 243, 256) | 1.273 | 0.414 | 0.143 | 1.006 |
| 10 | (49, 576, 625) | 1.204 | 0.406 | 0.242 | 1.268 |

## Interpretation

Die User-Metapher landet weiterhin auf dem richtigen Objekt, aber das Objekt
sollte präzise `Szpiro-/Diskriminantenhöhe` heißen. In dieser Form ist die
Korrelation mit `q` deutlich stärker als beim Modulargrad und direkt an die
abc/Szpiro-Wand gekoppelt.

Die normalisierte Faltings-Höhe bleibt als Arakelov-Variante nützlich, ist
aber für kleine Kurven stark archimedisch verschoben. Für die Backup-Route
sollte daher `FWS-h_delta` die Primärform sein.
