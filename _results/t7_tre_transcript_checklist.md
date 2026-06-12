# T₇ TRE Transcript Checklist — Minimalbedingungen für ehrliches `trace_row_embedding=true`

Case `60168/raw`, `ℓ=7`, Claim `_results/trace_row_embedding_60168_raw_t7_partial.json`.
Erst wenn **alle** Häkchen sitzen, darf der TRE-Verifier `trace_row_embedding=true` akzeptieren.

## Bereits erfüllt (Witness 2026-05-13)
- [x] **Transcript-Witness gezogen** — `mstar_s5_t7_row_origin_60168_raw_p7_i1_2026-05-13.json`.
- [x] **Rowhash gesetzt** — `a7c9b47d334f80801465ad60f61304c2e9ff7f4991419087c25105b801bbdabf`.
- [x] **Tracewert** — `a_7(E)=0` ⟹ `T_7 − a_7(E) = T_7` (Paper B / BEWEISNOTIZ_2:48; Witness `ap=0`).
- [x] **Formale Hecke-Zeile** — 8 Coset-Matrizen, `2(1,0)+(1,1)+…+(1,6)`; reduziert `2col_0 − col_1 − … − col_5`.

## Noch offen — Konventions-Match gegen kanonisches Q_E
- [ ] **hecke_convention_verified** — der kanonische HCT-Trace-Quotient nutzt **denselben** Hecke-Operator
      T₇ mit derselben Normierung/Trace-Subtraktion wie im Witness (`[1,j,0,7]`/`[7,0,0,1]`, `ap=0`).
- [ ] **compression_convention_verified** — die Quotienten-Kompression (welche Roh-Terme überleben:
      `(1,1)↦None`, `(1,2..6)↦col 1..5`) entspricht der kanonischen Quotientenbildung.
- [ ] **sign_convention_verified** — `sign=+1`-Orientierung stimmt mit der kanonischen Konvention überein
      (vgl. `splitlast`/`sign1` aus `N60168_raw_sign1_splitlast`).
- [ ] **integer_lift_convention_verified** — balancierter Lift `3862 ≡ −1 mod 3863` ist die kanonische
      Integer-Lift-Konvention (CRT-Normalform), nicht ein opportunistischer Repräsentant.
- [ ] **canonical_trace_module_binding.bound** — Zeile als Klasse **im kanonischen** M_E gebunden (hängt an CQ-3).

## Abhängigkeit
Die letzten fünf Häkchen setzen die **Source-Canonicality (CQ-3)** voraus (das kanonische Q_E/M_E muss
fixiert sein, bevor „dieselbe Konvention wie das kanonische Q_E" überhaupt prüfbar ist). ⟹ T₇-TRE und SC
sind gekoppelt; reihenfolge: SC fixiert Q_E → dann Konventions-Match → dann `trace_row_embedding=true`.

## Danach
Analog `T_5 − 2` (`a_5(E)=2`, eigener Witness ziehen/binden). Beide TRE-grün ⟹ q=2-PSC-2-Zahn
(`[[1,1],[1,0]]`) wird canonical-fähig. **Kein PCAT/FAQS/abc.**
