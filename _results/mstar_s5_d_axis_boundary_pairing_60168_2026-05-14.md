# S5 p=2 D-Axis Boundary Pairing

## Summary

- level: `60168`
- P1 D representatives: `384`
- mirror pairs: `192`
- quotient D columns: `192`
- quotient hits per mirror pair: `[{'key': '1', 'count': 192}]`
- bad pairs: `0`
- mirror residue failures: `0`

## Statement Checked

The raw D-axis in `P^1(Z/NZ)` consists of representatives
`u=gcd(u,N)`, `u` odd, `109|u`, `v` odd. The mirror
`normalize(-u,v)` pairs them two by two, and the sparse quotient
selects exactly one representative from each pair.

This is the boundary-spiegel reading of the 109 correction.

## Pair u Distribution

| u | pairs |
|---:|---:|
| 109 | 138 |
| 327 | 46 |
| 2507 | 6 |
| 7521 | 2 |