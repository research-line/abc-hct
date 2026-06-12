# Review Chain — abc Paper v0.1 — Step 5 (Widerleger)

**Modell:** Opus 4.7
**Datum:** 2026-04-29
**Paper:** An Unconditional Eta Bound and the Period Reformulation of the abc Conjecture via Frey Curves
**Datei:** `abc_Theta_Tamagawa_EN.tex`

---

## Vorbemerkung

Dies ist ein Ablehnungsbericht. Keine konstruktiven Vorschläge, nur Falsifikation.

---

## Angriffspunkte

### Angriff 1 (TÖDLICH): Cor 8.11 = Goldfeld 1988 Period Conjecture — nicht neu

**Exakte Stelle:** Titel; Abstract; Cor 8.11 (eq:abc_lattice); eq:abc_core; eq:equiv_chain.

**Warum:** Goldfeld formulierte 1988 explizit die **Period Conjecture** für Frey–Hellegouarch-Kurven: Periode ≥ c_ε·N^{-κ(ε)} impliziert die schwache abc-Vermutung. Identische geometrische Setting (Frey-Kurve), identische logische Richtung ("Periode-Schranke ⟹ abc"), nur leicht angepasster Exponent. Das Manuskript zitiert Goldfeld NICHT in Cor 8.11.

**Pathologie:** Cor 8.11 ist 38 Jahre alte Standard-Folklore, präsentiert als eigener Beitrag. Die Innovation reduziert sich auf eine Notations-Variante (Tamagawa-Zahlen-Sprache statt Modulgrad-Sprache).

---

### Angriff 2 (TÖDLICH): Theorem 8.10 ist eine Lehrbuch-Übung

**Exakte Stelle:** Theorem 8.10 (thm:eta_bound) + Beweis Z. 1029-1050.

**Warum:** Der Beweis besteht aus zwei elementaren Schritten:
1. τ ∈ F ⟹ Im(τ) ≥ √3/2 ⟹ |q| ≤ e^{-π√3} ≈ 0.00433 (Definition des Fundamentalbereichs).
2. Geometrische Reihen-Schranke.
Die Beschränktheit von |η(τ)|^24 auf F folgt sofort aus Holomorphie + SL₂(Z)-Quasi-Invarianz + Kompaktheit mod Spitze. Die explizite Konstante 0.005 ist eine numerische Auswertung, kein mathematisches Resultat.

**Pathologie:** Die Schranke 0.005 ist unabhängig von N (trivial « N^ε), löst aber das eigentliche Problem nicht: für kleine Im(τ_∞) (große Konduktoren) verschiebt die SL₂(Z)-Reduktion τ_∞ → τ' ∈ F das Problem in den λ₁-Faktor.

---

### Angriff 3 (TÖDLICH): Cor 8.11 reduziert abc auf strikt schwierigeres λ₁-Problem

**Exakte Stelle:** Cor 8.11 + rem:lambda1_omega.

**Warum:** Cor 8.11 beweist: λ₁ ≥ c·N^{-1/2-ε} ⟹ Szpiro. Da λ₁ ≤ Ω_E (rem:lambda1_omega), ist eine untere Schranke an λ₁ STÄRKER als an Ω_E. Das Korollar reduziert abc also nicht auf das bekannte Goldfeld-Problem, sondern auf ein strikt schwierigeres.

**Pathologie:** Die "Reformulierung" verstärkt die zu beweisende Aussage.

---

### Angriff 4 (SCHWER): Identifikation Δ_min = (2π/λ₁)^12 · |η(τ')|^24 ignoriert 2-adische Faktoren

**Exakte Stelle:** Beweis Cor 8.11, Z. 1074-1080; eq:frey_invariants.

**Warum:** Δ_min (Néron-Modell) ≠ Δ(Λ) (analytischer Diskriminant) in Allgemeinheit. Frey-Kurven haben Δ_min = (abc)^2/2^δ mit δ ∈ {0,4,8}. Der 2-adische Faktor 2^δ bis zu 256 ist in der Konstante 0.005 nicht kontrolliert.

---

### Angriff 5 (SCHWER): §4 enthält falschen Beweis im Haupttext

**Exakte Stelle:** Beweis Prop 4.2 Z. 412-438 + Erratum rem:erratum_gap.

**Warum desk-reject:** Der Beweis behauptet |η(ℓτ_p)| ≥ c > 0, was falsch ist. Das Inline-Erratum gesteht dies vollumfänglich ein. Kein Top-Journal akzeptiert einen Hauptsatz-Beweis, der im selben Paper als algebraisch falsch bezeichnet wird.

---

### Angriff 6 (SCHWER): Conj 4.1 nicht wohldefiniert — Selbst-Disqualifikation macht Paper inkohärent

**Exakte Stelle:** Conj 4.1 + rem:conj_welldefined.

**Warum:** Conj 4.1 ist (i) als p-adische Aussage trivial, (ii) als archimedische Aussage nicht wohldefiniert, (iii) als adelische Aussage nicht ausgearbeitet. 30% des Textes über eine gescheiterte Route belastet das Manuskript.

---

### Angriff 7 (SCHWER): Im(τ)-Werte in Tab 2 < √3/2 — aber Thm 8.10 verlangt ≥ √3/2

**Exakte Stelle:** Thm 8.10 + tab:eta.

**Warum:** Tab 2 zeigt Im(τ_∞) ∈ [0.27, 0.91]. Nur einer von 9 Werten liegt über √3/2 ≈ 0.866. Die Eta-Funktion ist NICHT SL₂(Z)-invariant: |η(γτ)|^24 = |cτ+d|^12 · |η(τ)|^24. Die Tabelle wertet η an nicht-reduziertem τ_∞ aus, während Thm 8.10 reduziertes τ' ∈ F voraussetzt. Die numerische Evidenz belegt Thm 8.10 NICHT.

---

### Angriff 8 (HEILBAR): Prop 3.1 letzter Schritt nicht ausgeschrieben

**Exakte Stelle:** Beweis Prop 3.1, Z. 332-335.

**Warum:** "at appropriate arguments" ist keine Beweisführung. Die Modulidentität muss explizit angewendet werden.

---

### Angriff 9 (SCHWER): Prop 7.7 (Diophantine Reformulation) empirisch falsifiziert

**Exakte Stelle:** Prop 7.7 + eq:diophantine_bound vs. tab:eta.

**Warum:** Prop 7.7 verlangt Im(τ_∞) ≥ ε'/(2π)·log N. Tabelle 2 zeigt Im(τ_∞) konstant in [0.27, 0.91] für N bis 260718. Diese widerspricht eq:diophantine_bound direkt.

---

### Angriff 10 (HEILBAR): Mining-Difficulty-Heuristik ist FST-Slogan, kein Argument

**Exakte Stelle:** rem:mining_difficulty, rem:poisson_regime, rem:katz_sarnak.

**Warum:** Der Autor räumt selbst ein (Z. 1308-1313): keine Technik überbrückt statistische Vorhersagen und deterministische Schranken. Das ist Marketing, kein Beweis.

---

### Angriff 11 (HEILBAR): IUT-Vergleich §10 ist prätentiös

**Exakte Stelle:** §10 Z. 1581-1611.

**Warum:** Das Paper stellt sich auf eine Stufe mit Mochizukis 700-seitiger Theorie, ohne eigene Strategie zur Theta-Conductor-Bound. §10 ist Selbst-Inflation.

---

### Angriff 12 (SCHWER): Self-Citation auf zirkuläres Vorgänger-Paper

**Exakte Stelle:** Z. 113-116 + Z. 1786 (GeigerBSD2026, GeigerIUT2026).

**Warum:** Das BSD-Paper wird als Begründung für "non-circularity" zitiert, enthält aber selbst eine "circularity at step (B3)". Non-circularity durch Selbstverweis ist keine externe Validierung.

---

### Angriff 13 (HEILBAR): Modulgrad-Formel fehlt 4π²-Faktor

**Exakte Stelle:** rem:modular_degree Z. 794-795.

**Warum:** Korrekt: deg φ = (4π²‖f‖²_Pet)/(c_E²·Vol(E(C))). Das "up to Manin constant" versteckt den 4π²-Faktor.

---

### Angriff 14 (SCHWER): Petersson-Norm-Asymptotik ohne Konvention

**Exakte Stelle:** eq:petersson_sym2 Z. 743-747.

**Warum:** ‖f‖² ≍ L(Sym²f,1)/N hängt von Volumen-Normierung auf Γ₀(N)\H ab. Keine Seitenangabe oder Formelnummer aus Iwaniec-Sarnak.

---

### Angriff 15 (TÖDLICH): "Sole remaining open content" — irreführende Inflation

**Exakte Stelle:** Abstract; rem:strategy_sec4; rem:significance; rem:numerical (boxed).

**Warum:** Die "Reduktion auf single bound" nutzt:
1. Goldfeld 1988 als "neue" Reformulierung
2. Elementaren Taschenrechner-Bound als "universelles Theorem"
3. λ₁-Schranke statt Ω_E-Schranke (strikt schwieriger)
4. Unkontrollierte 2-adische Faktoren in Δ_min

Das "single open inequality" ist weder neu, noch korrekt zugeordnet, noch vollständig bewiesen.

---

## Zusammenfassung

| # | Angriff | Einschätzung |
|---|---------|--------------|
| 1 | Cor 8.11 = Goldfeld 1988 (nicht neu) | **tödlich** |
| 2 | Thm 8.10 ist Lehrbuch-Übung | **tödlich** |
| 3 | λ₁-Problem strikt schwieriger als abc | **tödlich** |
| 4 | Δ_min vs. Δ(Λ): 2-adische Faktoren | schwer |
| 5 | §4 falscher Beweis im Haupttext | schwer |
| 6 | Conj 4.1 nicht wohldefiniert | schwer |
| 7 | Im(τ) < √3/2: Tab 2 ≠ Thm 8.10 Voraussetzung | schwer |
| 8 | Prop 3.1 letzter Schritt offen | heilbar |
| 9 | Prop 7.7 von Tab 2 widerlegt | schwer |
| 10 | Mining-Difficulty: Slogan statt Beweis | heilbar |
| 11 | IUT-Vergleich prätentiös | heilbar |
| 12 | Self-Citation auf zirkuläres Paper | schwer |
| 13 | Modulgrad ohne 4π² | heilbar |
| 14 | Petersson-Norm ohne Konvention | schwer |
| 15 | "Single bound" Marketing-Inflation | **tödlich** |

**Verdikt Widerleger:** Vier tödliche Angriffe. Paper überlebt in dieser Form kein Top-Journal. Desk-Reject. Erfordert grundsätzliche Neuausrichtung — entweder als Übersichtsartikel (mit Goldfeld-Zitat) oder als rein numerische Note über die Konstante 0.005 und das empirische Eta-Verhalten.

---

## Score-Trajektorie

| Step | Score | Hauptbefund |
|------|-------|-------------|
| Step 1 (Konstruktiv 1) | 5.5/10 | §4 vs. §7 Inkonsistenz |
| Step 2 (Experte) | 4.5/10 | Thm 4.2 algebraisch falsch; Conj. 4.1 nicht wohldefiniert |
| Step 3 (Konstruktiv 2) | 5.5/10 | E1-E6 Fixes; E6 unfixiert; Struktur-Probleme |
| Step 4 (Experte 2) | 6.0/10 | λ₁/Ω_E-Äquivalenz nur Hinrichtung; Titel/§4 |
| **Step 5 (Widerleger)** | **— (adversarial)** | 4 tödliche Angriffe: Neuheit, Trivialität Thm 8.10, λ₁-Schwierigkeit, Marketing-Inflation |
