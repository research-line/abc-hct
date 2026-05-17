# H3a Affine P1 Prefix Cells

Datum: 2026-05-16

Diese Tabelle dokumentiert die rein kombinatorische Übersetzung des
Sage-Manin-Prefixes in die affine `P1(Z/NZ)`-Zelle.

Für Gewicht 2 gilt:

```text
ManinSymbolList_gamma0(N,2) = P1List(N)
P1List(N)[0] = (0,1)
P1List(N)[k] = (1,k-1), 1 <= k <= N
```

Solange `d-2 < N`, ist daher:

```text
P1List(N)[0..d-2] = {(0,1)} union {(1,t): 0<=t<=d-3}.
```

| Level | Status | d | T5-Indexblock | Affine Zelle | T7-Zeile |
|---:|---|---:|---|---|---|
| 80224 | raw/anc belegt | 10568 | `0..10566` | `{(0,1)} union {(1,t):0<=t<=10565}` | `(1,0)` |
| 120336 | raw belegt | 21136 | `0..21134` | `{(0,1)} union {(1,t):0<=t<=21133}` | `(1,0)` |
| 240672 | erwartet, Lauf aktiv | 42256 | `0..42254` | `{(0,1)} union {(1,t):0<=t<=42253}` | `(1,0)` |

Diese Datei ist kein Rangbeweis. Sie belegt nur, dass der beobachtete
Indexprefix in den abgeschlossenen Fällen eine kanonische affine
Manin-Zellmenge ist.

