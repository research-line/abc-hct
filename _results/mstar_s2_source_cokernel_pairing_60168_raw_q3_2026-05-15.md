# S2 Source-Cokernel Pairing

Case: `N60168_raw_source_plus_p2repair_sign1`.
Columns: `31680`.

## Repair Rows

| index | row id | origin |
|---:|---|---|
| 31680 | `T_5_minus_2_batch_11/575` | `repair_only` |
| 31681 | `T_7_minus_0_batch_1/1` | `repair_only` |

## Prime Pairings

| prime | source rank | defect dim | pairing rank | superset rank | saturates | seconds |
|---:|---:|---:|---:|---:|---|---:|
| 3 | 31679 | 1 | 1 | 31680 | True | 10675.209 |

## Pairing Matrices

### q = 3

Rows are a basis of `right_kernel(A mod q)`; columns are repair rows.

```text
1 0
```

## Interpretation

`saturates=True` means the repair rows generate the row-cokernel
of the source block modulo the tested prime. This is the dual
Cokernel form of the S2 determinant/Fitting witness.
