# R1 faithful-AL 80224/raw Statuscheck

Datum: `2026-06-16`
Verdikt: `faithful_al_certificate_ready`
Claim-Upgrade: `false`

## Laufstatus

- Phase: `finished`
- Sekunden: `756239.565`
- Zielrang: `10567`
- Sequenzlänge: `21138` (erwartet `21138`)
- Pairing: `_pari_tensor_solve`
- Primary Pairing materialisiert: `False`

## Prüfungen

- `pass` — status_json_present: _results\r1_faithful_al_80224_raw_2026-06-14.status.json
- `pass` — canonical_script_present: _scripts\mstar_h3a_qb3_wiedemann_production.sage
- `pass` — canonical_script_has_new_hash: 0a2c2b6e7a98f7c65d179ca76c61bf363e4f64f51dd7166e5293e6e20aa6890e
- `unknown` — asus_alias_matches_canonical: canonical=0a2c2b6e7a98f7c65d179ca76c61bf363e4f64f51dd7166e5293e6e20aa6890e; alias=None
- `pass` — sequence_length_matches_rank_target: sequence_length=21138; expected=21138
- `pass` — status_pairing_tensor_solve: _pari_tensor_solve
- `pass` — status_primary_pairing_not_materialized: False
- `pass` — final_json_present: _results\r1_faithful_al_80224_raw_2026-06-14.json
- `pass` — final_md_present: _results\r1_faithful_al_80224_raw_2026-06-14.md
- `pass` — faithful_al_certificate_found: True
- `pass` — rank_A_full: True
- `pass` — rank_A_matches_target: rank_A=10567; target=10567
- `pass` — schur_nonzero: True
- `pass` — operator_kind: pari_tensor_solve_atkin_lehner_twist
- `pass` — primary_pairing_not_materialized: False

## Nächster Schritt

Keinen lokalen Sage-Lauf starten. Auf Mac-Final-JSON/MD warten; danach faithful_al_certificate_found=true, rank_A_full=true, rank_A=target, schur_nonzero=true und nicht-identische Tensor-Solve-Operator-Metadaten verlangen.
