# H3a pi_N to Sage Basis Wrapper

Compares the witness T-Manin quotient coordinates with Sage's
`ModularSymbols(Gamma0(N),2,sign=1)` basis.

```text
N/sign/q:                    109 / 1 / 3863
V_SI columns:                27
Sage dimension:              9
free columns from pi_N:       [0, 1, 2, 3, 4, 5, 6, 7, 16]
free-to-Sage rank:           9
free-to-Sage isomorphism:    True
missing V_SI columns:        []
S/I consistency errors:      0
T rows nonzero in Sage:      0
Hecke rank in Sage:          8
Hecke+repair rank in Sage:   9
repair adds Sage rank:       True
pairing tests available:     True
```

## Repair in Sage basis

```text
[[1, -3], [2, -3], [3, 2], [4, -1], [5, -5], [6, -1], [7, 4], [8, -4]]
```

## Induced phi in Sage basis

```text
[[1, 1], [2, 1403], [5, -1054], [7, -1054]]
```

## Pairing tests

```text
{'available': True, 'full_sign0_dim': 17, 'plus_dim': 9, 'minus_dim': 8, 'Bpp_rank': 8, 'Bpq_rank': 7, 'Bqq_rank': 8, 'Bal_rank': 9, 'Bal_determinant_signed': 26, 'phi_on_hecke_source_nonzero': [], 'phi_on_repair_sage_signed': 705, 'phi_repair_pairing_signed': 705, 'phi_on_u_right_signed': 722, 'phi_on_u_left_signed': 722, 'alpha_right_from_phi_signed': -925, 'alpha_left_from_phi_signed': -925, 'phi_vs_repair_Bpp_right': {'consistent': False, 'scale': '1932', 'mismatches': [{'i': 2, 'a': 1403, 'b': -7, 'scale': '2007', 'expected': '1932'}, {'i': 3, 'a': 0, 'b': 3, 'kind': 'zero-mismatch'}, {'i': 4, 'a': 0, 'b': -5, 'kind': 'zero-mismatch'}, {'i': 5, 'a': -1054, 'b': -9, 'scale': '1834', 'expected': '1932'}, {'i': 6, 'a': 0, 'b': 3, 'kind': 'zero-mismatch'}, {'i': 7, 'a': -1054, 'b': 7, 'scale': '1505', 'expected': '1932'}, {'i': 8, 'a': 0, 'b': -5, 'kind': 'zero-mismatch'}]}, 'phi_vs_repair_Bpp_left': {'consistent': False, 'scale': '492', 'mismatches': [{'i': 1, 'a': 1, 'b': 0, 'kind': 'zero-mismatch'}, {'i': 4, 'a': 0, 'b': -4, 'kind': 'zero-mismatch'}, {'i': 5, 'a': -1054, 'b': -14, 'scale': '1179', 'expected': '492'}, {'i': 6, 'a': 0, 'b': 5, 'kind': 'zero-mismatch'}, {'i': 7, 'a': -1054, 'b': 7, 'scale': '1505', 'expected': '492'}, {'i': 8, 'a': 0, 'b': -1, 'kind': 'zero-mismatch'}]}, 'phi_vs_repair_Bal_right': {'consistent': False, 'scale': '1', 'mismatches': [{'i': 2, 'a': 1403, 'b': 0, 'kind': 'zero-mismatch'}, {'i': 3, 'a': 0, 'b': 40, 'kind': 'zero-mismatch'}, {'i': 4, 'a': 0, 'b': 41, 'kind': 'zero-mismatch'}, {'i': 5, 'a': -1054, 'b': 43, 'scale': '245', 'expected': '1'}, {'i': 6, 'a': 0, 'b': 1, 'kind': 'zero-mismatch'}, {'i': 7, 'a': -1054, 'b': -19, 'scale': '1682', 'expected': '1'}, {'i': 8, 'a': 0, 'b': -11, 'kind': 'zero-mismatch'}]}, 'phi_vs_repair_Bal_left': {'consistent': False, 'scale': '1931', 'mismatches': [{'i': 2, 'a': 1403, 'b': 6, 'scale': '3453', 'expected': '1931'}, {'i': 3, 'a': 0, 'b': 4, 'kind': 'zero-mismatch'}, {'i': 4, 'a': 0, 'b': 23, 'kind': 'zero-mismatch'}, {'i': 5, 'a': -1054, 'b': 32, 'scale': '2140', 'expected': '1931'}, {'i': 6, 'a': 0, 'b': -19, 'kind': 'zero-mismatch'}, {'i': 7, 'a': -1054, 'b': -9, 'scale': '1834', 'expected': '1931'}, {'i': 8, 'a': 0, 'b': 2, 'kind': 'zero-mismatch'}]}, 'al_preimage_right_entries_signed': [[1, -1596], [2, -1657], [3, 1], [4, -1806], [5, -488], [6, 1612], [7, 1685], [8, 1117]], 'al_preimage_left_entries_signed': [[1, -979], [2, -703], [3, 365], [4, -1047], [5, -186], [6, 1775], [7, 1433], [8, -1555]], 'al_defect_right_entries_signed': [[1, -1593], [2, -1654], [3, -1], [4, -1805], [5, -483], [6, 1613], [7, 1681], [8, 1121]], 'al_defect_left_entries_signed': [[1, -976], [2, -700], [3, 363], [4, -1046], [5, -181], [6, 1776], [7, 1429], [8, -1551]], 'al_preimage_right_source_repair_decomposition': {'available': True, 'source_repair_rank': 9, 'repair_coefficient_mod_q': 2938, 'repair_coefficient_signed': -925, 'same_projective_restline_as_repair': True, 'source_coefficients_signed': [[1, 34], [2, 1279], [3, -455], [4, 378], [5, -1868], [6, -988], [7, 1407]], 'normalized_minus_repair_entries_signed': [[1, 1291], [2, 1408], [3, 946], [4, -778], [5, 941], [6, -1571], [7, -1906], [8, 458]]}, 'al_preimage_left_source_repair_decomposition': {'available': True, 'source_repair_rank': 9, 'repair_coefficient_mod_q': 2938, 'repair_coefficient_signed': -925, 'same_projective_restline_as_repair': True, 'source_coefficients_signed': [[1, 1239], [2, 1469], [3, -1293], [4, -91], [5, 1394], [6, 1644], [7, 960]], 'normalized_minus_repair_entries_signed': [[1, -969], [2, 1858], [3, -1652], [4, 236], [5, 1375], [6, -1567], [7, -1296], [8, 1530]]}}
```

## AL-corrected primal candidate

```text
Bal rank:             9
Bal determinant:      26
phi on Hecke source:  []
phi(repair):          705
phi(u_right):         722
alpha_right via phi:  -925
phi(u_left):          722
alpha_left via phi:   -925
repair * Bal matches phi:    False
repair * Bal^T matches phi:  False
u_right = phi * Bal^-1:      [[1, -1596], [2, -1657], [3, 1], [4, -1806], [5, -488], [6, 1612], [7, 1685], [8, 1117]]
delta_right = u_right-repair:[[1, -1593], [2, -1654], [3, -1], [4, -1805], [5, -483], [6, 1613], [7, 1681], [8, 1121]]
u_left = phi * (Bal^T)^-1:   [[1, -979], [2, -703], [3, 365], [4, -1047], [5, -186], [6, 1775], [7, 1433], [8, -1555]]
delta_left = u_left-repair:  [[1, -976], [2, -700], [3, 363], [4, -1046], [5, -181], [6, 1776], [7, 1429], [8, -1551]]
u_right over Source+repair:  {'available': True, 'source_repair_rank': 9, 'repair_coefficient_mod_q': 2938, 'repair_coefficient_signed': -925, 'same_projective_restline_as_repair': True, 'source_coefficients_signed': [[1, 34], [2, 1279], [3, -455], [4, 378], [5, -1868], [6, -988], [7, 1407]], 'normalized_minus_repair_entries_signed': [[1, 1291], [2, 1408], [3, 946], [4, -778], [5, 941], [6, -1571], [7, -1906], [8, 458]]}
u_left over Source+repair:   {'available': True, 'source_repair_rank': 9, 'repair_coefficient_mod_q': 2938, 'repair_coefficient_signed': -925, 'same_projective_restline_as_repair': True, 'source_coefficients_signed': [[1, 1239], [2, 1469], [3, -1293], [4, -91], [5, 1394], [6, 1644], [7, 960]], 'normalized_minus_repair_entries_signed': [[1, -969], [2, 1858], [3, -1652], [4, 236], [5, 1375], [6, -1567], [7, -1296], [8, 1530]]}
```

## Interpretation

If `free-to-Sage isomorphism` is true and the T rows vanish in Sage,
the operational basis bridge `pi_N : V_SI -> M^+` is verified for this
small level.  In this smoke case the Atkin-Lehner-twisted plus-pairing
is nondegenerate, but the raw repair vector is not the vector dual to
phi.  The next object is therefore the AL-corrected primal candidate
`u_N` and the defect `delta_N = u_N-r_N`.
