# Q_B-3 Rank-Jump Reduction Ledger

Datum: `2026-05-23`

## Kernbefund

Aus den vorhandenen Restlinien-JSONs folgt bereits:

```text
source rank = d-1
phi(source) = 0
phi(repair) = beta != 0
```

Also liegt die Repair-Zeile nicht im Source-Hyperplane, und
`Source + Repair` ist eine Quotientenbasis. Mit der Standard-
Nichtdegeneriertheit von `B_AL` ist der volle Gramblock
`G=C B_AL C^T` damit vollrangig. Der offene Q_B-3-Kern ist nur noch
der Source-only-Block `A`.

## Fälle

| Level | Mode | d | source rank | beta | Source+Repair Basis | rank(G) | offen |
|---:|---|---:|---:|---:|---|---|---|
| 80224 | raw | 10568 | 10567 | -1 | ja | closed_by_basis_plus_B_AL_nondegenerate | rank(A)=10567 |
| 80224 | anc | 10568 | 10567 | -1 | ja | closed_by_basis_plus_B_AL_nondegenerate | rank(A)=10567 |

## Reduktion

Für jeden gelisteten Fall ist `rank(G)=d` nicht mehr der
rechnerische Engpass. Es genügt, `rank(A)=d-1` für den
Source-only-Gramblock zu zertifizieren. Bei `beta != 0` folgt dann
`s != 0` und damit `Q_B(phi) != 0` über die Schur-Identität.

## Nächster Verifier

Der nächste Großlevel-Verifier sollte daher nicht `G^-1` und auch
nicht sofort `A*x=b` berechnen, sondern zuerst ein matrixfreies
Rangzertifikat für `A` erzeugen.
