# M* LEB Snapshot

Source: `_results\mstar_defect_budget_snapshot_2026-05-09.json`

## Summary

- Cases: 15
- LEB-visible cases: 11
- Nonlocal-tail cases: 3

## Top External Non-Tamagawa Tails

| label | tail | tail/logN | two/logN | Tamagawa/logN | level/logN | verdict |
|---|---:|---:|---:|---:|---:|---|
| Reyssat_ANC_orientation | `5^3 * 3863` | 1.056195 | 0.559387 | 0.223755 | 0.736709 | nonlocal-tail |
| Reyssat_raw | `5 * 3863` | 0.796424 | 0.559387 | 0.539465 | 0.736709 | nonlocal-tail |
| 13+243=256 | `5` | 0.369416 | 0.636395 | 0.477296 | 0.636395 | nonlocal-tail |
| 625+2048=2673 | `7` | 0.246989 | 0.879792 | 0.644177 | 1.223517 | small-nonlocal-tail |
| ABCHome_2 | `1` | 0.000000 | 1.019288 | 0.807303 | 1.749934 | LEB-visible |

## Interpretation

- ABCHome_2 is LEB-visible: its stress is 2-adic/level/Tamagawa-visible, not an external nonlocal tail.
- Reyssat remains the nonlocal test: the factor 3863 is not paid by the local Tamagawa/component ledger.
- LEB therefore helps with local stress cases, but it does not prove NL-DualSmall.
