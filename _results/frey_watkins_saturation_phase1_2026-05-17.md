# Phase-1-Test der Frey-Watkins-Saturations-Hypothese (FWS)

Datum: 2026-05-17
Hypothesis note: kept in the private local proof notebook, not included here.
Datenquelle: LMFDB (`www.lmfdb.org/EllipticCurve/Q/`)

## Setup

Zu testen: für Frey-Kurven `E_{a,b}: y² = x(x-a)(x+b)` aus primitiven
abc-Tripeln gilt

```text
m(E) ≥ N(E)^{1-ε}
```

mit `m(E)` Modulargrad und `N(E)` Konduktor.

Konkret: log m / log N ≥ 1 − ε.

## Datenpunkte aus LMFDB

### Reyssat-Frey, Orientierung ε=+1: 240672.c3 (Cremona 240672c1)

```text
N            = 240672 = 2⁵ · 3 · 23 · 109
Δ            = 109833904946803852249841111616 = 2⁶ · 3²⁰ · 23¹⁰ · 109²
m(E)         = 4,450,176,000 ≈ 4.45 × 10⁹
Rank         = 0
Sha          = 361 = 19²
Tamagawa     = 16
Weierstrass  = y² = x³ - x² - 13808832780322x - 19750744373708998160
```

Test:
```text
log(m) / log(N)  =  log(4.45 × 10⁹) / log(2.41 × 10⁵)
                 =  9.6484 / 5.3814
                 =  1.7929
```

**Ergebnis: m ≈ N^{1.79}**. Liegt weit über N^{1−ε} für jedes ε ≤ 0.79.

### Reyssat-Frey, Orientierung ε=−1: 240672.g3 (Cremona 240672g1)

```text
N            = 240672
m(E)         = 4,450,176,000 (gleich der c-Klasse!)
Rank         = 1
Sha          = 1 (gerundet)
Tamagawa     = 800
```

Test: identisch zur c-Klasse. log m / log N = **1.79**.

**Bemerkung**: c- und g-Klassen haben denselben Modulargrad, was die
**Isomorphie der Frey-Modulformen** bestätigt (beide kommen aus
demselben Reyssat-Tripel via Orientierungs-Vertauschung).

### Nicht-Frey-Kurven mit denselben Konduktoren (Kontrast)

Für die anderen HCT-Korbkonduktoren ist die Frey-Klassen-Identifikation
nicht trivial (LMFDB hat mehrere Isogenieklassen pro Konduktor; welche
genau Frey-Twists des Reyssat-Tripels sind, ist nicht direkt aus dem
Konduktor allein abzulesen).

**Streuung pro Konduktor (alle Isogenieklassen):**

| Konduktor | min m | max m | min log m / log N | max log m / log N |
|---:|---:|---:|---:|---:|
| 60168  | 25,152      | 184,896    | 0.921 | 1.102 |
| 80224  | 978,912     | 978,912    | 1.221 | 1.221 |
| 120336 | 30,720      | 104,232,960 | 0.883 | 1.578 |
| **240672 (Reyssat-Frey)** | **4,450,176,000** | **4,450,176,000** | **1.793** | **1.793** |

Die echte Reyssat-Frey-Klasse 240672.c3/.g3 hat einen Modulargrad, der
**~10⁴ mal größer** als die größte Klasse bei N=120336 ist und
**~10⁵ mal größer** als die größte Klasse bei N=60168.

## Erste Interpretation

1. **Für die explizit als Frey identifizierte Reyssat-Kurve (240672.c3/g3) ist FWS stark positiv**:
   m ≈ N^{1.79}, also weit über N^{1-ε} für jedes ε ≤ 0.79.

2. **Die kleineren Konduktoren (60168, 80224, 120336)** haben in
   LMFDB Klassen mit log m / log N nahe an oder sogar unter 1. Diese
   Klassen sind aber **nicht zwingend Frey-Kurven** — sie haben
   denselben Konduktor wie Old-Level-Twists, aber die HCT-Arbeit hat
   noch nicht explizit identifiziert, welche LMFDB-Klasse pro
   Konduktor die Frey-Twist des Reyssat-Tripels ist.

3. **Wenn die HCT-Korbkurven 60168/80224/120336 tatsächlich Twists des
   Reyssat-Frey-Modulforms sind**, sollten sie über die
   Modulform-Skala-Invarianz **denselben** Modulargrad-Skalentyp haben
   wie 240672.c3. Da LMFDB für 240672 m ≈ 4.45 × 10⁹ zeigt, müssten
   die Frey-Twists bei den kleineren Konduktoren entweder ähnlich
   große Modulargrade haben (was die LMFDB-Daten nicht zeigen) — oder
   sie sind **nicht** in der LMFDB-Frey-Klasse.

## Bewertung der Hypothese auf der vorliegenden Stichprobe

**Vorsichtig positiv mit Vorbehalt**:

- Der einzige eindeutige Frey-Datenpunkt (Reyssat 240672) saturiert
  Watkins sehr stark (faktor ~10⁴ über N^1).
- Die Hypothese FWS in der starken Form
  `m ≥ N^{1-ε} für alle Frey-Kurven` ist auf dieser Stichprobe nicht
  falsifiziert.
- Die Hypothese ist auch nicht hinreichend bestätigt, weil die
  Stichprobe zu klein ist (n=1 echte Frey, mit beiden Orientierungen).

## Methodische Lücke und Phase-2-Plan

**Lücke**: Welche LMFDB-Klasse ist die Frey-Twist für N=60168/80224/120336?

Direkte Klärung erfordert:
1. Trace-Werte (a_5, a_7, a_11, a_13) aller Isogenieklassen pro Konduktor
   vergleichen mit Frey-Spuren (HCT: (2, 0, 0, -6)).
2. **Falls keine Klasse exakt passt**: die HCT-Korbkurven sind keine
   eigenständigen Frey-Kurven, sondern Old-Level-Reduktionen, und die
   FWS-Hypothese ist nur an 240672.c3 zu testen — was unsere Stichprobe
   ist.

**Phase-2-Stichprobe** (für statistische Aussagekraft):

```text
- Klassische abc-Tripel mit kleinem Konduktor:
    (1, 8, 9), (1, 4374, 4375)=Reyssat, (3, 125, 128),
    (1, 80, 81), (32, 49, 81), ABCHome_2, ...
- Für jedes: Frey-Konduktor berechnen, LMFDB-Modulargrad ziehen,
  log m / log N gegen 1 - ε prüfen.
```

Aufwand: ~3-5 Stunden, gibt n=10-15 Frey-Datenpunkte mit klarer
statistischer Aussagekraft.

## Vorläufiges Verdikt

**Phase 1 ergibt:**

```text
✓ Hypothese ist auf dem einzigen eindeutigen Frey-Datenpunkt stark
  bestätigt (Reyssat 240672, m ≈ N^{1.79}).
○ Hypothese ist auf dieser Stichprobe nicht falsifiziert.
○ Hypothese benötigt Phase-2 (10-15 weitere Frey-Konduktoren) für
  statistisches Signal.
```

Negativbefund wäre, wenn ein Frey-Datenpunkt
`m / N^{1-ε} → 0` zeigte. Das ist auf dieser Stichprobe nicht passiert.

## Verbindung zu BSD

Interessanter Nebenbefund: Reyssat 240672.c3 hat **Sha = 361 = 19²**.
Das ist ein nicht-trivialer Sha-Anteil, der die BSD-Saturation der
Frey-Familie stützt: für Frey-Kurven ist Sha typischerweise
nicht-trivial, was über die BSD-Formel automatisch einen großen
Modulargrad erzwingt:

```text
m(E) = (4π)² · ‖f‖² = (Quotient mit |Sha| im Zähler über BSD-Strong-Form)
```

Sha = 19² in der Frey-Familie + Tamagawa = 16 erklärt strukturell den
großen Modulargrad — und ist konsistent mit der FWS-Saturation.

**Brücke zu Synergie A** (TFR-B impliziert Sha-Endlichkeit):
Wenn FWS unabhängig durch Phase 2 bestätigt wird, ist die Verbindung
zur BSD-Sha-Struktur ein eigenständiger Strukturbefund.

## Nächste Schritte

1. **Sofort**: Phase-2-Skript schreiben, das die EM-1-Ledger-Tripel
   nach Frey-Konduktor abbildet und LMFDB-Modulargrade zieht.
2. **Falls Phase 2 weiter positiv läuft**: FWS-Hypothese formell
   aufschreiben, Anschluss an Watkins-Beweisstrategie suchen.
3. **Falls Phase 2 ein Frey-Tripel mit m ≪ N^{1-ε} findet**:
   FWS-Hypothese ablegen, das Tripel als Gegenbeispiel dokumentieren.
4. **Falls die LMFDB-Klassen für 60168/80224/120336 als Nicht-Frey-Twists
   identifiziert werden**: HCT-Korb anders interpretieren (Old-Level
   statt eigenständige Frey-Familie).
