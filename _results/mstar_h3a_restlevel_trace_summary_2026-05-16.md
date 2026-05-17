# H3a Restlevel Trace Summary

This table summarizes the existing q=3863 sparse trace-closure runs.

| Level | Mode | q | cols | qdim after Manin | before kill | kill stage | final qdim | status |
|---:|---|---:|---:|---:|---|---|---:|---|
| 60168 | `anc` | 3863 | 31680 | 10576 | `T_5_minus_2_batch_12 / qdim 1` | `T_5_minus_2_batch_13` | 0 | `killed` |
| 60168 | `raw` | 3863 | 31680 | 10576 | `T_5_minus_2_batch_12 / qdim 1` | `T_5_minus_2_batch_13` | 0 | `killed` |
| 80224 | `anc` | 3863 | 31680 | 10568 | `T_5_minus_2_batch_14 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |
| 80224 | `raw` | 3863 | 31680 | 10568 | `T_5_minus_2_batch_14 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |
| 120336 | `anc` | 3863 | 63360 | 21136 | `T_5_minus_2_batch_24 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |
| 120336 | `raw` | 3863 | 63360 | 21136 | `T_5_minus_2_batch_24 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |
| 240672 | `anc` | 3863 | 126720 | 42256 | `T_5_minus_2_batch_48 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |
| 240672 | `raw` | 3863 | 126720 | 42256 | `T_5_minus_2_batch_48 / qdim 1` | `T_7_minus_0_batch_1` | 0 | `killed` |

## Reading

All eight mapped restlevel/mode cases are killed at q=3863 by canonical Trace rows.  For the larger levels the pattern is especially rigid: a long T5 ladder leaves a one-dimensional residue and the first T7 batch kills it.  This is a q=3863 local trace-closure certificate, not yet a uniform all-prime Fitting theorem.
