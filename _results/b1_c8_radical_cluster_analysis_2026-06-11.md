# B1/C8: Radikal-Cluster-Analyse der de-Smit-Champions (2026-06-11)

240 Tripel geparst (a+b=c exakt), q-Nachrechnung: 240/240 innerhalb 0.005.

**(2) Potenz-Bilder (x ≥ 100, k=2,3, alle Slots):** 10 Treffer; volle Verdopplungs-Bilder (c′=c²): 1 — Vorhersage der Kompositions-Kontraktion q→2q/(1+q): leer.

| P₀ | Primes>P₀ | Paare ≥1 gem. | Null (μ±σ) | z | Paare ≥2 gem. | Null | z | Komp.-Größen |
|---|---|---|---|---|---|---|---|---|
| 7 | 238 | 17265 | 17185±217 | +0.4 | 5696 | 5806.5±126.5 | -0.9 | [237] |
| 13 | 236 | 9595 | 9519±99 | +0.8 | 1449 | 1557.1±76.1 | -1.4 | [231] |
| 50 | 227 | 1402 | 1417±7 | -2.1 | 42 | 29.5±6.9 | +1.8 | [190] |

**Top-Mehrfach-Sharing-Paare (P₀=13):**
- Ranks [48, 142] | 9 gemeinsame Primes > 13: [17, 19, 23, 37, 43, 61, 127, 173, 4817]
- Ranks [10, 32] | 4 gemeinsame Primes > 13: [17, 23, 29, 31]
- Ranks [32, 216] | 4 gemeinsame Primes > 13: [17, 23, 29, 47]
- Ranks [48, 188] | 4 gemeinsame Primes > 13: [17, 23, 37, 43]
- Ranks [101, 211] | 4 gemeinsame Primes > 13: [19, 23, 29, 53]
- Ranks [142, 188] | 4 gemeinsame Primes > 13: [17, 23, 37, 43]

Laufzeit: 49.7s. JSON: `_results/b1_c8_radical_cluster_analysis_2026-06-11.json`

## Befund (2026-06-11) — B1 GESCHLOSSEN

**(B1-Statistik) Keine breite Kompositions-Struktur:** Nach Umstellung des
Nullmodells auf degree-erhaltende Edge-Swaps (Stub-Matching hatte
Schein-Exzesse z ≈ 10–15 produziert — Kanten-Verlust-Bias!) sind alle
Sharing-Statistiken Konfigurationsmodell-kompatibel (|z| ≤ 2.1).

**(B1-Strukturen) Zwei reale Kompositionen exakt verifiziert:**
1. Verdopplungs-Paar Rang 5 → 73: (1, 2·3⁷, 5⁴·7) → (1², b(a+c), c²)
   exakt; Erhalt über 1.4 NUR weil a+c = 2³·547 radikal-arm
   (Erhalt-Kriterium rad(a+c) ≤ c^{1/q} real instanziiert).
2. Materialpaar Rang 48 ↔ 142: v = 3⁷·11⁴·61·173², w = 2²⁶·19³·127 mit
   s = v+w und u = w−v BEIDE radikal-arm ⟹ (u², 4vw, s²) = Rang 48 und
   (su, v², w²) = Rang 142 (4 Gleichungen exakt geprüft). Erklärt die
   4 gemeinsamen Primes > 50 vollständig.

**Urteil:** Alle Operationen sind Informations-Konsumenten mit endlicher
Ausbeute; keine maßerhaltende Randomisierung im Tripelraum. **B1
(Ajtai-Selbstreduktion) geschlossen.** Details + Kontraktions-Lemma
q → 2q/(1+q): `MG_b1_kill_test_part2_composition_2026-06-11.md`.
