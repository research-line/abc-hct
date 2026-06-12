# B2(d): Konstruktives orthonormales Teilsystem + Cancellation (2026-06-11)

Cliquengrößen (Zeilen-nnz): {1: 1, 2: 2, 3: 84468, 4: 13, 5: 21743, 6: 9911, 9: 2, 10: 1, 11: 8, 12: 28, 13: 10495}

**Greedy-Independent-Set: 27489 Spalten (21.7% aller Spalten)** — Turán-Garantie wäre 5700.
Verifikation G_S = I (20 × 256er-Stichproben, atol 1e-12): BESTANDEN.

| K | θ′ Median | θ′ p95 | θ′ max | Cancellation-Faktor Median | p95 |
|---|---|---|---|---|---|
| 64 | 0.0006 | 0.0072 | 0.0099 | 1.000 | 1.000 |
| 128 | 0.0019 | 0.0056 | 0.0119 | 0.479 | 1.000 |
| 256 | 0.0021 | 0.0066 | 0.0099 | 0.245 | 0.765 |
| 512 | 0.0025 | 0.0074 | 0.0102 | 0.133 | 0.399 |

θ′(I,J) = |⟨Σ_I φ, Σ_J φ⟩|/K (weak-flat-RIP-Größe); Cancellation = |Σ a_r b_r|/Σ|a_r b_r|.
Laufzeit: 14.9s. JSON: `_results/b2_orthonormal_system_witness_240672_2026-06-11.json`

## Befund

1. **Erstes unbedingtes, konstruktives Resultat der B2-Linie:** Die
   Witness-Matrix enthält ein explizit konstruiertes (min-degree-greedy),
   **exakt orthonormales Teilsystem von 27 489 Spalten (21.7%)** —
   fast 5× über der Turán-Garantie (5700); Verifikation G_S = I mit
   atol 10⁻¹² bestanden. Auf diesem Teilsystem gilt δ_s = 0 für ALLE
   s ≤ 27 489 — perfekte RIP; jede Nullkombination des Gesamtsystems
   muss den Koinzidenz-Graphen benutzen.
2. **weak-flat-RIP-Größe θ′ ist empirisch winzig:** Median 0.0006–0.0025,
   p95 < 0.008, max ≈ 0.012 bis K = 512. Das Zielniveau für ein
   deterministisches Lemma ist damit beziffert: θ′ ≲ 0.01.
3. **Das analytische Horn ist real:** Der Cancellation-Faktor
   |Σ a_r b_r|/Σ|a_r b_r| fällt von 1.0 (K=64) auf 0.133 (K=512) —
   die ±1-Vorzeichenstruktur der Manin-/Heilbronn-Relationen erzeugt
   echte, mit K wachsende Auslöschung (Faktor ~7.5).
4. **Hypergraph-Struktur dreischichtig sauber:** 84 468 Dreiecke
   (manin_T), ~31 654 5er/6er-Cliquen (U₃-Sterne), 10 495 13er-Cliquen
   (T₅-Sterne) — die Objekte des Struktur-Horns sind vollständig
   enumeriert.

**Formuliertes nächstes Beweisziel (B2-Hauptlemma-Kandidat):**
deterministische θ′-Schranke aus der P¹(ℤ/N)-Kombinatorik der drei
Cliquen-Schichten + Vorzeichenstruktur; empirische Zielmarke θ′ ≲ 0.01.
Zirkularität: reine Graph-/Charaktersummen-Kombinatorik, kein rad-Input.
