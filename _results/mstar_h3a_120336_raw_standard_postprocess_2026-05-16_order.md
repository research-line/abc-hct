# H3a Residue-Line Order Certificate

Case: `N120336_raw_sign1_splitlast`.
Level: `120336`, mode: `raw`, q: `3863`.
Columns: `63360`.

## Split

Original source rows: `63360`.
Source prefix rows: `63359`.
Repair row: `T_7_minus_0_batch_1/1`.
Repair stage: `T_7_minus_0_batch_1`.

## Checks

| Check | Passed |
|---|---|
| `original_full_count_equals_ncols` | `True` |
| `source_prefix_count_equals_ncols_minus_one` | `True` |
| `single_repair_row` | `True` |
| `mixed_count_equals_ncols` | `True` |
| `split_rule_is_final_or_specified` | `True` |
| `repair_stage_matches_expectation` | `True` |

Certified: `True`.

## Interpretation

Because the source witness is an ordered list of rank-increasing rows over q, the first n-1 rows have rank n-1 and the final repair row raises the rank to n. Thus the repair row is nonzero on the one-dimensional row-cokernel residue.
