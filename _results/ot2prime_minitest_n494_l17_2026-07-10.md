# OT-2'-Mini-Test - N=494, ell=17 (Instanz-Zertifikat)

Autor: LG. Design: `_codex/CODEX_OT2_ANTWORT_2026-07-02.md`, Abschnitt 6.
Kein abc-Claim - reines Instanz-Zertifikat.

## Kernbefund

**Ausgang 3 - all-p-Kongruenz (inkl. U_p) einer FREMDEN Orbit.** Die Orbit(s) [4] sind mod einer Primstelle ueber 17 an ALLEN n <= B (inkl. U_2,U_13,U_19) zu f_E kongruent - unabhaengig per Residuenkoerper-Reduktion verifiziert (Ideal-Kriterium und direkte Gegenprobe stimmen ueberein: ja). Damit ist die naive OT-2 (kein g!=f_E mit all-p-Kongruenz) in der N=494/ell=17-Instanz am Newform-Level FALSCH. Der ambiente SNF-Quotient Q_E (unten) zeigt hingegen KEINE 17-Torsion - genau die von Codex (Abschnitt 4/6) benannte Objekttrennung: Q_E misst NICHT das volle Newform-Kongruenzmodul.

| Groesse | Wert |
|---|---|
| Frey-Kurve (a,b) | (13, 19), ainvs=(0, 6, 0, -247, 0) |
| Conductor N | 494 |
| Index [SL2:Gamma0(N)] | 840 |
| Sturm-Bound B | 140 |
| schlechte Primstellen | [2, 13, 19] |
| deg phi | 68 = 2^2 * 17 |
| Newform-Orbits | 8 |
| Target-Orbit-Index (f_E) | [1] |
| Design-Ausgang | 3 (full_sturm_fremde_orbit_OT2_gegenbeispiel) |

## Kongruenz-Report pro Orbit

| Orbit | Koerper (Grad) | target | good_away_from_N | good_plus_bad_U_p | full_sturm | killed_by_U_p | direkt-verif. (N(lam)) |
|---|---|---|---|---|---|---|---|
| 0 | Q(deg 1) | - | False | False | False | - | - |
| 1 | Q(deg 1) | ja | True | True | True | - | ja (N=17) |
| 2 | Q(deg 1) | - | False | False | False | - | - |
| 3 | Q(deg 1) | - | False | False | False | - | - |
| 4 | Q(deg 3) | - | True | True | True | - | ja (N=17) |
| 5 | Q(deg 3) | - | False | False | False | - | - |
| 6 | Q(deg 3) | - | False | False | False | - | - |
| 7 | Q(deg 4) | - | False | False | False | - | - |

Ideal-Kriterium vs. direkte Residuenkoerper-Gegenprobe (Nicht-Target): stimmen ueberein. Verifizierte all-p-Kongruenz-Orbits: [4].

## SNF-Zusatztest (Pruefpunkt b): M^+ / sum (T_n - a_n(E)) M^+

Ambient: `ModularSymbols(494,2,sign=1)`, dim=74, Hecke-Konvention: row.

| Variante | #Generatoren n | free_rank | Torsions-Invariantenfaktoren | Torsionsordnung | len_2 | len_3 | len_5 | len_17 |
|---|---|---|---|---|---|---|---|---|
| (i) away-from-N | 61 | 1 | 2, 2, 4, 4, 4, 4, 4, 4, 4 | 2^16 | 16 | 0 | 0 | 0 |
| (ii) VOLL | 140 | 1 | 2, 2, 2, 2 | 2^4 | 4 | 0 | 0 | 0 |

Von (i) nach (ii) getoetete ell-Torsion (U_p-Kill sichtbar): ell=2: 16->4

ACHTUNG Objekttrennung: Die VOLLE SNF-Variante ist nur eine 2-Gruppe (Q_E = 2^4, keine 17-Torsion), ABER der Newform-Kongruenz-Report weist eine verifizierte all-p-Kongruenz mod 17 mit Orbit [4] nach. Der ambiente Manin-/SNF-Quotient Q_E misst also NICHT das volle Newform-Kongruenzmodul (Codex Abschnitt 4/6). Die SNF allein wuerde OT-2 faelschlich als zertifiziert ausweisen.

Laufzeit: 8.3 s. Kontext-Vorlage: `_scripts/qe_snf_crosscheck_n1056.sage`, `_results/qe_snf_crosscheck_n494_2026-07-02.json`.

## Addendum (post-run, LG): unabhaengige Corroboration via Kongruenzzahl

Dritte, vom q-Entwicklungs-Vergleich unabhaengige Gegenprobe (andere Sage-Routine):

- `E.modular_degree()`  = 68 = 2^2 * 17
- `E.congruence_number()` = 68 = 2^2 * 17  =>  **17 | C_E**

`E.congruence_number()` misst den Modul der Newform-Kongruenzen (ARS). Dass 17 | C_E,
bestaetigt die Orbit-4-all-p-Kongruenz mod 17 ein drittes Mal (nach Ideal-Kriterium
und Residuenkoerper-Reduktion). Damit ist die Objekttrennung scharf: die 17 ist eine
ECHTE Newform-Kongruenzprimzahl (17 | C_E = 68), erscheint aber NICHT im ambienten
Manin-/SNF-Quotienten Q_E = 2^4. Der frueher aus `qe_snf_crosscheck` (N=494: #Q_E=2^4,
"odd-torsion trivial") gezogene Schluss "17 ist keine Hecke-Kongruenzprimzahl" traegt
daher am Newform-Level NICHT; #Q_E ist nicht die Kongruenzzahl. (Reproduzierbar:
`sage -python -c "from sage.all import*; E=EllipticCurve([0,6,0,-247,0]); print(E.congruence_number().factor())"`.)