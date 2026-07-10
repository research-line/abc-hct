# Kongruenz-/Jordan-Sweep - Q_E-Serien-Korpus (kein abc-Claim)

Autor: LG. F_ell-Strukturtest je (N,ell) in `ModularSymbols(N,2,sign=1)` tensor F_ell (integrale Struktur, row, nur Primstellen p<=Sturm).

## Interpretation (neutral)

Jordan-Struktur bestaetigt; Daten konsistent mit multiplicity one UND Freiheit von M^+_m. T_m/I_f ist NICHT der Kongruenzmodul, sondern das Bild in O_lambda (torsionsfrei); Kongruenzmasse in O/eta bzw. T_m/(I_f+I_g). Q_E ~= T_m/I_f -> O_lambda erklaert odd-Torsionsfreiheit AUCH bei Kongruenz. Kein Versagen.

## Stufe 1: Korpus (modular_degree, congruence_number)

| N | dim | Sturm | deg phi | C_E | odd-Kongruenzprimzahlen | Q_E (Ref) | Q_E odd-frei |
|---|---|---|---|---|---|---|---|
| 109 | 9 | 18 | 2^2 | 2^2 | - | 1 | ja |
| 48 | 12 | 16 | 2^2 | (error:ValueError('BUG in modular degree or congruence number computation of: Elliptic Curve defined by y^2 = x^3 + x^2 - 24*x + 36 over Rational Field')) | - | 2^8 | ja |
| 240 | 56 | 96 | 2^5 * 3^2 | (error:ValueError('BUG in modular degree or congruence number computation of: Elliptic Curve defined by y^2 = x^3 - x^2 - 5336*x + 151536 over Rational Field')) | [3] | 2^18 | ja |
| 494 | 74 | 140 | 2^2 * 17 | 2^2 * 17 | [17] | 2^4 | ja |
| 645 | 92 | 176 | 2^3 * 11 | 2^3 * 11 | [11] | 2^8 | ja |
| 590 | 94 | 180 | 2^3 * 3 * 5 | 2^3 * 3 * 5 | [3, 5] | 2^4 | ja |
| 1961 | 172 | 342 | 2^2 * 3 * 19 | 2^2 * 3 * 19 | [3, 19] | 2^4 | ja |
| 1056 | 200 | 384 | 2^7 * 3 * 5 | (timeout_240s) | [3, 5] | 2^33 | ja |

Kurven mit MEHREREN odd-Kongruenzprimzahlen: [590, 1961, 1056]

## Stufe 2+3: F_ell-Strukturtest + Jordan-Verdikt

| N | ell | dim | (a) coinv | socle (geom) | (b) gen (alg) | (c) im Bild | Gorenstein | jordan_nonsplit | konsistent |
|---|---|---|---|---|---|---|---|---|---|
| 240 | 3 | 56 | 1 | 1 | 2 | True | ok | True | True |
| 494 | 17 | 74 | 1 | 1 | 2 | True | ok | True | True |
| 645 | 11 | 92 | 1 | 1 | 2 | True | ok | True | True |
| 590 | 3 | 94 | 1 | 1 | 2 | True | ok | True | True |
| 590 | 5 | 94 | 1 | 1 | 3 | True | ok | True | True |
| 1961 | 3 | 172 | 1 | 1 | 2 | True | ok | True | True |
| 1961 | 19 | 172 | 1 | 1 | 2 | True | ok | True | True |
| 1056 | 3 | 200 | 1 | 1 | 2 | True | ok | True | True |
| 1056 | 5 | 200 | 1 | 1 | 2 | True | ok | True | True |

Spalten: (a) Ko-Invarianten dim M^+/m M^+; socle = geom. Vielfachheit (joint Eigenraum); (b) alg. Vielfachheit (verallg. m-Eigenraum); (c) socle im Bild m*M^+; jordan_nonsplit := gen>socle UND (c); konsistent := ell echte Kongruenzprimzahl => jordan_nonsplit UND coinv=1.

## Auffaelligkeiten

Keine. Alle getesteten (N,ell) konsistent: jede odd-Kongruenzprimzahl ell|C_E ist Jordan-verklebt (gen>socle, socle im Bild) bei Ko-Invarianten-Dimension 1 - d.h. die odd-Kongruenz existiert am Newform-Level, bleibt aber im ambienten Q_E (= T_m/I_f -> O_lambda, torsionsfrei) unsichtbar. Serie bestaetigt das 494/645-Muster.

Laufzeit: 549.3 s.

## Addendum (post-run, LG): C_E-Luecken 48/240 geschlossen (odd-Primzahl-Menge)

`E.congruence_number()` warf fuer N=48 und N=240 den Sage-internen ValueError
("BUG in modular degree or congruence number"); N=1056 lief in den 240s-Guard.
Fuer 48/240 nachgereicht via `A.congruence_number(A_complement)` ueber den
Newform-Faktor der kuspidalen `ModularSymbols(N,2,sign=1)` (`_scripts/cn_gapfill.py`,
`_results/cn_gapfill_2026-07-10.json`):

- N=48:  sign=+1-Kongruenzzahl = 2   -> **odd-Primzahlen: keine** (echte Kontrolle wie 109).
- N=240: sign=+1-Kongruenzzahl = 2^5*3 -> **odd-Primzahl: {3}**, KEINE Extra-Primzahl jenseits deg phi.

CAVEAT: Die sign=+1-Modularsymbol-Kongruenzzahl weicht im 2-Teil und in der
odd-VIELFACHHEIT vom vollen C_E ab (ARS deg phi | C_E gilt fuer diese Rohwerte
nicht). Die odd-Primzahl-MENGE ist aber verlaesslich (Hecke-Eigenform-Kongruenzen
sind vorzeichen-unabhaengig) - und genau die ist fuer die F_ell-Kandidatenwahl
gebraucht. Ergebnis: KEINE odd-Kongruenzprimzahl jenseits von deg phi bei 48/240;
Kandidatenwahl (odd-Teiler von deg phi) bestaetigt. N=1056 (dim 200) bleibt eine
C_E-Luecke; die deg-phi-Kandidaten {3,5} wurden getestet (beide Jordan-konsistent),
und in allen 7 berechenbaren Faellen ist odd(C_E) = odd(deg phi).