# RC4 Certificate Bundle

Case: `N60168_raw_sign1_rc3d`

## Claim

The rowhash-bound source-row witness proves full rank of the 60168/raw quotient over GF(3863), so the quotient is zero at the recorded final stage.

## Summary

- Level: `60168`
- Mode: `raw`
- Sign: `1`
- q: `3863`
- Final stage: `T_5_minus_2_batch_13`
- Final quotient dimension: `0`
- Audit rank: `31680`
- Audit checks: `True`

## Files

| Role | Path | Bytes | SHA256 |
|---|---|---:|---|
| result-json | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_2026-05-12.json` | 4945 | `660fbe7b46e8b890f1a94d78ea56c792559f3d2841f40f267e55950cbcabc571` |
| result-md | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_2026-05-12.md` | 1790 | `de88b8806a21bdd1dee3d99d41b9bb17e9686774d2082e2cf3a30d60db702dce` |
| audit-json | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_audit_2026-05-12.json` | 509 | `62f49fde8835652263f93c7ceb4082d094d45699f35477a3403925640a0cbb81` |
| audit-md | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_audit_2026-05-12.md` | 562 | `03ffaacdeaa6784c932c91797240b1204ed3bceb4b9e272b311f16618a0d8a95` |
| run-log | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_2026-05-12.log` | 5717 | `db147b59b4aa8bc046151bfdff564f41dcd9054d41db73fc587ea8ee4da25994` |
| run-err | `_results\mstar_nomagma_rc3d_rowhash_60168_raw_2026-05-12.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| script | `_scripts\mstar_nomagma_sparse_hecke_quotient.py` | 44231 | `5f6a452acb282944e0b9c30b0a064ec65651a14dea3fccd253a96bc70b08cb71` |
| script | `_scripts\mstar_rc3_source_witness_audit.py` | 12696 | `05c2e8183839f3888ddc094996402d3839985c00b70c5f72262ccbcd7b44c51c` |
| script | `_scripts\mstar_rc4_certificate_bundle.py` | 6959 | `1fda0b78f4a84a2de624e59d723d9a9c772fcaefc39ae191ac1bfda9797ac952` |

## Trees

| Role | Path | Files | Bytes | Tree SHA256 |
|---|---|---:|---:|---|
| source-witness | `_results\rc3d_rowhash_source_witness_60168_raw_2026-05-12` | 2 | 8228735 | `a009ee6aa102f503c526c9ebf84939427b1bd2573c0ad8ac80ebe55241a6b440` |
| rowhash-transcript | `_results\rc3d_rowhash_transcript_60168_raw_2026-05-12` | 29 | 15912428 | `cca50f7399fee682d8940bc7bbff6fc3b2d9aefeeacc0b048b26b126d47e4354` |

## Verification Notes

- Result JSON/MD records the killed quotient and stage history.
- Audit JSON/MD recomputes rank with Sage matrix rank and checks transcript binding.
- Source-witness tree contains the exported independent original rows.
- Transcript tree contains per-stage rowhash indexes and digest files.
- Run err file is expected to be empty.
