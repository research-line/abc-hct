# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `7919`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 218 | raw | 1 | 330 | 83 | killed | 0 | 0.444 |
| sage | 218 | anc | 1 | 330 | 83 | killed | 0 | 0.217 |

## Level 218 / raw / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.027 |
| T_5_minus_2_batch_1 | 256 | 2972 | 580 | 3938 | 83 | 0 | True | 0.107 |

## Level 218 / anc / backend sage

Traces: `{'5': 2, '7': 0, '11': 0, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 324 | 966 | 324 | 966 | 54 | 29 | False | 0.025 |
| T_5_minus_2_batch_1 | 256 | 2972 | 580 | 3938 | 83 | 0 | True | 0.123 |

