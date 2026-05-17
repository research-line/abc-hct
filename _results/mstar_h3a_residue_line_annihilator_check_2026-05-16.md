# H3a Residue-Line Annihilator Check

This diagnostic tests the naive finite-support candidate obtained from
the split-last repair row itself.  A true left residue functional must
annihilate all source rows and pair nontrivially with the repair row.

## 80224/raw

```text
case:                       _results\h3a_residue_line_witness_80224_raw_standard_2026-05-16\N80224_raw_sign1_splitlast
q:                          3863
source rows:                31679
functional support:         [0, 1, 2, 3, 4, 5]
functional coefficients:    [2, -1, -1, -1, 1, -1]
source nonzero pairings:    16
source annihilated:         False
repair pairing signed:      9
repair pairing nonzero:     True
```

First nonzero source pairings:

| row_id | stage | symbol | dot |
|---|---|---:|---:|
| `manin_T_relations_after_SI/4` | `manin_T_relations_after_SI` | 7 | 1 |
| `T_5_minus_2_batch_1/0` | `T_5_minus_2_batch_1` | 0 | -8 |
| `T_5_minus_2_batch_1/1` | `T_5_minus_2_batch_1` | 1 | 3 |
| `T_5_minus_2_batch_1/2` | `T_5_minus_2_batch_1` | 2 | 1 |
| `T_5_minus_2_batch_1/3` | `T_5_minus_2_batch_1` | 3 | -2 |
| `T_5_minus_2_batch_1/4` | `T_5_minus_2_batch_1` | 4 | -2 |
| `T_5_minus_2_batch_1/5` | `T_5_minus_2_batch_1` | 5 | -2 |
| `T_5_minus_2_batch_1/6` | `T_5_minus_2_batch_1` | 6 | -2 |

## 80224/anc

```text
case:                       _results\h3a_residue_line_witness_80224_anc_standard_2026-05-16\N80224_anc_sign1_splitlast
q:                          3863
source rows:                31679
functional support:         [0, 1, 2, 3, 4, 5]
functional coefficients:    [2, -1, -1, -1, 1, -1]
source nonzero pairings:    16
source annihilated:         False
repair pairing signed:      9
repair pairing nonzero:     True
```

First nonzero source pairings:

| row_id | stage | symbol | dot |
|---|---|---:|---:|
| `manin_T_relations_after_SI/4` | `manin_T_relations_after_SI` | 7 | 1 |
| `T_5_minus_2_batch_1/0` | `T_5_minus_2_batch_1` | 0 | -8 |
| `T_5_minus_2_batch_1/1` | `T_5_minus_2_batch_1` | 1 | 3 |
| `T_5_minus_2_batch_1/2` | `T_5_minus_2_batch_1` | 2 | 1 |
| `T_5_minus_2_batch_1/3` | `T_5_minus_2_batch_1` | 3 | -2 |
| `T_5_minus_2_batch_1/4` | `T_5_minus_2_batch_1` | 4 | -2 |
| `T_5_minus_2_batch_1/5` | `T_5_minus_2_batch_1` | 5 | -2 |
| `T_5_minus_2_batch_1/6` | `T_5_minus_2_batch_1` | 6 | -2 |

## 120336/raw

```text
case:                       _results\h3a_residue_line_witness_120336_raw_standard_2026-05-16\N120336_raw_sign1_splitlast
q:                          3863
source rows:                63359
functional support:         [0, 1, 2, 3, 4, 5]
functional coefficients:    [2, -1, -1, -1, -1, -1]
source nonzero pairings:    16
source annihilated:         False
repair pairing signed:      9
repair pairing nonzero:     True
```

First nonzero source pairings:

| row_id | stage | symbol | dot |
|---|---|---:|---:|
| `manin_T_relations_after_SI/4` | `manin_T_relations_after_SI` | 7 | 1 |
| `T_5_minus_2_batch_1/0` | `T_5_minus_2_batch_1` | 0 | -8 |
| `T_5_minus_2_batch_1/1` | `T_5_minus_2_batch_1` | 1 | 3 |
| `T_5_minus_2_batch_1/2` | `T_5_minus_2_batch_1` | 2 | 1 |
| `T_5_minus_2_batch_1/3` | `T_5_minus_2_batch_1` | 3 | -2 |
| `T_5_minus_2_batch_1/4` | `T_5_minus_2_batch_1` | 4 | -2 |
| `T_5_minus_2_batch_1/5` | `T_5_minus_2_batch_1` | 5 | -2 |
| `T_5_minus_2_batch_1/6` | `T_5_minus_2_batch_1` | 6 | -2 |

## Interpretation

If `source_annihilated` is false, the compact six-term repair row is not
itself the dual residue functional.  It remains useful as the quotient
residue vector, but CFR-3.4 must use the dual functional obtained after
S/I/T-Manin reduction, not a raw dot product against prefix columns.
