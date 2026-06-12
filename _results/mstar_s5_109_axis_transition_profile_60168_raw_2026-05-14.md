# S5 p=2 109-Axis Transition Profile

## Summary

- level: `60168`
- q: `3863`
- D-axis size: `192`
- transition records: `2304`
- records per D-column: `[{'key': '12', 'count': 192}]`
- term distribution: `[{'key': 'TT', 'count': 768}, {'key': 'id', 'count': 768}, {'key': 'T', 'count': 768}]`
- relative bucket / term distribution: `[{'key': 'even-intermediate:T', 'count': 768}, {'key': 'base-gcd-v-line:TT', 'count': 384}, {'key': 'base-gcd-v-line:id', 'count': 384}, {'key': 'target-109d-axis:id', 'count': 384}, {'key': 'target-109d-axis:TT', 'count': 384}]`
- quotient scalar distribution: `[{'key': '1', 'count': 1152}, {'key': '-1', 'count': 1152}]`

## Image Relation Distribution

| relation | count |
|---|---:|
| other | 1152 |
| same-u | 576 |
| exact | 576 |

## Relative Bucket / Term / Scalar

| bucket:term:scalar | count |
|---|---:|
| `base-gcd-v-line:TT:1` | 384 |
| `base-gcd-v-line:id:-1` | 384 |
| `even-intermediate:T:-1` | 384 |
| `even-intermediate:T:1` | 384 |
| `target-109d-axis:id:1` | 384 |
| `target-109d-axis:TT:-1` | 384 |

## Relative Bucket / Term / Scalar / Image Relation

| bucket:term:scalar:relation | count |
|---|---:|
| `base-gcd-v-line:id:-1:other` | 384 |
| `even-intermediate:T:-1:other` | 384 |
| `target-109d-axis:TT:-1:other` | 384 |
| `base-gcd-v-line:TT:1:same-u` | 192 |
| `base-gcd-v-line:TT:1:exact` | 192 |
| `even-intermediate:T:1:same-u` | 192 |
| `even-intermediate:T:1:exact` | 192 |
| `target-109d-axis:id:1:exact` | 192 |
| `target-109d-axis:id:1:same-u` | 192 |

## Per-D Full Signatures

| signature | D columns |
|---|---:|
| `base-gcd-v-line:TT:1:exact:1|base-gcd-v-line:TT:1:same-u:1|base-gcd-v-line:id:-1:other:2|even-intermediate:T:-1:other:2|even-intermediate:T:1:exact:1|even-intermediate:T:1:same-u:1|target-109d-axis:TT:-1:other:2|target-109d-axis:id:1:exact:1|target-109d-axis:id:1:same-u:1` | 192 |

## Raw Image gcd Pair

| gcd(image_u,N),gcd(image_v,N) | count |
|---|---:|
| `109,1` | 528 |
| `1,109` | 528 |
| `327,1` | 264 |
| `1,327` | 264 |
| `109,3` | 264 |
| `3,109` | 264 |
| `2507,1` | 24 |
| `1,2507` | 24 |
| `23,109` | 24 |
| `109,23` | 24 |
| `7521,1` | 12 |
| `1,7521` | 12 |
| `23,327` | 12 |
| `3,2507` | 12 |
| `109,69` | 12 |
| `69,109` | 12 |
| `2507,3` | 12 |
| `327,23` | 12 |

## Samples

```json
[
  {
    "target_col": 108,
    "target_uv": [
      109,
      1
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 109,
    "source_uv": [
      1,
      108
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125351,
    "image_uv": [
      109,
      551
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 108,
    "target_uv": [
      109,
      1
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 110,
    "source_uv": [
      1,
      109
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 110,
    "image_uv": [
      1,
      109
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 326,
    "target_uv": [
      327,
      1
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 327,
    "source_uv": [
      1,
      326
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126333,
    "image_uv": [
      327,
      367
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 326,
    "target_uv": [
      327,
      1
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 328,
    "source_uv": [
      1,
      327
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 328,
    "image_uv": [
      1,
      327
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 544,
    "target_uv": [
      109,
      221
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 545,
    "source_uv": [
      1,
      544
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125133,
    "image_uv": [
      109,
      331
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 544,
    "target_uv": [
      109,
      221
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 546,
    "source_uv": [
      1,
      545
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 546,
    "image_uv": [
      1,
      545
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 761,
    "target_uv": [
      109,
      79
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 763,
    "source_uv": [
      1,
      762
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125274,
    "image_uv": [
      109,
      473
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 761,
    "target_uv": [
      109,
      79
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 764,
    "source_uv": [
      1,
      763
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 764,
    "image_uv": [
      1,
      763
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 978,
    "target_uv": [
      327,
      307
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 981,
    "source_uv": [
      1,
      980
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126190,
    "image_uv": [
      327,
      61
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 978,
    "target_uv": [
      327,
      307
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 982,
    "source_uv": [
      1,
      981
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 982,
    "image_uv": [
      1,
      981
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 1193,
    "target_uv": [
      109,
      251
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1199,
    "source_uv": [
      1,
      1198
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125104,
    "image_uv": [
      109,
      301
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 1193,
    "target_uv": [
      109,
      251
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1200,
    "source_uv": [
      1,
      1199
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 1200,
    "image_uv": [
      1,
      1199
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 1408,
    "target_uv": [
      109,
      85
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1417,
    "source_uv": [
      1,
      1416
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125268,
    "image_uv": [
      109,
      467
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 1408,
    "target_uv": [
      109,
      85
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1418,
    "source_uv": [
      1,
      1417
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 1418,
    "image_uv": [
      1,
      1417
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 1624,
    "target_uv": [
      327,
      37
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 1635,
    "source_uv": [
      1,
      1634
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126321,
    "image_uv": [
      327,
      331
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 1624,
    "target_uv": [
      327,
      37
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 1636,
    "source_uv": [
      1,
      1635
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 1636,
    "image_uv": [
      1,
      1635
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 1838,
    "target_uv": [
      109,
      65
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1853,
    "source_uv": [
      1,
      1852
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125288,
    "image_uv": [
      109,
      487
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 1838,
    "target_uv": [
      109,
      65
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 1854,
    "source_uv": [
      1,
      1853
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 1854,
    "image_uv": [
      1,
      1853
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 2050,
    "target_uv": [
      109,
      523
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 2071,
    "source_uv": [
      1,
      2070
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 124834,
    "image_uv": [
      109,
      29
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 2050,
    "target_uv": [
      109,
      523
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 2072,
    "source_uv": [
      1,
      2071
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 2072,
    "image_uv": [
      1,
      2071
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 2266,
    "target_uv": [
      327,
      79
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 2289,
    "source_uv": [
      1,
      2288
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126306,
    "image_uv": [
      327,
      289
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 2266,
    "target_uv": [
      327,
      79
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 2290,
    "source_uv": [
      1,
      2289
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 2290,
    "image_uv": [
      1,
      2289
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 2484,
    "target_uv": [
      2507,
      1
    ],
    "target_d": 23,
    "target_gcd_v": 1,
    "source_index": 2507,
    "source_uv": [
      1,
      2506
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126673,
    "image_uv": [
      2507,
      47
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 2484,
    "target_uv": [
      2507,
      1
    ],
    "target_d": 23,
    "target_gcd_v": 1,
    "source_index": 2508,
    "source_uv": [
      1,
      2507
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 2508,
    "image_uv": [
      1,
      2507
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 2697,
    "target_uv": [
      109,
      265
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 2725,
    "source_uv": [
      1,
      2724
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125090,
    "image_uv": [
      109,
      287
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 2697,
    "target_uv": [
      109,
      265
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 2726,
    "source_uv": [
      1,
      2725
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 2726,
    "image_uv": [
      1,
      2725
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 2904,
    "target_uv": [
      327,
      41
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 2943,
    "source_uv": [
      1,
      2942
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126244,
    "image_uv": [
      327,
      143
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 2904,
    "target_uv": [
      327,
      41
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 2944,
    "source_uv": [
      1,
      2943
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 2944,
    "image_uv": [
      1,
      2943
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 3114,
    "target_uv": [
      109,
      533
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3161,
    "source_uv": [
      1,
      3160
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 124824,
    "image_uv": [
      109,
      19
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 3114,
    "target_uv": [
      109,
      533
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3162,
    "source_uv": [
      1,
      3161
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 3162,
    "image_uv": [
      1,
      3161
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 3329,
    "target_uv": [
      109,
      463
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3379,
    "source_uv": [
      1,
      3378
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 124894,
    "image_uv": [
      109,
      89
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 3329,
    "target_uv": [
      109,
      463
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3380,
    "source_uv": [
      1,
      3379
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 3380,
    "image_uv": [
      1,
      3379
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 3537,
    "target_uv": [
      327,
      67
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 3597,
    "source_uv": [
      1,
      3596
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126311,
    "image_uv": [
      327,
      301
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 3537,
    "target_uv": [
      327,
      67
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 3598,
    "source_uv": [
      1,
      3597
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 3598,
    "image_uv": [
      1,
      3597
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 3747,
    "target_uv": [
      109,
      347
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3815,
    "source_uv": [
      1,
      3814
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 125009,
    "image_uv": [
      109,
      205
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 3747,
    "target_uv": [
      109,
      347
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 3816,
    "source_uv": [
      1,
      3815
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 3816,
    "image_uv": [
      1,
      3815
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 3957,
    "target_uv": [
      109,
      373
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 4033,
    "source_uv": [
      1,
      4032
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 124983,
    "image_uv": [
      109,
      179
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 3957,
    "target_uv": [
      109,
      373
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "source_index": 4034,
    "source_uv": [
      1,
      4033
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 4034,
    "image_uv": [
      1,
      4033
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  },
  {
    "target_col": 4165,
    "target_uv": [
      327,
      85
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 4251,
    "source_uv": [
      1,
      4250
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "TT",
    "image_index": 126304,
    "image_uv": [
      327,
      283
    ],
    "image_relation": "same-u",
    "term_coeff": 1,
    "quotient_scalar": 1,
    "reduced_coeff": 1
  },
  {
    "target_col": 4165,
    "target_uv": [
      327,
      85
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "source_index": 4252,
    "source_uv": [
      1,
      4251
    ],
    "relative_source_bucket": "base-gcd-v-line",
    "term": "id",
    "image_index": 4252,
    "image_uv": [
      1,
      4251
    ],
    "image_relation": "other",
    "term_coeff": 1,
    "quotient_scalar": -1,
    "reduced_coeff": -1
  }
]
```
