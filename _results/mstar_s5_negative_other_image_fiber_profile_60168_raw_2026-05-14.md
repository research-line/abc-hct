# S5 p=2 Negative Other Image Fiber Profile

## Summary

- input: `_results/mstar_s5_109_axis_transition_profile_60168_raw_2026-05-14.json`
- level: `60168`
- other records: `1152`
- image_v mod 109 zero: `1152`
- source_v mod 109 zero: `384`
- image_u = gcd(target_v,N): `1152`
- CRT inverse relation ok: `1152`
- CRT sign distribution: `[{'key': 'plus', 'count': 576}, {'key': 'minus', 'count': 576}]`
- S/swap target distribution: `[{'key': 'swap=target|S=mirror', 'count': 576}, {'key': 'S=target|swap=mirror', 'count': 576}]`

## Field Distribution

| field | count | image_v=0 mod109 | image_u=g | source_v=0 mod109 | S/swap pattern |
|---|---:|---:|---:|---:|---|
| `base-gcd-v-line:id:-1:other` | 384 | 384 | 384 | 384 | `[{'key': 'swap=target|S=mirror', 'count': 192}, {'key': 'S=target|swap=mirror', 'count': 192}]` |
| `even-intermediate:T:-1:other` | 384 | 384 | 384 | 0 | `[{'key': 'S=target|swap=mirror', 'count': 192}, {'key': 'swap=target|S=mirror', 'count': 192}]` |
| `target-109d-axis:TT:-1:other` | 384 | 384 | 384 | 0 | `[{'key': 'S=target|swap=mirror', 'count': 192}, {'key': 'swap=target|S=mirror', 'count': 192}]` |

## Interpretation

Every negative `other` record lands on the image fiber

```text
image_v ≡ 0 mod 109.
```

In fact, every negative `other` raw image has

```text
image_u = gcd(target_v,N),
```

so the image fiber is the base line `(g,109*r)` attached to the
target `(109*d,v)`, where `g=gcd(v,N)`.

The CRT relation is

```text
(r/d)*(v/g) ≡ ±1 mod 552/(d*g).
```

The plus/minus signs occur in exactly balanced halves.

The source coordinate is on this fiber only in the base `id` field,
where source and raw image coincide. The `T` and `T^2` other fields
have varying source residues.

The S/swap split says that each raw image either maps directly to the
D target under the S-operation, or maps to the `same-u` mirror which
is already controlled by the P1 normalizer mirror lemma.
