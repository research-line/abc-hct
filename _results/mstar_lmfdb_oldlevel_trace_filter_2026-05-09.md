# M* LMFDB Oldlevel Trace Filter

Datum: 2026-05-09
Quelle: `LMFDB mf_newforms`

## Ergebnis

- Angefragte Levels: 13
- Geladene Levels: 13
- Trivial-Charakter-Orbit/Orientierungs-Tests: 238
- Trace-Survivor: 0

## Level-Summary

| Level | Faktor | Newdim | Orbitdim geladen | Abdeckung | Tests | Survivor |
|---:|---:|---:|---:|---|---:|---:|
| 109 | `109` | 8 | 8 | orbit-traces | 6 | 0 |
| 218 | `2 * 109` | 10 | 10 | orbit-traces | 10 | 0 |
| 327 | `3 * 109` | 19 | 19 | orbit-traces | 8 | 0 |
| 872 | `2^3 * 109` | 27 | 27 | orbit-traces | 12 | 0 |
| 1744 | `2^4 * 109` | 54 | 54 | orbit-traces | 34 | 0 |
| 2507 | `23 * 109` | 199 | 199 | orbit-traces | 10 | 0 |
| 3488 | `2^5 * 109` | 108 | 108 | orbit-traces | 20 | 0 |
| 15042 | `2 * 3 * 23 * 109` | 397 | 397 | orbit-traces | 56 | 0 |
| 20056 | `2^3 * 23 * 109` | 594 | 594 | orbit-traces | 18 | 0 |
| 40112 | `2^4 * 23 * 109` | 1188 | 1188 | orbit-traces | 64 | 0 |
| 60168 | `2^3 * 3 * 23 * 109` | 1188 | 0 | newspace-only | 0 | 0 |
| 80224 | `2^5 * 23 * 109` | 2376 | 0 | newspace-only | 0 | 0 |
| 120336 | `2^4 * 3 * 23 * 109` | 2376 | 0 | newspace-only | 0 | 0 |

## Survivor

Keine. Alle geladenen trivialen Gewicht-2-Newform-Orbits sterben bereits an einem Trace-Test.

## Nicht Geschlossen

Für diese Levels enthält `mf_newspaces` zwar den trivialen Newspace, aber `mf_newforms`
liefert keine Orbit-Dekomposition mit Traces. Sie sind daher durch diesen externen
Trace-Filter nicht geschlossen:

- 60168, 80224, 120336

## Interpretation

Der Test ist nur notwendig: Bei einem Orbit vom Grad `d` müsste für jedes getestete gute `p`
`trace(T_p) ≡ d * a_p(E) (mod 3863)` gelten. Ein Fehlschlag schließt den Orbit als Träger
der gesuchten Reyssat-Kongruenz aus. Ein Survivor wäre dagegen noch kein Beweis, sondern
müsste mit Koeffizientenfeld, Primideal über 3863 und Hecke-Eigenwerten weiter geprüft werden.

## Fetch-Fehler

- Keine.
