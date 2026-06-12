# M*: Sage-Direktzugriff auf kleine Zellen

Datum: 2026-05-10

## Ergebnis

| Level | Sign | Status | Ambient | Newdim | Befund |
|---:|---:|---|---:|---:|---|
| 109 | 1 | ok | 9 | 8 | decomp [1, 1, 1, 1, 4] |
| 218 | 1 | ok | 29 | 10 | decomp [1, 1, 1, 1, 1, 2, 3] |
| 60168 | 1 | timeout |  |  | Timeout 90s |

## Schluss

Auf kleinen Levels funktioniert der `sign=+1`-Quotient und liefert Zerlegungen. Auf \(60168\) timeoutet aber bereits der Aufbau des ModularSymbols-Raums. Lokaler Sage-Direktzugriff auf die kleinen LMFDB-AL-Zellen ist damit weiterhin blockiert.
