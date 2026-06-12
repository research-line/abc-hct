# M*: LMFDB-SQL-Probe für Restlevel-Daten

Datum: 2026-05-10

## Quelle

Abfrage des öffentlichen LMFDB-PostgreSQL-Mirrors `devmirror.lmfdb.xyz` auf die Tabellen `mf_newspaces` und `mf_newforms`.

## Newspace-Zeilen

| Level | Label | Newdim | plus_dim | Sturm | AL-Zellen | AL min-max | Newform-Orbits | Trace T5,T7,T11,T13 |
|---:|---|---:|---:|---:|---:|---|---:|---|
| 60168 | 60168.2.a | 1188 | 574 | 21120 | 16 | 67-82 | 0 | 0,8,0,8 |
| 80224 | 80224.2.a | 2376 | 1170 | 21120 | 8 | 292-302 | 0 | 0,0,0,0 |
| 120336 | 120336.2.a | 2376 | 1152 | 42240 | 16 | 143-154 | 0 | 0,0,0,0 |
| 240672 | 240672.2.a | 4752 | 2336 | 84480 | 16 | 287-307 | 0 | 0,0,0,0 |

## Befund

Die LMFDB enthält für diese vier Levels Newspace-Daten, aber keine `mf_newforms`-Orbitzeilen. `hecke_orbit_dims`, `num_forms` und `hecke_cutter_primes` sind in den Newspace-Zeilen leer. Damit sind die fehlenden Orbit-/Hecke-Feld-Daten bestätigt.

Positiv ist die `ALdims`-Information: Die Atkin-Lehner-Zellen sind viel kleiner als der volle Newspace. Für \(60168\) liegen sie nur zwischen 67 und 82 Dimensionen. Das erklärt, warum eine echte Faktor-/Signraumrechnung aussichtsreich wäre, aber lokale Sage-Routen müssen diese Zellen vor dem vollen Newspace-Matrixbau materialisieren.

## Schluss

Der SQL-Mirror liefert keine fertigen Newform-Orbits, aber er gibt einen klaren Zielzustand für Magma oder eine tiefere Sage-Zerlegung: nicht 1188- bis 4752-dimensionale Räume angreifen, sondern die Atkin-Lehner-Zellen und danach Faktoren/Hecke-Orbits.

