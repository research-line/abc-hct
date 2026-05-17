# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 210 | raw | 1 | 576 | 148 | killed | 0 | 0.193 |
| sage | 210 | anc | 1 | 576 | 148 | killed | 0 | 0.159 |
| sage | 420 | raw | 1 | 1152 | 292 | killed | 0 | 0.366 |
| sage | 420 | anc | 1 | 1152 | 292 | killed | 0 | 0.350 |

## Level 210 / raw / backend sage

Traces: `{'5': 1, '7': 1, '11': -4, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 552 | 1656 | 552 | 1656 | 92 | 56 | False | 0.026 |
| T_5_minus_1 | 576 | 5446 | 1128 | 7102 | 123 | 25 | False | 0.005 |
| T_7_minus_1 | 576 | 7436 | 1704 | 14538 | 140 | 8 | False | 0.012 |
| T_11_minus_-4 | 576 | 14059 | 2280 | 28597 | 148 | 0 | True | 0.025 |

## Level 210 / anc / backend sage

Traces: `{'5': 1, '7': -1, '11': 4, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 552 | 1656 | 552 | 1656 | 92 | 56 | False | 0.001 |
| T_5_minus_1 | 576 | 5446 | 1128 | 7102 | 123 | 25 | False | 0.006 |
| T_7_minus_-1 | 576 | 7487 | 1704 | 14589 | 139 | 9 | False | 0.010 |
| T_11_minus_4 | 576 | 14041 | 2280 | 28630 | 148 | 0 | True | 0.023 |

## Level 420 / raw / backend sage

Traces: `{'5': 1, '7': 1, '11': -4, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 1104 | 3312 | 1104 | 3312 | 184 | 108 | False | 0.002 |
| T_5_minus_1 | 1152 | 11264 | 2256 | 14576 | 249 | 43 | False | 0.017 |
| T_7_minus_1 | 1152 | 15892 | 3408 | 30468 | 276 | 16 | False | 0.038 |
| T_11_minus_-4 | 1152 | 30168 | 4560 | 60636 | 292 | 0 | True | 0.078 |

## Level 420 / anc / backend sage

Traces: `{'5': 1, '7': -1, '11': 4, '13': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 1104 | 3312 | 1104 | 3312 | 184 | 108 | False | 0.003 |
| T_5_minus_1 | 1152 | 11264 | 2256 | 14576 | 249 | 43 | False | 0.017 |
| T_7_minus_-1 | 1152 | 16000 | 3408 | 30576 | 277 | 15 | False | 0.033 |
| T_11_minus_4 | 1152 | 30146 | 4560 | 60722 | 292 | 0 | True | 0.073 |

