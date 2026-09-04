# R1 Faithful-AL 80224/raw — Field Check

Date: 2026-06-27
Input: `_results/r1_faithful_al_80224_raw_2026-06-14.json`

## Result

**All critical checks pass:** `True`

## Summary

| Field | Value |
|---|---|
| Level | 80224 |
| Mode | raw |
| q | 5077 |
| rank(A) | 10567 / 10567 |
| s_N signed | 1789 |
| Q_B(schur) signed | 1243 |
| seconds | 756239.559 |
| operator_kind | pari_tensor_solve_atkin_lehner_twist |
| pairing_kind | _pari_tensor_solve |

## Checks

```json
{
  "file_exists_and_readable": true,
  "top_level_faithful_al_certificate_found": true,
  "rank_A_equals_target": true,
  "rank_A_full": true,
  "rank_certificate_connection_verified": true,
  "rank_certificate_constant_nonzero": true,
  "rank_certificate_degree_equals_target": true,
  "solve_certificate_connection_verified": true,
  "solve_certificate_vector_relation_zero": true,
  "solve_certificate_solve_residual_zero": true,
  "schur_nonzero": true,
  "q_is_5077": true,
  "mode_raw": true,
  "level_80224": true,
  "operator_kind_not_identity": true,
  "primary_pairing_materialized_false": true,
  "input_hashes_present": true,
  "operator_factor_metadata_present": true
}
```

## Caveats

```json
{
  "direct_matches_schur": null,
  "note": "direct_matches_schur=false is expected for matrix-free-schur (no dense G materialized); schur_nonzero=true is the operative gate"
}
```
