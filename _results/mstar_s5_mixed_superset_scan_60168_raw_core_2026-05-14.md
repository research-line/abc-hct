# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_source_plus_p2repair_sign1

ncols `31680`, source rows `31682`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 31680 | True | 31682 | 30.350 | None |
| 3 | 31680 | True | 31682 | 135.049 | None |
| 5 | 31680 | True | 31682 | 152.037 | None |
| 7 | 31680 | True | 31682 | 143.134 | None |
| 11 | 31680 | True | 31682 | 143.029 | None |
| 17 | 31680 | True | 31682 | 134.441 | None |
| 31 | 31680 | True | 31682 | 122.656 | None |

Full-rank primes: `[2, 3, 5, 7, 11, 17, 31]`.
Exception candidates: `[]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
