# B2(g): Signierte Spektralanalyse — λ_min auf adversarialen Trägern (2026-06-11)

Träger-Familien: cluster (Mikro-Cluster-Vereinigungen), ball (BFS im 0.2-Graphen um schwerste Kanten), topdeg (höchster gewichteter Grad), consecutive, random. 24 Trials/Zelle.

| s | Familie | λ_min median | λ_min min | δ median | δ max | singulär |
|---|---|---|---|---|---|---|
| 16 | cluster | 0.4000 | 0.3333 | 1.012 | 1.414 | 0/24 |
| 16 | ball | 0.2519 | -0.0000 | 2.215 | 2.878 | 2/24 |
| 16 | topdeg | 1.0000 | 0.7248 | 0.000 | 0.275 | 0/24 |
| 16 | consecutive | 0.3537 | 0.1855 | 0.646 | 0.814 | 0/24 |
| 16 | random | 1.0000 | 1.0000 | 0.000 | 0.000 | 0/24 |
| 32 | cluster | 0.3828 | 0.1686 | 1.289 | 1.612 | 0/24 |
| 32 | ball | 0.2001 | -0.0000 | 2.906 | 3.479 | 2/24 |
| 32 | topdeg | 0.8608 | 0.6486 | 0.139 | 0.351 | 0/24 |
| 32 | consecutive | 0.4174 | 0.1817 | 0.583 | 0.818 | 0/24 |
| 32 | random | 1.0000 | 0.7418 | 0.000 | 0.258 | 0/24 |
| 64 | cluster | 0.3692 | 0.1686 | 1.389 | 1.612 | 0/24 |
| 64 | ball | 0.1601 | -0.0000 | 3.578 | 4.018 | 2/24 |
| 64 | topdeg | 0.7062 | 0.5286 | 0.294 | 0.471 | 0/24 |
| 64 | consecutive | 0.3105 | 0.0776 | 0.690 | 0.922 | 0/24 |
| 64 | random | 1.0000 | 0.5000 | 0.000 | 0.500 | 0/24 |
| 128 | cluster | 0.3633 | 0.2557 | 1.433 | 1.763 | 0/24 |
| 128 | ball | 0.1173 | -0.0000 | 3.817 | 4.293 | 3/24 |
| 128 | topdeg | 0.5982 | 0.4286 | 0.417 | 0.703 | 0/24 |
| 128 | consecutive | 0.2794 | 0.1104 | 0.721 | 1.022 | 0/24 |
| 128 | random | 0.8142 | 0.6619 | 0.186 | 0.338 | 0/24 |
| 256 | cluster | 0.2385 | 0.0000 | 1.493 | 1.805 | 1/24 |
| 256 | ball | 0.0939 | -0.0000 | 3.967 | 4.403 | 4/24 |
| 256 | topdeg | 0.4286 | 0.3251 | 0.711 | 1.050 | 0/24 |
| 256 | consecutive | 0.2762 | 0.0684 | 0.738 | 0.932 | 0/24 |
| 256 | random | 0.7113 | 0.5918 | 0.289 | 0.408 | 0/24 |
| 512 | cluster | 0.1835 | -0.0000 | 1.619 | 2.003 | 3/24 |
| 512 | ball | 0.0621 | -0.0000 | 4.082 | 4.440 | 4/24 |
| 512 | topdeg | 0.3815 | 0.2104 | 0.959 | 1.584 | 0/24 |
| 512 | consecutive | 0.2519 | 0.0971 | 0.802 | 1.100 | 0/24 |
| 512 | random | 0.5918 | 0.4299 | 0.408 | 0.687 | 0/24 |

**Worst-Ball-512-Eigenvektor:** λ_min = -0.0000, Masse Top-10-Spalten 100.0%, Masse auf Mikro-Clustern 100.0%

Laufzeit: 483.2s. JSON: `_results/b2_signed_spectral_adversarial_2026-06-11.json`

## Befund (2026-06-11)

**(g1) Der perkolierte Mittelbereich erzeugt KEINE Kerne.** topdeg
(Gershgorin-Worst-Spalten, Radius bis 15!), consecutive und random sind
über alle s ≤ 512 NIE singulär (λ_min ≥ 0.21 / 0.07 / 0.43). Die
Vorzeichen-Cancellation schlägt die Betragsschranken real — direkter
empirischer Beleg für den v3(iii)-Mechanismus (signiert statt Betrag).

**(g2) Alle beobachteten Singularitäten leben in den Mikro-Clustern.**
Ball-/Cluster-Singularfälle (2–4/24) haben Eigenvektor-Masse 100% auf
Mikro-Clustern, konzentriert auf ≤10 Spalten.

**(g3) VOLLSTÄNDIGE Block-Enumeration (alle 2.634 Mikro-Cluster
diagonalisiert):** Genau **2 singuläre Blöcke**; beide Kernvektoren sind
**antiparallele Spaltenpaare** (φ_38007 = −φ_120130, nnz 3;
φ_71782 = −φ_123997, nnz 1) — verifiziert ‖Ax‖_∞ = 0.0 exakt. KEINE
Fast-Singularität daneben: nächstes Block-λ_min ≥ 0.05 ist leer,
p1 = 0.362, median 0.466; nur 11/2634 Blöcke unter 0.3.
⟹ **Die einzigen dünnen Kernvektoren mit Träger ≤ 6 der gesamten
126.672×126.720-Witness-Matrix sind die 2 trivialen Duplikat-Paare.**
Hauptlemma v3(ii) ist damit auf Block-Ebene VOLLSTÄNDIG erledigt
(unbedingt, durch endliche Rechnung).

**(g4) Offene quantitative Frage (ehrlich):** Ball-λ_min-Median fällt
monoton 0.25 → 0.06 (s = 16 → 512) ohne erkennbares Plateau. Ob
Fast-Kerne mit Träger 10³–10⁴ über viele Blöcke + Mittelbereichskanten
existieren, ist offen — nächster Messschritt: Skalierungs-Fit
λ_min(s) ~ s^(−α) und Eigenvektor-Lokalisierung der flachsten Richtungen.
