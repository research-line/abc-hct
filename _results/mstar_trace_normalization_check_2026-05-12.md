# M*: Frey-Trace-Normalisierung

Datum: 2026-05-12

## Modell

Geprüft wird das Frey-Modell

$$E_{a,b}: y^2=x(x-a)(x+b).$$

Für gute Primzahlen gilt

$$a_p(E)=p+1-\#E(\mathbb F_p)
=-\sum_{x\in\mathbb F_p}\left(\frac{x(x-a)(x+b)}{p}\right).$$

## Ergebnis

| Mode | a | b | p | #E(F_p) | a_p count | a_p sum | expected | OK |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| raw | 2 | 6436341 | 5 | 4 | 2 | 2 | 2 | ok |
| raw | 2 | 6436341 | 7 | 8 | 0 | 0 | 0 | ok |
| raw | 2 | 6436341 | 11 | 12 | 0 | 0 | 0 | ok |
| raw | 2 | 6436341 | 13 | 20 | -6 | -6 | -6 | ok |
| anc | 6436341 | 2 | 5 | 4 | 2 | 2 | 2 | ok |
| anc | 6436341 | 2 | 7 | 8 | 0 | 0 | 0 | ok |
| anc | 6436341 | 2 | 11 | 12 | 0 | 0 | 0 | ok |
| anc | 6436341 | 2 | 13 | 20 | -6 | -6 | -6 | ok |

## Schluss

Die Trace-Normalisierung für die No-Magma-Hecke-Tests ist geschlossen: raw und anc liefern bei p=5,7,11,13 dieselben Werte `a_5=2`, `a_7=0`, `a_11=0`, `a_13=-6`.
