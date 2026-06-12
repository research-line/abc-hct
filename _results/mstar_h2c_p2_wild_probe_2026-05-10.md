# M* H2C-C p=2 Wild Probe

## Sampled Frey Normal Forms

Rows sample curves `a=2^r u`, `b` odd, `gcd(u,b)=1`.

| r=v2(abc) | expected | signatures `(delta2, Kodaira, c2, f2; allowance)` |
|---:|---|---|
| 1 | bounded additive | (6, III, 2, 5; 2) |
| 2 | bounded additive | (8, I0*, 2, 4; 4); (8, I1*, 2, 3; 4); (8, I1*, 4, 3; 5) |
| 3 | bounded additive | (10, I2*, 4, 4; 3); (10, III*, 2, 3; 2) |
| 4 | bounded good/additive | (0, I0, 1, 0; 0); (12, I4*, 4, 4; 4) |
| 5 | potentially multiplicative depth | (2, I2, 2, 1; 2); (14, I6*, 4, 4; 3) |
| 6 | potentially multiplicative depth | (4, I4, 2, 1; 3); (4, I4, 4, 1; 4); (16, I8*, 4, 4; 6) |
| 7 | potentially multiplicative depth | (6, I6, 2, 1; 2); (6, I6, 6, 1; 2); (18, I10*, 4, 4; 3) |
| 8 | potentially multiplicative depth | (8, I8, 2, 1; 4); (8, I8, 8, 1; 6); (20, I12*, 4, 4; 4) |
| 9 | potentially multiplicative depth | (10, I10, 2, 1; 2); (10, I10, 10, 1; 2); (22, I14*, 4, 4; 3) |
| 10 | potentially multiplicative depth | (12, I12, 2, 1; 3); (12, I12, 12, 1; 4); (24, I16*, 4, 4; 5) |
| 11 | potentially multiplicative depth | (14, I14, 2, 1; 2); (14, I14, 14, 1; 2); (26, I18*, 4, 4; 3) |
| 12 | potentially multiplicative depth | (16, I16, 2, 1; 5); (16, I16, 16, 1; 8); (28, I20*, 4, 4; 4) |
| 13 | potentially multiplicative depth | (18, I18, 2, 1; 2); (18, I18, 18, 1; 2); (30, I22*, 4, 4; 3) |
| 14 | potentially multiplicative depth | (20, I20, 2, 1; 3); (20, I20, 20, 1; 4); (32, I24*, 4, 4; 7) |
| 15 | potentially multiplicative depth | (22, I22, 2, 1; 2); (22, I22, 22, 1; 2); (34, I26*, 4, 4; 3) |
| 16 | potentially multiplicative depth | (24, I24, 2, 1; 4); (24, I24, 24, 1; 6); (36, I28*, 4, 4; 4) |
| 17 | potentially multiplicative depth | (26, I26, 2, 1; 2); (26, I26, 26, 1; 2); (38, I30*, 4, 4; 3) |
| 18 | potentially multiplicative depth | (28, I28, 2, 1; 3); (28, I28, 28, 1; 4); (40, I32*, 4, 4; 5) |
| 19 | potentially multiplicative depth | (30, I30, 2, 1; 2); (30, I30, 30, 1; 2); (42, I34*, 4, 4; 3) |
| 20 | potentially multiplicative depth | (32, I32, 2, 1; 6); (32, I32, 32, 1; 10); (44, I36*, 4, 4; 4) |
| 21 | potentially multiplicative depth | (34, I34, 2, 1; 2); (34, I34, 34, 1; 2); (46, I38*, 4, 4; 3) |
| 22 | potentially multiplicative depth | (36, I36, 2, 1; 3); (36, I36, 36, 1; 4); (48, I40*, 4, 4; 6) |
| 23 | potentially multiplicative depth | (38, I38, 2, 1; 2); (38, I38, 38, 1; 2); (50, I42*, 4, 4; 3) |
| 24 | potentially multiplicative depth | (40, I40, 2, 1; 4); (40, I40, 40, 1; 6); (52, I44*, 4, 4; 4) |

## 15-Case Ledger Audit

| label | r | expected | Kodaira(2) | delta2 | c2 | f2 | v2(c2)+v2(delta2) |
|---|---:|---|---|---:|---:|---:|---:|
| Reyssat_ANC_orientation | 1 | bounded additive | III | 6 | 2 | 5 | 2 |
| Reyssat_raw | 1 | bounded additive | III | 6 | 2 | 5 | 2 |
| classic_4374 | 1 | bounded additive | III | 6 | 2 | 5 | 2 |
| 1+8=9 | 3 | bounded additive | I2* | 10 | 4 | 4 | 3 |
| 1+80=81 | 4 | bounded good/additive | I4* | 12 | 4 | 4 | 4 |
| 32+49=81 | 5 | potentially multiplicative depth | I2 | 2 | 2 | 1 | 2 |
| 5+27=32 | 5 | potentially multiplicative depth | I2 | 2 | 2 | 1 | 2 |
| classic_2401 | 5 | potentially multiplicative depth | I6* | 14 | 4 | 4 | 3 |
| 1+63=64 | 6 | potentially multiplicative depth | I4 | 4 | 4 | 1 | 4 |
| 3+125=128 | 7 | potentially multiplicative depth | I10* | 18 | 4 | 4 | 3 |
| 13+243=256 | 8 | potentially multiplicative depth | I8 | 8 | 2 | 1 | 4 |
| 1+1023=1024 | 10 | potentially multiplicative depth | I12 | 12 | 12 | 1 | 4 |
| 625+2048=2673 | 11 | potentially multiplicative depth | I18* | 26 | 4 | 4 | 3 |
| 1+4095=4096 | 12 | potentially multiplicative depth | I16 | 16 | 16 | 1 | 8 |
| ABCHome_2 | 21 | potentially multiplicative depth | I34 | 34 | 34 | 1 | 2 |

## Interpretation

- The sampled local pattern corrects the too-simple split:
  r=1,2,3 are bounded additive cases; r=4 is bounded good/additive;
  r>=5 has potentially multiplicative depth with possible I_n* variants.
- The conductor exponent and star/wild part remain bounded in the sample.
- The unbounded part is the rank-1 Tate/Néron depth measured by delta2.
- Therefore H2C-C reduces to rank-1 2-adic depth plus a uniform bounded wild/star comparison index.
