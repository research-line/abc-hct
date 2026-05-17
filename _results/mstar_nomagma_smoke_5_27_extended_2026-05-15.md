# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5, 7, 11, 13, 17, 19, 23, 29]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 240 | raw | 1 | 576 | 144 | survivor_candidate | 4 | 1.258 |
| sage | 240 | anc | 1 | 576 | 144 | survivor_candidate | 1 | 1.224 |

## Level 240 / raw / backend sage

Traces: `{'5': -1, '7': -4, '11': 0, '13': 2, '17': 6, '19': -4, '23': 0, '29': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.032 |
| T_5_minus_-1 | 576 | 5132 | 1104 | 6704 | 128 | 16 | False | 0.005 |
| T_7_minus_-4 | 576 | 8872 | 1680 | 15576 | 139 | 5 | False | 0.015 |
| T_11_minus_0 | 576 | 13072 | 2256 | 28648 | 139 | 5 | False | 0.025 |
| T_13_minus_2 | 576 | 16132 | 2832 | 44780 | 140 | 4 | False | 0.035 |
| T_17_minus_6 | 576 | 21260 | 3408 | 66040 | 140 | 4 | False | 0.063 |
| T_19_minus_-4 | 576 | 22402 | 3984 | 88442 | 140 | 4 | False | 0.073 |
| T_23_minus_0 | 576 | 27774 | 4560 | 116216 | 140 | 4 | False | 0.096 |
| T_29_minus_-6 | 576 | 31150 | 5136 | 147366 | 140 | 4 | False | 0.129 |

## Level 240 / anc / backend sage

Traces: `{'5': -1, '7': 4, '11': 0, '13': 2, '17': 6, '19': 4, '23': 0, '29': -6}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.001 |
| T_5_minus_-1 | 576 | 5132 | 1104 | 6704 | 128 | 16 | False | 0.006 |
| T_7_minus_4 | 576 | 8864 | 1680 | 15568 | 141 | 3 | False | 0.017 |
| T_11_minus_0 | 576 | 13072 | 2256 | 28640 | 141 | 3 | False | 0.023 |
| T_13_minus_2 | 576 | 16132 | 2832 | 44772 | 143 | 1 | False | 0.038 |
| T_17_minus_6 | 576 | 21260 | 3408 | 66032 | 143 | 1 | False | 0.060 |
| T_19_minus_4 | 576 | 22376 | 3984 | 88408 | 143 | 1 | False | 0.068 |
| T_23_minus_0 | 576 | 27774 | 4560 | 116182 | 143 | 1 | False | 0.100 |
| T_29_minus_-6 | 576 | 31150 | 5136 | 147332 | 143 | 1 | False | 0.103 |

