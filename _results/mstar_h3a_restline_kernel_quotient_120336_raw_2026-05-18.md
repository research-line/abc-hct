# H3a Quotient Restline Kernel

This is the quotient-functional input for the later AL scalar test
`Q_B(phi)=phi B_AL^{-1} phi^T`.

```text
case:                   _results/h3a_residue_line_witness_120336_raw_standard_2026-05-16/N120336_raw_sign1_splitlast
level/mode/q:           120336 / raw / 3863
V_SI columns:           63360
T-Manin rows/rank:      42224 / 42224
Hecke rows:             21135
quotient ncols:         21136
quotient rank:          21135
quotient kernel dim:    1
kernel support size:    9957
repair pairing signed:  -1
repair pairing nonzero: True
source annihilated:     True
ready for AL scalar:    True
kernel engine:          sparse-python
seconds:                85693.420
```

## Kernel Head

```text
[[1, 1], [3, -1], [5, 1], [7, -1], [9, 1], [11, -1], [13, 1], [15, -1], [17, 1], [19, -1], [21, 1], [23, -1], [25, 1], [27, -1], [29, 1], [31, -1], [33, 1], [35, -1], [37, 1], [39, -1], [41, 1], [43, -1], [45, 1], [47, -1], [49, 1], [51, -1], [53, 1], [55, -1], [57, 1], [59, -1], [61, 1], [63, -1], [65, 1], [67, -1], [69, 1], [71, -1], [73, 1], [75, -1], [77, 1], [79, -1], [81, 1], [83, -1], [85, 1], [87, -1], [89, 1], [91, -1], [93, 1], [95, -1], [97, 1], [99, -1], [101, 1], [103, -1], [105, 1], [107, -1], [109, 1], [111, -1], [113, 1], [115, -1], [117, 1], [119, -1], [121, 1], [123, -1], [125, 1], [127, -1], [129, 1], [131, -1], [133, 1], [135, -1], [137, 1], [139, -1], [141, 1], [143, -1], [145, 1], [147, -1], [149, 1], [151, -1], [153, 1], [155, -1], [157, 1], [159, -1]]
```

## Repair Projection

```text
[[0, 2], [1, -1], [2, -1], [3, -1], [4, -1], [5, -1]]
```

## Interpretation

`ready_for_al_scalar=true` means the projected Hecke source has a unique
right-kernel line, all source rows vanish on it, and the repair row pairs
nontrivially with it.  The remaining step is to push this quotient
functional through the Atkin-Lehner pairing.
