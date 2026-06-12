# S5 Sparse Basis Deletion Pairs

Case: `N60168_raw_source_plus_p2repair_sign1`.
Rows: `31682`, columns: `31680`.

| prime | pivot | order | rank | deleted count | deleted row ids | seconds |
|---:|---|---|---:|---:|---|---:|
| 2 | max | original | 31680 | 2 | `['T_5_minus_2_batch_1/0', 'T_5_minus_2_batch_11/574']` | 4497.345 |

## Interpretation

Each full-rank run selects `ncols` independent rows.  Since the mixed
witness has `ncols + 2` rows, the complement is a deletion pair for
a square maximal minor over that test prime.  Common deletion pairs
across primes are candidates for a single determinant witness.
