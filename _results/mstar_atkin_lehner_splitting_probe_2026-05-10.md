# M*: Atkin-Lehner-Splitting-Probe

Datum: 2026-05-10

## Zweck

Die Probe bildet im Sage-ModularSymbols-Newspace über GF(3863) die Atkin-Lehner-Sign-Unterräume und schneidet sie mit den Kernen der Operatoren T_l-a_l(E).

## Zusammenfassung

- Worker: 6
- OK: 4
- Timeouts: 2
- Fehler: 0
- Nicht getötete Worker: 0

## Resultate

| Level | Mode | Status | Newdim | Atkin-Divisoren | Befund | Zeit |
|---:|---|---|---:|---|---|---:|
| 109 | raw | ok | 16 | 109 | alle Signräume getötet | 0.155s |
| 109 | anc | ok | 16 | 109 | alle Signräume getötet | 0.082s |
| 218 | raw | ok | 20 | 109 | alle Signräume getötet | 0.392s |
| 218 | anc | ok | 20 | 109 | alle Signräume getötet | 0.360s |
| 60168 | raw | timeout |  | [109] |  |  |
| 60168 | anc | timeout |  | [109] |  |  |

## Detail

### Level 109 / raw

- W_109: involution_defect_rank=0, killed_all_signs=True
  - sign 1: dim=6, after first Hecke cut=0, final=0
  - sign -1: dim=10, after first Hecke cut=0, final=0

### Level 109 / anc

- W_109: involution_defect_rank=0, killed_all_signs=True
  - sign 1: dim=6, after first Hecke cut=0, final=0
  - sign -1: dim=10, after first Hecke cut=0, final=0

### Level 218 / raw

- W_109: involution_defect_rank=0, killed_all_signs=True
  - sign 1: dim=12, after first Hecke cut=0, final=0
  - sign -1: dim=8, after first Hecke cut=0, final=0

### Level 218 / anc

- W_109: involution_defect_rank=0, killed_all_signs=True
  - sign 1: dim=12, after first Hecke cut=0, final=0
  - sign -1: dim=8, after first Hecke cut=0, final=0

## Schluss

Die kleine API-Probe validiert die Signraum-Route. Sie schließt noch keinen Restlevel und ersetzt keinen FOG-FC-Beweis; sie liefert aber den nächsten sinnvollen Workerpfad vor schweren Level-60168-Läufen.
