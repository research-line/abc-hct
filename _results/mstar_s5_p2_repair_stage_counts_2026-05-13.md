# S5 p=2 Repair Stage Counts

Case: `60168/raw`, fixed `GF(3863)` quotient, repair prime `2`.

Source file:

```text
_results/s5_repair_witness_60168_raw_p2_2026-05-13/N60168_raw_p2_sign1/repair_rows.jsonl
```

## Independent Rows By Stage

| Stage | Independent rows |
|---|---:|
| `manin_T_relations_after_SI` | 21104 |
| `T_5_minus_2_batch_1` | 999 |
| `T_5_minus_2_batch_2` | 1000 |
| `T_5_minus_2_batch_3` | 1000 |
| `T_5_minus_2_batch_4` | 1000 |
| `T_5_minus_2_batch_5` | 1000 |
| `T_5_minus_2_batch_6` | 1000 |
| `T_5_minus_2_batch_7` | 1000 |
| `T_5_minus_2_batch_8` | 1000 |
| `T_5_minus_2_batch_9` | 1000 |
| `T_5_minus_2_batch_10` | 1000 |
| `T_5_minus_2_batch_11` | 575 |
| `T_5_minus_2_batch_12` | 0 |
| `T_5_minus_2_batch_13` | 1 |
| `T_7_minus_0_batch_1` | 1 |

Total: `31680`.

## Final T7 Row

The only exported T7 row is also the final rank-increasing row:

```json
{"row":[[0,2],[1,3862],[2,3862],[3,3862],[4,3862],[5,3862]],"row_id":"T_7_minus_0_batch_1/1","row_line_sha256":"a7c9b47d334f80801465ad60f61304c2e9ff7f4991419087c25105b801bbdabf","stage":"T_7_minus_0_batch_1","stage_row_index":1}
```

Under symmetric lift and reduction modulo `2`, this row has support

```text
{1,2,3,4,5}
```

because `3862` represents `-1`, while the coefficient `2` in column `0`
vanishes modulo `2`.

## Diagnostic Meaning

Before T7, the repair witness reaches rank `31679`, leaving a one-dimensional
mod-2 nullity. The first T7 batch contributes exactly one independent row in
this witness and removes that final nullity.

This is a coordinate-level diagnostic, not yet an invariant theorem. It points
to a sharper S5-U1 question:

```text
Is the p=2 defect a single parity/boundary class killed by the first T7
relation, and can that be formulated as a Smith-/mapping-cone statement?
```

