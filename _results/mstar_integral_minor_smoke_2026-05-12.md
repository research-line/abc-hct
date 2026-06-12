# Integral Minor Smoke

Rows are lifted from `GF(q)` to symmetric integer representatives.
A nonzero determinant `D` kills all field characteristics not dividing `D` for the same square row set.

| Case | ncols | q | det bits | q divides det | exceptional primes | status |
|---|---:|---:|---:|---|---|---|
| N109_anc_sign1 | 27 | 3863 | 17 | False | 2, 3, 7, 107 | ok |
| N109_raw_sign1 | 27 | 3863 | 17 | False | 2, 3, 7, 107 | ok |
| N218_anc_sign1 | 83 | 3863 | 51 | False | 2, 2081, 50129281393 | ok |
| N218_raw_sign1 | 83 | 3863 | 51 | False | 2, 2081, 50129281393 | ok |

Interpretation: this is only a smoke-level S5 diagnostic. It does not prove a global field-prime basket,
but it shows how an integral source-row minor would reduce all-but-finitely-many field characteristics
to the prime divisors of an explicit determinant.
