# M* LEB-2 Local Formula Probe

Source: `_results\mstar_15case_tail_ledger_2026-05-09.json`

## Candidate

\[
v_2(\operatorname{Cong}_2(E))
\le
v_2\!\left(\prod_p c_p(E)\right)
+
\sum_{p\mid N} v_2\!\left(v_p(\Delta_{\min}(E))\right)
+O(1).
\]

## Summary

- Cases: 15
- Sharp envelope successes: 14/15
- Sharp envelope plus one successes: 15/15
- Log-depth envelope successes: 15/15

## Top v2 Degree Cases

| label | v2(deg) | v2(Tam) | sum v2(delta) | sharp | deficit | sharp+1 deficit | p2 type | p2 delta |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| ABCHome_2 | 16 | 7 | 9 | 16 | 0 | 0 | I34 | 34 |
| 1+4095=4096 | 14 | 8 | 9 | 17 | 0 | 0 | I16 | 16 |
| classic_2401 | 13 | 8 | 7 | 15 | 0 | 0 | I6* | 14 |
| Reyssat_raw | 10 | 5 | 5 | 10 | 0 | 0 | III | 6 |
| Reyssat_ANC_orientation | 10 | 4 | 5 | 9 | 1 | 0 | III | 6 |
| classic_4374 | 10 | 6 | 6 | 12 | 0 | 0 | III | 6 |

## Interpretation

- The sharp local envelope pays 14/15 cases exactly or with slack.
- The only sharp deficit is Reyssat_ANC_orientation, by one 2-adic unit.
- Adding an O(1) orientation/isogeny/comparison allowance pays all 15 cases.
- This is a target theorem shape, not a proof; it avoids defining the allowance by the modular degree.
