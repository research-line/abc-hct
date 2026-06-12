# H3a Quotient Restline Kernel

This is the quotient-functional input for the later AL scalar test
`Q_B(phi)=phi B_AL^{-1} phi^T`.

```text
case:                   C:\Users\User\OneDrive\.TOPICS\.RESEARCH\.LAB\.HCT\abc\_results\remod_q5077_smoke_n109_2026-05-23\N109_raw_sign1_splitlast
level/mode/q:           109 / raw / 5077
V_SI columns:           27
T-Manin rows/rank:      18 / 18
Hecke rows:             8
quotient ncols:         9
quotient rank:          8
quotient kernel dim:    1
kernel support size:    3
repair pairing signed:  -1382
repair pairing nonzero: True
source annihilated:     True
ready for AL scalar:    True
kernel engine:          sparse-python
seconds:                0.039
```

## Kernel Head

```text
[[6, 1], [7, -462], [8, -2306]]
```

## Repair Projection

```text
[[1, 2538], [2, -1], [4, -2], [5, 1], [6, -3], [7, -1], [8, 3]]
```

## Interpretation

`ready_for_al_scalar=true` means the projected Hecke source has a unique
right-kernel line, all source rows vanish on it, and the repair row pairs
nontrivially with it.  The remaining step is to push this quotient
functional through the Atkin-Lehner pairing.
