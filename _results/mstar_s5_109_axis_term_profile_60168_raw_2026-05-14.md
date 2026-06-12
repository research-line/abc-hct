# S5 p=2 109-Axis Term Profile

## Summary

- level: `60168`
- q: `3863`
- D-axis size: `192`
- D columns with records: `192`
- per-D record count: `[{'key': '12', 'count': 192}]`
- term signature distribution: `[{'key': 'id:4|T:4|TT:4', 'count': 192}]`
- relative-bucket/term signature distribution: `[{'key': 'base-gcd-v-line:TT:2|base-gcd-v-line:id:2|even-intermediate:T:4|target-109d-axis:TT:2|target-109d-axis:id:2', 'count': 192}]`
- nonstandard examples: `0`

## Term Signatures

| signature | D columns |
|---|---:|
| `id:4|T:4|TT:4` | 192 |

## Relative Bucket / Term Signatures

| signature | D columns |
|---|---:|
| `base-gcd-v-line:TT:2|base-gcd-v-line:id:2|even-intermediate:T:4|target-109d-axis:TT:2|target-109d-axis:id:2` | 192 |

## Global Relative Bucket By Term

| bucket,term | count |
|---|---:|
| `even-intermediate:T` | 768 |
| `base-gcd-v-line:TT` | 384 |
| `base-gcd-v-line:id` | 384 |
| `target-109d-axis:id` | 384 |
| `target-109d-axis:TT` | 384 |

## Samples

```json
[
  {
    "col": 108,
    "uv": [
      109,
      1
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 109,
        "source": [
          1,
          108
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 110,
        "source": [
          1,
          109
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 60059,
        "source": [
          1,
          60058
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 60060,
        "source": [
          1,
          60059
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 60441,
        "source": [
          2,
          545
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 74937,
        "source": [
          2,
          29537
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 115504,
        "source": [
          12,
          545
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 116808,
        "source": [
          12,
          4457
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124806,
        "source": [
          109,
          1
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125243,
        "source": [
          109,
          442
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125245,
        "source": [
          109,
          444
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125351,
        "source": [
          109,
          551
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 326,
    "uv": [
      327,
      1
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 327,
        "source": [
          1,
          326
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 328,
        "source": [
          1,
          327
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 59841,
        "source": [
          1,
          59840
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 59842,
        "source": [
          1,
          59841
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 65890,
        "source": [
          2,
          11443
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 69488,
        "source": [
          2,
          18639
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 109269,
        "source": [
          8,
          2935
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 113851,
        "source": [
          8,
          12099
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 126150,
        "source": [
          327,
          1
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 126176,
        "source": [
          327,
          40
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126285,
        "source": [
          327,
          226
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126333,
        "source": [
          327,
          367
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 544,
    "uv": [
      109,
      221
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 545,
        "source": [
          1,
          544
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 546,
        "source": [
          1,
          545
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 59623,
        "source": [
          1,
          59622
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 59624,
        "source": [
          1,
          59623
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 102969,
        "source": [
          6,
          545
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 107710,
        "source": [
          6,
          19505
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 108074,
        "source": [
          8,
          545
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 115046,
        "source": [
          8,
          14489
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124916,
        "source": [
          109,
          112
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125024,
        "source": [
          109,
          221
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125025,
        "source": [
          109,
          222
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125133,
        "source": [
          109,
          331
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 761,
    "uv": [
      109,
      79
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 763,
        "source": [
          1,
          762
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 764,
        "source": [
          1,
          763
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 59405,
        "source": [
          1,
          59404
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 59406,
        "source": [
          1,
          59405
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 97826,
        "source": [
          4,
          5119
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 100226,
        "source": [
          4,
          9919
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 104130,
        "source": [
          6,
          4027
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 104786,
        "source": [
          6,
          5995
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124884,
        "source": [
          109,
          79
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125166,
        "source": [
          109,
          364
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125274,
        "source": [
          109,
          473
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125323,
        "source": [
          109,
          522
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      }
    ]
  },
  {
    "col": 978,
    "uv": [
      327,
      307
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 981,
        "source": [
          1,
          980
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 982,
        "source": [
          1,
          981
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 59187,
        "source": [
          1,
          59186
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 59188,
        "source": [
          1,
          59187
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 61639,
        "source": [
          2,
          2941
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 73739,
        "source": [
          2,
          27141
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 96738,
        "source": [
          4,
          2943
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 101314,
        "source": [
          4,
          12095
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 126190,
        "source": [
          327,
          61
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 126258,
        "source": [
          327,
          164
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126305,
        "source": [
          327,
          286
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126313,
        "source": [
          327,
          307
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 1193,
    "uv": [
      109,
      251
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 1199,
        "source": [
          1,
          1198
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 1200,
        "source": [
          1,
          1199
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 58969,
        "source": [
          1,
          58968
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 58970,
        "source": [
          1,
          58969
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 62076,
        "source": [
          2,
          3815
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 73302,
        "source": [
          2,
          26267
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 122000,
        "source": [
          24,
          4663
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 122171,
        "source": [
          24,
          5341
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124946,
        "source": [
          109,
          142
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 124996,
        "source": [
          109,
          192
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125054,
        "source": [
          109,
          251
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125104,
        "source": [
          109,
          301
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 1408,
    "uv": [
      109,
      85
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 1417,
        "source": [
          1,
          1416
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 1418,
        "source": [
          1,
          1417
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 58751,
        "source": [
          1,
          58750
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 58752,
        "source": [
          1,
          58751
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 62184,
        "source": [
          2,
          4031
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 73194,
        "source": [
          2,
          26051
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 120474,
        "source": [
          24,
          85
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 122934,
        "source": [
          24,
          9919
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124890,
        "source": [
          109,
          85
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125160,
        "source": [
          109,
          358
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125268,
        "source": [
          109,
          467
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125329,
        "source": [
          109,
          528
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      }
    ]
  },
  {
    "col": 1624,
    "uv": [
      327,
      37
    ],
    "target_d": 3,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 1635,
        "source": [
          1,
          1634
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 1636,
        "source": [
          1,
          1635
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 58533,
        "source": [
          1,
          58532
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 58534,
        "source": [
          1,
          58533
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 65563,
        "source": [
          2,
          10789
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 69815,
        "source": [
          2,
          19293
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 95430,
        "source": [
          4,
          327
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 102622,
        "source": [
          4,
          14711
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 126152,
        "source": [
          327,
          4
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126174,
        "source": [
          327,
          37
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 126297,
        "source": [
          327,
          262
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 126321,
        "source": [
          327,
          331
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      }
    ]
  },
  {
    "col": 1838,
    "uv": [
      109,
      65
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 1853,
        "source": [
          1,
          1852
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 1854,
        "source": [
          1,
          1853
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 58315,
        "source": [
          1,
          58314
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 58316,
        "source": [
          1,
          58315
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 96629,
        "source": [
          4,
          2725
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 101423,
        "source": [
          4,
          12313
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 103478,
        "source": [
          6,
          2071
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 105438,
        "source": [
          6,
          7951
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124870,
        "source": [
          109,
          65
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125180,
        "source": [
          109,
          378
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125288,
        "source": [
          109,
          487
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125309,
        "source": [
          109,
          508
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      }
    ]
  },
  {
    "col": 2050,
    "uv": [
      109,
      523
    ],
    "target_d": 1,
    "target_gcd_v": 1,
    "term_counts": {
      "id": 4,
      "T": 4,
      "TT": 4
    },
    "relative_bucket_term_counts": {
      "base-gcd-v-line:TT": 2,
      "base-gcd-v-line:id": 2,
      "even-intermediate:T": 4,
      "target-109d-axis:TT": 2,
      "target-109d-axis:id": 2
    },
    "records": [
      {
        "row_index": 2071,
        "source": [
          1,
          2070
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 2072,
        "source": [
          1,
          2071
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 58097,
        "source": [
          1,
          58096
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "TT"
      },
      {
        "row_index": 58098,
        "source": [
          1,
          58097
        ],
        "relative_source_bucket": "base-gcd-v-line",
        "term": "id"
      },
      {
        "row_index": 108179,
        "source": [
          8,
          755
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 114941,
        "source": [
          8,
          14279
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 124834,
        "source": [
          109,
          29
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125216,
        "source": [
          109,
          414
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125273,
        "source": [
          109,
          472
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "TT"
      },
      {
        "row_index": 125324,
        "source": [
          109,
          523
        ],
        "relative_source_bucket": "target-109d-axis",
        "term": "id"
      },
      {
        "row_index": 125487,
        "source": [
          138,
          407
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      },
      {
        "row_index": 125551,
        "source": [
          138,
          763
        ],
        "relative_source_bucket": "even-intermediate",
        "term": "T"
      }
    ]
  }
]
```
