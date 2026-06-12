# S5 p=2 P1 Normalizer Mirror Check

## Summary

- level: `60168`
- checked divisor-u representatives: `126719`
- same-u normalizer hits: `126719`
- bad same-u mirrors: `0`
- D-axis representatives in P1List: `384`
- bad D-axis mirrors: `0`

## Statement Checked

For every normalized pair `(u,v)` with `u|N` and `u!=0`:

```text
normalize(-u,v) = (u,w)  =>  w+v ≡ 0 mod N/u.
```

On the D-axis this is the `same-u` mirror used in the S5-p=2
CRT-/Boundary handproof skeleton.

## Bad Examples

```json
[]
```
