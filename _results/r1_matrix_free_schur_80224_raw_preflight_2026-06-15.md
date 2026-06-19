# R1 Matrix-Free Schur 80224/raw Preflight

Status: `stopped_preflight_plus_basis_timeout`

Der Preflight wurde nach ungefähr 30 Minuten bewusst gestoppt. Er erreichte die Phase `building_B_AL_plus_basis` und kam nicht bis `_pari_tensor`, Atkin-Lehner `W`, deterministischem `bal_apply` oder `A_matvec`.

```text
level:                       80224
q:                           5077
operator_kind:               pari_tensor_solve_atkin_lehner_twist
primary_pairing_materialized: false
last phase:                  building_B_AL_plus_basis
last status seconds:         839.608
observed stop seconds:       1828
sage_dim:                    10568
free_to_sage_nnz:            514410
sign0_dim:                   21121
source_nnz:                  1623421
source_max_row_len:          7774
```

Interpretation: Der neue matrixfreie Schur-Code ist auf N=109 grün, aber bei `80224/raw` liegt der nächste Engpass vor `_pari_tensor`, nämlich im sign0-Plusbasis-Aufbau. Der Job bleibt blockiert; nicht auf `queued` setzen.

## Input Hashes

```json
{
  "case_manifest_sha256": "bc543938d47a718a098eb5fb9f084ad01ad42f1de17fa08efa0a41264e1ef35f",
  "case_rows_sha256": "d5179cc724245312725837cff05bec2d8413facf6207bde6f771ad9f9fcc791a",
  "pi_json_sha256": "db18f587fe4622f80e44409e0ee68c124b54f96c8a7a5dfa4b8c6babc12c8372",
  "operator_script_sha256": "fed7cb1604653d14af2dff4ccc68e828787860ad643c340406375d9082903d6c",
  "status_json_sha256": "5fbe2c4e6adbc65990f17e98f2cbc9506ecffba1d57ddc895ed91cac5a028d47",
  "log_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
