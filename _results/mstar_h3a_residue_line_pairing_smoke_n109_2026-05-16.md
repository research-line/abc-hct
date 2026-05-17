# S2 Source-Cokernel Pairing

Case: `N109_raw_sign1_splitlast`.
Columns: `27`.

## Repair Rows

| index | row id | origin |
|---:|---|---|
| 26 | `T_5_minus_2_batch_1/8` | `repair_only` |

## Prime Pairings

| prime | source rank | defect dim | pairing rank | superset rank | saturates | seconds |
|---:|---:|---:|---:|---:|---|---:|
| 3863 | 26 | 1 | 1 | 27 | True | 0.001 |

## Pairing Matrices

### q = 3863

Rows are a basis of `right_kernel(A mod q)`; columns are repair rows.

```text
395
```

## Interpretation

`saturates=True` means the repair rows generate the row-cokernel
of the source block modulo the tested prime. This is the dual
Cokernel form of the S2 determinant/Fitting witness.
