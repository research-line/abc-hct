# No-Magma Sparse Hecke Quotient

Date: 2026-05-10
Backend requested: `sage`
q: `3863`
Primes: `[5, 7, 11, 13]`

## Summary

| Backend | Level | Mode | Sign | Manin symbols | 2-term cols | Status | Final quotient dim | Seconds |
|---|---:|---|---:|---:|---:|---|---:|---:|
| sage | 30 | raw | 1 | 72 | 20 | killed | 0 | 0.060 |
| sage | 30 | anc | 1 | 72 | 20 | survivor_candidate | 2 | 0.035 |
| sage | 60 | raw | 1 | 144 | 38 | killed | 0 | 0.039 |
| sage | 60 | anc | 1 | 144 | 38 | survivor_candidate | 3 | 0.065 |
| sage | 120 | raw | 1 | 288 | 72 | killed | 0 | 0.096 |
| sage | 120 | anc | 1 | 288 | 72 | survivor_candidate | 4 | 0.159 |
| sage | 240 | raw | 1 | 576 | 144 | survivor_candidate | 1 | 0.332 |
| sage | 240 | anc | 1 | 576 | 144 | survivor_candidate | 5 | 0.359 |

## Level 30 / raw / backend sage

Traces: `{'5': 1, '7': 0, '11': 4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 60 | 180 | 60 | 180 | 10 | 10 | False | 0.024 |
| T_5_minus_1 | 72 | 430 | 132 | 610 | 14 | 6 | False | 0.001 |
| T_7_minus_0 | 72 | 610 | 204 | 1220 | 18 | 2 | False | 0.001 |
| T_11_minus_4 | 72 | 771 | 276 | 1991 | 20 | 0 | True | 0.002 |

## Level 30 / anc / backend sage

Traces: `{'5': 1, '7': 0, '11': -4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 60 | 180 | 60 | 180 | 10 | 10 | False | 0.000 |
| T_5_minus_1 | 72 | 430 | 132 | 610 | 14 | 6 | False | 0.000 |
| T_7_minus_0 | 72 | 610 | 204 | 1220 | 18 | 2 | False | 0.001 |
| T_11_minus_-4 | 72 | 781 | 276 | 2001 | 18 | 2 | False | 0.002 |
| T_13_minus_-2 | 72 | 851 | 348 | 2852 | 18 | 2 | False | 0.002 |

## Level 60 / raw / backend sage

Traces: `{'5': 1, '7': 0, '11': 4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 120 | 360 | 120 | 360 | 20 | 18 | False | 0.000 |
| T_5_minus_1 | 144 | 992 | 264 | 1352 | 29 | 9 | False | 0.001 |
| T_7_minus_0 | 144 | 1552 | 408 | 2904 | 35 | 3 | False | 0.002 |
| T_11_minus_4 | 144 | 2166 | 552 | 5070 | 38 | 0 | True | 0.003 |

## Level 60 / anc / backend sage

Traces: `{'5': 1, '7': 0, '11': -4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 120 | 360 | 120 | 360 | 20 | 18 | False | 0.000 |
| T_5_minus_1 | 144 | 992 | 264 | 1352 | 29 | 9 | False | 0.001 |
| T_7_minus_0 | 144 | 1552 | 408 | 2904 | 35 | 3 | False | 0.002 |
| T_11_minus_-4 | 144 | 2184 | 552 | 5088 | 35 | 3 | False | 0.003 |
| T_13_minus_-2 | 144 | 2466 | 696 | 7554 | 35 | 3 | False | 0.006 |

## Level 120 / raw / backend sage

Traces: `{'5': 1, '7': 0, '11': 4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 240 | 720 | 240 | 720 | 40 | 32 | False | 0.001 |
| T_5_minus_1 | 288 | 2248 | 528 | 2968 | 57 | 15 | False | 0.002 |
| T_7_minus_0 | 288 | 3712 | 816 | 6680 | 67 | 5 | False | 0.007 |
| T_11_minus_4 | 288 | 5368 | 1104 | 12048 | 72 | 0 | True | 0.011 |

## Level 120 / anc / backend sage

Traces: `{'5': 1, '7': 0, '11': -4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 240 | 720 | 240 | 720 | 40 | 32 | False | 0.001 |
| T_5_minus_1 | 288 | 2248 | 528 | 2968 | 57 | 15 | False | 0.002 |
| T_7_minus_0 | 288 | 3712 | 816 | 6680 | 67 | 5 | False | 0.005 |
| T_11_minus_-4 | 288 | 5396 | 1104 | 12076 | 67 | 5 | False | 0.008 |
| T_13_minus_-2 | 288 | 6416 | 1392 | 18492 | 68 | 4 | False | 0.012 |

## Level 240 / raw / backend sage

Traces: `{'5': 1, '7': 0, '11': 4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.002 |
| T_5_minus_1 | 576 | 5076 | 1104 | 6648 | 119 | 25 | False | 0.008 |
| T_7_minus_0 | 576 | 8564 | 1680 | 15212 | 135 | 9 | False | 0.019 |
| T_11_minus_4 | 576 | 13264 | 2256 | 28476 | 142 | 2 | False | 0.029 |
| T_13_minus_-2 | 576 | 16230 | 2832 | 44706 | 143 | 1 | False | 0.041 |

## Level 240 / anc / backend sage

Traces: `{'5': 1, '7': 0, '11': -4, '13': -2}`

| Stage | Rows added | nnz added | Total rows | Total nnz | Rank | Quotient dim | Killed | Rank seconds |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| manin_T_relations_after_SI | 528 | 1572 | 528 | 1572 | 88 | 56 | False | 0.001 |
| T_5_minus_1 | 576 | 5076 | 1104 | 6648 | 119 | 25 | False | 0.007 |
| T_7_minus_0 | 576 | 8564 | 1680 | 15212 | 135 | 9 | False | 0.016 |
| T_11_minus_-4 | 576 | 13280 | 2256 | 28492 | 137 | 7 | False | 0.028 |
| T_13_minus_-2 | 576 | 16230 | 2832 | 44722 | 139 | 5 | False | 0.041 |

