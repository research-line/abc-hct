# H3a Manin Intersection Pairing Wrapper

Case: `_results/h3a_wait_postprocess_smoke_n109_2026-05-16/N109_raw_sign1_splitlast`
N: `109`, q: `3863`, witness ncols: `27`, Sage dim: `9`
Bases match (ncols == sage_dim): `False`
Pairing method: `None`
Pairing error: `None`

## Ergebnis

`B_N * r_N` wurde bewusst nicht verglichen.

Der Witness lebt im RC3-Spaltenraum nach S/I-Quotient, während
`ModularSymbols(Gamma0(N),2,sign=1)` in Sage bereits vollständig
T-Manin-reduziert ist. Es fehlt also die Projektionsmatrix vom
Witness-Spaltenraum in die Sage-ModularSymbols-Koordinaten.

## Nächster Schritt

Die Basisbrücke konstruieren: RC3-Spalte -> Manin-Symbol-Repräsentant
-> Sage-ModularSymbols-Koordinate. Erst danach ist der Vergleich
`phi_N = B_N(r_N,-)` aussagekräftig.
