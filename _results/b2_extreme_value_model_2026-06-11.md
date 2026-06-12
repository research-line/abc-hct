# B2(k): Extremwert-Modell für das λ_min-Power-Law (2026-06-11)

**(1) Tail-Fit** (400 Bälle, s=16): unterer Tail F(λ) ~ λ^β mit **β = 6.081** ⟹ Vorhersage α = 1/β = **0.164** — gemessen (g2): ball_rand 0.392, ball_heavy 0.532.

λ_min-Quantile der kleinen Bälle: p1: 0.1461, p5: 0.1948, p25: 0.2608, p50: 0.3028

**(2) Lokalitäts-Reduktion** (κ = λ_min(S)/min lokale Fenster ≤ 24; Cauchy-Interlacing ⟹ κ ≤ 1 exakt):

| s | κ median | κ min | κ max | λ_min med | lokales min med |
|---|---|---|---|---|---|
| 128 | 0.632 | 0.426 | 0.897 | 0.1251 | 0.2188 |
| 256 | 0.421 | 0.263 | 0.701 | 0.0815 | 0.1948 |
| 512 | 0.436 | 0.322 | 0.757 | 0.0747 | 0.1789 |

Laufzeit: 10.8s. JSON: `_results/b2_extreme_value_model_2026-06-11.json`

## Befund (2026-06-11)

**(k1) Naives Order-Statistics-Modell FALSIFIZIERT:** β = 6.08 aus dem
16er-Ball-Tail ⟹ α_pred = 0.16 ≠ gemessen 0.39–0.53. Das einfache
i.i.d.-Extremwert-Bild mit 16er-Bällen als lokaler Einheit reicht nicht
(Korrekturkandidaten: korrelierte Extremwerte, richtige lokale Einheit
= Radius-1-Fenster, nicht-asymptotischer Tail).

**(k2) LOKALITÄTS-REDUKTION HÄLT (der beweisrelevante Teil):**
κ = λ_min(S)/min(lokale Radius-1-Fenster ≤ 24) ∈ [0.26, 0.90] in allen
32 Trials (s = 128–512), Median 0.42–0.63. Mit Cauchy-Interlacing
(κ ≤ 1 exakt) gilt: **λ_min(global) ≍ lokales Fenster-Minimum bis Faktor
~2–4.** Die globale Flachheit ist durch endliche lokale Konfigurationen
bestimmt — die Reduktions-Hypothese L(κ ≥ 1/4) ist empirisch gedeckt
und ist die richtige Lemma-Form für v3(iii) (statt des Power-Law-Fits).
