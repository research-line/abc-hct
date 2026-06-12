# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N109_raw_sign1

ncols `27`, source rows `27`, pivot `max`, engine `sparse-order`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 25 | False | 27 | 0.000 | 5 |
| 3 | 26 | False | 27 | 0.000 | 6 |
| 5 | 27 | True | 27 | 0.000 | 6 |

Full-rank primes: `[5]`.
Exception candidates: `[2, 3]`.

## N218_raw_sign1

ncols `83`, source rows `83`, pivot `max`, engine `sparse-order`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 80 | False | 83 | 0.001 | 13 |
| 3 | 83 | True | 83 | 0.002 | 18 |
| 5 | 83 | True | 83 | 0.002 | 22 |

Full-rank primes: `[3, 5]`.
Exception candidates: `[2]`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
