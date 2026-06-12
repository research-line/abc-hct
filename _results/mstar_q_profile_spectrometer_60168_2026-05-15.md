# q-Profile Spectrometer

Date: 2026-05-15

Diagnostic only: `qdim` and `trace_codim_S` are quotient-profile metrics, not direct valuations of `Q_ad^exc`.

| source | q | level | mode | operators | stages | final qdim | trace_codim_S | residual fraction | extra batches (tail estimate) |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| mstar_nomagma_sparse_hecke_quotient_60168_raw_T5_quotient_numpy_mac_2026-05-10.json | 3863 | 60168 | raw | T_5-2 | 13 | 0 | 10576 | 0.000000 | 0 |
| mstar_nomagma_qdep_60168_raw_q997_T5cap14_2026-05-15.json | 997 | 60168 | raw | T_5-2 | 14 | 1336 | 9240 | 0.126324 | 4 |
| mstar_nomagma_qdep_60168_raw_q997_T5cap3_T7T11T13_2026-05-15.json | 997 | 60168 | raw | T_11-0, T_13--6, T_5-2, T_7-0 | 12 | 6 | 10570 | 0.000567 | 1 |

## Operator reductions

### mstar_nomagma_sparse_hecke_quotient_60168_raw_T5_quotient_numpy_mac_2026-05-10.json
- `T_5-2`: reduction `10576` over `13` batches
- stages/log(level): `1.181`

### mstar_nomagma_qdep_60168_raw_q997_T5cap14_2026-05-15.json
- `T_5-2`: reduction `9240` over `14` batches
- stages/log(level): `1.272`

### mstar_nomagma_qdep_60168_raw_q997_T5cap3_T7T11T13_2026-05-15.json
- `T_11-0`: reduction `2789` over `3` batches
- `T_13--6`: reduction `2203` over `3` batches
- `T_5-2`: reduction `2789` over `3` batches
- `T_7-0`: reduction `2789` over `3` batches
- stages/log(level): `1.090`

## Reading

- `q=3863` is spike-like on `N=60168/raw`: `T_5` alone reaches zero.
- `q=997` is generic-like: `T_5` alone leaves a substantial rest, while `T_5,T_7,T_11,T_13` reduce the rest to `6`.
- The useful invariant is therefore a q-dependent residual profile, not a q-independent kill depth.
