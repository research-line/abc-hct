# M*: Traceword-Index-Proxy

Datum: 2026-05-10

## Kurzbefund

- Geladene Oldlevel-Orbits: 119, Dimensionssumme 2604.
- Testprimes: [5, 7, 11, 13, 17, 19, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97].
- Erste vollständige Trace-only-Partition: k=4.
- Erste vollständige Dim+Trace-Partition: k=4.
- Erste Frey-relative externe GCD-Nullmasse: k=4.
- Bei k=4, also [5, 7, 11, 13], Trace-only-Kollisionscluster: 0.
- Bei k=4 Dim+Trace-Kollisionscluster: 0.
- Bei k=4 externe Frey-GCD-Masse/log N: 0.000000.

## Partitionen nach k

| k | letzter p | Cluster trace | Kollisionscluster trace | max trace | Cluster dim+trace | Kollisionscluster dim+trace | max dim+trace |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | 29 | 27 | 11 | 69 | 31 | 6 |
| 2 | 7 | 102 | 9 | 4 | 106 | 9 | 3 |
| 3 | 11 | 118 | 1 | 2 | 118 | 1 | 2 |
| 4 | 13 | 119 | 0 | 1 | 119 | 0 | 1 |
| 5 | 17 | 119 | 0 | 1 | 119 | 0 | 1 |
| 6 | 19 | 119 | 0 | 1 | 119 | 0 | 1 |
| 7 | 29 | 119 | 0 | 1 | 119 | 0 | 1 |
| 8 | 31 | 119 | 0 | 1 | 119 | 0 | 1 |
| 9 | 37 | 119 | 0 | 1 | 119 | 0 | 1 |
| 10 | 41 | 119 | 0 | 1 | 119 | 0 | 1 |
| 11 | 43 | 119 | 0 | 1 | 119 | 0 | 1 |
| 12 | 47 | 119 | 0 | 1 | 119 | 0 | 1 |
| 13 | 53 | 119 | 0 | 1 | 119 | 0 | 1 |
| 14 | 59 | 119 | 0 | 1 | 119 | 0 | 1 |
| 15 | 61 | 119 | 0 | 1 | 119 | 0 | 1 |
| 16 | 67 | 119 | 0 | 1 | 119 | 0 | 1 |
| 17 | 71 | 119 | 0 | 1 | 119 | 0 | 1 |
| 18 | 73 | 119 | 0 | 1 | 119 | 0 | 1 |
| 19 | 79 | 119 | 0 | 1 | 119 | 0 | 1 |
| 20 | 83 | 119 | 0 | 1 | 119 | 0 | 1 |
| 21 | 89 | 119 | 0 | 1 | 119 | 0 | 1 |
| 22 | 97 | 119 | 0 | 1 | 119 | 0 | 1 |

## Frey-relative externe GCD-Masse

| k | letzter p | extern gcd>1 | 3863-Survivor | Sum log extern/log N | max extern | externe Primstütze |
|---:|---:|---:|---:|---:|---|---|
| 1 | 5 | 128 | 0 | 31.900478 | 127 | 5, 7, 11, 17, 19, 41, 43, 47, 53, 59, 61, 73, 97, 103, 127 |
| 2 | 7 | 14 | 0 | 2.070231 | 17 | 5, 7, 17 |
| 3 | 11 | 6 | 0 | 1.031146 | 17 | 5, 7, 17 |
| 4 | 13 | 0 | 0 | 0.000000 | 1 | - |
| 5 | 17 | 0 | 0 | 0.000000 | 1 | - |
| 6 | 19 | 0 | 0 | 0.000000 | 1 | - |
| 7 | 29 | 0 | 0 | 0.000000 | 1 | - |
| 8 | 31 | 0 | 0 | 0.000000 | 1 | - |
| 9 | 37 | 0 | 0 | 0.000000 | 1 | - |
| 10 | 41 | 0 | 0 | 0.000000 | 1 | - |
| 11 | 43 | 0 | 0 | 0.000000 | 1 | - |
| 12 | 47 | 0 | 0 | 0.000000 | 1 | - |
| 13 | 53 | 0 | 0 | 0.000000 | 1 | - |
| 14 | 59 | 0 | 0 | 0.000000 | 1 | - |
| 15 | 61 | 0 | 0 | 0.000000 | 1 | - |
| 16 | 67 | 0 | 0 | 0.000000 | 1 | - |
| 17 | 71 | 0 | 0 | 0.000000 | 1 | - |
| 18 | 73 | 0 | 0 | 0.000000 | 1 | - |
| 19 | 79 | 0 | 0 | 0.000000 | 1 | - |
| 20 | 83 | 0 | 0 | 0.000000 | 1 | - |
| 21 | 89 | 0 | 0 | 0.000000 | 1 | - |
| 22 | 97 | 0 | 0 | 0.000000 | 1 | - |

## Interpretation

Auf den geladenen Oldlevel-Orbits verhält sich die kleine Testalgebra
sehr stark: wenige kleine \(T_\ell\) trennen fast sofort die sichtbaren
Orbittraces, und relativ zur Frey-Spur ist die externe Produkt-GCD-Masse
ab \(k=4\) null. Das ist genau das Verhalten, das der Small-Index-
Generator-Satz verlangen würde.

Der Test ist aber nur ein Index-Proxy: Er verwendet Orbittraces statt
vollständiger Koeffizientenfeld-Ordnungen und enthält keine Daten für den
echten New-Level \(240672\). Er stützt die Route, beweist sie aber nicht.
