# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `auto`
q: `3863`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 192 | raw | 1 | 384 | 96 | survivor_candidate | 1 | 0.346 |

## Level 192 / raw / backend sage

Traces: `{'5': 2, '7': 0, '11': -4, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 360 | 1044 | 360 | 1044 | 60 | 36 | False | 0.003 |
| T_5_minus_2_batch_1 | 384 | 4052 | 744 | 5096 | 88 | 8 | False | 0.019 |
| T_7_minus_0_batch_1 | 384 | 5292 | 1128 | 10388 | 92 | 4 | False | 0.030 |
| T_11_minus_-4_batch_1 | 384 | 8696 | 1512 | 19084 | 95 | 1 | False | 0.041 |
| T_13_minus_2_batch_1 | 384 | 10152 | 1896 | 29236 | 95 | 1 | False | 0.043 |

