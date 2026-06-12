# B2(f): Struktur-Kern-Klassifikation + generischer Teil (2026-06-11)

Kanten gesamt: 1345054 | Gewichts-Quantile: median 0.1961, p99 0.4629, p99.9 0.5345, max 1.0000 | exakt parallel: 2

| θ_c | schwere Kanten | Kern-Spalten | Anteil | Komponenten | max Komp. |
|---|---|---|---|---|---|
| 0.5 | 3505 | 6115 | 4.83% | 2634 | 6 |
| 0.3 | 167155 | 117079 | 92.39% | 3689 | 106132 |
| 0.2 | 640024 | 126720 | 100.00% | 1 | 126720 |
| 0.1 | 1319287 | 126720 | 100.00% | 1 | 126720 |
| 0.05 | 1345054 | 126720 | 100.00% | 1 | 126720 |

**Klassifikation (θ_c = 0.3, 167155 Kanten):** beide Spalten-nnz ≤2: 4.6%, ≤4: 48.8%

Multiplizität gemeinsamer Zeilen: {'1.0': 123801, '2.0': 24377, '3.0': 11956, '4.0': 7021}

Top Schicht-Signaturen (maninT, U₃, T₅): (1, 0, 0)×70677, (0, 0, 1)×49726, (0, 2, 0)×16918, (0, 0, 3)×8880, (0, 0, 2)×7383, (0, 0, 4)×7019

Top Spalten-nnz-Paare (lo, hi): (3, 3)×25964, (2, 3)×20640, (2, 4)×16192, (2, 5)×11119, (4, 5)×10613, (2, 2)×7616

**Generischer Teil (θ_c = 0.5):** 120605 Spalten (95.2%). Gershgorin: max 15.023, p99 10.487, median 3.712; <0.5: 0.0%, <1: 0.7%. Adversarial θ′: K=64: 0.500, K=128: 0.500, K=256: 0.500, K=512: 0.500, K=1024: 0.500

**Generischer Teil (θ_c = 0.3):** 9641 Spalten (7.6%). Gershgorin: max 1.871, p99 1.276, median 0.381; <0.5: 65.0%, <1: 95.5%. Adversarial θ′: K=64: 0.293, K=128: 0.291, K=256: 0.290, K=512: 0.289, K=1024: 0.273

Laufzeit: 9.8s. JSON: `_results/b2_structure_kernel_classification_2026-06-11.json`

## Befund (Klassifikation, 2026-06-11)

**(f1) Anatomie des schweren Kerns (w ≥ 0.5):** 3.505 Kanten, 6.115 Spalten
(4,8%), 2.634 Zusammenhangskomponenten — **alle ≤ 6 Spalten** (2.034 Paare,
366 Dreier, 224 Vierer, 7 Fünfer, 3 Sechser). Schicht-Signaturen
(maninT, U₃, T₅) der gemeinsamen Zeilen: (0,0,4)×2007, (0,3,0)×719,
(0,0,3)×451, (0,0,2)×139, (0,2,0)×135 — **rein maninT: nur 16**. Der
Struktur-Kern besteht also fast ausschließlich aus **kohärenten
Hecke-Multikanten** (Spaltenpaare mit 2–4 gemeinsamen T₅-/U₃-Zeilen und
gleichgerichteten Vorzeichenprodukten) = kurze Zykel/Multikanten im
Hecke-Korrespondenz-Graphen. Die manin-Dreiecke erzeugen praktisch keinen
schweren Kern (ihr 1:2-Vorzeichengesetz + Normverdünnung hält sie unter 0.5).

**(f2) Exakte Gewichtsformel:** 98,1% aller Matrixeinträge sind ±1 (Rest ±2)
⟹ w_ij ≈ mult_ij/√(nnz_i·nnz_j) bei kohärenten Vorzeichen. Check: häufigstes
nnz-Paar der 0.5-Kanten ist (7,8) mit mult 4 → 4/√56 = 0.535 = exakt der
Median der 0.5-Kanten-Gewichte. **Klassifikation = „Multikanten mit
kohärenten Vorzeichen" — ein endliches, lokales, algebraisch ansprechbares
Objekt** (Anbindung an C1: das sind die Kandidaten für die Fitting-/S5-
Strukturklassen).

**(f3) Gershgorin-Weg falsifiziert:** Median-Kantengewicht der GESAMTEN
Matrix ist 0.196; bei θ_c = 0.3 perkoliert der Graph (eine Komponente mit
106k Spalten); |·|-Radius median 3.7 selbst nach 0.5-Kern-Entfernung.
**Betragsschranken können Hauptlemma v2(a) nicht tragen** — der generische
Teil lebt ausschließlich von Vorzeichen-Cancellation (signierte Kantensummen).

**(f4) Adversary saturiert die Schwelle:** Matching-θ′ im generischen Teil
≈ θ_c (0.5 → 0.500; 0.3 → 0.273). Allgemein gilt: worst-case-flat-RIP über
beliebige Träger ist nie besser als das maximale Einzelkantengewicht.
**Der BDFKK-Unterschied ist damit vollständig quantifiziert:** Chirps haben
dichte, aber uniform-kleine Kohärenz (~1/√p); unsere Matrix hat sparse
Koinzidenz (ρ = 1.7e-4), aber wenn ≠ 0, dann typisch ~0.2. Flat-RIP über
alle Träger ist strukturell unmöglich — nicht nur empirisch.

**⟹ Hauptlemma v3 (Drei-Skalen-Zerlegung):**
(i) exakt-orthonormale Schicht (27.489er-IS, BEWIESEN, L1);
(ii) Mikro-Cluster-Kern w ≥ 0.5: endlich klassifiziert, ≤6er-Blöcke,
direkt diagonalisierbar — Eigenwerte pro Block explizit prüfbar;
(iii) perkolierter Mittelbereich w ∈ [~0.05, 0.5): der gesamte
mathematische Gehalt sitzt hier und MUSS über signierte Kantensummen
laufen (1:2-Dreiecksgesetz, Weg-Vorzeichen im Hecke-Graphen,
Charaktersummen) — Spektrum statt Kohärenz. Für CR-2b ist die richtige
Größe x^T G_S x mit Vorzeichen, nicht θ′ über flache Summen.
