# S5 p=2 Full T5 Residue Law Profile

## Summary

- level: `60168`
- mode: `raw`
- q: `3863`
- T5 rows checked: `126720`
- odd D-hit rows: `1536`
- odd rows with exactly one D hit: `1536`
- odd rows with exactly one matrix hit: `1536`
- residue-law good rows: `1536`
- bad rows: `0`

## Law

For an odd D-hit in the full `T_5-a_5(E)` row, the hit comes from
exactly one standard matrix `[1,a;0,5]`, `a=1,2,3,4`, and the source
`(u,v)` satisfies

```text
5*v + a*u == 0 mod 109.
```

The dual matrix and the `a=0` matrix do not contribute to odd D-hits.

## Source u

| u | count |
|---:|---:|
| 1 | 1104 |
| 3 | 368 |
| 23 | 48 |
| 69 | 16 |

## Matrix a

| a | count |
|---:|---:|
| 4 | 384 |
| 2 | 384 |
| 3 | 384 |
| 1 | 384 |

## Source u x a

| u,a | count |
|---|---:|
| u=1,a=4 | 276 |
| u=1,a=2 | 276 |
| u=1,a=3 | 276 |
| u=1,a=1 | 276 |
| u=3,a=3 | 92 |
| u=3,a=1 | 92 |
| u=3,a=4 | 92 |
| u=3,a=2 | 92 |
| u=23,a=3 | 12 |
| u=23,a=4 | 12 |
| u=23,a=1 | 12 |
| u=23,a=2 | 12 |
| u=69,a=1 | 4 |
| u=69,a=2 | 4 |
| u=69,a=3 | 4 |
| u=69,a=4 | 4 |