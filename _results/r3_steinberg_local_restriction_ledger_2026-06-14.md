# R3/D1 Steinberg-lokaler Restriktions-Ledger (2026-06-14)

exc[q] = #q-exzeptionelle Steinberg-Primes (q|p^2-1) im Primtraeger S_odd=primes(abc)_>2.
Frage: waechst exc ~ omega (KILL) oder bleibt es kontrolliert/random-duenn (GO-Signal)?

| q | mean exc | max exc | mean exc/omega | random 2/(q-1) | frac mit exc>0 |
|---|---:|---:|---:|---:|---:|
| 101 | 0.0166 | 1 | 0.00284 | 0.02 | 0.0166 |
| 251 | 0.0041 | 1 | 0.00046 | 0.008 | 0.0041 |
| 1009 | 0.0 | 0 | 0.0 | 0.001984 | 0.0 |
| 3863 | 0.0 | 0 | 0.0 | 0.000518 | 0.0 |
| 5077 | 0.0 | 0 | 0.0 | 0.000394 | 0.0 |

Lesart: liegt mean_exc/omega nahe am Random-Erwartungswert 2/(q-1) und << 1, dann sind
die exzeptionellen (Selmer-Defekt tragenden) Stellen DUENN -> der lokale Steinberg-Term
expandiert NICHT mit jeder Primstelle; der adjungierte Selmer-Defekt-Support ist sublinear
in omega (GO-Signal fuer K1, nicht-zirkulaer). Liegt exc ~ omega -> KILL.

ACHTUNG: rein lokaler Handle; die volle Sel_{L*}-Dimension braucht zusaetzlich den
globalen H^1(Q_S,Ad^0)-Schnitt (naechste, schwerere Stufe).