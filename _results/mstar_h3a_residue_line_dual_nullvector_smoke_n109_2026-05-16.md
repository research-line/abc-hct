# H3a Residue-Line Dual Nullvector Diagnostic

Computes the genuine mod-q dual residue functional `phi` as a right
nullvector of the source-row matrix in the split-last witness.

## 109/raw

```text
case:                       _results\h3a_wait_postprocess_smoke_n109_2026-05-16\N109_raw_sign1_splitlast
q:                          3863
ncols:                      27
source rows/rank:           26 / 26
dependent source rows:      0
free columns:               [6]
max basis row length:       9
phi support size:           11
phi support range:          6..21
phi prefix 0..15:           {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 1, '7': -1054, '8': 0, '9': 0, '10': -1054, '11': -1054, '12': 1, '13': 1, '14': 1, '15': 0}
source nonzero pairings:    0
source annihilated:         True
repair pairing signed:      705
repair pairing nonzero:     True
```

## Interpretation

A result with `source_annihilated=true` and `repair_pairing_nonzero=true`
is the mod-q version of CFR-3.4.  It identifies the dual residue line;
an integer or odd-local proof still has to explain this nullvector
canonically through Manin S/I/T relations rather than through a single
finite-field computation.
