# CX2+CX3: Codex-Audit-Tests an den de-Smit-Champions (2026-06-11)

**CX2 (Subtorus-Nähe):** rank-corr(q, score) = 0.027; Score-Median hohe q: 0.3686, niedrige q: 0.3691; exakte Subtorus-Punkte: 0.

Top-5 subtorus-nächste: [{'rank': 120, 'q': 1.4234, 'score': np.float64(0.0726)}, {'rank': 74, 'q': 1.4384, 'score': np.float64(0.0847)}, {'rank': 214, 'q': 1.4048, 'score': np.float64(0.1223)}, {'rank': 230, 'q': 1.4017, 'score': np.float64(0.1275)}, {'rank': 110, 'q': 1.4283, 'score': np.float64(0.131)}]

**CX3 (additive Geschlossenheit vs. Zufalls-Träger):** n = 230; z-Median = 54724726672.49 (Mittel 53789366686.45); Anteil z > 2: 100.0%; rank-corr(q, z) = -0.051; z-Median hohe/niedrige q: 56034767664.75 / 54303518288.41.

Laufzeit: 24.4s. JSON: `_results/cx2_cx3_codex_tests_2026-06-11.json`

## Befund (2026-06-11) — beide Tests NEGATIV

**CX2 (Subtorus-Naehe): TOT.** rank-corr(q, Score) = 0.027 (n=240), Score-
Mediane hohe/niedrige q praktisch gleich, 0 exakte Subtorus-Punkte. Hohe
Qualitaet sitzt NICHT systematisch nahe an Subtori — Codex' eigenes
Kill-Kriterium erfuellt (unlikely intersections liefert dann nur
Finitaet-pro-S). Konsistent mit dem Konfigurationsmodell-Befund (B1/C8).

**CX3 (additive Geschlossenheit): NEGATIV, mit Methoden-Caveat.** Das
interne Signal ist sauber: rank-corr(q, Geschlossenheit) = -0.051 ~ 0 —
innerhalb der Champions korreliert Qualitaet NICHT mit anomaler additiver
Geschlossenheit des Traegers. Der Baseline-z-Vergleich ist dagegen
konstruktionsbedingt unbrauchbar (Zufalls-Traeger ohne kleine Primes haben
closure ~ 0 konstant, sd -> 0, z explodiert) — ein degree-/size-matched
Nullmodell waere noetig, lohnt aber angesichts des Null-Signals intern
nicht. CX3 zu den Akten.

**Konsequenz:** Beide billigen Codex-Tests bestaetigen das B1/C8-Bild —
die Champion-Traeger tragen keine verborgene multiplikative oder additive
Sonderstruktur, die als Hebel taugen koennte.
