# Survivor-Census auf Level N=240672 selbst (2026-06-10)

**Anlass:** v3 (q'=5077, Nicht-Kongruenzprim) zeigt nach T₁₃ dasselbe Plateau
qdim=3 wie v2/v2b (q=3863). Frage: Wie viel des Plateaus ist rational-strukturell
(über ℤ, also q-unabhängig) durch Isogenieklassen auf N selbst erklärbar?

**Methode:** LMFDB-API `ec_curvedata` (alle Isogenieklassen auf Conductor 240672,
ein Vertreter pro Klasse), lokale Punktzählung über F_p für die guten Primzahlen
{5,7,11,13,17,19,23,29,31}. Script: `_scripts/survivor_census_level_n_240672.py`.
Maschinenlesbar: `_results/survivor_census_level_n_240672_2026-06-10.json`.

**Referenz f_E = 240672.g:** a₅=2, a₇=0, a₁₁=0, a₁₃=−6, a₁₇=6, a₁₉=0, a₂₃=1, a₂₉=−2, a₃₁=4.

## Ergebnis: genau 2 von 8 Klassen überleben die bisher getesteten Replay-Primes

8 Isogenieklassen auf N=240672. a_p-Profile (p = 5,7,11,13,17,19,23,29,31):

| Klasse | a_p-Profil | Separatoren (gute p) |
|---|---|---|
| 240672.a | −1, 3, 0, 0, −6, 6, −1, −2, 8 | 5,7,13,17,19,23,31 |
| 240672.b | 0, 4, 3, −1, 2, −2, −1, −6, −5 | alle |
| **240672.c** | **2, 0, 0, −6, 6, 0, −1, −2, −4** | **nur 23, 31** |
| 240672.d | 4, 0, −5, −1, −2, 6, −1, 6, 9 | 5,11,13,17,19,23,29,31 |
| 240672.e | −1, −3, 0, 0, −6, −6, 1, −2, −8 | 5,7,13,17,19,31 |
| 240672.f | 0, −4, −3, −1, 2, 2, 1, −6, 5 | 5,7,11,13,17,19,29,31 |
| **240672.g** | **2, 0, 0, −6, 6, 0, 1, −2, 4** | — (f_E selbst) |
| 240672.h | 4, 0, 5, −1, −2, −6, 1, 6, −9 | 5,11,13,17,19,29,31 |

Bisher getestete gute Replay-Primes (v1+v2+v2b bis T₁₉, v3 bis T₁₃): {7, 11, 13, 17, 19}.
**Überlebende:** nur 240672.g (f_E) und 240672.c (χ₋₁-Twist; identisch auf allen
p≡1 mod 4 und auf allen a_p=0; Differenz nur Vorzeichen bei p≡3 mod 4 mit a_p≠0).

## Konsequenzen

1. **2 der 3 Plateau-Dimensionen sind q-unabhängig rational erklärt:** f_E + c.
   Der Twist c wird von KEINEM der bisher getesteten Operatoren getrennt — sein
   erster guter Separator ist **T₂₃** (läuft gerade in v2b und steht in v3 an),
   der zweite T₃₁. (T₃ trennt auch — U₃: a₃(g)=+1, a₃(c)=−1 — ist aber in keinem
   Replay-Lauf enthalten.)
2. **Die dritte Plateau-Dimension ist NICHT rational erklärbar:** weder auf N
   selbst (dieser Census) noch auf den 2-Kopien-Teiler-Leveln (H1-Census
   2026-06-10). Kandidaten: nicht-rationaler Orbit (mod 3863 die
   Ribet-Kongruenzkomponente), Eisenstein-Anteil, oder fehlende Witness-Zeilen
   mod 5077 (Rank-Selektions-Caveat).
3. **Verfeinerte Vorhersagen (registriert VOR den T₂₃-Ergebnissen):**
   - **v2b (q=3863), T₂₃:** qdim 3→2 (c stirbt), danach stabil 2
     (f_E + mod-3863-Kongruenzkomponente, die mod 3863 von keinem T_p getrennt
     werden kann). Die ursprüngliche §5-Vorhersage „bleibt 3" war zu grob — sie
     übersah, dass c ein separierbarer Plateau-Bewohner ist.
   - **v3 (q'=5077), T₂₃:** qdim 3→2 (c stirbt). Fällt danach (T₂₉/T₃₁ oder
     schon T₇/T₁₁/T₁₇/T₁₉) auch die dritte Dimension, ist **Gate 2 GRÜN**
     (qdim=1 beobachtet ⟹ qdim_Q=1). Bleibt v3 bei 2 stabil: dritte Dimension
     überlebt mod 5077 alle Operatoren → Witness-Caveat prüfen
     (voller q'-Produktionslauf) oder echte zweite Kongruenz.
   - **Scharfe Diskriminierung:** Fällt v2b bei T₂₃ NICHT auf 2, ist der Twist c
     nicht im berechneten Quotienten präsent — dann ist die Plateau-Buchhaltung
     (1+2-Zerlegung) neu zu schreiben.

**Status:** Diagnostik, kein Claim-Upgrade. Gate 2 weiter ROT bis v3-T₂₃/T₂₉/T₃₁.

**Begriffskorrektur (Nachtrag 2026-06-10 Abend, ausgelöst durch Codex-Audit):**
23 | N = 2⁵·3·23·109 ist **Levelprime** — „a₂₃" ist der U₂₃-Eigenwert
(multiplikative Reduktion, ±1), kein good-prime-T₂₃-Eigenwert. Die
Punktzählung liefert ihn dennoch korrekt (Knoten zählt als 1 affine Lösung
→ count = p+1−a_p). Die Operator-Implementierung der Replay-Läufe ist
validiert: Sages HeilbronnCremona-Pfad (von t7_replay benutzt) liefert für
p || N exakt die U_p-Eigenwerte — empirisch bestätigt an 8/8 Testfällen
(N=14, 15, 21, 33; Mac-Sage 2026-06-10). Die T₂₃-Separations-Vorhersagen
gelten unverändert, sind aber als U₂₃-Aussagen zu lesen. Gleiches gilt für
U₃ (a₃(g)=+1, a₃(c)=−1) im hecke_cremona-Produktionsjob.

**KORREKTUR (2026-06-10 Nacht):** Die Separator-Vorhersagen oben übersahen,
dass das Replay-Fundament bereits 31 673 U₃-Zeilen enthält (T_3_minus_1 in
`source_rows.jsonl`) — U₃ ist der schärfste c-Separator, der Twist war im
Plateau nie vorhanden. Messung bestätigt: v2b U₂₃ Batch 1 → qdim=3 (kein
Drop). Korrigierte Lesart: Plateau = f_E + 2 Nicht-Twist-Dimensionen.
Details: `MG_congruence_prime_3863_obstruction_2026-06-10.md` §7c.
