# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 109 | raw | 1 | 110 | 27 | killed | 0 | 0.015 |
| sage | 109 | anc | 1 | 110 | 27 | killed | 0 | 0.004 |
| sage | 218 | raw | 1 | 330 | 83 | killed | 0 | 0.012 |
| sage | 218 | anc | 1 | 330 | 83 | killed | 0 | 0.015 |

## Level 109 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.002 |
| T_5_minus_2_batch_1 | 20 | 104 | 124 | 400 | 27 | 0 | True | 0.000 |

## Level 109 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.001 |
| T_5_minus_2_batch_1 | 20 | 104 | 124 | 400 | 27 | 0 | True | 0.000 |

## Level 218 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.005 |
| T_5_minus_2_batch_1 | 20 | 118 | 344 | 1084 | 74 | 9 | False | 0.001 |
| T_5_minus_2_batch_2 | 20 | 134 | 364 | 1218 | 83 | 0 | True | 0.002 |

## Level 218 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.006 |
| T_5_minus_2_batch_1 | 20 | 118 | 344 | 1084 | 74 | 9 | False | 0.001 |
| T_5_minus_2_batch_2 | 20 | 134 | 364 | 1218 | 83 | 0 | True | 0.002 |

