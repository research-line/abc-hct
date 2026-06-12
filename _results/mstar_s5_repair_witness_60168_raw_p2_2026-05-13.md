# S5 Fixed-Quotient Full Relation Rank

Level `60168`, mode `raw`, q `3863`.
Columns in fixed quotient: `31680`.

## Stage Reconstruction

| stage | rows | nnz | transcript match | seconds |
|---|---:|---:|---|---:|
| manin_T_relations_after_SI | 126624 | 379872 | True | 1.421 |
| T_5_minus_2_batch_1 | 1000 | 6984 | True | 0.005 |
| T_5_minus_2_batch_2 | 1000 | 6997 | True | 0.005 |
| T_5_minus_2_batch_3 | 1000 | 6997 | True | 0.005 |
| T_5_minus_2_batch_4 | 1000 | 6997 | True | 0.005 |
| T_5_minus_2_batch_5 | 1000 | 6994 | True | 0.005 |
| T_5_minus_2_batch_6 | 1000 | 6989 | True | 0.005 |
| T_5_minus_2_batch_7 | 1000 | 6996 | True | 0.005 |
| T_5_minus_2_batch_8 | 1000 | 6996 | True | 0.005 |
| T_5_minus_2_batch_9 | 1000 | 6997 | True | 0.005 |
| T_5_minus_2_batch_10 | 1000 | 6993 | True | 0.005 |
| T_5_minus_2_batch_11 | 1000 | 6987 | True | 0.006 |
| T_5_minus_2_batch_12 | 1000 | 6997 | True | 0.005 |
| T_5_minus_2_batch_13 | 1000 | 6995 | True | 0.006 |
| T_7_minus_0_batch_1 | 1000 | 7985 | not checked | 0.006 |

## Ranks

| prime | source rank | full rank | repaired? | seconds source | seconds full |
|---:|---:|---:|---|---:|---:|
| 2 | 31678 | 31680 | True | 14.335 | 81.166 |

## Repair Witness

Directory: `_results/s5_repair_witness_60168_raw_p2_2026-05-13/N60168_raw_p2_sign1`.
Prime: `2`.
Rank: `31680` / `31680`.
Rows exported: `31680`.


## Interpretation

A repaired result means the full reconstructed row set has full rank modulo
the test prime in the same GF(3863)-quotient coordinates, even if the
exported source minor had dropped rank modulo that prime.
