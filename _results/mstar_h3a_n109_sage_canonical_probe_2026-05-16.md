# H3a N=109 Sage Canonical Probe

Level `109`, sign `1`, mode `raw`, dimension `9`.
Decomposition dimensions: `[1, 1, 3, 4]`.

## Decomposition Trace Data

| Component | Dimension | Trace data |
|---:|---:|---|
| 0 | 1 | `{'5': {'charpoly': 'x - 3', 'eigenvalue': '3', 'frey_difference': '1'}, '7': {'charpoly': 'x - 2', 'eigenvalue': '2', 'frey_difference': '2'}, '11': {'charpoly': 'x - 1', 'eigenvalue': '1', 'frey_difference': '1'}, '13': {'charpoly': 'x', 'eigenvalue': '0', 'frey_difference': '6'}}` |
| 1 | 1 | `{'5': {'charpoly': 'x - 6', 'eigenvalue': '6', 'frey_difference': '4'}, '7': {'charpoly': 'x - 8', 'eigenvalue': '8', 'frey_difference': '8'}, '11': {'charpoly': 'x - 12', 'eigenvalue': '12', 'frey_difference': '12'}, '13': {'charpoly': 'x - 14', 'eigenvalue': '14', 'frey_difference': '20'}}` |
| 2 | 3 | `{'5': {'charpoly': 'x^3 + 6*x^2 + 5*x - 13'}, '7': {'charpoly': 'x^3 + x^2 - 16*x + 13'}, '11': {'charpoly': 'x^3 + 13*x^2 + 54*x + 71'}, '13': {'charpoly': 'x^3 + x^2 - 16*x + 13'}}` |
| 3 | 4 | `{'5': {'charpoly': 'x^4 - x^3 - 5*x^2 + 4*x + 3'}, '7': {'charpoly': 'x^4 + 3*x^3 - 10*x^2 - 23*x - 2'}, '11': {'charpoly': 'x^4 - 12*x^3 + 33*x^2 + 47*x - 177'}, '13': {'charpoly': 'x^4 + 7*x^3 - 10*x^2 - 93*x + 16'}}` |

## Intersection Numbers

| Pair | Intersection number |
|---|---:|
| `0-1` | 1 |
| `0-2` | 1 |
| `0-3` | 4 |
| `1-2` | 1 |
| `1-3` | 9 |
| `2-3` | 8 |

| Factor vs complement | Intersection number |
|---|---:|
| `0` | 4 |
| `1` | 9 |
| `2` | 8 |
| `3` | 288 |

## Individual Operators

| l | a_l(E) | det(T_l-a_l) | factorization | non-unit Smith factors |
|---:|---:|---:|---|---|
| 5 | 2 | 116 | `{'2': 2, '29': 1}` | `[116]` |
| 7 | 0 | 416 | `{'2': 5, '13': 1}` | `[2, 2, 104]` |
| 11 | 0 | 150804 | `{'2': 2, '3': 2, '59': 1, '71': 1}` | `[150804]` |
| 13 | -6 | -17040 | `{'2': 4, '3': 1, '5': 1, '71': 1}` | `[2, 2, 4260]` |

## Stacked Trace Presentations

| Stack | Shape | Rank | Index | Factorization | non-unit Smith factors |
|---|---|---:|---:|---|---|
| `5` | `[9, 9]` | 9 | 116 | `{'2': 2, '29': 1}` | `[116]` |
| `5+7` | `[18, 9]` | 9 | 4 | `{'2': 2}` | `[4]` |
| `5+7+11` | `[27, 9]` | 9 | 4 | `{'2': 2}` | `[4]` |
| `5+7+11+13` | `[36, 9]` | 9 | 4 | `{'2': 2}` | `[4]` |

## Interpretation

On the canonical 9-dimensional Sage quotient, the first trace presentation `5` has index 116, while the full tested stack `5+7+11+13` has index 4 with factorization `{'2': 2}`.  This is the canonical Trace-Fitting datum to compare with H3a-B; arbitrary source-row minors remain rank certificates and should not be read as intrinsic congruence modules.
For N=109, the residual index 4 is visibly explained by the 1-dimensional component 1: it has T5=6 and T7=8, hence trace differences 4 and 8 against the Frey target (2,0).
