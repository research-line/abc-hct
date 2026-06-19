# R1 Faithful-AL Schur Certificate

Level: `80224`
q: `5077`
Status: `blocked_matrix_free_schur_solver_required`
faithful_al_certificate_found: `False`
operator_kind: `pari_tensor_solve_atkin_lehner_twist`
operator_is_identity: `False`
operator_kind_not_identity: `True`

## Guard

The faithful-AL operator is implemented as a tensor solve and does not call M0._pari_pairing(), but this driver still refuses to build the full source+repair Gram matrix at this dimension. Wire the tensor-solve apply into a matrix-free Schur/Wiedemann solver before queuing the large certificate.

No identity-pairing fallback was used.

## Input Hashes

```json
{
  "case_manifest_sha256": "bc543938d47a718a098eb5fb9f084ad01ad42f1de17fa08efa0a41264e1ef35f",
  "case_rows_sha256": "d5179cc724245312725837cff05bec2d8413facf6207bde6f771ad9f9fcc791a",
  "pi_json_sha256": "db18f587fe4622f80e44409e0ee68c124b54f96c8a7a5dfa4b8c6babc12c8372",
  "operator_script_sha256": "53b28b52cf7ecc23c86766e6459e8b5a9c7130e21feb3fdaeeb646388869f3d3"
}
```

## Transcript Metadata

```json
{
  "scope": "large_guard_tensor_solve_operator_available_no_gram",
  "checkpoint_stride": 0,
  "matvec_checkpoints": [],
  "operator_logic": "P_solve_pari_tensor_W_Pt_no_pari_pairing",
  "large_next_step": "matrix_free_schur_or_wiedemann_solver",
  "seed_start": 1,
  "seed_count": 16,
  "suffix_terms": 4
}
```
