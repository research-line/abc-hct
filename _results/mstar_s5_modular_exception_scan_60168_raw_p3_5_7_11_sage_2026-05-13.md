# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_sign1

ncols `31680`, source rows `31680`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 3 | 31679 | False | 31680 | 79.529 | None |
| 5 | 31679 | False | 31680 | 78.094 | None |
| 7 | 31680 | True | 31680 | 77.431 | None |
| 11 | 31680 | True | 31680 | 72.664 | None |

Full-rank primes: `[7, 11]`.
Exception candidates: `[3, 5]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
