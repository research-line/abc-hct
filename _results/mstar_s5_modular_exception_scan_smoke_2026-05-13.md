# S5 Modular Exception-Prime Scan

The scan recomputes the rank of the lifted source-row witness modulo
selected primes.  Full rank modulo `r` excludes `r` as a divisor of
this source minor; rank drop marks `r` as an exception candidate.

## N109_raw_sign1

ncols `27`, source rows `27`, pivot `max`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 25 | False | 27 | 0.001 | 5 |
| 3 | 26 | False | 27 | 0.001 | 6 |
| 5 | 27 | True | 27 | 0.000 | 6 |
| 7 | 26 | False | 27 | 0.000 | 6 |
| 11 | 27 | True | 27 | 0.000 | 6 |
| 13 | 27 | True | 27 | 0.001 | 6 |
| 17 | 27 | True | 27 | 0.001 | 6 |
| 19 | 27 | True | 27 | 0.001 | 6 |
| 23 | 27 | True | 27 | 0.001 | 6 |
| 29 | 27 | True | 27 | 0.001 | 6 |
| 31 | 27 | True | 27 | 0.001 | 6 |

Full-rank primes: `[5, 11, 13, 17, 19, 23, 29, 31]`.
Exception candidates: `[2, 3, 7]`.

## N218_raw_sign1

ncols `83`, source rows `83`, pivot `max`.

| prime | rank | full rank | rows seen | seconds | max basis row len |
|---:|---:|---|---:|---:|---:|
| 2 | 80 | False | 83 | 0.002 | 13 |
| 3 | 83 | True | 83 | 0.003 | 18 |
| 5 | 83 | True | 83 | 0.004 | 22 |
| 7 | 83 | True | 83 | 0.005 | 20 |
| 11 | 83 | True | 83 | 0.021 | 23 |
| 13 | 83 | True | 83 | 0.018 | 23 |
| 17 | 83 | True | 83 | 0.005 | 23 |
| 19 | 83 | True | 83 | 0.006 | 23 |
| 23 | 83 | True | 83 | 0.006 | 23 |
| 29 | 83 | True | 83 | 0.007 | 23 |
| 31 | 83 | True | 83 | 0.003 | 23 |

Full-rank primes: `[3, 5, 7, 11, 13, 17, 19, 23, 29, 31]`.
Exception candidates: `[2]`.

## N60168_raw_sign1

Status: `skipped_max_ncols` for ncols `31680`.

## Interpretation

This is a certified-recursion diagnostic.  It does not bound all
exception primes, but it shows which tested primes are already
excluded by the same integral source-row minor and which would need
new baskets or a different integral witness.
