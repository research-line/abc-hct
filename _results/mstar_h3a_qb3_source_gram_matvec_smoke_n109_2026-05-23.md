# H3a Q_B-3 Source-Gram Matvec Smoke

Level: `109`
Status: `computed`

## Smoke

```text
quotient dim:          9
source rows:           8
rank(A):               8 / 8
rank(A) full:          True
B_AL rank:             9
matvec tests pass:     True
```

Each test checks `A*v == C_source*(B_AL*(C_source^T*v))`.
