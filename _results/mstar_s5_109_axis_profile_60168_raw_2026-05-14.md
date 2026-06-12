# S5 p=2 109-Axis Profile

## Summary

- level: `60168`
- mode: `raw`
- q: `3863`
- quotient columns: `31680`
- D-axis size: `192`
- Manin rows checked: `126720`
- Manin rows meeting D oddly: `2304`
- Manin D-column hit frequency: `[{'key': '12', 'count': 192}]`
- T5 rows checked: `13000`
- T5 rows meeting D oddly: `238`

## D-Axis By u

| u | count |
|---:|---:|
| 109 | 138 |
| 327 | 46 |
| 2507 | 6 |
| 7521 | 2 |

## D-Axis Formula Check

| d | u=109*d | count | expected 2*(69/d) |
|---:|---:|---:|---:|
| 1 | 109 | 138 | 138 |
| 3 | 327 | 46 | 46 |
| 23 | 2507 | 6 | 6 |
| 69 | 7521 | 2 | 2 |

## Manin Bad Source gcd(u,N)

| gcd(u,N) | count |
|---:|---:|
| 1 | 552 |
| 109 | 552 |
| 2 | 276 |
| 3 | 184 |
| 327 | 184 |
| 4 | 138 |
| 8 | 138 |
| 6 | 92 |
| 12 | 46 |
| 24 | 46 |
| 23 | 24 |
| 2507 | 24 |
| 46 | 12 |
| 69 | 8 |
| 7521 | 8 |
| 92 | 6 |
| 184 | 6 |
| 138 | 4 |
| 276 | 2 |
| 552 | 2 |

## T5 Bad Source Residues

| residue | count |
|---:|---:|
| 21 | 60 |
| 65 | 60 |
| 43 | 59 |
| 87 | 59 |

Formula: `v == -a*5^{-1} mod 109` for `a=1,2,3,4`; since `5^{-1}=22`, this gives residues `87,65,43,21`.

## T5 Hit Matrices

| matrix label | hit count |
|---|---:|
| a=4 | 60 |
| a=2 | 60 |
| a=3 | 59 |
| a=1 | 59 |

## Examples

```json
{
  "manin_odd": [
    {
      "row_index": 109,
      "source": [
        1,
        108
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 108,
          "uv": [
            109,
            1
          ]
        }
      ]
    },
    {
      "row_index": 110,
      "source": [
        1,
        109
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 108,
          "uv": [
            109,
            1
          ]
        }
      ]
    },
    {
      "row_index": 327,
      "source": [
        1,
        326
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 326,
          "uv": [
            327,
            1
          ]
        }
      ]
    },
    {
      "row_index": 328,
      "source": [
        1,
        327
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 326,
          "uv": [
            327,
            1
          ]
        }
      ]
    },
    {
      "row_index": 545,
      "source": [
        1,
        544
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 544,
          "uv": [
            109,
            221
          ]
        }
      ]
    },
    {
      "row_index": 546,
      "source": [
        1,
        545
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 544,
          "uv": [
            109,
            221
          ]
        }
      ]
    },
    {
      "row_index": 763,
      "source": [
        1,
        762
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 761,
          "uv": [
            109,
            79
          ]
        }
      ]
    },
    {
      "row_index": 764,
      "source": [
        1,
        763
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 761,
          "uv": [
            109,
            79
          ]
        }
      ]
    },
    {
      "row_index": 981,
      "source": [
        1,
        980
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 978,
          "uv": [
            327,
            307
          ]
        }
      ]
    },
    {
      "row_index": 982,
      "source": [
        1,
        981
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 978,
          "uv": [
            327,
            307
          ]
        }
      ]
    },
    {
      "row_index": 1199,
      "source": [
        1,
        1198
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1193,
          "uv": [
            109,
            251
          ]
        }
      ]
    },
    {
      "row_index": 1200,
      "source": [
        1,
        1199
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1193,
          "uv": [
            109,
            251
          ]
        }
      ]
    },
    {
      "row_index": 1417,
      "source": [
        1,
        1416
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1408,
          "uv": [
            109,
            85
          ]
        }
      ]
    },
    {
      "row_index": 1418,
      "source": [
        1,
        1417
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1408,
          "uv": [
            109,
            85
          ]
        }
      ]
    },
    {
      "row_index": 1635,
      "source": [
        1,
        1634
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1624,
          "uv": [
            327,
            37
          ]
        }
      ]
    },
    {
      "row_index": 1636,
      "source": [
        1,
        1635
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1624,
          "uv": [
            327,
            37
          ]
        }
      ]
    },
    {
      "row_index": 1853,
      "source": [
        1,
        1852
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1838,
          "uv": [
            109,
            65
          ]
        }
      ]
    },
    {
      "row_index": 1854,
      "source": [
        1,
        1853
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1838,
          "uv": [
            109,
            65
          ]
        }
      ]
    },
    {
      "row_index": 2071,
      "source": [
        1,
        2070
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2050,
          "uv": [
            109,
            523
          ]
        }
      ]
    },
    {
      "row_index": 2072,
      "source": [
        1,
        2071
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2050,
          "uv": [
            109,
            523
          ]
        }
      ]
    }
  ],
  "t5_odd": [
    {
      "row_index": 22,
      "source": [
        1,
        21
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 108,
          "uv": [
            109,
            1
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            4,
            0,
            5
          ],
          "label": "a=4",
          "hits": [
            {
              "col": 108,
              "uv": [
                109,
                1
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 66,
      "source": [
        1,
        65
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 326,
          "uv": [
            327,
            1
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            2,
            0,
            5
          ],
          "label": "a=2",
          "hits": [
            {
              "col": 326,
              "uv": [
                327,
                1
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 153,
      "source": [
        1,
        152
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 761,
          "uv": [
            109,
            79
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            3,
            0,
            5
          ],
          "label": "a=3",
          "hits": [
            {
              "col": 761,
              "uv": [
                109,
                79
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 197,
      "source": [
        1,
        196
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 978,
          "uv": [
            327,
            307
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            1,
            0,
            5
          ],
          "label": "a=1",
          "hits": [
            {
              "col": 978,
              "uv": [
                327,
                307
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 240,
      "source": [
        1,
        239
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1193,
          "uv": [
            109,
            251
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            4,
            0,
            5
          ],
          "label": "a=4",
          "hits": [
            {
              "col": 1193,
              "uv": [
                109,
                251
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 284,
      "source": [
        1,
        283
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1408,
          "uv": [
            109,
            85
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            2,
            0,
            5
          ],
          "label": "a=2",
          "hits": [
            {
              "col": 1408,
              "uv": [
                109,
                85
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 371,
      "source": [
        1,
        370
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 1838,
          "uv": [
            109,
            65
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            3,
            0,
            5
          ],
          "label": "a=3",
          "hits": [
            {
              "col": 1838,
              "uv": [
                109,
                65
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 415,
      "source": [
        1,
        414
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2050,
          "uv": [
            109,
            523
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            1,
            0,
            5
          ],
          "label": "a=1",
          "hits": [
            {
              "col": 2050,
              "uv": [
                109,
                523
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 458,
      "source": [
        1,
        457
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2266,
          "uv": [
            327,
            79
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            4,
            0,
            5
          ],
          "label": "a=4",
          "hits": [
            {
              "col": 2266,
              "uv": [
                327,
                79
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 502,
      "source": [
        1,
        501
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2484,
          "uv": [
            2507,
            1
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            2,
            0,
            5
          ],
          "label": "a=2",
          "hits": [
            {
              "col": 2484,
              "uv": [
                2507,
                1
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 589,
      "source": [
        1,
        588
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 2904,
          "uv": [
            327,
            41
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            3,
            0,
            5
          ],
          "label": "a=3",
          "hits": [
            {
              "col": 2904,
              "uv": [
                327,
                41
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 633,
      "source": [
        1,
        632
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 3114,
          "uv": [
            109,
            533
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            1,
            0,
            5
          ],
          "label": "a=1",
          "hits": [
            {
              "col": 3114,
              "uv": [
                109,
                533
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 676,
      "source": [
        1,
        675
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 3329,
          "uv": [
            109,
            463
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            4,
            0,
            5
          ],
          "label": "a=4",
          "hits": [
            {
              "col": 3329,
              "uv": [
                109,
                463
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 720,
      "source": [
        1,
        719
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 3537,
          "uv": [
            327,
            67
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            2,
            0,
            5
          ],
          "label": "a=2",
          "hits": [
            {
              "col": 3537,
              "uv": [
                327,
                67
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 807,
      "source": [
        1,
        806
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 3957,
          "uv": [
            109,
            373
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            3,
            0,
            5
          ],
          "label": "a=3",
          "hits": [
            {
              "col": 3957,
              "uv": [
                109,
                373
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 851,
      "source": [
        1,
        850
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 4165,
          "uv": [
            327,
            85
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            1,
            0,
            5
          ],
          "label": "a=1",
          "hits": [
            {
              "col": 4165,
              "uv": [
                327,
                85
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 894,
      "source": [
        1,
        893
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 4371,
          "uv": [
            109,
            377
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            4,
            0,
            5
          ],
          "label": "a=4",
          "hits": [
            {
              "col": 4371,
              "uv": [
                109,
                377
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 938,
      "source": [
        1,
        937
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 4579,
          "uv": [
            109,
            475
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            2,
            0,
            5
          ],
          "label": "a=2",
          "hits": [
            {
              "col": 4579,
              "uv": [
                109,
                475
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 1025,
      "source": [
        1,
        1024
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 4994,
          "uv": [
            109,
            47
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            3,
            0,
            5
          ],
          "label": "a=3",
          "hits": [
            {
              "col": 4994,
              "uv": [
                109,
                47
              ]
            }
          ]
        }
      ]
    },
    {
      "row_index": 1069,
      "source": [
        1,
        1068
      ],
      "d_hit_count": 1,
      "d_hits": [
        {
          "col": 5201,
          "uv": [
            109,
            169
          ]
        }
      ],
      "matrix_hits": [
        {
          "matrix": [
            1,
            1,
            0,
            5
          ],
          "label": "a=1",
          "hits": [
            {
              "col": 5201,
              "uv": [
                109,
                169
              ]
            }
          ]
        }
      ]
    }
  ]
}
```
