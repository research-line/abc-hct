# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N60168_raw_source_plus_T5b11r575_sign1

ncols `31680`, source rows `31681`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 31679 | False | 31681 | 41.067 | None |
| 3 | 31680 | True | 31681 | 300.217 | None |
| 5 | 31680 | True | 31681 | 479.808 | None |
| 31 | 31680 | True | 31681 | 392.654 | None |

Full-rank primes: `[3, 5, 31]`.
Exception candidates: `[2]`.

## N60168_raw_source_plus_T7b1r1_sign1

ncols `31680`, source rows `31681`, pivot `max`, engine `sage-matrix`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 31679 | False | 31681 | 89.932 | None |
| 3 | 31679 | False | 31681 | 257.915 | None |
| 5 | 31680 | True | 31681 | 260.318 | None |
| 31 | 31680 | True | 31681 | 178.997 | None |

Full-rank primes: `[5, 31]`.
Exception candidates: `[2, 3]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
