# H3a Q_B-3 Source-Gram Matvec Smoke

Level: `80224`
Status: `blocked_by_dense_guard`

## Guard

Quotient dimension `10568` exceeds dense guard
`256`.

Large-level contract:

```text
u = C_source^T v
w = B_AL u
out = C_source w
```

Target: `rank(A)=10567`.
