# S5 Repair Certificate Bundle

Case: `N60168_raw_p2_s5_repair`

## Claim

The fixed-quotient S5 repair witness proves full rank modulo 2 for the 60168/raw quotient using T5 batches 1-13 plus T7 batch 1.

## Summary

- Level: `60168`
- Mode: `raw`
- Sign: `1`
- q: `3863`
- Repair prime: `2`
- ncols: `31680`
- Repair rows: `31680`
- Audit rank: `31680`
- Audit checks: `True`

## Files

| Role | Path | Bytes | SHA256 |
|---|---|---:|---|
| result-json | `_results\mstar_s5_repair_witness_60168_raw_p2_2026-05-13.json` | 19481 | `3f1857ab214655c91b6afaa0029f523c328456b66946dbbc27bbf9c429cc57b1` |
| result-md | `_results\mstar_s5_repair_witness_60168_raw_p2_2026-05-13.md` | 1593 | `9029b94ce90c1f915051b7d93f9f3fd0d858f24dd974bedbe050e596e8c00541` |
| audit-json | `_results\mstar_s5_repair_witness_60168_raw_p2_audit_2026-05-13.json` | 466 | `60f1e18580399d3c9d396f94745a1e7fde596a2882dd54489c376ddb94ce9654` |
| audit-md | `_results\mstar_s5_repair_witness_60168_raw_p2_audit_2026-05-13.md` | 242 | `7c86ddc1ff74797190e9570ea3560bfeb4c9d36880bd16b370ac2e59c0918504` |
| run-log | `_results\mstar_s5_repair_witness_60168_raw_p2_2026-05-13.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| run-err | `_results\mstar_s5_repair_witness_60168_raw_p2_2026-05-13.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| script | `_scripts\mstar_s5_fixedquotient_full_rank.py` | 21007 | `76f90998181af380e14491d0ff9ae21480f5f10c75fc30fdaa5b391f1acf291d` |
| script | `_scripts\mstar_s5_repair_witness_audit.py` | 6899 | `520cad58b5cdca98f54ebf6fff13d949733a08ad2d0087f612159446e0860c9f` |
| script | `_scripts\mstar_s5_repair_certificate_bundle.py` | 6612 | `08f69d1cedd6171e4477ea8ce1d1d5b11101009a21393718c4f213137b34bc98` |

## Trees

| Role | Path | Files | Bytes | Tree SHA256 |
|---|---|---:|---:|---|
| repair-witness | `_results\s5_repair_witness_60168_raw_p2_2026-05-13` | 2 | 8237171 | `6d2e1196c78ba3b00a0947b54efbd0de85b50eb3aabcd78dfed76bf1aeeafc9d` |
| repair-transcript | `_results\s5_repair_transcript_60168_raw_T5b13_T7b1_2026-05-13` | 31 | 16026571 | `3691413ea2973ce8c5ee12bf4a91777310812631b1bb7515a2320d7a4b05aa52` |

## Verification Notes

- Result JSON/MD records the fixed-quotient repair computation.
- Repair witness tree contains exported independent rows over the fixed GF(3863) quotient.
- Repair transcript tree contains per-stage rowhash indexes, including T7 batch 1.
- Audit JSON/MD recomputes rank modulo 2 and checks transcript binding.
- Run err file is expected to be empty.
