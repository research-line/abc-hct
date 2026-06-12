# T₅−2 TRE Transcript Checklist — Minimalbedingungen für ehrliches `trace_row_embedding=true`

Case `60168/raw`, `ℓ=5`, Claim `_results/trace_row_embedding_60168_raw_t5_partial.json`.

## Bereits erfüllt (real gebunden)
- [x] **Rowhash gesetzt** — `2578c0ce429aef9be25542091120652f1809745705c80d5053aea547c898e3f5`
      (Superset-Witness `s5_mixed_superset_witness_60168_raw_2026-05-14`).
- [x] **Tracewert** — `a_5(E)=2` ⟹ `T_5 − a_5(E) = T_5 − 2` (Paper B / BEWEISNOTIZ_2:48).
- [x] **Exportierte Sparse-Zeile** — `[[7037,3862],[7038,1],[7039,3862],[7040,3862],[7041,3862],[10015,2],[22583,3862]]`.
- [x] **Paarungsrolle** — Superset-Index 31680, im q=2-Paarungs-Witness mit `[[1,1],[1,0]]`, `saturates=true`.

## Noch offen — Formal-Origin (fehlt, anders als T₇)
- [ ] **source_manin_symbol** — welches Manin-Symbol erzeugt die Zeile.
- [ ] **formal_hecke_row** — explizite `T_5(source)`-Expansion (Coset-Matrizen) und `T_5(source) − 2·source`.
- [ ] **quotient_compression_mapping** — welche Roh-Terme auf welche Quotientenspalten gehen.
  → braucht einen dedizierten `mstar_s5_t5_row_origin`-Lauf (analog T₇ 2026-05-13).

## Noch offen — Konventions-Match gegen kanonisches Q_E (gekoppelt an CQ-3)
- [ ] **hecke_convention_verified** · [ ] **compression_convention_verified** ·
      [ ] **sign_convention_verified** · [ ] **integer_lift_convention_verified** ·
      [ ] **canonical_trace_module_binding.bound**.

## Reihenfolge
Formal-Origin ziehen → gegen die bekannte `2578c0ce…`-Zeile konsistenzprüfen → SC fixiert kanonisches Q_E →
Konventions-Match → `trace_row_embedding=true`. Dann T₅ + T₇ bereit fürs gekoppelte q=2-Gate. **Kein PCAT/FAQS/abc.**
