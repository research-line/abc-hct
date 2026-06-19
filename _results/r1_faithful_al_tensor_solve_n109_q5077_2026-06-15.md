# R1 Faithful-AL Schur Certificate

Level: `109`
q: `5077`
Status: `computed`
faithful_al_certificate_found: `True`
operator_kind: `pari_tensor_solve_atkin_lehner_twist`
operator_is_identity: `False`
operator_kind_not_identity: `True`

## Certificate

```text
rank(A):          8 / 8
rank(A) full:     True
s_N:              1567 mod 5077
s_N nonzero:      True
beta:             -1382
Q_B(schur):       -1250
Q_B(direct):       -1250
direct match:     True
B_AL rank:        9
```

Interpretation: this is a small-level faithful-AL smoke using
`pari_tensor_solve_atkin_lehner_twist`. It is not an identity-pairing
result.

## Input Hashes

```json
{
  "case_manifest_sha256": "dc0148f87e3d778d0ae2df48d766cb40f95eaf18bafab0cdeeeaaba69993036e",
  "case_rows_sha256": "7c7b3347fe23e145e6761614d54471f9749ecb04a73f8ceedc9836f7cb79d6b3",
  "pi_json_sha256": "5a6dab709fd8fc667239f00ce0f974f6576425dba620cc8cc5adbf66cbd55af4",
  "operator_script_sha256": "53b28b52cf7ecc23c86766e6459e8b5a9c7130e21feb3fdaeeb646388869f3d3",
  "C_source_repair_sha256": "ecc0feca9d3e91bc5e12f27adeb25439207402b64ab67c0c53f7496c83f32c4c",
  "G_source_repair_sha256": "2f9056ba915aba9644d9b4b4565f90fabd7ab8cf4e36244d0dd763f988f8587d",
  "G_dense_comparison_sha256": "2f9056ba915aba9644d9b4b4565f90fabd7ab8cf4e36244d0dd763f988f8587d",
  "B_AL_sha256": "b556231a4fd04d3497c057103b2e87e4fdfda455ca69125e12e2000d0995c05b",
  "B_AL_P_sha256": "e200b0c11561df5dcf58eb67155a18c2c1fa61673292897b2f79b12af704cf60",
  "B_AL_tensor_sha256": "cd811ba3fdeeca792798ae2f713e2f597737ad8cbfad93eb496d0056fcc9384a",
  "B_AL_W_sha256": "8651b7248ee799bf6de2d83516797afd61a63467bce1eeb0505a64d86060d136"
}
```

## Transcript Metadata

```json
{
  "scope": "tensor_solve_smoke_schur_with_optional_dense_comparison",
  "checkpoint_stride": 0,
  "matvec_checkpoints": [],
  "operator_logic": "P_solve_pari_tensor_W_Pt_no_pari_pairing",
  "comparison": "schur_and_optional_dense_pairing_comparison",
  "seed_start": 1,
  "seed_count": 16,
  "suffix_terms": 4
}
```
