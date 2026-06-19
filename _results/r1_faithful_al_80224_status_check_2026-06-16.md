# R1 faithful-AL 80224/raw Statuscheck

Datum: `2026-06-16`
Verdikt: `running_or_incomplete`
Claim-Upgrade: `false`

## Laufstatus

- Phase: `matrix_free_schur_rank_seed`
- Sekunden: `110087.798`
- Zielrang: `10567`
- Sequenzlänge: `21138` (erwartet `21138`)
- Pairing: `_pari_tensor_solve`
- Primary Pairing materialisiert: `False`

## Prüfungen

- `pass` — status_json_present: _results\r1_faithful_al_80224_raw_2026-06-14.status.json
- `pass` — canonical_script_present: _scripts\mstar_h3a_qb3_wiedemann_production.sage
- `pass` — canonical_script_has_new_hash: 6f98fe6fe96a45668e859666fd4389d9ef9369955439f5d5bcf3d9d4ee6916a5
- `pass` — asus_alias_matches_canonical: canonical=6f98fe6fe96a45668e859666fd4389d9ef9369955439f5d5bcf3d9d4ee6916a5; alias=6f98fe6fe96a45668e859666fd4389d9ef9369955439f5d5bcf3d9d4ee6916a5
- `pass` — sequence_length_matches_rank_target: sequence_length=21138; expected=21138
- `pass` — status_pairing_tensor_solve: _pari_tensor_solve
- `pass` — status_primary_pairing_not_materialized: False
- `fail` — final_json_present: _results\r1_faithful_al_80224_raw_2026-06-14.json
- `fail` — final_md_present: _results\r1_faithful_al_80224_raw_2026-06-14.md

## Nächster Schritt

Keinen lokalen Sage-Lauf starten. Auf Mac-Final-JSON/MD warten; danach faithful_al_certificate_found=true, rank_A_full=true, rank_A=target, schur_nonzero=true und nicht-identische Tensor-Solve-Operator-Metadaten verlangen.
