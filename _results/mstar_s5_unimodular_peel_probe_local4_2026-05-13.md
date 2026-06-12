# S5 Near-Unimodular Peel Probe

This diagnostic performs a determinant-safe leaf peel on symmetric
integer lifts of source-row witnesses.  A peeled pivot is an active row
or column with exactly one active nonzero entry whose absolute value
is at most the configured pivot bound, so it splits off an explicit
small determinant factor by Laplace expansion.  With pivot bound `1`,
this is a unit-factor probe.

| Case | n | nnz | unit edge % | pivot bound | peeled pivots | pivot abs counts | core rows | core cols | core nnz | core avg row deg | interpretation |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| N109_raw_sign1 | 27 | 95 | 89.47 | 4 | 3 | `{2: 1, 3: 1, 4: 1}` | 24 | 24 | 89 | 3.708 | small_core |
| N218_raw_sign1 | 83 | 341 | 91.50 | 4 | 3 | `{1: 2, 4: 1}` | 80 | 80 | 331 | 4.138 | small_core |
| N60168_raw_sign1 | 31680 | 137273 | 92.30 | 4 | 17 | `{1: 16, 4: 1}` | 31663 | 31663 | 137217 | 4.334 | large_core |

## Interpretation

### N109_raw_sign1

The unit peel leaves a small core.  The determinant/SNF budget is reduced to this core rather than the full matrix.

Small-core determinant bits: `13`, divisible by q: `False`.
Factorization: `{'2': 1, '3': 1, '7': 1, '107': 1}`.

### N218_raw_sign1

The unit peel leaves a small core.  The determinant/SNF budget is reduced to this core rather than the full matrix.

Small-core determinant bits: `49`, divisible by q: `False`.
Factorization: `{'2': 2, '2081': 1, '50129281393': 1}`.

### N60168_raw_sign1

The unit peel leaves a large core.  The current source-row witness does not visibly support a near-unimodular minor by this simple leaf-peeling certificate.

## Consequence

A complete or small-core peel would be strong evidence for a
near-unimodular or locally budgeted S5 route.  A large core means
the current mod-q rank witness is good as a rank certificate but
not optimized for a small integral-index certificate.
