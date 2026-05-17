# H3a Residue-Line Functional Diagnostic

Decodes the T7 repair row of each splitlast witness as a finite-
support functional on the affine cusp-fan prefix.  Convention:
column 0 = `e_inf = (0,1)`, column k+1 = `e_k = (1,k)`.

## 80224/raw

```text
witness:               _results\h3a_residue_line_witness_80224_raw_standard_2026-05-16\N80224_raw_sign1_splitlast
q:                     3863
row id:                T_7_minus_0_batch_1/1
hecke prime / ap:      7 / 0
manin symbol index:    1
support size:          6
support columns:       [0, 1, 2, 3, 4, 5]
support symbols:       ['e_inf=(0,1)', 'e_0=(1,0)', 'e_1=(1,1)', 'e_2=(1,2)', 'e_3=(1,3)', 'e_4=(1,4)']
coefficients (mod q):  [2, 3862, 3862, 3862, 1, 3862]
coefficients (signed): [2, -1, -1, -1, 1, -1]
consecutive prefix:    True
compact prefix block:  True
leading on e_inf=2:    True
```

## 80224/anc

```text
witness:               _results\h3a_residue_line_witness_80224_anc_standard_2026-05-16\N80224_anc_sign1_splitlast
q:                     3863
row id:                T_7_minus_0_batch_1/1
hecke prime / ap:      7 / 0
manin symbol index:    1
support size:          6
support columns:       [0, 1, 2, 3, 4, 5]
support symbols:       ['e_inf=(0,1)', 'e_0=(1,0)', 'e_1=(1,1)', 'e_2=(1,2)', 'e_3=(1,3)', 'e_4=(1,4)']
coefficients (mod q):  [2, 3862, 3862, 3862, 1, 3862]
coefficients (signed): [2, -1, -1, -1, 1, -1]
consecutive prefix:    True
compact prefix block:  True
leading on e_inf=2:    True
```

## 120336/raw

```text
witness:               _results\h3a_residue_line_witness_120336_raw_standard_2026-05-16\N120336_raw_sign1_splitlast
q:                     3863
row id:                T_7_minus_0_batch_1/1
hecke prime / ap:      7 / 0
manin symbol index:    1
support size:          6
support columns:       [0, 1, 2, 3, 4, 5]
support symbols:       ['e_inf=(0,1)', 'e_0=(1,0)', 'e_1=(1,1)', 'e_2=(1,2)', 'e_3=(1,3)', 'e_4=(1,4)']
coefficients (mod q):  [2, 3862, 3862, 3862, 3862, 3862]
coefficients (signed): [2, -1, -1, -1, -1, -1]
consecutive prefix:    True
compact prefix block:  True
leading on e_inf=2:    True
```

## Cross-case comparison

```text
cases compared:        3
consistent support:    True
common support:        [0, 1, 2, 3, 4, 5]
consistent signature:  False
signatures (per case):
  80224/raw: [2, -1, -1, -1, 1, -1]
  80224/anc: [2, -1, -1, -1, 1, -1]
  120336/raw: [2, -1, -1, -1, -1, -1]
```

## Interpretation

If support is the consecutive prefix `[0, 1, ..., k]` and the leading
coefficient on `e_inf` equals 2, the repair row is consistent with a
canonical Boundary/Cusp functional `phi` whose value on `e_inf` is the
Eisenstein/cuspidal weight `T5-a5` contributes via `(p+1-a_p)`.
Any per-level variation visible only in higher-index coefficients then
reflects the T-Manin 3-term reduction acting at the affine prefix tail,
and is fixed by the canonical Manin S/I/T-relations at that level.