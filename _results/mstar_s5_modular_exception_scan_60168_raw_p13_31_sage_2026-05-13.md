# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_sign1

ncols `31680`, source rows `31680`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 13 | 31680 | True | 31680 | 74.787 | None |
| 17 | 31680 | True | 31680 | 72.381 | None |
| 19 | 31680 | True | 31680 | 66.010 | None |
| 23 | 31680 | True | 31680 | 63.926 | None |
| 29 | 31680 | True | 31680 | 63.428 | None |
| 31 | 31679 | False | 31680 | 61.543 | None |

Full-rank primes: `[13, 17, 19, 23, 29]`.
Exception candidates: `[31]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
