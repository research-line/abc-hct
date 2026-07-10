# OT-2'-Mini-Test - N=645, ell=11 (Instanz-Zertifikat)

Autor: LG. Design: `_codex/CODEX_OT2_ANTWORT_2026-07-02.md`, Abschnitt 6.
Zweite Instanz zu N=494/ell=17. Kein abc-Claim - reines Instanz-Zertifikat.

## Kernbefund

**Ausgang 3 - all-p-Kongruenz (inkl. U_p) einer FREMDEN Orbit.** Die Orbit(s) [10] sind mod einer Primstelle ueber 11 an ALLEN n <= B (inkl. U_3,U_5,U_43) zu f_E kongruent - unabhaengig per Residuenkoerper-Reduktion verifiziert (Ideal-Kriterium und direkte Gegenprobe stimmen ueberein: ja). Damit ist die naive OT-2 (kein g!=f_E mit all-p-Kongruenz) in der N=645/ell=11-Instanz am Newform-Level FALSCH. Prueft, ob der ambiente SNF-Quotient Q_E die 11-Torsion zeigt (unten) - falls nicht: dieselbe Objekttrennung wie bei N=494.

Unabhaengige Corroboration: deg phi = 88 = 2^3 * 11, congruence_number C_E = 88 = 2^3 * 11 -> 11 TEILT C_E.

| Groesse | Wert |
|---|---|
| Frey-Kurve (a,b) | (5, 43), ainvs=(0, 38, 0, -215, 0) |
| Conductor N | 645 |
| Index [SL2:Gamma0(N)] | 1056 |
| Sturm-Bound B | 176 |
| schlechte Primstellen | [3, 5, 43] |
| deg phi | 88 = 2^3 * 11 |
| congruence_number C_E | 88 = 2^3 * 11 |
| 11 | C_E ? | ja |
| Newform-Orbits | 12 |
| Target-Orbit-Index (f_E) | [3] |
| Design-Ausgang | 3 (full_sturm_fremde_orbit_OT2_gegenbeispiel) |

## Kongruenz-Report pro Orbit

| Orbit | Koerper (Grad) | target | good_away_from_N | good_plus_bad_U_p | full_sturm | killed_by_U_p | direkt-verif. (N(lam)) |
|---|---|---|---|---|---|---|---|
| 0 | Q(deg 1) | - | False | False | False | - | - |
| 1 | Q(deg 1) | - | False | False | False | - | - |
| 2 | Q(deg 1) | - | False | False | False | - | - |
| 3 | Q(deg 1) | ja | True | True | True | - | ja (N=11) |
| 4 | Q(deg 1) | - | False | False | False | - | - |
| 5 | Q(deg 1) | - | False | False | False | - | - |
| 6 | Q(deg 2) | - | False | False | False | - | - |
| 7 | Q(deg 3) | - | False | False | False | - | - |
| 8 | Q(deg 3) | - | False | False | False | - | - |
| 9 | Q(deg 3) | - | False | False | False | - | - |
| 10 | Q(deg 5) | - | True | True | True | - | ja (N=11) |
| 11 | Q(deg 5) | - | False | False | False | - | - |

Ideal-Kriterium vs. direkte Residuenkoerper-Gegenprobe (Nicht-Target): stimmen ueberein. Verifizierte all-p-Kongruenz-Orbits: [10].

## SNF-Zusatztest (Pruefpunkt b): M^+ / sum (T_n - a_n(E)) M^+

Ambient: `ModularSymbols(645,2,sign=1)`, dim=92, Hecke-Konvention: row.

| Variante | #Generatoren n | free_rank | Torsions-Invariantenfaktoren | Torsionsordnung | len_2 | len_3 | len_5 | len_11 |
|---|---|---|---|---|---|---|---|---|
| (i) away-from-N | 91 | 1 | 2, 2, 2, 2, 2, 4, 4, 8 | 2^12 | 12 | 0 | 0 | 0 |
| (ii) VOLL | 176 | 1 | 2, 2, 2, 2, 2, 2, 2, 2 | 2^8 | 8 | 0 | 0 | 0 |

Von (i) nach (ii) getoetete ell-Torsion (U_p-Kill sichtbar): ell=2: 12->8

ACHTUNG Objekttrennung (wie N=494): Die VOLLE SNF-Variante ist nur eine 2-Gruppe (Q_E = 2^8, keine 11-Torsion), ABER der Newform-Kongruenz-Report weist eine verifizierte all-p-Kongruenz mod 11 mit Orbit [10] nach. Der ambiente Manin-/SNF-Quotient Q_E misst also NICHT das volle Newform-Kongruenzmodul (Codex Abschnitt 4/6). Das 494-Muster wiederholt sich.

Laufzeit: 26.4 s. Kontext-Vorlage: `_scripts/qe_snf_crosscheck_n1056.sage`, `_results/qe_snf_crosscheck_n645_2026-07-02.json`.