# ★-Kern Falsifikator -- Selbst-Kalibrierung (2026-07-10)

**Autor:** LG  |  **Modus:** train  |  **Status:** Programm-Instrument, kein Claim.
**Spec:** MG_starcore_fahndungsblatt_2026-07-10.md (Section E, T0-T5).

> Zweck: Der Falsifikator wird glaubwuerdig gemacht, indem Referenz-Kandidaten mit
> BEKANNTEM Soll-Verdikt durchlaufen. Erwartung != Ergebnis -> Test-Logik korrigieren,
> nicht die Erwartung (Fahndungsblatt-Guard).

## Frage

Reproduzieren die kodierten Tests T0-T5 die a-priori bekannten Verdikte der fuenf
Referenz-Kandidaten (ein Provenienz-Kill, ein Support-only-Kill, ein Bewertungs-Kill,
ein Nutzlos-Park, ein Zirkularitaets-Kill)?

## Setup

**Korpus (`starcore_corpus_2026-07-10.json`):**

| Quelle | n | Zweck |
|---|---:|---|
| Watkins (c<=80, mit N + deg phi) | 982 | Zirkularitaet (T3), Nutzen (T4) |
| Brute-Force voll-glatte S-Unit-Tripel | 1412 | Traeger-Buckets (T1/T5), Hochqualitaet (T4) |
| Zufallskontrollen (magnitude-gematcht) | 4000 | T4-Kontrastgruppe |
| **gesamt** | **6394** | |

- **Traeger-Buckets** (>=2 Mitglieder, >=2 distinkte Exponentenmuster): **218** (mit 2374 Tripeln).
- **omega-Bereich:** 1 .. 12.  **Hochqualitaets-Tripel (q>1.2):** 37.  **deg-phi-Tripel:** 981.
- **Glatt-Konstruktion:** voll-glatte S-Unit-Tripel a+b=c, a<=b, alle S-glatt, gcd(a,b)=1, c<=bound, S=[2, 3, 5, 7, 11, 13, 17], c<=1000000.
- **deg-phi-Quelle:** Watkins-Spalte 'deg' als Modulgrad deg phi interpretiert.
- **Holdout:** support-level ~80/20-Split, seeded (Indizes in `starcore_holdout_indices_2026-07-10.json`); Wertung hier auf **train**.

## Ergebnis -- Kalibrierungs-Tabelle (erwartet vs. gemessen)

| Kandidat | mech. | erwartet | T0 | T1 | T2 | T3 | T4 | T5 | Gesamt | Kalib. |
|---|---|---|---|---|---|---|---|---|---|---|
| G_omega | derived | kill (T5=kill,T1=pass,T2=pass) | PASS | PASS | PASS | PASS | PASS | KILL | **KILL** | OK |
| G_lograd | presupposed | kill (T0=kill) | KILL | - | - | - | - | - | **KILL** | OK |
| G_quality_proxy | derived | kill (T1=kill) | PASS | KILL | PASS | PASS | PARK | PASS | **KILL** | OK |
| G_noise | derived | kill (T1=kill,T4=park) | PASS | KILL | PASS | PASS | PARK | PASS | **KILL** | OK |
| G_degphi_proxy | derived | kill (T3=kill) | PASS | KILL | PASS | KILL | datenlos | PASS | **KILL** | OK |

## Schwellen-Begruendung (praeregistriert)

| Test | Schwelle | Wert | Begruendung |
|---|---|---|---|
| T1 | T1_within_bucket_variance_ratio_max | 0.1 | Ein bewertungs-stiller G aendert sich nicht mit Exponenten -> die Within-Bucket-Varianz (gleicher rad-Traeger, wachsende Exponenten) ist ~ 0. KILL wenn > 10% der Gesamtvarianz aus Within-Bucket-Variation stammt. Zusaetzlich KILL wenn G konstant ist (keine Reaktion auf rad-Variation = sieht das Radikal nicht). |
| T2 | T2_omega_scaling_growth_factor_max | 2.0 | rad^{o(1)}-Ziel erlaubt nur O(1) pro bad prime -> |G|/omega beschraenkt. KILL wenn das obere (90%-)Quantil von |G|/omega vom untersten zum obersten omega-Terzil um mehr als Faktor 2 waechst (Tamagawa-/p+-1-Klasse akkumuliert Groesse pro Primteiler). Der Quotient von Quantilen ist skalenfrei (G-Skala kuerzt sich). |
| T3 | T3_partial_corr_abs_max | 0.3 | Nicht-Zirkularitaet (N3): partielle Korrelation corr(G, log deg phi | log rad) muss ~ 0 sein. |partielle Korrelation| > 0.30 (mehr als schwacher Zusammenhang) -> versteckter deg-phi-/Perioden-Proxy -> KILL. |
| T4 | T4_min_abs_cohen_d | 0.5 | Nutzen/Trennschaerfe: |Cohen d| >= 0.50 (mittlerer Effekt) zwischen hochqualitativen (q > 1.2) und magnitude-gematchten Zufallstripeln. Darunter PARK (nutzlos != falsch), KEIN Kill. Mindest-Power (T4_min_group_size=10): sind weniger als 10 auswertbare Tripel je Gruppe vorhanden (z.B. auf dem duennen Holdout), ist die Effektgroesse nicht belastbar -> T4 = datenlos (ehrlich) statt Zufallsverdikt. T4 ist weich; auf unterbesetzten Splits nicht asserted. |
| T5 | T5_cardinality_eta2_min | 0.98 | Support-only (N5): (A) bewertungs-blind (Within-Ratio <= 0.10, gleiches Signal wie T1) UND (B) omega (Support-Kardinalitaet) erklaert >= 98% der Between-Bucket-Varianz -> G traegt nur die Kardinalitaet des Traegers, kein arithmetisches Gewicht davon, WELCHE Primzahlen -> KILL. Ein arithmetisch gewichtetes G (z.B. log rad = Summe log p) erfuellt (A), aber NICHT (B) (unterscheidet gleich-grosse Traeger verschiedener Primzahlen) und ueberlebt T5. |

## Verdikt

**KALIBRIERUNG BESTANDEN** -- alle fuenf Referenz-Kandidaten liefern exakt das
erwartete Verdikt (inkl. der pro-Test-Asserts). Der Falsifikator trennt die vier
Kill-Mechanismen (Provenienz T0, Bewertungs-Sensitivitaet T1, Zirkularitaet T3,
Support-only T5) und den Nutzlos-Park (T4) wie spezifiziert.

## Pro-Kandidat-Register

### G_omega  --  Gesamt: **KILL**

- omega(rad(abc)) = Anzahl distinkter Primteiler (reine Traegermengen-Funktion)
- advice_level=A1, mechanism_class=derived, aktive Tripel=5390, nutzbare Buckets=180, Modus=train

| Test | Score | Verdikt | Kill-/Park-Grund |
|---|---|---|---|
| T0 |  | PASS |  |
| T1 | 0 | PASS |  |
| T2 | 1 | PASS |  |
| T3 | 0.1552 | PASS |  |
| T4 | -1.393 | PASS |  |
| T5 | 1 | KILL | support-only: omega (Kardinalitaet) erklaert 100.0% (>=98%) der Between-Bucket-Varianz -> G traegt nur WIE VIELE, nicht WELCHE Primzahlen (N5) |

**Verdikt-Begruendung:** T5: support-only: omega (Kardinalitaet) erklaert 100.0% (>=98%) der Between-Bucket-Varianz -> G traegt nur WIE VIELE, nicht WELCHE Primzahlen (N5)

### G_lograd  --  Gesamt: **KILL**

- log rad(abc) = Zielgroesse selbst als Input (praesupponiert)
- advice_level=A3, mechanism_class=presupposed, aktive Tripel=5390, nutzbare Buckets=180, Modus=train

| Test | Score | Verdikt | Kill-/Park-Grund |
|---|---|---|---|
| T0 |  | KILL | mechanism_class=presupposed -> Zielgroesse als Input vorausgesetzt (KILL ohne Rechnung) |

**Verdikt-Begruendung:** T0: mechanism_class=presupposed -> Zielgroesse als Input vorausgesetzt (KILL ohne Rechnung)

### G_quality_proxy  --  Gesamt: **KILL**

- log c (Groessen-Proxy; waechst mit Exponenten-Aufblaehung im Bucket)
- advice_level=A1, mechanism_class=derived, aktive Tripel=5390, nutzbare Buckets=180, Modus=train

| Test | Score | Verdikt | Kill-/Park-Grund |
|---|---|---|---|
| T0 |  | PASS |  |
| T1 | 0.441689 | KILL | Var(G|Bucket)/Var(G) = 0.4417 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt) |
| T2 | 1.0849 | PASS |  |
| T3 | -0.0175 | PASS |  |
| T4 | 0.1346 | PARK | |Cohen d| = 0.135 < 0.50 -> keine Trennschaerfe (PARK, kein Kill) |
| T5 |  | PASS | nicht support-only: G ist bewertungs-sensitiv (within_ratio 0.4417 > 0.10) -> T1-Domaene |

**Verdikt-Begruendung:** T1: Var(G|Bucket)/Var(G) = 0.4417 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt)

### G_noise  --  Gesamt: **KILL**

- deterministischer Pseudo-Zufall aus sha256(a,b,c)
- advice_level=A0, mechanism_class=derived, aktive Tripel=5390, nutzbare Buckets=180, Modus=train

| Test | Score | Verdikt | Kill-/Park-Grund |
|---|---|---|---|
| T0 |  | PASS |  |
| T1 | 0.885032 | KILL | Var(G|Bucket)/Var(G) = 0.8850 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt) |
| T2 | 0.652 | PASS |  |
| T3 | 0.0037 | PASS |  |
| T4 | 0.0919 | PARK | |Cohen d| = 0.092 < 0.50 -> keine Trennschaerfe (PARK, kein Kill) |
| T5 |  | PASS | nicht support-only: G ist bewertungs-sensitiv (within_ratio 0.8850 > 0.10) -> T1-Domaene |

**Verdikt-Begruendung:** T1: Var(G|Bucket)/Var(G) = 0.8850 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt)

### G_degphi_proxy  --  Gesamt: **KILL**

- log(deg phi) (Modulgrad-Proxy; nur Watkins-Subkorpus mit deg-Spalte)
- advice_level=A2, mechanism_class=derived, aktive Tripel=5390, nutzbare Buckets=180, Modus=train

| Test | Score | Verdikt | Kill-/Park-Grund |
|---|---|---|---|
| T0 |  | PASS |  |
| T1 | 0.153359 | KILL | Var(G|Bucket)/Var(G) = 0.1534 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt) |
| T2 | 0.8951 | PASS |  |
| T3 | 1 | KILL | |corr(G, log deg phi | log rad)| = 1.000 > 0.30 -> versteckter deg-phi-/Perioden-Proxy (N3) |
| T4 |  | datenlos | underpowered: n_highq=0, n_control=0 (< 10) -> Effektgroesse nicht belastbar |
| T5 |  | PASS | nicht support-only: G ist bewertungs-sensitiv (within_ratio 0.1534 > 0.10) -> T1-Domaene |

**Verdikt-Begruendung:** T1: Var(G|Bucket)/Var(G) = 0.1534 > 0.10 -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt); T3: |corr(G, log deg phi | log rad)| = 1.000 > 0.30 -> versteckter deg-phi-/Perioden-Proxy (N3)

## Artefakte

- Skript: `_scripts/starcore_falsifier.py` (Tests T0-T5, Korpus-Bau, Holdout, Kalibrierung).
- Schwellen: `_scripts/starcore_thresholds_preregistered_2026-07-10.json`.
- Korpus/Cache: `_data/starcore_corpus_2026-07-10.json`; Holdout-Indizes: `_data/starcore_holdout_indices_2026-07-10.json`.
- Ergebnis: `_results/starcore_falsifier_calibration_2026-07-10.json` + `_results/starcore_falsifier_calibration_2026-07-10.md`.
- Kein abc-Claim-Upgrade; die Majorisierungs-Ungleichung bleibt Handarbeit.
