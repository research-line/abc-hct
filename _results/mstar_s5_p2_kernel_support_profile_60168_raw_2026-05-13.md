# S5 p=2 Kernel Support Profile

Input: `_results\mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json`

## Summary

- ncols: `31680`
- support size: `21128`
- support density: `0.666919`
- support bitvector SHA256: `9696951ea1070e50f3c44ad0b3340e254ba3b962ee5532f33a6619642c7a8da1`
- complement size: `10552`
- T7 support modulo 2: `[1, 2, 3, 4, 5]`
- T7 intersection with kernel support: `[1, 3, 5]`
- T7 pairing modulo 2: `1`
- support parity counts: `{'0': 10473, '1': 10655}`
- complement parity counts: `{'0': 5367, '1': 5185}`

## Coarse Blocks

Block size `2880` gives the clearest low-resolution picture:

| block | columns | support | density |
|---:|---:|---:|---:|
| 0 | `0-2879` | 1458 | 0.5062 |
| 1 | `2880-5759` | 1510 | 0.5243 |
| 2 | `5760-8639` | 1551 | 0.5385 |
| 3 | `8640-11519` | 1618 | 0.5618 |
| 4 | `11520-14399` | 1690 | 0.5868 |
| 5 | `14400-17279` | 1765 | 0.6128 |
| 6 | `17280-20159` | 1855 | 0.6441 |
| 7 | `20160-23039` | 1961 | 0.6809 |
| 8 | `23040-25919` | 2230 | 0.7743 |
| 9 | `25920-28799` | 2817 | 0.9781 |
| 10 | `28800-31679` | 2673 | 0.9281 |

## Gap Profile

- support gap counts: `{'1': 10578, '2': 10546, '3': 3}`
- complement gap counts, truncated in JSON by natural keys: `{'1': 3, '2': 7078, '3': 1672, '4': 1555, '5': 5, '6': 8, '7': 10, '8': 7, '9': 62, '10': 11, '11': 10, '12': 30, '13': 6, '14': 28, '15': 6, '16': 3, '17': 46, '18': 8, '25': 1, '602': 1, '2776': 1}`

Longest consecutive support runs:

| start | end | length |
|---:|---:|---:|
| 25323 | 28097 | 2775 |
| 30989 | 31589 | 601 |
| 31644 | 31667 | 24 |
| 28126 | 28142 | 17 |
| 28551 | 28567 | 17 |
| 28631 | 28647 | 17 |
| 29136 | 29152 | 17 |
| 29295 | 29311 | 17 |
| 29561 | 29577 | 17 |
| 29642 | 29658 | 17 |
| 29801 | 29817 | 17 |
| 28153 | 28168 | 16 |

Longest step-2 support runs:

| start | end | length |
|---:|---:|---:|
| 1 | 585 | 293 |
| 2083 | 2539 | 229 |
| 586 | 884 | 150 |
| 3162 | 3368 | 104 |
| 1038 | 1240 | 102 |
| 2543 | 2675 | 67 |
| 5474 | 5606 | 67 |
| 1371 | 1483 | 57 |
| 1484 | 1596 | 57 |
| 885 | 987 | 52 |
| 1597 | 1687 | 46 |
| 1973 | 2059 | 44 |

## Residues

| modulus | nonempty residues | min | max | top residues |
|---:|---:|---:|---:|---|
| 2 | 2 | 10473 | 10655 | `1:10655, 0:10473` |
| 3 | 3 | 7039 | 7049 | `0:7049, 2:7040, 1:7039` |
| 4 | 4 | 5210 | 5365 | `3:5365, 1:5290, 0:5263, 2:5210` |
| 5 | 5 | 4186 | 4262 | `4:4262, 2:4248, 1:4240, 0:4192, 3:4186` |
| 7 | 7 | 2990 | 3055 | `5:3055, 0:3035, 1:3030, 3:3026, 2:2999, 4:2993` |
| 8 | 8 | 2599 | 2684 | `3:2684, 7:2681, 5:2655, 0:2648, 1:2635, 4:2615` |
| 11 | 11 | 1874 | 1956 | `2:1956, 0:1944, 9:1944, 4:1941, 8:1935, 6:1934` |
| 16 | 16 | 1295 | 1353 | `7:1353, 11:1347, 0:1342, 9:1338, 3:1337, 5:1332` |
| 24 | 24 | 855 | 907 | `7:907, 15:899, 11:897, 3:896, 21:894, 5:892` |
| 32 | 32 | 633 | 686 | `19:686, 27:681, 0:679, 7:678, 9:678, 23:675` |
| 48 | 48 | 417 | 458 | `27:458, 31:458, 23:455, 29:453, 35:452, 12:452` |
| 60 | 60 | 332 | 373 | `19:373, 17:367, 51:367, 12:364, 23:363, 7:362` |
| 120 | 120 | 160 | 190 | `79:190, 27:187, 63:187, 34:187, 21:186, 25:186` |
| 240 | 240 | 74 | 101 | `23:101, 199:101, 197:99, 211:99, 27:98, 49:97` |
| 480 | 480 | 33 | 55 | `289:55, 291:53, 39:52, 211:52, 247:52, 287:52` |

## Interpretation

- The kernel vector is broad and coordinate-dependent; it is not a five-column Boundary vector.
- Residue counts are balanced, so there is no visible simple congruence-class explanation.
- Coarse block density rises strongly with column order, which is compatible with quotient-basis/order effects rather than an invariant geometric support.
- The proof-grade invariant extracted from this profile is therefore the odd pairing of the unique pre-T7 quotient direction with the T7 Cusp-star row.
