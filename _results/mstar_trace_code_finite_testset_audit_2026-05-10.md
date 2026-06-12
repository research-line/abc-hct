# M*: Trace-Code finite Testmengen-Audit

Datum: 2026-05-10

## Kurzbefund

- Geladene Oldlevel-Orbitdaten schließen alle sichtbaren rationalen/oldlevel
  Kandidaten für \(q=3863\): 10 Levels,
  geladene Orbit-Dimension 2604, Survivor 0.
- Drei große Oldlevels haben nur Newspace-Zeilen, aber keine nutzbaren Orbitdaten:
  [60168, 80224, 120336] mit Newdim-Summe 5940.
- Der echte New-Level \(N=240672\) hat Newdim
  4752; öffentliche Orbitdaten fehlen.
- Die naive Trace-Sieve-Schranke für den New-Level liegt bei
  26806.16 log N,
  also weit über dem \(o(\log N)\)-Ziel.
- Reyssat-\(3863\) bleibt externer Spike:
  \(\log 3863/\log 240672=0.666538\),
  Cross-Class-Hits 0,
  Oldlevel-Hits 0.

## Level-Tabelle

| Level | Faktor | Newdim | Orbitdim geladen | Coverage | Tests | Survivor |
|---:|---|---:|---:|---|---:|---:|
| 109 | 109 | 8 | 8 | orbit-traces | 6 | 0 |
| 218 | 2 * 109 | 10 | 10 | orbit-traces | 10 | 0 |
| 327 | 3 * 109 | 19 | 19 | orbit-traces | 8 | 0 |
| 872 | 2^3 * 109 | 27 | 27 | orbit-traces | 12 | 0 |
| 1744 | 2^4 * 109 | 54 | 54 | orbit-traces | 34 | 0 |
| 2507 | 23 * 109 | 199 | 199 | orbit-traces | 10 | 0 |
| 3488 | 2^5 * 109 | 108 | 108 | orbit-traces | 20 | 0 |
| 15042 | 2 * 3 * 23 * 109 | 397 | 397 | orbit-traces | 56 | 0 |
| 20056 | 2^3 * 23 * 109 | 594 | 594 | orbit-traces | 18 | 0 |
| 40112 | 2^4 * 23 * 109 | 1188 | 1188 | orbit-traces | 64 | 0 |
| 60168 | 2^3 * 3 * 23 * 109 | 1188 | 0 | newspace-only | 0 | 0 |
| 80224 | 2^5 * 23 * 109 | 2376 | 0 | newspace-only | 0 | 0 |
| 120336 | 2^4 * 3 * 23 * 109 | 2376 | 0 | newspace-only | 0 | 0 |

## Interpretation

Die vorhandenen Daten geben einen positiven Hinweis nur für den geladenen
Oldlevel-Teil: endliche Trace-Wörter töten dort die \(3863\)-Kandidaten.
Für den eigentlichen New-Level \(240672\) und die drei großen Rest-Oldlevels
fehlen aber genau die Orbitdaten, die ein Minimum-Distance-Verhalten belegen
oder widerlegen könnten.

Damit bleibt die finite Testmengenroute kein Beweisweg aus vorhandenen Daten.
Sie muss als theoretischer Satz formuliert werden: Frey-Legendre Trace-Code
Minimum Distance für primitive nichtlokale New-Level-Orbits.
