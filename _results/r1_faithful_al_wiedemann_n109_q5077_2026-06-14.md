# R1 Faithful-AL Schur Certificate

Level: `109`
q: `5077`
Status: `computed`
faithful_al_certificate_found: `True`
operator_kind: `pari_pairing_atkin_lehner_twist`
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

Interpretation: this is a dense small-level faithful-AL smoke using
`_pari_pairing` with the Atkin-Lehner twist. It is not an
identity-pairing result.

## Input Hashes

```json
{
  "case_manifest_sha256": "dc0148f87e3d778d0ae2df48d766cb40f95eaf18bafab0cdeeeaaba69993036e",
  "case_rows_sha256": "7c7b3347fe23e145e6761614d54471f9749ecb04a73f8ceedc9836f7cb79d6b3",
  "pi_json_sha256": "5a6dab709fd8fc667239f00ce0f974f6576425dba620cc8cc5adbf66cbd55af4",
  "operator_script_sha256": "bfec5d65a96947080b295eef61c81cc7250153f659202ccc193fd8f1e3b006cb",
  "C_source_repair_sha256": "ecc0feca9d3e91bc5e12f27adeb25439207402b64ab67c0c53f7496c83f32c4c",
  "B_AL_sha256": "b556231a4fd04d3497c057103b2e87e4fdfda455ca69125e12e2000d0995c05b"
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
