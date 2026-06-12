# M*: Sage-Optimierungs-API-Probe

Datum: 2026-05-10

## Kurzbefund

- Probes: 5.
- OK: 5.
- Timeouts: 0.
- Errors: 0.

## Ergebnisse

| Probe | Level | Status | Dimensionen | Zeit | Hinweis |
|---|---:|---|---|---:|---|
| cuspforms_newspace_methods | 109 | ok | total_dimension=8; new_dimension=8 | 0.371 | Atkin-Methoden: _compute_atkin_lehner_matrix, atkin_lehner_operator |
| cuspforms_newspace_hecke_matrix | 109 | ok | total_dimension=8; new_dimension=8 | 0.284 |  |
| modularsymbols_QQ_newspace_hecke_matrix | 109 | ok | ambient_dimension=17; cuspidal_dimension=16; new_dimension=16 | 0.092 | Atkin-Methoden: _compute_atkin_lehner_matrix, atkin_lehner_operator |
| modularsymbols_GF_newspace_hecke_matrix | 11 | ok | ambient_dimension=3; cuspidal_dimension=2; new_dimension=2 | 0.088 | Atkin-Methoden: _compute_atkin_lehner_matrix, atkin_lehner_operator |
| modularsymbols_GF_newspace_hecke_matrix | 109 | ok | ambient_dimension=17; cuspidal_dimension=16; new_dimension=16 | 0.083 | Atkin-Methoden: _compute_atkin_lehner_matrix, atkin_lehner_operator |

## Interpretation

Diese Probe entscheidet nur über verfügbare Sage-APIs auf kleinen Levels.
Ein positiver kleiner Test heißt nicht, dass die Restlevels leicht werden.
Ein Timeout oder Fehler schließt aber eine Optimierungsroute als naiv
nutzbar aus.
