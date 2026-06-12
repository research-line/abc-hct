# S5/K2-Mod-q-Scan 60168/raw bis q = 100

Datum: 2026-05-14

## Gegenstand

Getestet wurde der rowhash-gebundene RC3d-Source-Minor

```text
_results/rc3d_rowhash_source_witness_60168_raw_2026-05-12/N60168_raw_sign1
```

mit der Sage-Matrix-Rangengine. Für die größeren Primzahlen wurde jeweils ein
Prime-pro-Job-Lauf mit `--checkpoint-jsonl` verwendet.

## Ergebnis

| q | Rang | Spalten | Vollrang? | Sekunden | Quelle |
|---:|---:|---:|---|---:|---|
| 2 | 31678 | 31680 | nein | 16.523 | `_results/mstar_s5_modular_exception_scan_60168_raw_p2_sage_2026-05-13.json` |
| 3 | 31679 | 31680 | nein | 79.529 | `_results/mstar_s5_modular_exception_scan_60168_raw_p3_5_7_11_sage_2026-05-13.json` |
| 5 | 31679 | 31680 | nein | 78.094 | `_results/mstar_s5_modular_exception_scan_60168_raw_p3_5_7_11_sage_2026-05-13.json` |
| 7 | 31680 | 31680 | ja | 77.431 | `_results/mstar_s5_modular_exception_scan_60168_raw_p3_5_7_11_sage_2026-05-13.json` |
| 11 | 31680 | 31680 | ja | 72.664 | `_results/mstar_s5_modular_exception_scan_60168_raw_p3_5_7_11_sage_2026-05-13.json` |
| 13 | 31680 | 31680 | ja | 74.787 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 17 | 31680 | 31680 | ja | 72.381 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 19 | 31680 | 31680 | ja | 66.010 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 23 | 31680 | 31680 | ja | 63.926 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 29 | 31680 | 31680 | ja | 63.428 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 31 | 31679 | 31680 | nein | 61.543 | `_results/mstar_s5_modular_exception_scan_60168_raw_p13_31_sage_2026-05-13.json` |
| 37 | 31680 | 31680 | ja | 161.761 | `_results/mstar_s5_modular_exception_scan_60168_raw_p37_sage_checkpoint_2026-05-14.json` |
| 41 | 31680 | 31680 | ja | 171.771 | `_results/mstar_s5_modular_exception_scan_60168_raw_p41_sage_checkpoint_2026-05-14.json` |
| 43 | 31680 | 31680 | ja | 280.572 | `_results/mstar_s5_modular_exception_scan_60168_raw_p43_sage_checkpoint_2026-05-14.json` |
| 47 | 31680 | 31680 | ja | 251.985 | `_results/mstar_s5_modular_exception_scan_60168_raw_p47_sage_checkpoint_2026-05-14.json` |
| 53 | 31680 | 31680 | ja | 160.020 | `_results/mstar_s5_modular_exception_scan_60168_raw_p53_sage_checkpoint_2026-05-14.json` |
| 59 | 31680 | 31680 | ja | 142.017 | `_results/mstar_s5_modular_exception_scan_60168_raw_p59_sage_checkpoint_2026-05-14.json` |
| 61 | 31680 | 31680 | ja | 134.628 | `_results/mstar_s5_modular_exception_scan_60168_raw_p61_sage_checkpoint_2026-05-14.json` |
| 67 | 31680 | 31680 | ja | 173.859 | `_results/mstar_s5_modular_exception_scan_60168_raw_p67_sage_checkpoint_2026-05-14.json` |
| 71 | 31680 | 31680 | ja | 166.836 | `_results/mstar_s5_modular_exception_scan_60168_raw_p71_sage_checkpoint_2026-05-14.json` |
| 73 | 31680 | 31680 | ja | 149.150 | `_results/mstar_s5_modular_exception_scan_60168_raw_p73_sage_checkpoint_2026-05-14.json` |
| 79 | 31680 | 31680 | ja | 135.986 | `_results/mstar_s5_modular_exception_scan_60168_raw_p79_sage_checkpoint_2026-05-14.json` |
| 83 | 31680 | 31680 | ja | 138.382 | `_results/mstar_s5_modular_exception_scan_60168_raw_p83_sage_checkpoint_2026-05-14.json` |
| 89 | 31680 | 31680 | ja | 121.168 | `_results/mstar_s5_modular_exception_scan_60168_raw_p89_sage_checkpoint_2026-05-14.json` |
| 97 | 31680 | 31680 | ja | 111.143 | `_results/mstar_s5_modular_exception_scan_60168_raw_p97_sage_checkpoint_2026-05-14.json` |

## Bilanz

Vollrangig im Source-Minor:

```text
7,11,13,17,19,23,29,37,41,43,47,53,59,61,67,71,73,79,83,89,97
```

Source-Minor-Ausnahmen bis `q = 100`:

```text
2,3,5,31
```

Diese vier Ausnahmen sind im fixierten Quotientenpfad bereits repariert. Das
qmax100-Fenster erzeugt also keine neue versteckte Defektadresse für den
aktuellen `60168/raw`-Source-Minor.

## Status

Das ist ein starker endlicher K2-Kalibrator, aber noch kein globaler
CR-2b-Beweis. Benötigt bleibt eine uniforme Kompressionsaussage: kleiner
Smith-Defekt, strukturell beschränkte Ausnahmeprimmenge oder ein theoretischer
Satz, der relevante externe `q` in endlich viele Prüfprimes zwingt.
