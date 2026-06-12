# S5 Minor Budget Probe

This diagnostic reads source-row witnesses, lifts entries from `GF(q)`
to symmetric integer representatives, and reports sparsity plus the
Hadamard log2 determinant bound.  It is a scale probe, not a determinant
or Smith-normal-form certificate.

| Case | ncols | rows | avg nnz | max nnz | avg l1 | max l1 | Hadamard log2 bound |
|---|---:|---:|---:|---:|---:|---:|---:|
| N109_raw_sign1 | 27 | 27 | 3.519 | 7 | 4.000 | 8 | 28.7 |
| N218_raw_sign1 | 83 | 83 | 4.108 | 7 | 4.506 | 8 | 89.8 |
| N60168_raw_sign1 | 31680 | 31680 | 4.333 | 7 | 4.667 | 8 | 34283.8 |

Interpretation:

- The witness rows are very sparse and small after symmetric lift.
- Nevertheless, a generic determinant-minor budget is still far too
  large for a sublogarithmic FAQS bound at `60168`.
- The S5 route therefore needs a stronger structural certificate:
  a small Smith defect, a near-unimodular minor, or a finite
  exceptional-prime recursion rather than a raw Hadamard bound.
