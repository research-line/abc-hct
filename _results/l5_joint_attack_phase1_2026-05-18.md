# L5 Joint Attack Phase 1 — Theta-Konduktor-Schranke empirisch getestet

Datum: 2026-05-18
Skript: `_scripts/l5_phase1.gp`
Stichprobe: 59 hochqualitative Frey-Tripel (aus Phase-4-Korb)
Vorläufer-Notizen:
- `MG_l5_theta_conductor_joint_attack_2026-05-17.md`
- `MG_l5_tate_theta_local_formula_l5_2026-05-17.md`
- `MG_l5_theta_normalization_guardrail_2026-05-17.md`

## Test-Setup

Für jedes Frey-Tripel:

```text
L5_naive  =  log|Δ_min| / 2
            (Eta-Produktbilanz für l=5, aus Theta-Eta-Identität)

L5_AL     =  L5_naive  -  log ∏c_p
            (Atkin-Lehner-Korrektur durch Tamagawa-Reduktion)
```

Verglichen mit `log N`.

## Hauptbefund — KEINE Kompression

```text
n = 59 Tripel

L5_naive / log N:   min=1.00,  max=3.44,  mean=2.02
L5_AL    / log N:   min=0.66,  max=2.63,  mean=1.44
```

**Beide Größen wachsen linear mit q** — beweisen keine Kompression auf
`O(log N)`.

```text
Pearson r(L5_naive/logN, q) = +0.63
Pearson r(L5_AL/logN,    q) = +0.59
```

## Lineare Regression L5_AL/logN vs q

```text
L5_AL / log N  ≈  1.49 · q  -  0.24

Bei q=1.0:  L5_AL / log N  ≈  1.24
Bei q=1.5:  L5_AL / log N  ≈  1.99
Bei q=2.0:  L5_AL / log N  ≈  2.73
```

**Bei abc-Limes q → 2**: L5_AL ≈ 2.73·log N. Das ist weit über jeder
konstanten Schranke C·log N, was Phase 1 für die L5-Kompressionsroute
**negativ** macht.

## Verifikation der Failure-Mode-Vorhersage

`MG_l5_theta_normalization_guardrail_2026-05-17` hatte exakt das
vorhergesagt:

> Wenn die lokale Eta-Bilanz nur `Σ n_p log p` reproduziert, dann ist
> L5 nicht stärker als die zu beweisende Szpiro-Aussage. Dann wäre L5
> äquivalent oder zirkulär.

**Empirisch bestätigt:**
- L5_naive = log|Δ|/2 = (1/2) Σ n_p log p — direkt die Szpiro-Masse
- L5_AL reduziert das nur um die Tamagawa-Komponente (im Mittel 0.59
  in log-N-Einheiten)
- Die verbleibende Größe wächst weiterhin linear mit q

Damit ist **die naive und die AL-twistete Form von L5 äquivalent zu
Szpiro plus Tamagawa-Allowance**. Beide liefern keinen neuen Beweisweg.

## Champion-Stichprobe (q ≥ 1.3)

| Tripel | q | L5_naive/logN | L5_AL/logN | log Tama |
|---|---:|---:|---:|---:|
| Reyssat (2, 6436341, 6436343) | 1.630 | 2.698 | 2.159 | 6.685 |
| ABCHome_2 (121, 48234375, 48234496) | 1.626 | 3.438 | 2.631 | 8.784 |
| (1, 4374, 4375) | 1.568 | 2.236 | 1.724 | 4.159 |
| (1, 2400, 2401) | 1.456 | 2.283 | 1.536 | 5.545 |
| (3, 125, 128) | 1.427 | 2.220 | 1.714 | 2.773 |
| (625, 2048, 2673) | 1.361 | 2.962 | 2.318 | 5.075 |
| (1, 5831, 5832) | 1.320 | 2.354 | 1.780 | 4.564 |
| (1, 512, 513) | 1.318 | 2.034 | 1.466 | 3.871 |
| (1, 242, 243) | 1.311 | 1.776 | 1.247 | 3.689 |

**Alle hochqualitativen Tripel haben L5_AL/logN ∈ [1.2, 2.6]**, weit
über 1. Keine Kompression sichtbar.

## Konkrete Test-Tripel mit niedrigem L5_AL

```text
(1, 31, 32):    q=0.84, L5_AL/logN=0.66, L5_naive/logN=1.00
(5, 27, 32):    q=1.02, L5_AL/logN=0.71, L5_naive/logN=1.65
(1, 63, 64):    q=1.11, L5_AL/logN=0.74, L5_naive/logN=1.48
(1, 8, 9):      q=1.23, L5_AL/logN=0.75, L5_naive/logN=1.46
```

Tiefste L5_AL/logN-Werte gehören zu **kleinen Catalan-Tripeln**. Aber
selbst dort ist L5_AL/logN > 0.66 — nicht in der Größenordnung von
`O(1) / log N`, was eine echte Kompression wäre.

## Was die L5-Phase 1 zeigt

1. **L5-Eta-Bilanz ohne Normalisierung = Szpiro/2**:
   `Σ -log|θ_1(j/5|τ_p)|_p ≈ (1/2) log|Δ|` (Theta-Eta-Identität).

2. **AL-Twist subtrahiert log ∏c_p**: reduziert um Tamagawa-Energie,
   aber nicht um die volle Szpiro-Masse.

3. **Phase-1-Verdikt**: L5_AL bleibt linear in q, kein neuer Hebel.

## Was L5 dennoch leisten kann

Die L5-Guardrail-Notiz hatte zwei tiefere Normalisierungs-Pfade
identifiziert:

### Variante A: volle l-Torsionsbilanz

Statt nur `μ_l × {0}`-Punkte zu nehmen, alle `(a,b)`-Komponenten der
`l`-Torsionsgruppe `E_q[l] ≅ μ_l × (1/l)Z/Z`. Dann taucht
`v_p(q^{b/l}) = (b/l) n_p` explizit auf, was die n_p-Tiefe sieht.

Diese Form **wurde in Phase 1 nicht getestet** — wäre der nächste
Schritt, falls L5 weiter verfolgt wird.

### Variante B: Atkin-Lehner-paarweise Kompression

Statt `log ∏c_p` als naive Tamagawa-Reduktion, eine **paarweise
AL-Kompression** mit Vorzeichen-Cancellation:

```text
L5_AL2 = Σ_p (n_p log p - corrected AL-mass(p))
```

mit AL-Korrekturen die spezifisch die Frey-Twist-Symmetrie ausnutzen.
Empirische Erprobung wäre der nächste Schritt.

## Verdikt der Phase 1

```text
L5_naive:        empirisch = log|Δ|/2 — direkt Szpiro
L5_AL (Tama):    empirisch < log|Δ|/2 - log Tama — auch ≈ Szpiro
                  mit Tamagawa-Subtraktion
                  
Kompression auf O(log N):   NICHT GEFUNDEN
Linearer q-Trend:           BESTÄTIGT (slope ≈ 1.5 in log-N-Einheiten)
abc-Beweisweg aus L5:       NICHT ÜBER NAIVE/AL-NORMALISIERUNG
```

## Strategische Konsequenz

Die L5-Joint-Attack-Hoffnung lebt nur weiter, wenn:

1. **Variante A (volle l-Torsion)** eine zusätzliche Cancellation
   bringt, die in der Eta-Produktform nicht sichtbar ist.
2. **Variante B (paarweise AL)** strukturelle Selbst-Aufhebung über
   bestimmte Frey-Tamagawa-Strukturen liefert.

Beide Varianten sind technisch wesentlich aufwendiger als Phase 1
(brauchen explizite Tate-Sigma-Funktion bzw. AL-Vorzeichen-Tracking).
Ohne dass eine konkrete Cancellation-Heuristik nahelegt, dass eine
solche Kompression existiert, ist Phase 2/3 spekulativ.

## Pattern-A-Lehre erfüllt

Die L5-Phase-1-Negativität ist konsistent mit der Pattern-A-Lehre
aus `CORE/PATTERN_A_LESSON.md`:

> Reformulierungen einer offenen Vermutung in neuer Sprache liefern
> oft Äquivalenz, nicht Stärkung.

**L5-naive und L5-AL sind Reformulierungen von Szpiro in Theta-/
Eta-Sprache, nicht Stärkungen.**

Pattern-A in Aktion: Statt L5 als "Pseudo-Brücke" zu verkaufen, ehrlich
als Reformulierungs-Diagnostik einordnen.

## Bilanz nach L5-Phase 1

```text
Q_B-Hauptpfad (HCT):           wartet — Kern der HCT-Arbeit
L5 Joint Attack Phase 1:       NEGATIV (= Szpiro, keine Kompression)
L5 Variante A/B (l-Torsion):   spekulativ, technisch aufwendig
FWS-h (Faltings):               = Szpiro
FWS-c (Modulargrad):            Tamagawa-getrieben
ANC-Sha-Brücke:                BESTÄTIGT (Strukturbefund)
AL-Mittelung:                   ergänzend
Cusp-Volumen:                   tot
```

**Alle untersuchten Backup-Routen sind ausgeschöpft.** Die einzigen
substantiellen neuen Beträge sind:
- ANC-Sha-Strukturbefund (Champion + Catalan Patterns)
- Faltings-h-Saturation (sauberere Szpiro-Reformulierung)
- AL-Mittelung (ρ-Glättung)

Der harte Beweisweg bleibt der **HCT-Q_B-Hauptpfad**.
