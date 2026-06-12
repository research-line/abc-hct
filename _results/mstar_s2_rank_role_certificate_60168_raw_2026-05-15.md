# S2 Rank-Role Certificate 60168/raw

Datum: 2026-05-15

## Gegenstand

Dieser Bericht fasst die Source-Cokernel-Sättigung für den `60168/raw`-
Kalibrator zusammen, ohne für jede Ausnahmeprimzahl eine explizite
Rechtskernelbasis zu erzwingen.

Source-Witness:

```text
_results/rc3d_rowhash_source_witness_60168_raw_2026-05-12/N60168_raw_sign1
```

Mixed-Witness:

```text
_results/s5_mixed_superset_witness_60168_raw_2026-05-14/N60168_raw_source_plus_p2repair_sign1
```

Reparaturzeilen:

```text
t5 = T_5_minus_2_batch_11/575
t7 = T_7_minus_0_batch_1/1
```

## Zertifikatstabelle

| q | Source-Rang | Defekt | +t5 | +t7 | +t5+t7 | Zertifikat |
|---:|---:|---:|---:|---:|---:|---|
| 2 | 31678 | 2 | 31679 | 31679 | 31680 | explizites Rechtskernel-Pairing |
| 3 | 31679 | 1 | 31680 | 31679 | 31680 | t5 erzeugt den Quotienten |
| 5 | 31679 | 1 | 31680 | 31680 | 31680 | t5 und t7 erzeugen jeweils |
| 31 | 31679 | 1 | 31680 | 31680 | 31680 | t5 und t7 erzeugen jeweils |

Für q=2 liegt zusätzlich die explizite Pairing-Matrix gegen
`right_kernel(A mod 2)` vor:

```text
1 1
1 0
```

Quelle:

```text
_results/mstar_s2_source_cokernel_pairing_60168_raw_q2_2026-05-15.md
```

## Interpretation

Sei `A` der Source-Block und `C_q = F_q^n / row(A mod q)`. Dann gilt:

```text
rank([A; R] mod q) = n
  <=>  die Bilder der Zeilen R erzeugen C_q.
```

Für q=3,5,31 ist `dim C_q = 1`. In einer eindimensionalen Quotientengruppe ist
eine explizite Rechtskernelmatrix nicht die robuste Information; invariant ist
die Aussage, ob die Zusatzzeile ein nichtnulles Bild hat. Genau das leisten
die Ein-Zeilen-Rangrollen.

Damit sind alle Source-Ausnahmen im Fenster `q <= 100` durch die kanonische
Menge `{t5,t7}` gesättigt. Für alle übrigen Primzahlen im Fenster war der
Source-Minor selbst bereits vollrangig.

## Status

Geschlossen für den Kalibrator:

```text
q <= 100  =>  rank([A;t5;t7] mod q) = 31680.
```

Offen global:

```text
1. Kanonische Konstruktion von A_E und {t5_E,t7_E}.
2. Uniforme Kontrolle der Source-Cokernel-Dimension.
3. Basisfreie Erklärung des p=2-Zwei-Zeilen-Defekts.
4. Sublogarithmisches Budget für Ausnahmeprimzahlen außerhalb endlicher Fenster.
```
