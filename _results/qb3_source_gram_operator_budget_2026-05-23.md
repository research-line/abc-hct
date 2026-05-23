# Q_B-3 Source-Gram Operator Budget

Datum: `2026-05-23`

## Empfehlung

Do not materialize A.  Store/project C_source sparsely and implement the product C_source * (B_AL * (C_source^T v)).

## Fälle

| Level | Mode | d | rank(A) target | nnz(C) | density(C) | dense A entries | uint64 MiB |
|---:|---|---:|---:|---:|---:|---:|---:|
| 80224 | raw | 10568 | 10567 | 1623421 | 1.4537% | 111661489 | 851.91 |
| 80224 | anc | 10568 | 10567 | 1623421 | 1.4537% | 111661489 | 851.91 |

## Operator-Form

```text
input v in F_q^(d-1)
u = C_source^T v          sparse accumulation
w = B_AL u                Atkin-Lehner pairing application
out = C_source w          sparse row dot products
```

Der Rangverifier soll also nur Matvecs mit `A` brauchen.  Das ist
genau die Form, in der ein Wiedemann-/Lanczos-artiger finite-field
Rank-Test später angesetzt werden kann.
