# S5 p=2 Oriented Twelve Identity Audit

## Summary

- input: `_results\mstar_s5_109_axis_transition_profile_60168_raw_2026-05-14.json`
- level: `60168`
- D targets: `192`
- transition records: `2304`
- good targets: `192`
- bad targets: `0`
- records per target: `[{'key': '12', 'count': 192}]`
- scalar balance per target: `[{'key': '+6/-6', 'count': 192}]`

## Expected Per Target

| field | count |
|---|---:|
| `base-gcd-v-line:TT:1:exact` | 1 |
| `base-gcd-v-line:TT:1:same-u` | 1 |
| `base-gcd-v-line:id:-1:other` | 2 |
| `even-intermediate:T:-1:other` | 2 |
| `even-intermediate:T:1:exact` | 1 |
| `even-intermediate:T:1:same-u` | 1 |
| `target-109d-axis:TT:-1:other` | 2 |
| `target-109d-axis:id:1:exact` | 1 |
| `target-109d-axis:id:1:same-u` | 1 |

Thus each D target has six positive exact/same-u contributions and
six negative other contributions, arranged in the three source buckets
`base-gcd-v-line`, `even-intermediate`, and `target-109d-axis`.
