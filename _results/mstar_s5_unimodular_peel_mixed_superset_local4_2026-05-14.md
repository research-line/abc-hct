# S5 Near-Unimodular Peel Probe

This diagnostic performs a determinant-safe leaf peel on symmetric
integer lifts of source-row witnesses.  A peeled pivot is an active row
or column with exactly one active nonzero entry whose absolute value
is at most the configured pivot bound, so it splits off an explicit
small determinant factor by Laplace expansion.  With pivot bound `1`,
this is a unit-factor probe.

| Case | n | nnz | unit edge % | pivot bound | peeled pivots | pivot abs counts | core rows | core cols | core nnz | core avg row deg | interpretation |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| N60168_raw_source_plus_p2repair_sign1 | 31680 | 137286 | 92.30 | 4 | 17 | `{1: 16, 4: 1}` | 31665 | 31663 | 137229 | 4.334 | large_core |

## Interpretation

### N60168_raw_source_plus_p2repair_sign1

The unit peel leaves a large core.  The current source-row witness does not visibly support a near-unimodular minor by this simple leaf-peeling certificate.

## Consequence

A complete or small-core peel would be strong evidence for a
near-unimodular or locally budgeted S5 route.  A large core means
the current mod-q rank witness is good as a rank certificate but
not optimized for a small integral-index certificate.
