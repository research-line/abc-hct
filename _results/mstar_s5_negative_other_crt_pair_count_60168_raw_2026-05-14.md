# S5 p=2 Negative Other CRT Pair Count

## Summary

- input: `_results/mstar_s5_109_axis_transition_profile_60168_raw_2026-05-14.json`
- level: `60168`
- D representatives from P1List: `384`
- quotient D targets from transition records: `192`
- predicted image count per target: `[{'key': '2', 'count': 192}]`
- actual image count per target: `[{'key': '2', 'count': 192}]`
- sign set per target: `[{'key': "('+', '-')", 'count': 192}]`
- predicted equals actual: `[{'key': 'True', 'count': 192}]`
- bad targets: `0`

## Statement Checked

For each D-target `(109*d,v)` with `g=gcd(v,N)`, set
`h=552/(d*g)` and `v0=v/g`. The two predicted negative
basis-fiber images are obtained from

```text
(r/d)*v0 == +1 mod h
(r/d)*v0 == -1 mod h
gcd(r,552) == d
image = normalize(g,109*r).
```

The check compares this intrinsic CRT prediction with the negative
`other` images observed in the transition profile.
