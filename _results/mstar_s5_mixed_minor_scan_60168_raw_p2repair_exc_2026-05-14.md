# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_p2_sign1

ncols `31680`, source rows `31680`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 31680 | True | 31680 | 26.335 | None |
| 3 | 31680 | True | 31680 | 123.973 | None |
| 5 | 31680 | True | 31680 | 148.789 | None |
| 31 | 31680 | True | 31680 | 175.969 | None |

Full-rank primes: `[2, 3, 5, 31]`.
Exception candidates: `[]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
