# EM-2 Reyssat Orientation Audit

Date: 2026-05-09

## Result

The apparent conflict between EM-1 `root_number=-1` and LMFDB `240672.c3`
was an orientation-label issue.

| Curve | Model | LMFDB label | Global root number | Rank | Sha |
|---|---|---|---:|---:|---:|
| Original Frey orientation | `E_{2,6436341}` | `240672.g3` | -1 | 1 | 1 |
| Swapped orientation | `E_{6436341,2}` | `240672.c3` | +1 | 0 | 361 |

Both orientations share the same j-invariant, so the j-invariant alone does not
identify the Q-isomorphism class relevant for root-number/rank/Sha statements.

## PARI/GP Output

Mac Studio, PARI/GP 2.17.3:

```text
---
Frey_original_E_2_6436341
ainvs [0, 6436339, 0, -12872682, 0]
N_cond 240672
global_root -1
local_roots
2 f=5 kod=III tam=2 wp=1
3 f=1 kod=I_20 tam=20 wp=-1
23 f=1 kod=I_10 tam=10 wp=-1
109 f=1 kod=I_2 tam=2 wp=1
finite_product 1
minus_finite -1
---
Frey_swapped_E_6436341_2
ainvs [0, -6436339, 0, -12872682, 0]
N_cond 240672
global_root 1
local_roots
2 f=5 kod=III tam=2 wp=-1
3 f=1 kod=I_20 tam=2 wp=1
23 f=1 kod=I_10 tam=2 wp=1
109 f=1 kod=I_2 tam=2 wp=1
finite_product -1
minus_finite 1
---
LMFDB_240672_c3
ainvs [0, -1, 0, -13808832780322, -19750744373708998160]
N_cond 240672
global_root 1
local_roots
2 f=5 kod=III tam=2 wp=-1
3 f=1 kod=I_20 tam=2 wp=1
23 f=1 kod=I_10 tam=2 wp=1
109 f=1 kod=I_2 tam=2 wp=1
finite_product -1
minus_finite 1
---
LMFDB_240672_g3
ainvs [0, 1, 0, -13808832780322, 19750744373708998160]
N_cond 240672
global_root -1
local_roots
2 f=5 kod=III tam=2 wp=1
3 f=1 kod=I_20 tam=20 wp=-1
23 f=1 kod=I_10 tam=10 wp=-1
109 f=1 kod=I_2 tam=2 wp=1
finite_product 1
minus_finite -1
```

## LMFDB Single-Label JSON Checks

Endpoint pattern:

```text
https://www.lmfdb.org/EllipticCurve/Q/data/<label>?_format=json
```

Confirmed on 2026-05-09:

- `240672.c3`: rank 0, analytic rank 0, Sha 361, local roots
  `(-1,+1,+1,+1)`, global sign `+1`.
- `240672.g3`: rank 1, analytic rank 1, Sha 1, local roots
  `(+1,-1,-1,+1)`, global sign `-1`.
