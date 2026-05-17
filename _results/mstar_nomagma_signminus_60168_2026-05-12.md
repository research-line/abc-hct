# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 60168 | raw | -1 | 126720 | 31680 | killed | 0 | 1448.934 |
| sage | 60168 | anc | -1 | 126720 | 31680 | killed | 0 | 1487.432 |

## Level 60168 / raw / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 126720 | 379974 | 126720 | 379974 | 21135 | 10545 | False | 4.119 |
| T_5_minus_2_batch_1 | 999 | 6989 | 127719 | 386963 | 22134 | 9546 | False | 2.861 |
| T_5_minus_2_batch_2 | 1000 | 7000 | 128719 | 393963 | 23134 | 8546 | False | 5.599 |
| T_5_minus_2_batch_3 | 1000 | 6999 | 129719 | 400962 | 24134 | 7546 | False | 0.454 |
| T_5_minus_2_batch_4 | 1000 | 7000 | 130719 | 407962 | 25134 | 6546 | False | 3.420 |
| T_5_minus_2_batch_5 | 1000 | 6999 | 131719 | 414961 | 26134 | 5546 | False | 29.539 |
| T_5_minus_2_batch_6 | 1000 | 6997 | 132719 | 421958 | 27134 | 4546 | False | 125.922 |
| T_5_minus_2_batch_7 | 1000 | 6998 | 133719 | 428956 | 28134 | 3546 | False | 187.592 |
| T_5_minus_2_batch_8 | 1000 | 6999 | 134719 | 435955 | 29134 | 2546 | False | 208.415 |
| T_5_minus_2_batch_9 | 1000 | 6999 | 135719 | 442954 | 30134 | 1546 | False | 261.329 |
| T_5_minus_2_batch_10 | 1000 | 6999 | 136719 | 449953 | 31134 | 546 | False | 292.075 |
| T_5_minus_2_batch_11 | 1000 | 6996 | 137719 | 456949 | 31680 | 0 | True | 326.531 |

## Level 60168 / anc / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 126720 | 379974 | 126720 | 379974 | 21135 | 10545 | False | 4.095 |
| T_5_minus_2_batch_1 | 999 | 6989 | 127719 | 386963 | 22134 | 9546 | False | 2.880 |
| T_5_minus_2_batch_2 | 1000 | 7000 | 128719 | 393963 | 23134 | 8546 | False | 5.587 |
| T_5_minus_2_batch_3 | 1000 | 6999 | 129719 | 400962 | 24134 | 7546 | False | 0.455 |
| T_5_minus_2_batch_4 | 1000 | 7000 | 130719 | 407962 | 25134 | 6546 | False | 3.426 |
| T_5_minus_2_batch_5 | 1000 | 6999 | 131719 | 414961 | 26134 | 5546 | False | 33.489 |
| T_5_minus_2_batch_6 | 1000 | 6997 | 132719 | 421958 | 27134 | 4546 | False | 137.342 |
| T_5_minus_2_batch_7 | 1000 | 6998 | 133719 | 428956 | 28134 | 3546 | False | 193.132 |
| T_5_minus_2_batch_8 | 1000 | 6999 | 134719 | 435955 | 29134 | 2546 | False | 220.230 |
| T_5_minus_2_batch_9 | 1000 | 6999 | 135719 | 442954 | 30134 | 1546 | False | 265.224 |
| T_5_minus_2_batch_10 | 1000 | 6999 | 136719 | 449953 | 31134 | 546 | False | 294.504 |
| T_5_minus_2_batch_11 | 1000 | 6996 | 137719 | 456949 | 31680 | 0 | True | 326.125 |

