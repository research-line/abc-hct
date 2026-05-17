# H3a Reproducibility Batch 2026-05-17

This private repository batch contains curated computation scripts and result artifacts for the no-Magma H3a/Manin-Hecke route in the local abc/HCT project.

## Included

- `_scripts/mstar_h3a*`
- `_scripts/mstar_nomagma*`
- `_results/mstar_h3a_*` JSON/Markdown result summaries
- `_results/mstar_nomagma_*` JSON/Markdown result summaries where already curated
- H3a witness directories for:
  - `60168/raw`
  - `80224/raw`
  - `80224/anc`
  - `120336/raw`
  - `240672/raw`

## Main 240672/raw certificate

The current `240672/raw` standard run over `GF(3863)` reached:

- columns after two-term Manin relations: `126720`
- `T_5 - 2`: rank `126719`, quotient dimension `1`
- first `T_7 - 0` repair row: rank `126720`, quotient dimension `0`
- splitlast/order certificate: `certified=true`
- prefix profile: `T5` rows occupy the expected `0..d-2` prefix block with one `T7` repair row

Primary files:

- `_results/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.json`
- `_results/mstar_h3a_240672_raw_standard_auto_postprocess_2026-05-17_order.json`
- `_results/mstar_h3a_240672_raw_standard_prefix_profile_2026-05-17.json`
- `_results/rc3c_standard_witness_240672_raw_q3863_2026-05-16/`
- `_results/h3a_residue_line_witness_240672_raw_standard_auto_2026-05-17/`

## Excluded by policy

The following remain local/private and were not copied into this repository:

- `BEWEISNOTIZ*.md`
- `GAPS.md`, `TODO.md`, `MEMORY.md`
- `_proof-notes/`
- `_handoffs/`
- raw agent logs and transient process logs

## Pending

The Mac Studio independent rank verifier for `240672/raw` was still running at the time this batch was prepared. Its JSON/Markdown output should be added in a follow-up commit once present.
