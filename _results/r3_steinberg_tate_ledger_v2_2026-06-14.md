# R3/D1 v2 — Steinberg + Tate-Kanal Ledger (2026-06-14)

## (A) Fixed-q Diagnose (beide Kanaele) — erwartet: blind fuer grosses q

| q | char_mean | char_max | tate_mean | tate_max | char_frac>0 | tate_frac>0 |
|---|---:|---:|---:|---:|---:|---:|
| 101 | 0.0166 | 1 | 0.0 | 0 | 0.0166 | 0.0 |
| 251 | 0.00415 | 1 | 0.0 | 0 | 0.0041 | 0.0 |
| 1009 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 3863 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 5077 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |

Lesart A: char UND tate ≈0 fuer grosses festes q => der fixed-q-Ledger ist BLIND
(Messartefakt: q|p^2-1 braucht p>=q, q|e_p braucht e_p>=q; beide klein in Champions).
Das ist KEIN 'free conditions', sondern der falsche Messpunkt (advisor-Catch bestaetigt).

## (B) Kurvenspezifischer All-q-Scan (die informative Version)

n_qchar/qtate = #verschiedene kurvenspezifische exzeptionelle gute Primes je Kanal.

- **n_triples**: 241
- **mean_n_qall**: 3.237
- **mean_n_qtate**: 0.361
- **mean_mult_tate**: 0.411
- **max_n_qall**: 9
- **corr(n_qall, omega)**: 0.3443
- **corr(n_qall, q_abc)**: -0.217
- **corr(n_qtate, q_abc)**: 0.0712
- **corr(mult_tate, omega)**: -0.1077
- **frac_triples_with_qtate>0**: 0.3485

Lesart B: waechst die lokal-exzeptionelle Masse (n_qall / mult_tate) mit Qualitaet q_abc
oder omega? Schwache/keine Korrelation => der lokale Support ist duenn und qualitaets-
robust (stuetzt CR-2b-a No-hidden-basin). Starke Korrelation mit omega aber NICHT mit
q_abc => Masse skaliert mit Stellenzahl, nicht mit Qualitaet (kein Qualitaets-Hebel).

ENTSCHEIDET NICHT die Groesse (CR-2b-b): dafuer globaler H^1(Q_S,Ad^0)-Schnitt (R5.2).