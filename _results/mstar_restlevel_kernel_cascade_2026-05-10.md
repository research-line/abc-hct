# M*: Restlevel-Kernkaskade Smoke/Timeout

Datum: 2026-05-10

## Kurzbefund

Der neue Sage-Worker `_scripts/mstar_restlevel_kernel_cascade.py` wurde
syntaktisch geprüft und mit Sage auf Level `109` erfolgreich getestet.

Smoke:

- Level `109`, raw, Primes `5,7`.
- Ergebnis: \(T_5-a_5\) hat vollen Rang, Determinante `29` modulo `3863`.
- Level wird sofort getötet.

Erster Restlevel-Test:

- Level `60168`, raw/ANC, Prime `5`.
- Backend `cuspforms_newspace`.
- Manager-Timeout: 120 Sekunden pro Orientierung.
- Ergebnis: beide Worker timeout.

Zweiter Restlevel-Test nach Tooling-Recherche:

- Level `60168`, raw/ANC, Prime `5`.
- Backend `modsym_gf`, also `ModularSymbols(..., base_ring=GF(3863))`.
- Manager-Timeout: 120 Sekunden pro Orientierung.
- Ergebnis: beide Worker timeout.

## Interpretation

Die Worker-Architektur funktioniert, aber die naive Sage-Route
`CuspForms(...).new_subspace().hecke_matrix(5)` und auch der ungesplittete
`ModularSymbols(..., GF(3863)).cuspidal_subspace().new_subspace()`-Pfad sind
für `60168` noch nicht leicht genug. Das ist kein mathematischer Survivor; es
ist ein Infrastruktur-Befund.

## Nächster Rechenschritt

Nicht einfach Timeout erhöhen. Zuerst optimieren:

- Atkin-Lehner-Splitting vor Hecke-Matrix-Bau prüfen;
- modular-symbols statt modular-forms-newspace direkt über endliche Körper
  testen;
- Matrixaufbau persistent cachen;
- eventuell nur Rang von \(T_5-a_5\) statt Determinante/Charpoly erzwingen;
- Subprozess-Logging während Matrixbau verbessern.
