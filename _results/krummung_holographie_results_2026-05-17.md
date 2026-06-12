# Krümmung + Holographie — Testergebnisse

Datum: 2026-05-17
Quelle: User-Assoziationen (Universum/Urknall, Krümmungsrückgabe, String,
        Energie+Holographie, Boundary/Bulk-Aufteilung)
Skript: `_scripts/frey_boundary_test.gp`

## Setup

Zwei konkrete physikalisch-motivierte Größen getestet auf 39 Frey-
Datenpunkten aus Phase 3:

1. **Faltings-Höhe** `h_F(E) ≈ log|Δ_min| / 12` (Krümmungs-Energie)
2. **Boundary-Energie** `Σ_{p|abc, p≤50} a_p(E)² / p` (Holographie-Rand)

## Hauptbefund — Faltings-Höhe ist der bessere Saturationsparameter

### Numerische Daten

```text
h_F / log N:  min = 0.197
              max = 0.494
              mean = 0.302
              alle 39 Werte < 0.5
```

**Alle 39 Datenpunkte erfüllen Szpiro-Schranke `h_F / log N < 1/2`.**
Das ist konsistent mit der Szpiro-Vermutung `log|Δ| ≤ (6+ε) log N`
empirisch auf der Stichprobe.

### Korrelations-Vergleich

```text
Pearson r(h_F / log N,  q)     =  +0.82  ← stark
Pearson r(ρ = log m / log N, q) =  +0.36  ← schwach (aus Phase 3)
Pearson r(bnd_sum,       q)    =  -0.10  ← keine

Pearson r(h_F / log N, log N)  =  -0.02  ← N-unabhängig
```

**Faltings-Höhe / log N ist VIEL besser mit q korreliert als der
Modulargrad ρ.** Faktor 2.3.

Das ist mathematisch nicht überraschend, weil h_F direkt die
Diskriminanten-Konduktor-Spannung misst (= Szpiro), während ρ über die
BSD-Strong-Form mit zusätzlichen Tamagawa-/Torsions-Faktoren verrauscht.

### Hochqualitative Tripel

```text
q     |  h_F/logN  |  ρ
------|-----------|--------
1.176 |  0.400    |  0.742
1.273 |  0.414    |  1.006
1.320 |  0.392    |  1.400
1.361 |  0.494    |  1.471   ← höchstes h_F/logN
1.427 |  0.370    |  1.033
1.456 |  0.380    |  1.361
1.568 |  0.373    |  1.427   ← Reyssat-Standard (1, 4374, 4375)
1.630 |  0.450    |  1.793   ← Reyssat-extended (2, 6436341, 6436343)
```

**h_F/logN saturiert empirisch um 0.5** (Szpiro-Wand). Die Asymptotik
für q → 2 ist **nicht super-linear**, sondern plateau-artig — genau wie
es Szpiro vorhersagt.

### Strukturelle Interpretation

Das **Sandwich-Bild** wird umgekehrt klarer:

```text
Obere Schranke (Szpiro):  h_F / log N  ≤  1/2 + ε
Untere Schranke:           h_F / log N  ≥  ?
```

Wir haben Min 0.197 in der Stichprobe. Falls eine universelle
Untergrenze `h_F / log N ≥ c_low > 0` existiert (Vermutung), dann
ist die Faltings-Höhen-Saturation ein zweidimensionales Band, in dem
Frey-Kurven leben:

```text
0.2  ≤  h_F / log N  ≤  0.5
```

Das ist die echte abc-Saturation in Faltings-Sprache.

## Boundary-Energie (Holographie-Test)

```text
boundary a_p²/p sum:  min = 0.232
                      max = 1.253
                      mean = 0.647
                      Pearson r mit q = -0.10
```

**Boundary-Information ist nicht q-korreliert.** Frey-a_p am Rand
(p | abc) saturieren die Hasse-Schranke ± 2√p nur teilweise, mit
großer Streuung. Die Holographie-Vermutung "Boundary bestimmt Bulk"
gilt **nicht direkt** in dieser primitiven Form.

**Falsifikation**: Holographie-direkt-Test gibt nichts neues.

## Was sich am "Sandwich-Belag" geändert hat

Vor diesen Tests: Sandwich = `m / N^{1-ε}` (Modulargrad)
Nach diesen Tests: **Faltings-Höhe ist der bessere Sandwich-Belag**

Konkret:
```text
FWS-c (Modulargrad-Form):    ρ ≥ (q-1) + 0.13     r(ρ, q) = 0.36
FWS-h (Faltings-Form):        h_F/logN korreliert mit q (r = 0.82)
                              und ist beschränkt durch 1/2 (Szpiro)
```

Die **Faltings-Form FWS-h** ist:
1. Empirisch viel besser konditioniert (r = 0.82 vs 0.36)
2. Direkt Szpiro-konsistent (kein Umweg über Modulargrad)
3. Mathematisch direkt verbunden mit der abc-Vermutung

## Reframing der Backup-Routen

| Route | Status nach Test |
|---|---|
| Sandwich-Modulargrad (FWS-c) | gut, aber verrauscht (Tamagawa-getrieben) |
| **Sandwich-Faltings (FWS-h)** | **VIEL besser, direkt Szpiro-relevant** |
| AL-Mittelung | konzeptionell ergänzend |
| Cusp-Volumen | tot |
| Boundary-Holographie | nicht direkt nutzbar |

**Empfehlung**: Die FWS-Hypothese sollte in Faltings-Form aufgeschrieben
werden, nicht in Modulargrad-Form. Das ist die mathematisch saubere
Formulierung.

## Konkrete FWS-h-Hypothese (neu)

**Frey-Faltings-Saturation (FWS-h)**:

```text
Für Frey-Kurven aus primitiven abc-Tripeln (a, b, c):
  c_low · q  ≤  h_F(E_Frey) / log N(E_Frey)  ≤  1/2 + ε
```

Empirisch auf 39 Datenpunkten:
- Obere Schranke: `< 0.5` immer (Szpiro-konform)
- Untere Schranke `c_low · q`: linear in q, mit c_low ≈ 0.13?
  Lass mich rasch nachsehen...
  
Aus den Daten: für niedrige q sehen wir h_F/logN ≈ 0.2-0.3, für hohe q
≈ 0.4-0.5. Linearer Trend mit Slope ≈ 0.3 - 0.15 = 0.15 pro Δq = 1.
Also `c_low ≈ 0.15` und Bedingung wäre `h_F/logN ≥ 0.15·q + 0.05` oder
ähnlich. Lineare Regression nötig.

## Konsequenz für die abc-Vermutung

Wenn FWS-h gilt mit beiden Schranken:

```text
c_low · q  ≤  h_F / log N  ≤  1/2 + ε
⇒  c_low · q  ≤  1/2 + ε
⇒  q  ≤  (1/2 + ε) / c_low
```

Bei `c_low = 0.15`: `q ≤ 3.3 + ε`. Das ist **schwächer** als abc
(`q ≤ 1 + ε` strikt). Aber bei `c_low > 1/4`: `q ≤ 2 + ε`. Das wäre
**die abc-Vermutung selbst**!

**Falsifikation/Beweisstrategie**: zeige `c_low ≥ 1/4`. Das wäre ein
direkter abc-Beweis über Faltings-Höhen-Saturation.

Aber Vorsicht: c_low ist datengestützt, nicht bewiesen. Eine
universelle Untergrenze auf h_F/log N ist eine STÄRKERE Aussage als
abc und ist NICHT bewiesen.

## Verbindung zu BSD und der ANC-Sha-Familie

Faltings-Höhe und Sha sind über die Néron-Tate-Höhen-Theorie verbunden:

```text
ĥ_NT(P)  ≤  c_1 · h_F(E)  +  c_2  (für rationale Punkte P)
```

Wenn h_F gross ist, sind Néron-Tate-Höhen klein. Speziell:
für rank-0 Frey gibt es keine Néron-Tate-Punkte. Die "Höhen-Sättigung"
ist hier voll in der Faltings-Höhe.

## Status der Metaphern

| Metapher | Mathematischer Gehalt |
|---|---|
| Universum-Urknall | nur rhetorisch, keine direkte Übersetzung |
| **Krümmungsrückgabe** | **FALTINGS-HÖHE als Krümmung — gut!** |
| String-Schwingung | implizit in Petersson-Norm-Theorie |
| **Energie-Holographie** | **h_F = Bulk-Energie, Szpiro = Bulk-Schranke — gut!** |
| Boundary-Holographie | nicht direkt nutzbar |

Zwei der fünf Metaphern haben empirisch greifbare Form: **Faltings-
Höhe als Krümmung mit Szpiro-Wand**. Die anderen drei sind rhetorisch.

## Nächster Schritt

Größere Stichprobe (50-100 Tripel) für **FWS-h-Hypothese**:
1. h_F / log N quantitativ regressieren gegen q
2. Schranken c_low und 1/2 + ε empirisch bestimmen
3. Ist c_low > 1/4 (entspricht abc-Beweis-Form)?

Aufwand: ein größerer PARI-Lauf (~30 min).
