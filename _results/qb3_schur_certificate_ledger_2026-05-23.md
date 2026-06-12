# Q_B-3 Schur-Cofactor Ledger

Datum: 2026-05-23
Projekt: HCT/abc

## Kriterium

Für die Source+Repair-Basis schreibe

```text
G = [[A,b],[b^T,c]] = C B_AL C^T
s = c - b^T A^-1 b
Q_B(phi) = beta^2 * s^-1.
```

Damit ist Q_B-3 über dem Restkörper äquivalent zu `beta != 0` und
`s != 0`, sofern der Source-Block `A` nichtsingulär ist.  Alternativ
kann der Wrapper den Rangsprung `rank(G) = rank(A)+1` zertifizieren.

## Fälle

| Fall | Status | beta | Schur-/Q_B-Information |
|---|---|---:|---|
| `109/raw` | `passed` | 705 | Q_B=722, (G^-1)_rr=848, s=41 mod 3863 |
| `80224/raw` | `blocked_missing_al_pairing` | -1 | A vollrangig + s != 0 aus AL-Pairing noch zu berechnen; BSD-Heuristik Q_B=-239, s=-792 |
| `80224/anc` | `blocked_missing_al_pairing` | -1 | A vollrangig + s != 0 aus AL-Pairing noch zu berechnen |
| `120336/raw` | `blocked_missing_restline_kernel_json` | - | RC3c/order data exist, but the restline_kernel_quotient JSON with beta/source-annihilation fields is not present locally. |
| `240672/raw` | `blocked_missing_restline_kernel_json` | - | RC3c/order data exist and the minikill status file is present, but the restline_kernel_quotient JSON is not present locally. |

## Wrapper-Auftrag

Der nächste Pairing-Lauf soll nicht die vollständige inverse Matrix
ausgeben.  Ausreichend sind:

1. Rang von `A`.
2. Schur-Skalar `s` oder äquivalent der letzte Cofaktor.
3. Optional `Q_B = beta^2/s` als abgeleiteter Skalar.
4. Bei `s=0` ein kurzer Nullvektor-/Rank-Failure-Zeuge.

Der Smoke-Regressionstest ist `N=109`: `s=41 mod 3863` und
`Q_B=722 mod 3863` müssen reproduziert werden.
