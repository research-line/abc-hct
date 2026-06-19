# R1 Faithful-AL Schur Certificate

Level: `80224`
q: `5077`
Status: `blocked_matrix_free_faithful_al_required`
faithful_al_certificate_found: `False`
operator_kind: `not_constructed`
operator_is_identity: `False`
operator_kind_not_identity: `True`

## Guard

Quotient dimension exceeds dense guard. Refusing to fall back to identity-pairing; implement a matrix-free faithful-AL operator before running this level.

No identity-pairing fallback was used.

## Input Hashes

```json
{
  "case_manifest_sha256": "bc543938d47a718a098eb5fb9f084ad01ad42f1de17fa08efa0a41264e1ef35f",
  "case_rows_sha256": "d5179cc724245312725837cff05bec2d8413facf6207bde6f771ad9f9fcc791a",
  "pi_json_sha256": "db18f587fe4622f80e44409e0ee68c124b54f96c8a7a5dfa4b8c6babc12c8372",
  "operator_script_sha256": "bfec5d65a96947080b295eef61c81cc7250153f659202ccc193fd8f1e3b006cb"
}
```

## Transcript Metadata

```json
{
  "scope": "guard_only_no_matvec",
  "checkpoint_stride": 0,
  "matvec_checkpoints": [],
  "operator_logic": "faithful_al_required_identity_fallback_refused",
  "seed_start": 1,
  "seed_count": 16,
  "suffix_terms": 4
}
```
