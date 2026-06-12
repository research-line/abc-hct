# Conductor-/Oldform-Ledger v0

Datum: 2026-05-15
Status: raw-normalisierte Ledger-Tabelle; anc-Projektion noch offen

## Zweck

Dieses Ledger trennt drei Fragen, die in den letzten Loops vermischt waren:

```text
1. Ist N_test unterhalb, gleich oder oberhalb des Frey-Conductors N_E?
2. Welche raw-Oldform-Masse ist im vollen Niveau N_test erwartbar?
3. Bleibt nach HCT ein unerwarteter Survivor übrig?
```

Für raw-Modus wird in v0 die einfache Oldform-Heuristik verwendet:

```text
old_dim_expected_raw =
  sigma_0(N_test / N_E), wenn N_E | N_test,
  0, sonst.
```

Die normalisierten Größen sind:

```text
residual_dim = max(0, qdim_final - old_dim_expected_raw)
old_dim_deficit = max(0, old_dim_expected_raw - qdim_final)
```

`residual_dim > 0` wäre ein unerwarteter Survivor. `old_dim_deficit > 0`
heißt: HCT-Relationen töten sogar erwartete raw-Oldform-Masse; das ist beim
Spike-q gerade der interessante Zertifikatsfall, verlangt aber das
Einbettungslemma.

## Raw-Ledger

| Label | Tripel | N_E | N_test | q | mode | qdim_final | old_dim_expected_raw | residual_dim | old_dim_deficit | Status |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 109 | 3863 | raw | 0 | 0 | 0 | 0 | lower-level killed |
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 218 | 3863 | raw | 0 | 0 | 0 | 0 | lower-level killed |
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 60168 | 3863 | raw | 0 | 0 | 0 | 0 | lower-level killed |
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 80224 | 3863 | raw | 0 | 0 | 0 | 0 | lower-level killed |
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 120336 | 3863 | raw | 0 | 0 | 0 | 0 | lower-level killed |
| Reyssat | `(2, 3^10*109, 23^5)` | 240672 | 240672 | 3863 | raw | 0 | 1 | 0 | 1 | conductor-level spike kill |
| `(5,27)` | `(5, 27, 32)` | 30 | 30 | 3863 | raw | 1 | 1 | 0 | 0 | expected Frey newform |
| `(5,27)` | `(5, 27, 32)` | 30 | 60 | 3863 | raw | 2 | 2 | 0 | 0 | expected oldforms |
| `(5,27)` | `(5, 27, 32)` | 30 | 120 | 3863 | raw | 3 | 3 | 0 | 0 | expected oldforms |
| `(5,27)` | `(5, 27, 32)` | 30 | 240 | 3863 | raw | 4 | 4 | 0 | 0 | expected oldforms |
| `(1,80)` | `(1, 80, 81)` | 240 | 30 | 3863 | raw | 0 | 0 | 0 | 0 | below conductor killed |
| `(1,80)` | `(1, 80, 81)` | 240 | 60 | 3863 | raw | 0 | 0 | 0 | 0 | below conductor killed |
| `(1,80)` | `(1, 80, 81)` | 240 | 120 | 3863 | raw | 0 | 0 | 0 | 0 | below conductor killed |
| `(1,80)` | `(1, 80, 81)` | 240 | 240 | 3863 | raw | 1 | 1 | 0 | 0 | expected Frey newform |
| `(1,4374)` | `(1, 4374, 4375)` | 3360 | 210 | 3863 | raw | 0 | 0 | 0 | 0 | below conductor killed |
| `(1,4374)` | `(1, 4374, 4375)` | 3360 | 420 | 3863 | raw | 0 | 0 | 0 | 0 | below conductor killed |
| `(1,4374)` | `(1, 4374, 4375)` | 3360 | 3360 | 3863 | raw | 1 | 1 | 0 | 0 | expected Frey newform |

## Anc-Beobachtungen ohne Oldform-Normalisierung

Diese Werte sind wichtig, aber v0 rechnet ihnen noch keine
`old_dim_expected_anc` zu.

| Label | N_E | N_test | q | mode | qdim_final | Status |
|---|---:|---:|---:|---|---:|---|
| `(5,27)` | 30 | 30 | 3863 | anc | 0 | killed |
| `(5,27)` | 30 | 60 | 3863 | anc | 0 | killed |
| `(5,27)` | 30 | 120 | 3863 | anc | 0 | killed |
| `(5,27)` | 30 | 240 | 3863 | anc | 1 | survivor_candidate |
| `(1,80)` | 240 | 30 | 3863 | anc | 2 | survivor_candidate |
| `(1,80)` | 240 | 60 | 3863 | anc | 3 | survivor_candidate |
| `(1,80)` | 240 | 120 | 3863 | anc | 4 | survivor_candidate |
| `(1,80)` | 240 | 240 | 3863 | anc | 5 | survivor_candidate |
| `(1,4374)` | 3360 | 210 | 3863 | anc | 0 | killed |
| `(1,4374)` | 3360 | 420 | 3863 | anc | 0 | killed |
| `(1,4374)` | 3360 | 3360 | 3863 | anc | 1 | survivor_candidate |

## Befund

1. Die alte Formulierung, Reyssat habe hier einen Conductor um `10^7`, ist
   für diesen Projektstand überholt. Das Ledger setzt verbindlich
   `N_E(Reyssat)=240672`.

2. Der `(5,27)`-raw-Survivor ist vollständig durch erwartete Oldform-Masse
   erklärt:

   ```text
   qdim_final = sigma_0(N_test / 30)
   ```

   Also kein unerwarteter Survivor.

3. `(1,80)` und `(1,4374)` bestätigen den generischen conductor-level Fall:

   ```text
   N_test=N_E, q=3863, raw qdim_final=1.
   ```

   Nach raw-Oldform-Normalisierung bleibt jeweils `residual_dim=0`.

4. Reyssat ist der scharfe Spikefall:

   ```text
   N_test=N_E=240672, q=3863, qdim_final=0,
   old_dim_expected_raw=1, old_dim_deficit=1.
   ```

   Das ist der positive HCT-Befund, aber er ist nur beweisrelevant, wenn das
   Einbettungslemma den HCT-Kill tatsächlich als
   `v_3863(Q_ad^exc(E))=0` interpretiert.

5. `(1,4374)` am eigenen Conductor ist kein zusätzlicher Kill, sondern ein
   erwarteter Kalibrator-Survivor. Damit ist L-C2 als Rechenaufgabe erledigt.

## Nächste Ledger-Pflichten

```text
L-C1: old_dim_expected_anc definieren oder per AL-Projektion berechnen.
L-C3: Metrik-Extractor v2 soll diese Tabelle automatisch aus JSON erzeugen.
L-C4: Reyssat-Quellenstelle mit N_E=240672 in Paper B und alten Notizen prüfen.
```
