# B2(m): Z/4-Lift-Existenz, sparse Solver (2026-06-11)

## Ergebnis

- Z/4-Lift existiert: **JA**
- Unabhängige Mod-4-Verifikation: **JA**
- Rang über F2: `31678` von `31680`; Kerndimension `2`
- Rechte Seite r: `16778` Einsen in `31680` Zeilen
- Inkonsistente Zeilen: `0`
- Laufzeit Solver: `73.7s`; Gesamt: `75.2s`

## Lesart

Der Test löst exakt das lineare F2-System `M w = (M v mod 4)/2`.
Bei positivem Ergebnis ist `v + 2w` ein direkt verifizierter Z/4-Kernvektor
des symmetrisch gelifteten rc3c-Witness-Systems. Damit ist die offene
Lift-Komponente des Frustrationsgesetzes nicht mehr nur ein Programm,
sondern für den 60168/raw-Zeugen rechnerisch geschlossen.

JSON: `b2_z4_lift_existence_sparse_2026-06-11.json`
