# R1 Faithful-AL Schur Certificate

Level: `109`
q: `3863`
Status: `computed`
faithful_al_certificate_found: `True`
operator_kind: `pari_tensor_solve_atkin_lehner_twist`
operator_is_identity: `False`
operator_kind_not_identity: `True`

## Certificate

```text
rank(A):          8 / 8
rank(A) full:     True
s_N:              41 mod 3863
s_N nonzero:      True
beta:             705
Q_B(schur):       722
Q_B(direct):       722
direct match:     True
B_AL rank:        9
```

Interpretation: this is a small-level faithful-AL smoke using
`pari_tensor_solve_atkin_lehner_twist`. It is not an identity-pairing
result.

## Input Hashes

```json
{
  "case_manifest_sha256": "0ceeb810133ec2a50aea14ad4567d3fefe6373eedcd728f813eddd07018e9bd0",
  "case_rows_sha256": "9b467722b611356cfbfa39059df23dbed10d7d6d5d5581ce1fe825ead4cecfdb",
  "pi_json_sha256": "933153c9e2ad52975fa656930992d47857e687b81316c4c93473e669d198bff0",
  "operator_script_sha256": "53b28b52cf7ecc23c86766e6459e8b5a9c7130e21feb3fdaeeb646388869f3d3",
  "C_source_repair_sha256": "e7601ea26bf9e19ef9927cd949fc4ef0ff724277eb911c0e1ae02e7a4bc9c7b0",
  "G_source_repair_sha256": "a2977cb5896858d26e0abde58666c0676a9e1601c70a58e7776d8ce630b950c0",
  "G_dense_comparison_sha256": "a2977cb5896858d26e0abde58666c0676a9e1601c70a58e7776d8ce630b950c0",
  "B_AL_sha256": "ae7b41c8926ad2d78bb31398ad8b6b7c5862689b844864c37f972c90bf1baf8c",
  "B_AL_P_sha256": "0331382ed94b2539d6d37d06ebd0339d59da0fe98d1f88595d6d4dee23651501",
  "B_AL_tensor_sha256": "2f88cd4001af929a5880e45cf89eb26ba4d8e84c5b664e4a81a178d14f959d7a",
  "B_AL_W_sha256": "f458d5ec59213c7b39061327be6b1b6b1ea5eefa50161e70f7840b2e92e7a289"
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
