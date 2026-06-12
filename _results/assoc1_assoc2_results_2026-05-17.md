# Assoziationen 1 und 2 — Testergebnisse

Datum: 2026-05-17
Skripte: `_scripts/cusp_volume_test.gp` (Assoz 2), LMFDB-Lookup (Assoz 1)
Datenquellen:
- 41 Frey-Datenpunkte aus Phase 3
- LMFDB-Isogenieklassen für N ∈ {60168, 80224, 120336, 240672}

## Assoziation 1 — AL-Mittelung (Galois/Twist-Average)

### Test

Für jeden der vier abc-Korbkonduktoren: alle LMFDB-Isogenieklassen
ziehen, deren Modulargrade auswerten, geometrisches Mittel berechnen.

### Daten

| N | n_Klassen | m_min | m_max | m_geom | ρ_min | ρ_max | **ρ_geom** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 60168 | 3 | 25.152 | 184.896 | 55.456 | 0.921 | 1.102 | **0.993** |
| 80224 | 2 | 978.912 | 978.912 | 978.912 | 1.222 | 1.222 | **1.222** |
| 120336 | 17 | 30.720 | 1.04×10⁸ | 538.361 | 0.883 | 1.578 | **1.128** |
| 240672 | 8 | 125.568 | 8.90×10⁹ | 9.116×10⁶ | 0.947 | 1.849 | **1.293** |

### Hauptbefunde

1. **Streuung pro Konduktor ist enorm**: bei 240672 spannen die acht
   Klassen einen Modulargrad-Bereich von Faktor 70.000.

2. **Twist-Paar-Struktur sichtbar**: Bei 240672 vier identische
   Paare {a,e}, {b,f}, {c,g}, {d,h}. Jedes Paar = eine Newform mit
   beiden Galois-Orientierungen (rank 0 + rank 1, gleicher m).

3. **ρ_geom ist deutlich glatter als individuelle ρ-Werte.** Die
   Streuung pro Konduktor wird durch das geometrische Mittel auf
   einen einzigen aggregierten Wert reduziert:

   ```text
   N = 60168:  ρ_min = 0.92, ρ_max = 1.10  →  ρ_geom = 0.99
   N = 240672: ρ_min = 0.95, ρ_max = 1.85  →  ρ_geom = 1.29
   ```

4. **ρ_geom wächst nur mäßig mit log N**:
   ```text
   ρ_geom(60168)  = 0.99
   ρ_geom(80224)  = 1.22
   ρ_geom(120336) = 1.13
   ρ_geom(240672) = 1.29
   ```
   Trend: leichter Anstieg, aber keine super-lineare Skalierung.

### Bedeutung für FWS-c

ρ_geom ist eine **AL-glatte** Variante des Saturationsverhältnisses.
Sie eliminiert die Twist-spezifische Streuung und gibt eine
**einzige Aggregat-Zahl pro Konduktor**.

Die AL-glatte FWS-c-Hypothese wäre:

```text
ρ_geom(N)  ≥  1  für hinreichend große N (Frey-Familie)
```

Auf der vier-Punkte-Stichprobe ist sie **fast erfüllt**:
- 60168: ρ_geom = 0.993 (knapp darunter)
- 80224, 120336, 240672: ρ_geom ≥ 1.13

Die "Unterhebung" bei 60168 liegt nahe an 1 — eine ε-Korrektur würde sie
einschließen. Damit ist die AL-glatte Form von FWS deutlich näher an
der naiven Hypothese als die individuelle Form.

### Status

**ASSOZIATION 1 ist EMPIRISCH NÜTZLICH**, gibt eine bessere Hypothese-
Form als die individuelle Saturation. Für die Beweis-Strategie bleibt
sie aber konzeptionell ähnlich: Watkins-Average gibt obere AL-Schranke,
und wir müssten zeigen, dass Frey die AL-Average saturiert.

## Assoziation 2 — Cusp-zentriertes Petersson-Volumen

### Test

Für jede der 41 Frey-Kurven: Cusp-Volumen-Proxy

```text
V_cusp(E)  :=  Σ_{p prime ≤ 500, p ∤ N}  a_p(E)² / p
```

berechnen via PARI `ellan(E, 500)`.

### Daten

```text
n = 41
V_cusp:  min = 64.68
         max = 113.55
         mean = 89.88
         stddev = 9.30

Pearson r(V_cusp, log N) = 0.1071
```

### Hauptbefund

**Cusp-Volumen ist im Wesentlichen N-unabhängig.** Korrelation mit
log N ist praktisch null (r = 0.11). Werte streuen zwischen 65 und 114
um einen Mittelwert von 90 — unabhängig davon, ob N = 30 oder
N = 240672.

### Interpretation

Das passt zur Sato-Tate-Theorie:

```text
E[a_p²/p]  =  konst  (für typische Newforms)
V_cusp     ≈  π(M) · konst  (für M = 500: π(500) = 95)
```

Mit `konst ≈ 1`, gibt V_cusp ≈ 90. Genau das beobachten wir.

### Bedeutung für die Period-Reformulation

**Cusp-Volumen ist keine Frey-spezifische Größe.** Es gibt keine
Frey-versus-typisch-Newform-Unterscheidung. Damit liefert es **keinen
neuen Period-Untergrenze-Hebel**.

Das ist ein klares **negatives Resultat** — die Assoziation-2-Idee ist
empirisch widerlegt.

### Status

**ASSOZIATION 2 ist FALSIFIZIERT** als eigenständige Period-
Reformulations-Brücke. Cusp-Volumen ist Sato-Tate-Average ohne
Frey-Bias.

## Synthese

| Test | Ergebnis | Wert |
|---|---|---|
| Assoz 1 (AL-Mittelung) | EMPIRISCH NÜTZLICH | ρ_geom glättet, näher an FWS-Hypothese |
| Assoz 2 (Cusp-Volumen) | FALSIFIZIERT | keine Frey-Spezifizität |

**Konkrete Empfehlung**:

1. AL-Mittelung als Reformulierung von FWS-c in `MG_frey_watkins_quality_conditional_2026-05-17.md` aufnehmen — die AL-glatte Form ist sauberer.
2. Cusp-Volumen aus den Backup-Routen entfernen — kein neuer Hebel.

## Verbindung zur HCT-Hauptarbeit

AL-Mittelung passt zur bereits eingesetzten B_AL-Twist-Methode (Loop
314-317): wir arbeiten schon mit einer w_N-Spiegelung. Die volle
AL-Mittelung würde alle 16 AL-Twists (für 240672) ein-beziehen, statt
nur w_N allein. Das wäre eine **symmetrisierte HCT-Variante**.

Konkrete Frage: ist `B_AL-avg` (die über die ganze AL-Gruppe gemittelte
Paarung) besser konditioniert als `B_AL = B(·, w_N ·)` allein? Wenn ja,
könnte das die Q_B-Three-Lemma-Konstruktion vereinfachen.

## Nächste Schritte

1. AL-Mittelung in FWS-c-Notiz integrieren.
2. Cusp-Volumen als negativen Backup-Test ablegen.
3. Optional: ρ_geom für eine größere Konduktor-Familie systematisch
   testen, um den ρ_geom-Trend mit log N quantitativ zu erfassen.
