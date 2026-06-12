# M*: Capture decay probe

Datum: 2026-05-10

## Kurzbefund

- Geladene Orbits: 119 (238 mit raw/anc).
- Orbit-Dimensionssumme: 2604.
- \(3863\)-Survivor am Ende: 0.
- Nichttriviale End-GCDs: 40.
- End-Summe \(\sum \log\gcd / \log N\): 2.723080.
- Externe nichttriviale End-GCDs nach Entfernung von [2, 3, 23, 109]: 0.
- Externe End-Summe \(\sum \log\gcd_{exc} / \log N\): 0.000000.
- Median erstes \(\gcd=1\): k=2.0.

## Aggregation nach k

| k | Tests | gcd>1 | extern gcd>1 | 3863-Survivor | Sum log gcd/log N | Sum log extern/log N | max gcd | max extern |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 238 | 216 | 128 | 0 | 53.656630 | 31.900478 | 2^3 * 3 * 7 | 127 |
| 2 | 238 | 102 | 14 | 0 | 11.322409 | 2.070231 | 2 * 3 * 7 | 17 |
| 3 | 238 | 70 | 6 | 0 | 7.214013 | 1.031146 | 2 * 3 * 7 | 17 |
| 4 | 238 | 40 | 0 | 0 | 2.834957 | 0.000000 | 2^2 | 1 |
| 5 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 6 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 7 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 8 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 9 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 10 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 11 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 12 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 13 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 14 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 15 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 16 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 17 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 18 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 19 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 20 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 21 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |
| 22 | 238 | 40 | 0 | 0 | 2.723080 | 0.000000 | 2^2 | 1 |

## Interpretation

Für die geladenen Oldlevel-Orbits fällt die externe spurious
Produkt-GCD-Masse nach Entfernung der Bad-Primes aus \(2N\) auf null.
Die rohe Restmasse besteht aus \(2\)-Potenzartefakten und ist für FAQS
nicht extern relevant. Das stützt die Capture-Idee diagnostisch,
beweist aber nichts für den eigentlichen New-Level, weil dort die
Orbitdaten fehlen.
Außerdem ist der Test nur auf Orbit-Traces, nicht auf vollständige
Koeffizientenfeld-Primideale berechnet.
