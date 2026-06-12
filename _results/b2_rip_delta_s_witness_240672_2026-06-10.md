# B2: delta_s-RIP-Messung der Witness-Matrix 240672/raw (2026-06-10)

Matrix: 126672x126720, nnz=558529, Spalten normalisiert (R, symmetrischer Lift mod 3863).
400 Samples je Modus. Modi: random / consecutive / arith_prog (Index-Proxy für additive Struktur).

| s | Modus | δ Median | δ p95 | δ max | λ_min Median | λ_min min | Anteil singulär |
|---|---|---|---|---|---|---|---|
| 8 | random | 0.0000 | 0.0000 | 0.1291 | 1.0000 | 0.8709 | 0.000 |
| 8 | consecutive | 0.5245 | 0.7590 | 0.8387 | 0.4755 | 0.1613 | 0.000 |
| 8 | arith_prog | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.000 |
| 16 | random | 0.0000 | 0.0000 | 0.3162 | 1.0000 | 0.6838 | 0.000 |
| 16 | consecutive | 0.6104 | 0.8091 | 0.9158 | 0.3896 | 0.0842 | 0.000 |
| 16 | arith_prog | 0.0000 | 0.0000 | 0.2500 | 1.0000 | 0.7500 | 0.000 |
| 32 | random | 0.0000 | 0.1690 | 0.3333 | 1.0000 | 0.6667 | 0.000 |
| 32 | consecutive | 0.6711 | 0.8554 | 0.9244 | 0.3289 | 0.0756 | 0.000 |
| 32 | arith_prog | 0.0000 | 0.1690 | 0.5000 | 1.0000 | 0.5000 | 0.000 |
| 64 | random | 0.0000 | 0.2582 | 0.4082 | 1.0000 | 0.5918 | 0.000 |
| 64 | consecutive | 0.6803 | 0.8700 | 0.9144 | 0.3200 | 0.0856 | 0.000 |
| 64 | arith_prog | 0.0000 | 0.2582 | 0.5000 | 1.0000 | 0.5000 | 0.000 |
| 128 | random | 0.1890 | 0.4082 | 0.5000 | 0.8110 | 0.5000 | 0.000 |
| 128 | consecutive | 0.7119 | 0.8965 | 0.9714 | 0.2891 | 0.0680 | 0.000 |
| 128 | arith_prog | 0.1667 | 0.3348 | 0.5681 | 0.8333 | 0.4901 | 0.000 |

Laufzeit: 712.1s. JSON: `_results/b2_rip_delta_s_witness_240672_2026-06-10.json`

## Befund: Die BDFKK-Dichotomie existiert empirisch in der Witness-Matrix

1. **Random-Horn ist RIP-artig exzellent:** δ-Median = 0.000 bis s=64,
   selbst bei s=128 nur 0.19; λ_min nie unter 0.5; **0 singuläre Grams in
   6000 Samples**. Zufällige Spaltenmengen sind fast orthonormal — dünne
   Nullkombinationen in zufälliger Lage praktisch ausgeschlossen.
2. **Struktur-Horn reißt massiv aus — aber nur im consecutive-Modus:**
   δ-Median 0.52–0.71 (p95 bis 0.90), λ_min-Median ≈ 0.3, min 0.068.
   Benachbarte Quotientenspalten sind stark korreliert (gemeinsame
   manin_T-/2-Term-Relationen).
3. **Überraschung: arith_prog verhält sich wie random** (δ-Median 0.000) —
   die im Witness-Raum relevante „Struktur" ist NICHT generische additive
   Index-Struktur, sondern **relationsinduzierte Nachbarschaft** (P¹-/
   Manin-Graph). Das Energie-Analogon der Übersetzungsthese ist damit
   empirisch identifiziert: Relations-Koinzidenz, nicht Index-Arithmetik.
4. Für CR-2b/sparse-nullvector: Selbst strukturierte Mengen sind bei
   s ≤ 128 nie singulär — echte dünne Kernvektoren müssen noch
   strukturierter sein als konsekutiv; konsistent mit dem Befund, dass
   die bekannten Kernklassen (z.B. mod-2-Paritätsklasse, Support 21128)
   BREIT sind.

**Caveats:** Sampling-Quantile (kein Max über alle S); Index-Proxys;
ℝ-Lift (Kernfragen leben über F_q — Bezug heuristisch); 400 Samples/Modus.
