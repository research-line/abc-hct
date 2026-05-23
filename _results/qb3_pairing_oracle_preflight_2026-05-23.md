# Q_B-3 Pairing-Oracle Preflight

Datum: 2026-05-23
Projekt: HCT/abc

## Zweck

Dieses Preflight trennt die fertigen Restlinien-Inputs vom noch offenen
Atkin-Lehner-Pairing.  Der nächste große Lauf soll keine volle inverse
Matrix ausgeben, sondern ein kleines Schur-Zertifikat:

```text
G = [[A,b],[b^T,c]] = C B_AL C^T
s = c - b^T A^-1 b
Q_B(phi) = beta^2 / s.
```

Pflichtausgabe: `rank(A)`, `s`, optional `Q_B`, und bei Fehlern ein
Rank- oder Nullvektor-Zeuge.

## Regression

- `109/raw`: `passes=True`, `beta=705`, `s=41 mod 3863`, `Q_B=722`.
- Dieser Wert ist der harte Smoke-Test für jeden Schur-Wrapper.

## Große Fälle

| Fall | Status | beta | Dimension | Schur-Auftrag |
|---|---|---:|---:|---|
| `80224/raw` | `ready` | -1 | 10568 | `rank(A)=10567`, `s!=0`, `Q_B=beta^2/s` |
| `80224/anc` | `ready` | -1 | 10568 | `rank(A)=10567`, `s!=0`, `Q_B=beta^2/s` |
| `120336/raw` | `blocked` | - | - | No local restline_kernel_quotient JSON yet; rank/order artifacts are not a beta/source-annihilation substitute. |
| `240672/raw` | `blocked` | - | - | Restline kernel quotient is still running on the Mac; wait for the JSON/MD before Q_B-1/Q_B-2 status. |

## Größen-Guardrail

### `80224/raw`

- `G` hätte `111682624` Einträge; int64-Untergrenze `0.832 GiB`, GF(3863)-uint16-Untergrenze `213.02 MiB`.
- `A` hätte `111661489` Einträge; int64-Untergrenze `0.832 GiB`.
- Voll-symmetrische Pairing-Auswertung: `55846596` Paarungen.
- Entscheidung: kein dichtes `G^-1`; nur Schur-Cofactor-/Rangsprung-Zertifikat.

### `80224/anc`

- `G` hätte `111682624` Einträge; int64-Untergrenze `0.832 GiB`, GF(3863)-uint16-Untergrenze `213.02 MiB`.
- `A` hätte `111661489` Einträge; int64-Untergrenze `0.832 GiB`.
- Voll-symmetrische Pairing-Auswertung: `55846596` Paarungen.
- Entscheidung: kein dichtes `G^-1`; nur Schur-Cofactor-/Rangsprung-Zertifikat.

## Nächster Befehl

Der nächste Implementierungsschritt ist ein Sage-/Mac-Wrapper mit der
Schnittstelle:

```text
sage _scripts/mstar_h3a_qb3_schur_oracle.sage \
  --case-dir <splitlast-case> \
  --restline-json <restline_kernel_quotient.json> \
  --out-json <certificate.json> \
  --out-md <certificate.md> \
  --mode schur-certificate
```

Der Wrapper gilt erst als einsatzbereit, wenn er auf `N=109` `s=41`
und `Q_B=722 mod 3863` reproduziert.
