# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 109 | raw | 1 | 110 | 27 | killed | 0 | 0.041 |
| sage | 109 | anc | 1 | 110 | 27 | killed | 0 | 0.007 |
| sage | 218 | raw | 1 | 330 | 83 | killed | 0 | 0.028 |
| sage | 218 | anc | 1 | 330 | 83 | killed | 0 | 0.025 |

## Level 109 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.026 |
| T_5_minus_2 | 110 | 982 | 214 | 1278 | 27 | 0 | True | 0.001 |

## Level 109 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 104 | 296 | 104 | 296 | 18 | 9 | False | 0.000 |
| T_5_minus_2 | 110 | 982 | 214 | 1278 | 27 | 0 | True | 0.001 |

## Level 218 / raw / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.001 |
| T_5_minus_2 | 330 | 3838 | 654 | 4804 | 83 | 0 | True | 0.005 |

## Level 218 / anc / backend sage

Traces: `{'5': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.001 |
| T_5_minus_2 | 330 | 3838 | 654 | 4804 | 83 | 0 | True | 0.004 |

