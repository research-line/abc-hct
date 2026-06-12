# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_p2_sign1

ncols `31680`, source rows `31680`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 7 | 31679 | False | 31680 | 188.262 | None |
| 11 | 31679 | False | 31680 | 172.686 | None |
| 13 | 31680 | True | 31680 | 165.696 | None |
| 17 | 31679 | False | 31680 | 187.349 | None |
| 19 | 31680 | True | 31680 | 160.616 | None |
| 23 | 31680 | True | 31680 | 163.767 | None |
| 29 | 31680 | True | 31680 | 147.439 | None |

Full-rank primes: `[13, 19, 23, 29]`.
Exception candidates: `[7, 11, 17]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
