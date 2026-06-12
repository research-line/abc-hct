# Trace-Sieve Scale Check

N = 240672, log N = 12.391190, target 2 log N = 24.782381

Crude determinant bound:

\[
\log |\det(T_p-a_p(E))| \le d\log(4\sqrt p).
\]

For several primes, multiply/add these bounds. This is deliberately crude:
it measures why ordinary determinant/resultant estimates are too large.

## Oldlevel Rows

| Space | dim | bound/logN | bound/(2logN) |
|---:|---:|---:|---:|
| 109 | 8 | 45.13 | 22.56 |
| 218 | 10 | 56.41 | 28.21 |
| 327 | 19 | 107.18 | 53.59 |
| 872 | 27 | 152.31 | 76.15 |
| 1744 | 54 | 304.62 | 152.31 |
| 2507 | 199 | 1122.56 | 561.28 |
| 3488 | 108 | 609.23 | 304.62 |
| 15042 | 397 | 2239.49 | 1119.74 |
| 20056 | 594 | 3350.77 | 1675.39 |
| 40112 | 1188 | 6701.54 | 3350.77 |
| 60168 | 1188 | 6701.54 | 3350.77 |
| 80224 | 2376 | 13403.08 | 6701.54 |
| 120336 | 2376 | 13403.08 | 6701.54 |

## Aggregate / Full Level

| Space | dim | bound/logN | bound/(2logN) |
|---:|---:|---:|---:|
| loaded_oldlevel_sum | 8544 | 48196.94 | 24098.47 |
| level_240672_new | 4752 | 26806.16 | 13403.08 |
| level_240672_old | 37457 | 211295.96 | 105647.98 |
| level_240672_total | 42209 | 238102.13 | 119051.06 |

## Conclusion

Ordinary trace/resultant determinant bounds scale with the ambient dimension.
They are therefore many orders above the HOS-excess target. A proof needs
a Frey-specific integral repulsion or sparsity theorem, not just effective
multiplicity one or a small-prime trace sieve.
