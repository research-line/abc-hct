# Review Chain — abc Paper v0.1 — Step 7 (Abschluss)

**Modell:** Opus 4.7
**Datum:** 2026-04-29
**Paper:** *An Unconditional Eta Bound and the Period Reformulation of the abc Conjecture via Frey Curves*
**Autor:** Lukas Geiger (Independent Researcher, Bernau)
**Datei:** `abc_Theta_Tamagawa_EN.tex`
**Rolle:** Senior-Editor / Schluss-Gutachter (analytische Zahlentheorie)
**Vorlauf:** 6 Review-Schritte, 33 Loop-Iterationen

---

## 1. Gesamtbild

Nach sechs Review-Iterationen ist aus dem urspruenglich ueberreichten Manuskript ein deutlich konturierteres Werk geworden. Die ehrgeizige Anfangsbehauptung — eine vollstaendige Reduktion der abc-Vermutung auf eine Theta-Konduktor-Schranke — hat sich in der Pruefung als nicht haltbar erwiesen (Thm 4.2 algebraisch falsch) und wurde vom Autor durch einen ehrlichen Erratum-Block ersetzt. Was bleibt, ist ein wesentlich bescheideneres, aber dafuer **sauberes Resultat**:

> Eine **unbedingte**, explizit konstante obere Schranke $|\eta(\tau)|^{24} < 0{,}005$ auf dem $\mathrm{SL}_2(\mathbb{Z})$-Fundamentalbereich, kombiniert mit einer **bedingten** $\lambda_1$-Periodenversion der abc-Vermutung fuer Frey-Kurven.

Im Literaturkontext positioniert sich das Paper damit nicht mehr als Durchbruch, sondern als **quantitative Verfeinerung** der seit Goldfeld (1988/2002) bekannten Periodenversion: explizite Konstante $0{,}005$, $\lambda_1$-Lattice-Formulierung statt $\Omega_E$, expliziter $\eta$-Beweis. Das ist der Korridor, in dem Hindry/Silverman, Mihailescu und juengere Arbeiten zu effektiven Schranken arbeiten — eine Note, kein Theorem-of-the-Year.

Der Review-Prozess hat die "schweren" Defekte (algebraischer Fehler, fehlendes Goldfeld-Zitat, Aequivalenz statt Implikation, irrefuehrender Titel) sukzessive abgetragen. Die in Step 5 erhobenen "toedlichen" Angriffe sind in Step 6 saemtlich auf reparable Maengel oder strukturelle, aber kommunizierbare Limitierungen zurueckgefuehrt worden. Was jetzt noch zwischen dem Paper und einer Submission steht, ist nicht mathematischer, sondern **redaktioneller Natur**.

---

## 2. Staerken (was bleibt und was traegt)

1. **R1 (Theorem 8.10) ist unbedingt korrekt und elementar.** Der $|\eta|^{24}<0{,}005$-Beweis aus $\tau\in\mathcal{F}\Rightarrow \mathrm{Im}(\tau)\ge\sqrt{3}/2$ plus geometrischer Reihe ist neun Zeilen lang, prueffaehig und liefert eine konkrete numerische Konstante. Das ist genau die Art von tragfaehiger Mikro-Behauptung, die ein Note-Format vertraegt.
2. **Saubere Implikations-Struktur in Cor 8.11.** Nach den A1- und P1-Fixes ist die einseitige Implikation $\lambda_1 \ge c_\varepsilon \cdot N^{-1/2-\varepsilon} \Rightarrow \mathrm{abc}$ klar und konsistent formuliert. Die Reformulation auf $\lambda_1$-Sprache (Lattice-Formalismus) ist didaktisch wertvoll und macht die Periodenversion zugaenglicher als die klassische $\Omega_E$-Form.
3. **Ehrliches Erratum-Handling fuer §4.** Statt das algebraisch falsche Thm 4.2 zu verstecken oder herauszuschneiden, dokumentiert das Paper den Fehler explizit (`rem:erratum_gap`). Das ist wissenschaftlich vorbildlich und entzieht dem nahe liegenden "Reviewer-Skeptizismus" die Grundlage — sofern §4 in den Anhang wandert (siehe Schwaeche 3).
4. **Goldfeld-Verortung jetzt explizit.** Nach dem Goldfeld-2002-Fix ist die Beziehung zu Goldfelds Period-Conjecture als "quantitative refinement" klar gerahmt. Das nimmt dem schwersten Step-5-Angriff (Plagiats-Vorwurf) die Spitze.
5. **Numerische Tabellen sind robust.** Die 16 getesteten Frey-Tripel mit 9 dargestellten Faellen und der Tab-2-Caption-Hinweis auf den unreduzierten $\tau_\infty$ (P3-Fix) zeigen, dass die quantitative Seite ueber bloss illustrative Beispiele hinausgeht.

---

## 3. Verbleibende Schwaechen (hierarchisch nach Impact)

### Schwaeche 1 — Strukturell: §4-Beweis und Erratum noch im Haupttext (P2 offen)

Das ist die einzige derzeit noch **submission-blockierende** Schwaeche. Ein gescheiterter Beweis mit unmittelbar nachgelagertem Erratum mitten im Haupttext eines 8–12-Seiten-CRMath-Notes ist fuer einen Reviewer ein Sofort-Reject-Trigger — unabhaengig davon, wie ehrlich das Erratum formuliert ist. Verschiebung nach Anhang A entzieht diesem Einwand die Oberflaeche, ohne den intellektuellen Gehalt zu opfern. Aufwand: 1–2 Stunden.

### Schwaeche 2 — Strukturell, nicht reparabel: Neuheits-Limit gegenueber Goldfeld 1988

Cor 8.11 ist nach allen Fixes eine quantitative Verfeinerung (explizite Konstante, $\lambda_1$-Reformulierung), keine genuin neue Reduktion. Das ist ein **Decken-Effekt** auf die Publikationsklasse: realistisch CRMath / JTNB / Acta Arithmetica, nicht Annals / JAMS / Inventiones. Diese Limitierung ist nicht durch weitere Iterationen behebbar; sie muss in Cover Letter und Abstract ehrlich gerahmt werden ("explicit refinement of Goldfeld's Period Conjecture"). Behandlung: Erwartungsmanagement, kein Fix.

### Schwaeche 3 — Mathematisch: $\lambda_1$-Richtung nur hinreichend, abc $\Rightarrow \lambda_1$ offen

Cor 8.11 liefert nur die Hinrichtung. Die Rueckrichtung — dass abc tatsaechlich $\lambda_1 \ge c_\varepsilon N^{-1/2-\varepsilon}$ erzwingt — ist nicht bewiesen, und ohne sie ist die "Reformulation"-Sprache eine Ueberinterpretation. Nach P6 spricht das Paper konsequent von "sufficient condition", was die Lage korrekt darstellt. Damit ist die Schwaeche kommuniziert, nicht behoben — der eigentliche mathematische Gewinn der Aequivalenz steht noch aus.

(Die in der Step-3/4-Liste verbliebenen Punkte E1, E3, E4, E7 und P7 sind kosmetische Politur und beeinflussen die Submission-Entscheidung nicht. Sie sollten in der Endrevision mit erledigt werden, sind aber kein Tor.)

---

## 4. CRMath-Votum

**Empfehlung:** **Nicht jetzt — aber nach P2-Fix submission-bereit.**

Konkret:

- **Aktueller Zustand:** Submission-Risiko hoch wegen §4-Erratum im Haupttext (Schwaeche 1). Ein CRMath-Reviewer wird dieses Strukturproblem innerhalb der ersten Lesephase identifizieren und die Note vermutlich ohne inhaltliche Diskussion ablehnen.
- **Nach P2-Fix (1–2 Tage Aufwand):** Submission an **CRMath als Erstwahl** ist realistisch. Der Beitrag passt in das Note-Format, die explizite Konstante und die $\lambda_1$-Verpackung tragen einen modesten, aber klar identifizierbaren Mehrwert. Risiko: Neuheits-Frage (Schwaeche 2) — Reviewer koennte den Beitrag als zu inkrementell empfinden.
- **Backup-Strategie:** Bei CRMath-Ablehnung **Journal de Theorie des Nombres de Bordeaux (JTNB)** oder **Acta Arithmetica** — beide gleicher Tier, stilistisch toleranter gegenueber inkrementellen Verfeinerungen mit ehrlichem Framing. Eine fruehe Direkt-Submission an JTNB ist eine vertretbare risikominimierte Alternative.

**Cover-Letter-Linie:** "Explicit numerical refinement of Goldfeld's (2002) Period Conjecture for Frey curves, with an unconditional eta bound as auxiliary input." Nicht: "Reduction of abc to a single inequality." Wenn das Framing stimmt, ist die Note publizierbar.

**Aufwand bis Submission:**

| Schritt | Inhalt | Aufwand |
|---|---|---|
| P2 | §4-Beweis + Erratum nach Anhang A | 1–2 h |
| P7 | Néron-Differential-Normierung in `rem:lambda1_omega` | 1–2 h |
| E1, E3, E4, E7 | Apostol-Referenz, IUT-Vergleich kuerzen, Heuristik konsolidieren, Thm 8.10 elementaren Charakter anerkennen | 0.5–1 d |
| Format | CRMath-Class (lateximes), 8–12 Seiten, KI-Disclosure L1/L2 | 0.5 d |
| Cover Letter | "quantitative refinement"-Framing | 1 h |
| **Summe** | **2–3 Arbeitstage** | |

---

## 5. Finale Score: **6.5 / 10**

**Begruendung:**

- **+** Alle Step-5-"toedlichen" Angriffe sind in Step 6 entschaerft worden; das Paper hat kein einziges desk-reject-fatales Problem mehr.
- **+** P1 (Sprach-Konsistenz Aequivalenz vs. Implikation) ist umgesetzt — die Step-6-Regression ist behoben.
- **+** Der unbedingte Kernbeitrag (Thm 8.10) und das ehrliche Erratum-Handling sind echte Aktiva.
- **−** P2 (§4 nach Anhang) ist noch offen; das ist die eine strukturelle Submission-Bremse.
- **−** Neuheits-Limit gegenueber Goldfeld 1988 deckelt den maximal erreichbaren Score in dieser Paper-Konzeption auf etwa 8.0.

**Pfadangabe (was 6.5 in 8.0 verwandelt):**

| Stand | Score |
|---|---|
| Aktueller Stand (P1, P3, P4, P5, P6 done; P2, P7 + E-Fixes offen) | **6.5** |
| + P2 (§4 → Anhang) | 7.0 |
| + P7, E1, E3, E4, E7 | 7.5 |
| + CRMath-Format-Politur, Cover-Letter, KI-Disclosure | **8.0** |

8.0 ist der konzeptionelle Deckel: ueber Goldfeld 2002 hinaus traegt das Paper nicht weiter, das ist ehrlich und ausreichend fuer eine Note.

---

## 6. Score-Trajektorie (komplett)

| Step | Score | Hauptbefund |
|------|-------|-------------|
| Step 1 (Konstruktiv 1) | 5.5/10 | §4 vs. §7 Inkonsistenz |
| Step 2 (Experte) | 4.5/10 | Thm 4.2 algebraisch falsch; Conj 4.1 nicht wohldefiniert |
| Step 3 (Konstruktiv 2) | 5.5/10 | E1–E6 Fixes; E6 unfixiert; Strukturprobleme |
| Step 4 (Experte 2) | 6.0/10 | A1: $\lambda_1/\Omega_E$ nur Hinrichtung; Titel + §4-Struktur |
| Step 5 (Widerleger) | adversarial | 4 "toedliche" Angriffe (Goldfeld-Neuheit, Trivialitaet, $\lambda_1$, Marketing) |
| Step 6 (Neutralisierung) | 5.5/10 (vor P1) → 7.5/10 (Soll nach P1–P7) | Step-5-Angriffe groesstenteils entschaerft; interne Inkonsistenz P1 als Pflichtfix |
| **Step 7 (Abschluss)** | **6.5/10** | **Submission-Pfad klar; P2 als einziger blockierender Pflichtfix; Ziel-Score 8.0 nach Politur** |

---

## 7. Schlusswort

Nach 33 Iterationen liegt ein Paper vor, das sich seiner Reichweite bewusst ist: keine abc-Loesung, kein Beweis der Period-Conjecture, sondern eine ehrliche, technisch korrekte und numerisch konkrete Verfeinerung eines bekannten Resultats von Goldfeld. Genau diese Bescheidenheit — kombiniert mit dem unbedingten $\eta$-Bound als publikationsfaehiger Mikro-Beitrag — ist das, was eine **CRMath-Note** im besten Fall leisten soll.

Ein letzter Schliff (P2 + die kosmetischen Fixes), ein praeziser Cover Letter, und das Paper kann eingereicht werden. Der Autor sollte jetzt nicht mehr inhaltlich erweitern, sondern **schliessen**.

— Step 7 abgeschlossen.
