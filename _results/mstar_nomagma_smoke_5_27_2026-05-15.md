# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 30 | raw | 1 | 72 | 20 | survivor_candidate | 1 | 0.076 |
| sage | 30 | anc | 1 | 72 | 20 | killed | 0 | 0.010 |
| sage | 60 | raw | 1 | 144 | 38 | survivor_candidate | 2 | 0.068 |
| sage | 60 | anc | 1 | 144 | 38 | killed | 0 | 0.022 |
| sage | 120 | raw | 1 | 288 | 72 | survivor_candidate | 3 | 0.179 |
| sage | 120 | anc | 1 | 288 | 72 | killed | 0 | 0.194 |
| sage | 240 | raw | 1 | 576 | 144 | survivor_candidate | 4 | 0.398 |
| sage | 240 | anc | 1 | 576 | 144 | survivor_candidate | 1 | 0.361 |

## Level 30 / raw / backend sage

Traces: `{'5': -1, '7': -4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 60 | 180 | 60 | 180 | 10 | 10 | False | 0.027 |
| T_5_minus_-1 | 72 | 437 | 132 | 617 | 19 | 1 | False | 0.001 |
| T_7_minus_-4 | 72 | 616 | 204 | 1233 | 19 | 1 | False | 0.001 |
| T_11_minus_0 | 72 | 773 | 276 | 2006 | 19 | 1 | False | 0.002 |
| T_13_minus_2 | 72 | 840 | 348 | 2846 | 19 | 1 | False | 0.002 |

## Level 30 / anc / backend sage

Traces: `{'5': -1, '7': 4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 60 | 180 | 60 | 180 | 10 | 10 | False | 0.000 |
| T_5_minus_-1 | 72 | 437 | 132 | 617 | 19 | 1 | False | 0.001 |
| T_7_minus_4 | 72 | 609 | 204 | 1226 | 20 | 0 | True | 0.001 |

## Level 60 / raw / backend sage

Traces: `{'5': -1, '7': -4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 120 | 360 | 120 | 360 | 20 | 18 | False | 0.001 |
| T_5_minus_-1 | 144 | 1016 | 264 | 1376 | 34 | 4 | False | 0.001 |
| T_7_minus_-4 | 144 | 1584 | 408 | 2960 | 36 | 2 | False | 0.002 |
| T_11_minus_0 | 144 | 2164 | 552 | 5124 | 36 | 2 | False | 0.003 |
| T_13_minus_2 | 144 | 2430 | 696 | 7554 | 36 | 2 | False | 0.005 |

## Level 60 / anc / backend sage

Traces: `{'5': -1, '7': 4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 120 | 360 | 120 | 360 | 20 | 18 | False | 0.000 |
| T_5_minus_-1 | 144 | 1016 | 264 | 1376 | 34 | 4 | False | 0.001 |
| T_7_minus_4 | 144 | 1578 | 408 | 2954 | 38 | 0 | True | 0.002 |

## Level 120 / raw / backend sage

Traces: `{'5': -1, '7': -4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 240 | 720 | 240 | 720 | 40 | 32 | False | 0.001 |
| T_5_minus_-1 | 288 | 2284 | 528 | 3004 | 64 | 8 | False | 0.003 |
| T_7_minus_-4 | 288 | 3812 | 816 | 6816 | 69 | 3 | False | 0.006 |
| T_11_minus_0 | 288 | 5332 | 1104 | 12148 | 69 | 3 | False | 0.015 |
| T_13_minus_2 | 288 | 6366 | 1392 | 18514 | 69 | 3 | False | 0.016 |

## Level 120 / anc / backend sage

Traces: `{'5': -1, '7': 4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 240 | 720 | 240 | 720 | 40 | 32 | False | 0.001 |
| T_5_minus_-1 | 288 | 2284 | 528 | 3004 | 64 | 8 | False | 0.003 |
| T_7_minus_4 | 288 | 3806 | 816 | 6810 | 71 | 1 | False | 0.006 |
| T_11_minus_0 | 288 | 5332 | 1104 | 12142 | 71 | 1 | False | 0.011 |
| T_13_minus_2 | 288 | 6366 | 1392 | 18508 | 72 | 0 | True | 0.015 |

## Level 240 / raw / backend sage

Traces: `{'5': -1, '7': -4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.002 |
| T_5_minus_-1 | 576 | 5132 | 1104 | 6704 | 128 | 16 | False | 0.008 |
| T_7_minus_-4 | 576 | 8872 | 1680 | 15576 | 139 | 5 | False | 0.022 |
| T_11_minus_0 | 576 | 13072 | 2256 | 28648 | 139 | 5 | False | 0.034 |
| T_13_minus_2 | 576 | 16132 | 2832 | 44780 | 140 | 4 | False | 0.055 |

## Level 240 / anc / backend sage

Traces: `{'5': -1, '7': 4, '11': 0, '13': 2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.001 |
| T_5_minus_-1 | 576 | 5132 | 1104 | 6704 | 128 | 16 | False | 0.007 |
| T_7_minus_4 | 576 | 8864 | 1680 | 15568 | 141 | 3 | False | 0.020 |
| T_11_minus_0 | 576 | 13072 | 2256 | 28640 | 141 | 3 | False | 0.031 |
| T_13_minus_2 | 576 | 16132 | 2832 | 44772 | 143 | 1 | False | 0.049 |

