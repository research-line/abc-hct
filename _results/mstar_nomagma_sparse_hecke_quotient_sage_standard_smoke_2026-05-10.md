# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 109 | raw | 1 | 110 | 27 | killed | 0 | 0.085 |
| sage | 109 | anc | 1 | 110 | 27 | killed | 0 | 0.014 |
| sage | 218 | raw | 1 | 330 | 83 | killed | 0 | 0.042 |
| sage | 218 | anc | 1 | 330 | 83 | killed | 0 | 0.044 |

## Level 109 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.044 |
| T_5_minus_2 | 110 | 630 | 214 | 926 | 27 | 0 | True | 0.002 |

## Level 109 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.001 |
| T_5_minus_2 | 110 | 630 | 214 | 926 | 27 | 0 | True | 0.001 |

## Level 218 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.004 |
| T_5_minus_2 | 330 | 2170 | 654 | 3136 | 83 | 0 | True | 0.006 |

## Level 218 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.002 |
| T_5_minus_2 | 330 | 2170 | 654 | 3136 | 83 | 0 | True | 0.008 |

