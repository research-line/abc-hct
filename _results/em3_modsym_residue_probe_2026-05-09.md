# EM-3 Modularsymbol-Residuenprobe

**Datum:** 2026-05-09
**Status:** Ausgeführt als P1′-Surrogat, nicht als voller Hecke-Maximalideal-Test.

## Design

Für dieselben sechs P1-Matched-Control-Fälle wurden die periodennormalisierten PARI-Modularsymbolwerte auf dem Frey-Stern und auf 20 Random-Centern modulo der aktiven ungeraden Führer-Drop-Primzahlen ℓ reduziert.

Ein aktives ℓ erfüllt `D_ell = prod_{p|N(E), ell|v_p(Delta_min)} p > 1`, wobei `N(E)` und `Delta_min` direkt in PARI aus dem Frey-Modell bestimmt wurden. ℓ=2 bleibt ausgeschlossen, weil EM-1 gezeigt hat: `D_2=N` für Frey-Kurven und damit keine Bewertungstiefe diskriminiert.

## Ergebnis nach Tripel und ℓ

| Tripel | ℓ | D_ell | Drop-Primes | Frey support | Random mean support | Random median | Frey all-zero | Random all-zero | Befund |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|
| 1+2400=2401 | 7 | 2 | 2 | 1.000 | 0.950 | 1.000 | 0 | 0/20 | Saturiert |
| 1+4374=4375 | 3 | 2 | 2 | 0.800 | 0.825 | 0.875 | 0 | 0/20 | Kein Frey-Vorteil |
| 1+4374=4375 | 7 | 3 | 3 | 0.800 | 0.950 | 1.000 | 0 | 0/20 | Kein Frey-Vorteil |
| 1+6560=6561 | 7 | 2 | 2 | 0.200 | 0.950 | 1.000 | 0 | 0/20 | Kein Frey-Vorteil |
| 1+8=9 | 5 | 2 | 2 | 1.000 | 0.800 | 1.000 | 0 | 0/20 | Saturiert |
| 13+243=256 | 5 | 3 | 3 | 1.000 | 0.912 | 1.000 | 0 | 0/20 | Saturiert |
| 3+125=128 | 3 | 10 | 2,5 | 0.750 | 0.688 | 0.750 | 0 | 0/20 | Kein Frey-Vorteil |

## Gesamturteil

Aktive Tests: 7. Frey war in 0 Tests stärker als alle Random-Center. In 3 Tests war das Profil schlicht saturiert (Frey support = Random median = 1).

**Nullbefund:** Die aktive Drop-ℓ-Reduktion zeigt kein Frey-spezifisches Nichtverschwinden. Fast alle getesteten Sterne sind modulo ℓ bereits voll unterstützt; das Signal diskriminiert daher nicht zwischen Frey-Zentrum und Random-Centern.

## Konsequenz

Dieses Surrogat tötet P1′ noch nicht formal, weil es keine Projektion in die lokalen Hecke-Maximalideale konstruiert. Es zeigt aber, dass die naive Residuen-Nichtnullheit modulo Führer-Drop-ℓ genauso generisch ist wie die P1-Amplitude. Der nächste P1′-Schritt müsste echte Hecke-Quotienten/Maximalideale oder eine neue, deutlich schärfere Verschwindungsvorhersage liefern.
