# B2(i): Mikro-Cluster am 60168-Zeugen + C1-Vorbereitung (2026-06-11)

Matrix 31680×31680 (nnz 137273), Einträge ±1: 92.3%. Kanten: 209075 | w-Median 0.2236, p99 0.5000, max 0.8165 | exakt parallel: 0

**Kern w ≥ 0.5:** 4348 Kanten, 7665 Spalten (24.20%), 3322 Komponenten, Größen-Histogramm {'2': 2406, '3': 814, '4': 99, '5': 3} (max 5).

Schicht-Signaturen (maninT, T₅) top: (0, 2)×4001, (0, 3)×277, (0, 4)×38, (1, 0)×13, (1, 1)×10, (0, 1)×8

**Block-Spektren:** 0 singulär (echte dünne Kerne); λ_min p1 0.345, median 0.465; Blöcke < 0.3: 22.

Laufzeit: 2.5s. JSON: `_results/b2_microcluster_60168_c1_match_2026-06-11.json`

## Befund: Universalität + C1-Match (2026-06-11)

**(i1) Universalität der (f)-Klassifikation über Level:** Auch am
60168-Zeugen ist der schwere Kern mikro-lokal (3.322 Komponenten, ALLE
≤ 5 Spalten) und fast rein Hecke-getrieben: Signatur (maninT, T₅) =
(0,2)×4001 dominiert (zwei gemeinsame T₅-Zeilen; w_max = 2/√6 = 0.8165
exakt nach Gewichtsformel), maninT-only nur 13. Block-λ_min p1 = 0.345 —
fast identisch zur 240672-Konstante (0.362): **dieselbe Strukturkonstante
über Level.**

**(i2) NULL dünne Kerne:** 0 exakt parallele Paare, 0 singuläre Blöcke —
am 60168-Zeugen existiert kein einziger Kernvektor mit Träger ≤ 5. Die
2 Duplikat-Paare am 240672 waren level-spezifische Artefakte.

**(i3) C1-Match — Mikro-Cluster sind p2-Kern-homogen:**
- Anreicherung im mod-2-Kern-Support (21.128/31.680, Dichte 0.667):
  5.750 von 7.665 Cluster-Spalten im Support (erwartet 5.112 ± 41,
  **z = +15.5**).
- Komponentenweise Kohärenz: 2.001 Komponenten GANZ im Support
  (erwartet 1.332), 455 GANZ im Komplement (erwartet 298), nur 866
  gemischt (erwartet ~1.692). Die T₅-Multikanten verbinden bevorzugt
  Spalten DERSELBEN p2-Kern-Klasse.
- Vermutete Erklärung (zu beweisen): Hecke-Äquivarianz — mod 2 ist
  T₅−2 ≡ T₅, und der p2-Kern ist Hecke-stabil; die Multikanten
  (gemeinsame T₅-Zeilen) respektieren dann die Kern-Partition.
  **Das wäre der erste BEWEISBARE Struktur-Link B2 ↔ C1.**
- Anti-Korrelation mit Quotient-Blöcken: nur 0,1% der Cluster-Spalten
  in Blöcken 9–10 (Spaltenanteil 18,2%); T₇-Stern (5 Spalten) disjunkt.

**Caveat:** p2-Kern stammt aus dem Repair-Witness (p=2-Zeilensystem),
Mikro-Cluster aus dem rc3c-Witness (q=3863) — gleiche Spaltenbasis
(P¹-Symbole, 31.680, gleiche Pipeline), verschiedene Zeilensysteme.
