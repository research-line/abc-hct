# Q_B-3 Wiedemann Production Runbook

Datum: `2026-05-23`

Dieses Ledger startet keinen Großlauf. Es legt nur fest, was ein
produktionsfähiges Zertifikat für den Source-Gram-Rang liefern muss.

## Algorithmus

- Build the matrix-free operator A v = C_source B_AL C_source^T v.
- For each deterministic seed, generate s_k = u^T A^k v.
- Run Berlekamp-Massey on the scalar sequence.
- Accept a seed only if degree = target_rank and the final coefficient is nonzero.
- Export the full sequence and connection coefficients for local verification.

## Fälle

| Level | Mode | q | target rank | seq/seed | matvecs/seed | seed budget | max matvecs |
|---:|---|---:|---:|---:|---:|---:|---:|
| 80224 | raw | 3863 | 10567 | 21138 | 21137 | 16 | 338192 |
| 80224 | anc | 3863 | 10567 | 21138 | 21137 | 16 | 338192 |

## Pflichtfelder

Jedes Produktionszertifikat muss mindestens diese Felder enthalten:

```text
level
mode
q
target_rank
seed
degree
sequence_length
connection_coefficients_mod_q
sequence_mod_q
case_manifest_sha256
pi_json_sha256
operator_script_sha256
```

## Lokale Verifikation

### 80224 / raw

```powershell
python ./_scripts/qb3_wiedemann_certificate_verify.py --certificate ./_results/mstar_h3a_qb3_wiedemann_certificate_80224_raw_2026-05-23.json --expected-rank 10567 --expected-q 3863 --out-json ./_results/qb3_wiedemann_certificate_verify_80224_raw_2026-05-23.json --out-md ./_results/qb3_wiedemann_certificate_verify_80224_raw_2026-05-23.md
```

### 80224 / anc

```powershell
python ./_scripts/qb3_wiedemann_certificate_verify.py --certificate ./_results/mstar_h3a_qb3_wiedemann_certificate_80224_anc_2026-05-23.json --expected-rank 10567 --expected-q 3863 --out-json ./_results/qb3_wiedemann_certificate_verify_80224_anc_2026-05-23.json --out-md ./_results/qb3_wiedemann_certificate_verify_80224_anc_2026-05-23.md
```

## Beweislogik

Ein akzeptiertes Zertifikat beweist den portablen Sequenzteil:
`degree = n` und letzter Rekurrenzkoeffizient ungleich null. Zusammen
mit dem authentifizierten Matvec-Transcript für
`A=C_source B_AL C_source^T` ist das die rechnerische Form von
`rank(A)=n`.
