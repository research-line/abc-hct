# Task 1304 – R1-Mac-Verifier-Zertifikatsvalidierung

Datum: `2026-08-12`

## Ergebnis

Die vorliegende Mac-Ausgabe ist strukturell als Matrix-Free-Schur-Zertifikat
abgeschlossen: `faithful_al_certificate_found=true`, `rank_A_full=true`,
`rank_A=rank_A_target=10567`, `schur_nonzero=true` und
`primary_pairing_materialized=false`. Die Rangsequenz hat die erwartete Länge
`2*10567+4 = 21138`; Rang- und Solve-Zertifikat melden verifizierte
Verbindungskoeffizienten, eine Nichtnull-Konstante sowie Null-Relation und
Null-Rest.

Geprüfte Nachweise:

- [`r1_faithful_al_80224_raw_2026-06-14.json`](r1_faithful_al_80224_raw_2026-06-14.json)
- [`r1_faithful_al_80224_raw_2026-06-14.status.json`](r1_faithful_al_80224_raw_2026-06-14.status.json)
- [`r1_faithful_al_80224_raw_2026-06-14.md`](r1_faithful_al_80224_raw_2026-06-14.md)
- [`r1_faithful_al_80224_status_check_task1304_2026-08-12.json`](r1_faithful_al_80224_status_check_task1304_2026-08-12.json)

## Provenienzgrenze

Der Check bestätigt das vorhandene Remote-Ergebnis, erzeugt keinen neuen
Sage-/Mac-Lauf und hebt den wissenschaftlichen Claim nicht an. Die im Ergebnis
eingebettete Remote-Skript-Hashbindung (`6f98fe…`) weicht vom aktuellen lokalen
Skript-Hash (`0a2c2b…`) ab; außerdem ist der referenzierte Remod-Inputordner
lokal nicht vorhanden. Deshalb ist die lokale Reproduzierbarkeit gegen den
aktuellen Quellstand offen, obwohl das archivierte Zertifikat intern alle oben
genannten Felder erfüllt.

