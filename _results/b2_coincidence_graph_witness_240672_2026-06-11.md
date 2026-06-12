# B2: Koinzidenz-Graph der Witness-Matrix 240672/raw (2026-06-11)

Kanten (i~j ⟺ ⟨φ_i,φ_j⟩≠0): 1345054 | Dichte ρ = 1.675e-04

| Größe | max | median | p99 |
|---|---|---|---|
| Grad (Partner/Spalte) | 114 | 16.0 | 74.0 |
| Kantengewicht w_ij | 1.0000 | 0.1961 | 0.4629 |
| Gershgorin-Radius/Spalte | 15.6530 | 4.1603 | 11.7462 |

Isolierte Spalten: 0 | Spalten mit Gershgorin-Radius < 1: 0.1%

Random-Horn-Vorhersage P(s-Set unabhängig) = (1−ρ)^(s(s−1)/2): s=8: 0.995, s=16: 0.980, s=32: 0.920, s=64: 0.713, s=128: 0.256

Laufzeit: 2.5s. JSON: `_results/b2_coincidence_graph_witness_240672_2026-06-11.json`

## Befund: Der Random-Horn-Mechanismus ist vollständig verstanden

1. **Die Vorhersage P(s-Set unabhängig) = (1−ρ)^(s(s−1)/2) reproduziert die
   δ_s-Empirie vom 2026-06-10 quantitativ:** s ≤ 64: Mehrheit unabhängig ⟹
   δ-Median exakt 0 (gemessen ✓); s = 128: nur 26% unabhängig ⟹ δ-Median
   springt auf 0.19 (gemessen ✓). Zufällige Mengen sind RIP-gut, WEIL sie
   meist unabhängig im Koinzidenz-Graphen sind — und dann ist G_S = I exakt.
2. **w_max = 1.0:** Es existieren kollineare Spaltenpaare (±1-2-Term-
   Relationen) — das sind genau die consecutive-Ausreißer (δ → 0.97).
3. **Gershgorin global nutzlos (Median-Radius 4.2), S-intern scharf:**
   Die richtige Schranke ist der S-interne Radius — für dünn besetzte S
   praktisch 0.

## Mini-Lemma (deterministisch, mit gemessenen Konstanten)

Für die Witness-Matrix A (Spalten φ_i normiert), H = Koinzidenz-Graph
(i~j ⟺ ∃ Zeile, die i und j trifft), gemessen: ρ = 1.675·10⁻⁴,
Grad-Median 16, Grad-Max 114, w-Median 0.196:

- **(L1, exakt):** Ist S unabhängig in H, dann G_S = I — δ(S) = 0,
  keine dünne Nullkombination auf S. *Beweis:* ⟨φ_i,φ_j⟩ = Σ_r M_ri·M_rj
  hat nur Beiträge von Zeilen, die beide Spalten treffen. ∎
- **(L2, Gershgorin):** δ(S) ≤ max_{i∈S} Σ_{j∈S∖{i}} w_ij — kontrolliert
  durch die S-INTERNE gewichtete Kantenzahl.
- **(L3, Random-Horn):** P(uniformes s-Set unabhängig) ≈ (1−ρ)^(s(s−1)/2)
  — validiert gegen die 6000-Sample-Messung.

**Konsequenz fürs Programm:** Die weak-flat-RIP-Frage für die Witness-
Matrix REDUZIERT sich auf Graphkombinatorik: obere Schranken für
gewichtete Kantenzahlen e_H(I,J) zwischen disjunkten Spaltenmengen.
Das BDFKK-„Energie"-Analogon ist exakt e_H(S); dichte Teilgraphen von H
sind algebraisch beschreibbar (manin_T-Dreiecke, Heilbronn-Sterne,
P¹-Bahnen) — das Struktur-Horn hat eine benennbare Objektklasse.
Zirkularitäts-Check: reine Graphkombinatorik, kein rad-/Höhen-Input. ✓
