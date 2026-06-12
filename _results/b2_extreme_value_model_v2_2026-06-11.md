# B2(n): Extremwert-Modell v2 — Fenster-Tail (2026-06-11)

6000 Radius-1-Fenster (cap 24), λ-Quantile: p0.1: 0.1437, p1: 0.1894, p5: 0.2335, p25: 0.2939, p50: 0.3385

**Fenster-Tail β_w = 7.688 ⟹ α_pred = 0.130** (gemessen g2 ball_rand: 0.392).

**Absolute Vorhersage** λ_pred(s) = F_window⁻¹(ln2/s), Korridor [κ_min·λ_pred, λ_pred] mit κ_min = 0.26:

| s | gemessen (g2) | λ_pred | Korridor | im Korridor |
|---|---|---|---|---|
| 16 | 0.3022 | 0.2288 | [0.0595, 0.2288] | ✗ |
| 32 | 0.2164 | 0.2082 | [0.0541, 0.2082] | ✗ |
| 64 | 0.1547 | 0.1915 | [0.0498, 0.1915] | ✓ |
| 128 | 0.0963 | 0.1764 | [0.0459, 0.1764] | ✓ |
| 256 | 0.1105 | 0.1596 | [0.0415, 0.1596] | ✓ |
| 512 | 0.0568 | 0.1444 | [0.0375, 0.1444] | ✓ |
| 1024 | 0.0550 | 0.1363 | [0.0354, 0.1363] | ✓ |
| 2048 | 0.0371 | 0.1333 | [0.0346, 0.1333] | ✓ |
| 4096 | 0.0369 | 0.1229 | [0.0320, 0.1229] | ✓ |

Laufzeit: 18.2s. JSON: `_results/b2_extreme_value_model_v2_2026-06-11.json`

## Befund (2026-06-11)

**Korridor-Vorhersage trifft 7/9 Größen:** λ_pred(s) = F_window⁻¹(ln2/s)
mit κ-Korridor [0.26·λ_pred, λ_pred] enthält die (g2)-Messwerte für
s = 64…4096; bei s = 16/32 liegt die Messung ÜBER λ_pred (harmlose Seite:
kleine Bälle enthalten noch kein volles schlechtes Fenster). **Die
Größenordnung der globalen Flachheit wird von den lokalen Radius-1-Fenstern
getragen** — konsistent mit der κ-Reduktion aus (k).

**Steigung weiterhin unterschätzt:** β_w = 7.7 ⟹ α_pred = 0.13 ≠ 0.39.
Das i.i.d.-Fenster-Minimum fällt zu langsam; der gemessene Abfall wird
zusätzlich von KORRELIERTEN Wenig-Fenster-Kollektivmoden getrieben (genau
die 1/IPR ≈ 18–20-Ausnahmemoden aus g2). Verfeinerungs-Kandidat:
Radius-2-Konfigurationen als Einheit. Für die Lemma-Form irrelevant —
die beweisrelevante Aussage bleibt die κ-Reduktion (λ_min ≍ lokal).
