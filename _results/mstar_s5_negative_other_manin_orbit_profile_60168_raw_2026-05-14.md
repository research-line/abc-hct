# S5 p=2 Negative Other Manin Orbit Profile

## Summary

- input: `_results/mstar_s5_109_axis_transition_profile_60168_raw_2026-05-14.json`
- level: `60168`
- negative other records: `1152`
- unique negative images: `384`
- D targets: `192`
- images per target: `[{'key': '2', 'count': 192}]`
- records per image: `[{'key': '3', 'count': 384}]`
- orbit-source checks: `[{'key': 'True', 'count': 1152}]`
- per-image field signature: `[{'key': 'base-gcd-v-line:id:-1:other|even-intermediate:T:-1:other|target-109d-axis:TT:-1:other', 'count': 384}]`
- bad records: `0`

## Interpretation

For every negative base-fiber image `x=(g,109*r)`, the three negative
`other` records are exactly the Manin orbit

```text
id-source:  x
T-source:   T^2 x
TT-source:  T x
```

Since `T` has order three on `P^1`, this explains the three negative
`other` fields once the base-fiber images have been identified.
