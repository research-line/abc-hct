# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `997`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 218 | raw | 1 | 330 | 83 | killed | 0 | 0.431 |
| sage | 218 | anc | 1 | 330 | 83 | killed | 0 | 0.081 |

## Level 218 / raw / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.009 |
| T_5_minus_2_batch_1 | 256 | 2972 | 580 | 3938 | 83 | 0 | True | 0.055 |

## Level 218 / anc / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.007 |
| T_5_minus_2_batch_1 | 256 | 2972 | 580 | 3938 | 83 | 0 | True | 0.049 |

