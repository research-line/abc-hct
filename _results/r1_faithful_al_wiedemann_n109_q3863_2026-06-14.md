# R1 Faithful-AL Schur Certificate

Level: `109`
q: `3863`
Status: `computed`
faithful_al_certificate_found: `True`
operator_kind: `pari_pairing_atkin_lehner_twist`
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

Interpretation: this is a dense small-level faithful-AL smoke using
`_pari_pairing` with the Atkin-Lehner twist. It is not an
identity-pairing result.

## Input Hashes

```json
{
  "case_manifest_sha256": "0ceeb810133ec2a50aea14ad4567d3fefe6373eedcd728f813eddd07018e9bd0",
  "case_rows_sha256": "9b467722b611356cfbfa39059df23dbed10d7d6d5d5581ce1fe825ead4cecfdb",
  "pi_json_sha256": "933153c9e2ad52975fa656930992d47857e687b81316c4c93473e669d198bff0",
  "operator_script_sha256": "bfec5d65a96947080b295eef61c81cc7250153f659202ccc193fd8f1e3b006cb",
  "C_source_repair_sha256": "e7601ea26bf9e19ef9927cd949fc4ef0ff724277eb911c0e1ae02e7a4bc9c7b0",
  "B_AL_sha256": "ae7b41c8926ad2d78bb31398ad8b6b7c5862689b844864c37f972c90bf1baf8c"
}
```

## Transcript Metadata

```json
{
  "scope": "dense_smoke_direct_schur_and_direct_inverse",
  "checkpoint_stride": 0,
  "matvec_checkpoints": [],
  "operator_logic": "pari_pairing_atkin_lehner_twist",
  "comparison": "schur_and_direct_inverse",
  "seed_start": 1,
  "seed_count": 16,
  "suffix_terms": 4
}
```
