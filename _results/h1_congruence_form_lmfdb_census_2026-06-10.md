# H1-Census: Rationale Kongruenzform zu f_E = 240672.g (2026-06-10)

**Frage:** Existiert eine rationale Newform g (= Isogenieklasse) auf einem
Level M | 240672 mit N/M prim (⟹ 2 Oldform-Kopien bei Level N), deren a_p
für die guten Primzahlen {5,7,11,13,17,19,29,31} mit f_E übereinstimmen?
(Kongruenz mod 3863 ⟺ Gleichheit, da |a_p| ≤ 2√31 ≈ 11 ≪ 3863.)

**Methode:** LMFDB-API `ec_curvedata` (ein Vertreter pro Isogenieklasse),
lokale Punktzählung über F_p. Script:
`_scripts/h1_congruence_form_lmfdb_census.py`. Maschinenlesbar:
`_results/h1_congruence_form_lmfdb_census_2026-06-10.json`.

**Referenz-Eigenwerte f_E:** a₅=2, a₇=0, a₁₁=0, a₁₃=−6, a₁₇=6, a₁₉=0, a₂₉=−2, a₃₁=4.

## Ergebnis: KEIN rationaler Match

| Level M | N/M | Isogenieklassen | Voll-Matches | Bestes Agreement |
|---|---|---:|---:|---|
| 120336 | 2 | 17 | 0 | 3/8 (120336.a/b/p) |
| 80224 | 3 | 2 | 0 | 0/8 |
| 10464 | 23 | 6 | 0 | 3/8 (10464.c/f) |
| 2208 | 109 | 10 | 0 | 2/8 (2208.i) |

**`any_rational_match = False`** über alle 35 Isogenieklassen.

## Interpretation

- Die **stärkste/einfachste H1-Variante** (g rational auf M=120336 oder einem
  anderen 2-Kopien-Level) ist **widerlegt**.
- Die per Ribet existierende Kongruenzform g ≡ f_E mod λ (λ | 3863) muss daher
  sein: **(a)** nicht-rationaler Galois-Orbit (auf einem Teiler-Level oder auf
  N selbst), **(b)** Eisenstein-Anteil (H3), oder **(c)** auf einem Level M mit
  σ₀(N/M) ≠ 2 (dann muss die Kopien-Buchhaltung für qdim=3 anders aufgehen).
- Nicht-rationale Orbits sind der **generische Fall** für Kongruenzprimes
  dieser Größe; das Negativ-Ergebnis ist konsistent mit der Obstruktions-These
  und ändert nichts an Gate-2-Logik (v3/q'=5077 bleibt der Entscheidungslauf).
- Prüfung nicht-rationaler Orbits auf 120336/80224/10464 erfordert
  Modular-Symbols-Compute (Level > 10000, nicht in LMFDB-CMF-DB); auf 2208
  wäre die CMF-DB nutzbar (Level ≤ 10000), aber 2208 ist nach diesem Census
  als Kurven-Level bereits ausgeschlossen und als Orbit-Level nachrangig
  (2 Kopien wie 120336, aber kleinerer Raum).

**Diagnostischer Status:** Identifikation von g bleibt offen — nicht
Gate-2-relevant, aber für Paper B (Drainage-/Kongruenzmodul-Kapitel) wertvoll.
