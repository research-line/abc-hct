# R1 faithful-AL 80224/anc Preflight

Status: `ready_for_mac_cache_gate`
Claim-Upgrade: `false`

## Kernergebnis

- Lokaler Lauf: keiner. Dieses Preflight liest nur Metadaten und JSON-Dateien.
- `80224/anc`-Standardinput ist über q=`3863` vorhanden.
- Quotient: ncols `10568`, rank `10567`, kernel dim `1`.
- `ready_for_al_scalar`: `True`; `source_annihilated`: `True`.
- Alte finite/Identity-Queue-Jobs sind blockiert: `True`.

## Feldentscheidung

Empfehlung: `use_q3863_cache_gate_first` mit q=`3863`.

Der vollständige anc-Standardinput liegt bereits über q=3863 vor. Der raw-Abschluss über q=5077 ist ein gültiger Vergleichsanker, aber keine Voraussetzung für ein anc-Schur-Gate über einem endlichen Feld. Daher zuerst q=3863-Cache-Gates laufen lassen; q=5077-Remod bleibt für Redundanz, Uniformisierung oder ein Scheitern von q=3863 reserviert.

## Gate-Prüfungen

- `pass` — case_dir_present: _results\h3a_residue_line_witness_80224_anc_standard_2026-05-16\N80224_anc_sign1_splitlast
- `pass` — manifest_present: _results\h3a_residue_line_witness_80224_anc_standard_2026-05-16\N80224_anc_sign1_splitlast\manifest.json
- `pass` — rows_present: _results\h3a_residue_line_witness_80224_anc_standard_2026-05-16\N80224_anc_sign1_splitlast\mixed_rows.jsonl
- `pass` — manifest_level_80224: 80224
- `pass` — manifest_mode_anc: anc
- `pass` — manifest_q_3863: 3863
- `pass` — pi_json_present: _results\mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json
- `pass` — pi_level_80224: 80224
- `pass` — pi_mode_anc: anc
- `pass` — pi_q_3863: 3863
- `pass` — ready_for_al_scalar: True
- `pass` — source_annihilated: True
- `pass` — quotient_ncols_10568: 10568
- `pass` — quotient_rank_10567: 10567
- `pass` — kernel_dim_1: 1
- `pass` — free_columns_10568: 10568
- `pass` — repair_entries_present: 6
- `pass` — driver_present: _scripts\mstar_h3a_qb3_wiedemann_production.sage
- `pass` — old_queue_jobs_blocked: blocked; blocked
- `pass` — raw_reference_closed: found=True; mode=matrix-free-schur
- `pass` — rows_sha256_matches_manifest: computed=df74a6bd8b3e4fee7c11528ebb3a579d434da593c48d96e01d14918e39115c15; manifest=df74a6bd8b3e4fee7c11528ebb3a579d434da593c48d96e01d14918e39115c15

## Mac-Gate-Sequenz

1. Plusbasis-Cache-Gate mit `--bal-stop-after-plus-cache`.
2. Tensor/W/A-matvec-Cache-Gate mit `--matrix-free-schur-preflight-only`.
3. Full-Job erst danach mit `--matrix-free-schur-allow-large`.

Der alte `qb3_wiedemann_80224_anc_2026-05-23`-Job bleibt blockiert; sein `accepted_certificate_found`-Schema ist kein R1-faithful-AL-Nachweis.
