# B2(l): det-Ĝ-Inventar aller Mikro-Cluster-Blöcke, 60168 (2026-06-11)

Exakt-ganzzahlige Gram-Determinanten det Ĝ_S = det(A_S^T A_S) ∈ ℤ für alle
3.322 Mikro-Cluster-Blöcke (w ≥ 0.5, Größe ≤ 5) des rc3c-Witness 60168;
Primfaktorisierung via sympy. Script: Inline (Session 2026-06-11), JSON:
`b2_det_gram_inventory_60168_2026-06-11.json`.

## Befund

**(l1) det = 0: NULL Blöcke.** Das (i)-Resultat „keine dünnen Kerne mit
Träger ≤ 5" ist damit EXAKT-ARITHMETISCH etabliert (alle det ≥ 1), nicht
nur float-numerisch.

**(l2) Vollständiges Ausnahme-q-Inventar (q² | det Ĝ_S):**
**{2: 3.069 Blöcke, 3: 776, 19: 2}** — sonst NICHTS. Per Cauchy–Binet-
Brücke (Note §7.3): Ein F_q-Rangdefekt eines Blocks erfordert q² | det.
⟹ Für ALLE q ∉ {2, 3, 19} ist JEDER Mikro-Cluster-Block über F_q
vollrangig — BEWIESEN durch endliche Rechnung.
- **q = 3863 und q = 997 (die HCT-Witness-Primes) erscheinen NIRGENDS**,
  auch nicht in erster Potenz — die Witness-Wahl ist block-sauber.
- 2 und 3 sind exakt die bad-reduction-Primes (N = 60168 = 2³·3·23·109) —
  die „bekannten Verdächtigen" der Eisenstein-/Torsions-Theorie.
- 19² nur in 2 Blöcken (det = 722 = 2·19²) — isolierter Sonderfall,
  Kandidat für Einzelfall-Inspektion.

**(l3) det-Quantisierung:** Werte stark konzentriert auf {2,3,5}-glatte
Zahlen: det = 12 (1.476×), 36 (769×), 40 (707×) decken 89% ab. Die
flachsten Blöcke (λ_min < 0.3, 22 Stück) haben kleine dets (2–8.028) mit
gelegentlichen größeren Primfaktoren (839, 587, 223, 131, 101, 103) in
ERSTER Potenz — erste Potenz ist für Rangdefekt unschädlich.

## Fitting-Lesart (C1)

Das Mikro-Cluster-Niveau des Fitting-Tests ist BESTANDEN: Die
Elementarteiler-Primes der Struktur-Blöcke sind {2, 3} (+ Ausreißer 19²),
keine exotischen Kongruenzprimes. CR-2b-Escape über Mikro-Cluster ist
für q ∉ {2,3,19} block-weise unmöglich (exakt); für q ∈ {2,3} greifen
die bekannten S5-/Paritäts-Zertifikate (vgl. Frustrations-Gesetz,
`MG_b2_p2_frustration_law_2026-06-11.md`).
