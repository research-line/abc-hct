# Symplektische Eichung N=109 — Ergebnis (2026-07-10)

**Skript:** `_scripts/merel_invariant_gauge_n109.py` (v1)
**Artefakt:** `_results/merel_invariant_gauge_n109_2026-07-10.json`
**Baut auf:** `merel_delta_allowance_n109.py` (v3 / interne version 4) — Objekt-Konstruktion unverändert übernommen (Witness-Bridge nach M0, q=3863; B = A⁻ᵀ·Bsym·A⁻¹ Petersson-Pullback; 26 Source-Zeilen + r_N; T7-Restlinien-Familie; v3-φ'-Solve; N(S)-Schnitt ψ).
**Laufzeit:** 4,8 s (Mac Studio, `nice -n 10`, neben Großjob PID 65643).

## Selbstvalidierung — BESTANDEN

Die Reproduktion liefert alle v3-Referenz-Sollwerte exakt (Objektübernahme faithful):

| Sollwert | Referenz | Reproduziert |
|---|---|---|
| standard φ'(r_N) | 1772 | **1772** |
| standard ψ(r_N) | 687 | **687** |
| standard dim(N(S)∩Allowance) | 2 | **2** |
| standard Allowance-Rang | 8 | **8** |
| standard φ'-Vektor (17 Komp.) | fix | **identisch** |
| frey φ'(r_N) | −1065 (≡2798) | **−1065** |

## Hauptergebnis — die symplektische Eichung existiert NICHT (beide Konventionen)

| Größe | standard (a5=3,a7=2) | frey (a5=2,a7=0) |
|---|---|---|
| dim W_A | 9 | 9 |
| dim(W_A mod ker B) = Allowance-Rang | 8 | 8 |
| dim W_I (Vektoren) | 2 | 2 |
| dim(W_I ∩ ker B) | **1** | **1** |
| dim(W_I mod ker B) | **1** | **1** |
| dim B(W_I) (Funktionalraum) | **1** | **1** |
| Gram-Rang auf W_I | 0 | 0 |
| **g = B(u₁,u₂)** | **0** | **0** |
| WI_symplectic_nondegenerate | **false** | **false** |

### Verdikt (Spec-Interpretationszeile, Fall g=0)

> **g=0: W_I isotrop; symplektische Eichung nicht kanonisch verfügbar — Befund dokumentieren, integrale Route.**

Gilt identisch für standard und frey. **Kein abc-Claim** (war nie beabsichtigt).

## Warum — die Isotropie ist strukturell erzwungen, nicht zufällig

W_I ist 2-dimensional, zerfällt aber als
**W_I = ⟨k_w⟩ ⊕ ⟨w\*⟩** mit **k_w ∈ ker B** (dim(W_I∩ker B)=1) und einer einzigen Nicht-Kern-Richtung w\*.
Unter der alternierenden Form B ist damit die Gram-Matrix **zwangsläufig 0**:
B(k_w,·)=0 (Radikal), B(w\*,w\*)=0 (alternierend). Jeder 2-Raum, der einen ker-B-Vektor plus genau eine weitere Richtung enthält, ist isotrop. Ein symplektisches Komplement / eine kanonische Projektion π existiert daher prinzipiell nicht — unabhängig von Witness oder Prime. Die Schritte 4–6 (Projektion, inv, Invarianz-Selbsttests) entfallen mangels g≠0.

## Struktureller Zusatzbefund — der „reine" Schnitt ist 1-dimensional, nicht 2

Das Vektor-Gegenstück deckt auf, dass der **echte T7-Restlinien-Allowance-Schnitt** kleiner ist als v3 nahelegte:

- **B(W_I) = B(W_A) ∩ N(S)** ist **1-dimensional** (`match_BWI_eq_pure_BWAcapNS`=true — Reformulierung intern konsistent).
- Der v3-Schnitt hat **Dimension 2**, aber **B(W_I) ⊊ v3-Schnitt** (`match_BWI_subset_v3`=true, `match_v3_subset_BWI`=false).
- Die **zweite** Dimension in v3 stammt ausschließlich aus den ad-hoc-Generatoren **E_ker** und **E_row_eis** (Eisenstein-/Kern-Krücken), die *keine* T7-Restlinien-Funktionale B(w_c,−) sind. Das v3-Zeugnis (ψ_rN=687 bzw. −1552) nutzt diese Krücken mit nichttrivialen Koeffizienten.

Fazit: Die früher als „dim(N(S)∩Allowance)=2" geführte gate_invariant-Lücke ist im reinen (Petersson-symplektischen) Bild nur **1-dimensional**; die zweite Dimension war ein Artefakt der Eisenstein-/Kern-Beimischung.

## φ'(r_N) ist echt eich-abhängig (Negativkontrolle bestätigt)

Die eine echte Eichrichtung w\* bewegt φ'(r_N) nachweislich:

| Konvention | B(w\*, r_N) | φ'(r_N) → φ'+B(w\*,−) auf r_N |
|---|---|---|
| standard | 1491 | **1772 → 281** |
| frey | 147 | **−1065 → −1212** |

(`gauge_freedom_nontrivial_on_rN`=true; die ker-B-Richtung lässt φ'(r_N) erwartungsgemäß unverändert.) Damit ist der Nichtverschwindungswert 1772 **kein kanonischer Invarianten-Kandidat** — er hängt am Eich-Repräsentanten, und die einzige verfügbare Fixierung (symplektische Projektion) ist durch die Isotropie versperrt.

## Optionaler Datenpunkt (Schritt 8): Allowance-Rang ist ℓ-generisch

rank Span{B((T_ℓ−a_ℓ)e_c,−)} mit Kurven-a_ℓ (109a1):

| ℓ | a_ℓ | Familiengröße | Rang |
|---|---|---|---|
| 7 | 2 | 25 | **8** |
| 11 | 1 | 25 | **8** |
| 13 | 0 | 25 | **8** |

Der Rang 8 ist **nicht T7-spezifisch**, sondern über ℓ generisch.

## Auftragserweiterung CFR-5: h₇(e₀)-Eichung + N(S)-Landkarte

Ziel: Ist das satz-relevante Nichtverschwindens-Zertifikat **φ'(h₇e₀)** (statt nur φ'(r_N)) kanonisch rettbar? Zwei Lesarten von „h₇(e₀)" wurden parallel gerechnet — sie **fallen auseinander**, und beide sind negativ.

### Vorab-Befund: die Fan-Kombi ist NICHT T7·e₀

Die Vorgabe „h₇(e₀) = 2e₀+e₁+…+e₆ … das ist der alte Q7-Wert, der 0 war" ist durch Direktrechnung **falsifiziert**:

| Größe | standard | frey |
|---|---|---|
| φ'(2e₀+…+e₆) = q7_ungauged (Fan) | **1871** | **−1070** |
| φ'(T7·e₀) = q7_ungauged_T7e0 (= v3-„Q7") | **0** | **0** |
| 2e₀+…+e₆ == T7·e₀ ? (`h7e0_eq_T7e0`) | **false** | **false** |

Die Fan-Kombination und die Hecke-Wirkung T7·e₀ sind in M0-Koordinaten **verschiedene Vektoren** (die Bridge intertwined T7 nicht). Nur T7·e₀ liefert 0; die Fan-Kombi liefert 1871 ≠ 0.

### Lesart A — T7·e₀ (der wörtliche v3-„Q7"): FALL 3, ernst

| Messung | standard | frey |
|---|---|---|
| T7·e₀ im Source-Span (`T7e0_in_source_span`) | **true** | **true** |
| ∃ψ∈N(S): ψ(T7·e₀)≠0 (`exists_psi_detecting_T7e0`) | **false** | **false** |
| ψ(T7·e₀) über N(S)-Basis | **alle 0** | **alle 0** |
| Allowance-Eichung bewegt φ'(T7·e₀) | **false** | **false** |

> **T7·e₀ liegt (Klassen-Ebene) im Span der Source-Zeilen.** φ'(T7·e₀)=0 ist damit **strukturell erzwungen** (kein source-annihilierendes Funktional kann auf einer Source-Kombination ≠0 sein), gauge-**invariant**, und **kein** ψ∈N(S) sieht T7·e₀. Für die T7·e₀-Lesart **scheitert CFR-5 strukturell** bei N=109 in der Witness-Lesart — der ernste Fall-3-Befund. **Sofort-Meldung an den Hauptagenten.**

### Lesart B — Fan 2e₀+…+e₆: FALL 2, aber vollständig an r_N gekoppelt

| Messung | standard | frey |
|---|---|---|
| φ'(h₇e₀) ungeeicht (`q7_ungauged`) | 1871 | −1070 |
| Allowance-Eichung bewegt φ'(h₇e₀) (`allowance_gauge_moves_q7`) | **true** (ι(h₇e₀)=−1341) | **true** (−1388) |
| h₇e₀ im Source-Span | false | false |
| h₇e₀ ∈ Span(Sources, r_N) (`h7e0_in_S_plus_rN`) | **true** | **true** |
| rank(S)=8 → rank(S,r_N)=9 → rank(S,r_N,h₇e₀) | **9** (kein Zuwachs) | **9** |
| ∃ψ∈N(S): ψ(h₇e₀)≠0 | **true** | **true** |
| Detektions-Bild dim {ψ↦(ψ(r_N),ψ(h₇e₀))} (`ns_detection_image_dim_rN_h7e0`) | **1** | **1** |

**N(S)-Landkarte** (dim N(S)=9; nur die 3 detektierenden Basisvektoren ≠0, Rest (0,0,0)):

| ψ_i | ψ(r_N) | ψ(h₇e₀) | ψ(T7·e₀) |
|---|---|---|---|
| detektierend (×3) | ∓1119 | ±508 | **0** |
| blind (×6) | 0 | 0 | 0 |

Deutung: φ'(h₇e₀)=1871 ist **gauge-beliebig** (die 1-dim Allowance-Eichung mit ι(h₇e₀)=−1341≠0 erreicht mod 3863 jeden Wert, inkl. 0) → **kein kanonisches Zertifikat** (g=0). Es existieren zwar CFR-5-taugliche ψ∈N(S) (h₇e₀ ∉ Source-Span), aber das **Detektions-Bild ist 1-dimensional**: **jede** detektierende ψ sieht r_N und h₇e₀ im **festen Verhältnis** (−1119:508). Daraus folgt die exakte Relation

> **508·r_N + 1119·h₇e₀ ∈ Source-Span**  ⟺  **h₇e₀ ≡ c·r_N (mod Sources)**, konsistent mit φ'(h₇e₀)=c·φ'(r_N) (1871 = c·1772).

r_N-Sichtbarkeit und h₇e₀-Sichtbarkeit sind also **maximal gekoppelt, nicht entkoppelt**. Die Fan-Lesart von h₇e₀ trägt **keine von r_N unabhängige** Zertifikats-Information; die B_N/symplektische Route ist fürs CFR-5-Gate ohnehin die falsche Auswahlvorschrift (g=0). Konstruktions- vs. Existenzfrage sind zu trennen.

### CFR-5-Gesamtbild

Beide Lesarten kollabieren das CFR-5-Gate zurück: **T7·e₀** ist eine reine Source-Kombination (Fall 3, strukturell tot), **2e₀+…+e₆** ist bis auf Source-Rest ein Vielfaches von r_N (Fall 2, nichts Neues gegenüber r_N). In keiner Lesart entsteht ein eigenständiges, kanonisch nichtverschwindendes Klassen-Zertifikat auf h₇e₀.

## Nicht durchgeführt: q'=5077 (Spec Punkt 7, optional)

Übersprungen mit dokumentiertem Grund: Die `mixed_rows.jsonl`-Zeilen sind bereits als **GF(3863)-Residuen** gespeichert (z.B. Wert 3862 = −1 mod 3863), nicht als Rohintegers. Eine Reduktion dieser Residuen mod 5077 wäre mathematisch falsch (3862 ≠ −1 mod 5077). Ein faithful q'-Rerun bräuchte die Roh-Integer-Zeilen aus dem Zertifikatsgenerator, die in diesem Artefakt nicht vorliegen.

## Einordnung für die nächste Route

1. **Symplektische Eichung negativ entschieden:** W_I ist isotrop (g=0, strukturell), also gibt es keine kanonische Klassen-Ebene-Auswertung von φ'(r_N) oder φ'(h₇e₀) auf diesem Weg → **integrale Normalisierungs-Route** wird Pflichtweg. Die reine (krückenfreie) Lücke ist nur 1-dimensional.
2. **CFR-5 auf h₇e₀ ergibt kein eigenständiges Zertifikat** — in keiner der beiden Lesarten:
   - **T7·e₀ (wörtlicher Q7):** liegt klassen-eben im Source-Span → φ'(T7·e₀)=0 strukturell erzwungen, von keinem ψ∈N(S) gesehen. **Ernster Fall-3-Struktur-Befund gegen CFR-5 bei N=109 in der Witness-Lesart.**
   - **Fan 2e₀+…+e₆:** ≡ c·r_N mod Sources (Detektions-Bild dim 1), φ'-Wert gauge-beliebig → nichts unabhängig von r_N.
3. **Handlungsempfehlung:** Vor jedem weiteren „inv_Q7"-Aufbau die **Definition von h₇(e₀) klären** (Fan-Kombi vs. Hecke-T7·e₀ — sie unterscheiden sich hier real), und die **Witness-Lesart** für das CFR-5-Gate hinterfragen: die Q7-Restlinien-Eigenschaft ist in dieser Lesart bei N=109 entweder tot (T7·e₀) oder auf r_N reduzierbar (Fan). Der integrale/ideal-ebene Zugang, den der OT-Scope-Audit für Satz 1/3 andeutet, dürfte auch hier nötig sein.

_LG, 2026-07-10._
