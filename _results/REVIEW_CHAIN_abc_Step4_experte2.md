# Review Chain — abc Paper v0.1 — Step 4 (Experte 2)

**Modell:** Opus 4.7
**Datum:** 2026-04-29
**Paper:** A Theta-Tamagawa Route to the abc Conjecture via Frey Curves
**Datei:** `abc_Theta_Tamagawa_EN.tex`

---

## Gesamteindruck

Nach Iteration 30 ist das Paper substanziell ehrlicher. Die Substanz — Thm 8.10 (universelle Eta-Schranke `|η|^24 < 0.005`) und die Periodenreformulierung — ist tragfähig. Aber drei neue harte Probleme bleiben für eine CRMath-Einreichung:

1. **Neuer Befund A1:** Cor 8.11 behauptet "abc ⟺ λ₁ ≥ c·N^{-1/2-ε}", aber der Beweis liefert nur die Richtung **λ₁ ≥ N^{-1/2-ε} ⟹ Szpiro**. Die Rückrichtung (Szpiro ⟹ λ₁ ≥ N^{-1/2-ε}) ist nicht bewiesen. Zusätzlich: rem:lambda1_omega zeigt λ₁ ≤ Ω_E mit möglicherweise strikter Ungleichung. Drei verschiedene Boxed-Gleichungen (eq:abc_lattice, eq:equiv_chain, eq:abc_core) mit uneinheitlicher Richtungsaussage.

2. **A2:** Titel überstrapaziert Inhalt — "Route to abc" ohne funktionierenden Beweis.

3. **A3:** §4 Volltext-Beweis + Erratum strukturell unbefriedigend.

---

## A: Pflicht-Korrekturen für Journal-Einreichung

### A1 (KRITISCH — neuer Befund): Äquivalenzrichtung in Cor 8.11

**Problem:** Cor 8.11 behauptet Äquivalenz "abc ⟺ λ₁ ≥ c·N^{-1/2-ε}", aber der Beweis (Z. 1069-1078) liefert nur Hinrichtung (λ₁-Schranke ⟹ Szpiro via eq:delta_lambda). Umkehrung (Szpiro ⟹ λ₁-Schranke) braucht eine untere Schranke an |η|^24 für Frey-Kurven, die nicht im Paper steht.

Zusätzlich: eq:abc_lattice (Z. 1063), eq:equiv_chain (Z. 1166), eq:abc_core (Z. 1531) behaupten alle verschiedene Formulierungen mit "⟺" ohne durchgehend bewiesene Bikonditionalität.

**Fix:** "is equivalent to" → "follows from", "⟺" → "⟸" oder "(sufficient condition:)" in Cor 8.11 und eq:abc_lattice. In eq:equiv_chain Äquivalenzkette als "Conjectured equivalences" oder mit Quellenangaben markieren.

### A2 (KRITISCH): Titeländerung

**Vorschlag:** "An unconditional eta bound and the period reformulation of the abc conjecture"

Abstract: "We develop a non-circular reformulation" statt "route".

### A3 (WICHTIG): §4 in Appendix

Volltext-Beweis (Z. 411-438) + Erratum → Appendix A auslagern.
Haupttext: 3-5 Zeilen Skizze + Pointer. Proposition bleibt im Haupttext.

---

## B: Empfohlene Verbesserungen (Reviewer-Härtung)

**B1 (E5):** Prop. 3.1 letzter Schritt — Apostol §1.6 oder Köhler "Eta Products and Theta Series Identities" zitieren.

**B2 (E7):** Modulgrad-Formel: `deg φ = 4π²‖f‖²_Pet / (c_E²·Vol(E(C)))` mit Manin-Konstante c_E explizit.

**B3 (E9):** Im(τ)-Tabellenwerte erklären: vor vs. nach SL₂-Reduktion, mit Spalte für reduziertes Im(τ').

**B4:** §10 (IUT-Vergleich) für CRMath auf 3-4 Sätze + Verweis auf GeigerIUT2026 kürzen.

**B5:** Heuristisches Material (rem:mining_difficulty, rem:poisson_regime, rem:katz_sarnak) zu einem einzigen "Heuristic remark" verdichten.

**B6:** Manin-Drinfeld-Lücke in Prop. 7.5 explizieren (Rationalität ≠ Periodenformel direkt).

---

## C: Abgelehnte Vorschläge aus Step 3

**C1 (abgelehnt) — Strukturreorganisation §8→§5:** Für CRMath-Note nicht nötig; Abstract + rem:strategy_sec4 leiten bereits korrekt. Kosten überwiegen Nutzen.

**C2 (abgelehnt) — IUT-Vergleich vertiefen:** Gehört ins IUT-Forensik-Paper. §10 für CRMath kürzen, nicht vertiefen.

**C3 (abgelehnt) — Watkins/Goldfeld/Frey als Pflichtbibitems:** Nice-to-have, kein Blocker für CRMath.

**C4 (relativiert) — FST-Sprache:** "FST framework"-Begriff lokalisieren; Idee (mining difficulty) behalten.

---

## D: Minimaler Einreichungsplan (CRMath)

**Phase 1 — Pflichtfixes (1 Iteration):**
1. A1: Äquivalenzrichtung in Cor 8.11, eq:abc_lattice, eq:equiv_chain, eq:abc_core
2. A2: Titel + Abstract
3. A3: §4-Beweis → Appendix A
4. B1 (E5): Prop. 3.1 Apostol-Referenz
5. B2 (E7): Modulgrad-Formel 4π²

**Phase 2 — CRMath-Format (1 Iteration):**
6. Paper auf 8-12 Seiten kürzen (§10 kürzen, Heuristik-Tabellen als Appendix)
7. Abstract anpassen
8. KI-Disclosure (L1 oder L2) in Acknowledgements

**Nicht nötig:** Komplette Reorganisation, vollständige Bibitems, Im(τ)-Erklärung, Manin-Drinfeld-Fix.

**Backup-Journal:** Journal de Théorie des Nombres de Bordeaux (falls CRMath ablehnt).

**Geschätzter Aufwand:** 2-3 Arbeitstage bis Submission.

---

## E: Readiness-Score

| Zustand | Score |
|---------|-------|
| Aktuell (nach Iteration 30) | **6.0/10** |
| + A1-A3 (Pflichtfixes) | **7.0/10** |
| + A1-A3 + B1-B2 | **7.5/10** |
| + Vollständige Phase 1+2 | **8.0/10** |

---

## Score-Trajektorie

| Step | Score | Hauptbefund |
|------|-------|-------------|
| Step 1 (Konstruktiv 1) | 5.5/10 | §4 vs. §7 Inkonsistenz |
| Step 2 (Experte) | 4.5/10 | Thm 4.2 algebraisch falsch; Conj. 4.1 nicht wohldefiniert |
| Step 3 (Konstruktiv 2) | 5.5/10 | E1-E6 Fixes; Titel + §4 noch offen |
| **Step 4 (Experte 2)** | **6.0/10** | **Neue Lücke A1: λ₁/Ω_E-Äquivalenz nur Hinrichtung bewiesen**; Titel + §4-Struktur Blocker |

---

## Pflichtfixes für Step 5 (Widerleger)

1. A1: Äquivalenzrichtung auf einseitig umstellen
2. A2: Titel ändern
3. A3: §4 → Appendix
4. B1: Prop. 3.1 Referenz
5. B2: Modulgrad 4π²-Faktor

Step 5 sollte gezielt prüfen:
- Hält die A1-Korrektur (nur Hinrichtung) einer harten Lesung stand?
- Ist Thm 8.10 wirklich neu oder implizit in Standardliteratur?
- Ist die non-circularity gegenüber BSD-Vorgängerpaper haltbar?
