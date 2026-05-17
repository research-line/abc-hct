# H3a pi_N Projection from Witness

Builds `pi_N : V_SI -> V_SI/<T-Manin>` from the T-Manin rows already
present in the split-last witness.

```text
case:                      _results\h3a_wait_postprocess_smoke_n109_2026-05-16\N109_raw_sign1_splitlast
level/mode/q:              109 / raw / 3863
ncols in V_SI:             27
T rows / T rank:           18 / 18
quotient dim:              9
free columns:              [0, 1, 2, 3, 4, 5, 6, 7, 16]
pivot columns:             [8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
N=109 matches Sage dim 9:  True
Hecke source rows:         8
rank pi(Hecke source):     8
rank plus pi(repair):      9
repair adds rank:          True
```

## Projected repair row

```text
{'support_size': 7, 'support': [1, 2, 4, 5, 6, 7, 8], 'coefficients_signed': [1931, -1, -2, 1, -3, -1, 3], 'truncated': False}
```

## Induced dual phi on quotient

```text
induced support:              [6, 7, 8]
induced coefficients signed:  [1, -1054, -1403]
T-row nonzero pairings:       0
Hecke-source nonzero pairings:0
repair pairing signed:        705
repair pairing nonzero:       True
```

## Interpretation

For N=109 the T-Manin rows reconstruct the missing basis bridge from
the RC3 S/I column space to a 9-dimensional quotient.  This does not
yet identify Sage's modular-symbol basis, but it supplies the first
half of `pi_N` and turns the Loop-315 blocker into a concrete finite
linear algebra object.
