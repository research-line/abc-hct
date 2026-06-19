# R1 Faithful-AL 80224/raw Preflight

Status: `ready_for_draft_job`

## Befund

- Lokaler Lauf: keiner. Dieses Preflight liest nur Metadaten und JSON-Dateien.
- Inputs bereit: `True`.
- Case: `_results\h3a_residue_line_witness_80224_raw_remod_q5077_2026-05-23\N80224_raw_sign1_splitlast`; Level `80224`, q `5077`, ncols `31680`.
- Pi-JSON: `_results\mstar_h3a_restline_kernel_quotient_remod_q5077_80224_raw_mac_2026-05-24.json`; free columns `10568`, ready_for_al_scalar `True`.
- Vorhandener Identity-Nachweis: accepted `True`, pairing_kind `identity`, degree `10567` / target `10567`.

## Entscheidung

Der vorhandene 80224/raw-Nachweis ist ein Identity-Pairing-Fingerprint und darf nicht als faithful-AL-Zertifikat gezählt werden. Für R1 ist ein neuer Mac-Job nötig, der `rank(A)` und `s_N != 0` mit echtem `C_src` und nicht-identischem AL-Operatorpfad belegt.

## Queue-Sicherheit

- Alter Queue-Job: `_compute_queue\jobs\qb3_wiedemann_80224_raw_2026-05-23.json`.
- Status: `blocked`.
- Identity-artig: `True`.
- Nicht reaktivieren, solange der Operatorpfad nicht geändert ist.

## Nächster Schritt

Einen draft/blocked Mac-Job für `80224/raw` anlegen oder zuerst eine kurze Theorie-/Design-Note zum matrixfreien faithful-AL-Operator schreiben. Der Laptop bleibt für Sage-Läufe gesperrt.
