# EM-2 Q1 Baseline Bins

Date: 2026-05-09

Source: John Cremona ecdata `allcurves` files, one representative per isogeny class.

Method: `NCURVE=1`; sign counted by rank parity `w=-1` for odd rank and `w=+1` for even rank.
Caveat: this is an ecdata rank-parity baseline, not a fresh PARI `ellrootno` run for every class.
The exact `N=240672` slice is cross-checked against the direct PARI/LMFDB audit.

| Bin | Classes | w=-1 | w=+1 | Fraction w=-1 | Conductors |
|---|---:|---:|---:|---:|---:|
| primary_[100000,200000]_union_[300000,500000] | 1292882 | 653131 | 639751 | 0.5052 | 174099 |
| sensitivity_[200000,300000]_excluding_240672 | 434144 | 218840 | 215304 | 0.5041 | 58643 |
| exact_N_240672_crosscheck | 8 | 4 | 4 | 0.5000 | 1 |

Rank-count details:

- `primary_[100000,200000]_union_[300000,500000]`: r=0:464576, r=1:646736, r=2:175175, r=3:6395
- `sensitivity_[200000,300000]_excluding_240672`: r=0:156918, r=1:216867, r=2:58385, r=3:1973, r=4:1
- `exact_N_240672_crosscheck`: r=0:4, r=1:4

Interpretation:

- The pre-registered large-conductor primary baseline is essentially balanced.
- The exact Reyssat conductor `N=240672` is also balanced at class level in the direct T2 audit (4/8).
- Therefore EM-2 does not show a strong root-number enrichment signal; the observed Reyssat `w=-1` remains descriptive/hypothesis-generating.

Source URLs and any missing edge files are listed in the companion JSON file.

Missing source files:
- `https://raw.githubusercontent.com/JohnCremona/ecdata/master/allcurves/allcurves.500000-509999`
