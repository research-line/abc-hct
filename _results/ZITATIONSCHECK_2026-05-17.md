# Zitationscheck 2026-05-17 -- abc Eta/Periodenpaper

## Projekt

- Projekt: `C:\Users\User\OneDrive\.TOPICS\.RESEARCH\.LAB\.HCT\abc`
- Paper: `abc_Theta_Tamagawa_EN.tex`, `abc_Theta_Tamagawa_DE.tex`
- Auswahlgrund: Im zentralen `CHECKED-REGISTRY.md` war für das Root-Paper der HCT/abc-Linie noch kein eigener `research-zitation-check` dokumentiert. Der Ast hatte EN/DE-Fassungen und eine aktive mathematische Bibliographie.

## Befund vor Korrektur

- EN: 30 aktive Cite-Keys, 35 Bibitems.
- DE: 31 aktive Cite-Keys, 35 Bibitems.
- Unzitierte Grundlagenquellen: `Masser1985`, `Oesterle1988`, `Frey1986`, `Mazur1977`; zusätzlich war `HoffsteinRamakrishnan1995` nicht aktiv in EN verankert.
- `GeigerIUT2026` verwies noch auf den alten Version-DOI `10.5281/zenodo.19960782`; die Zenodo-API löst den Concept-Record inzwischen auf den neuesten Record `20223276` auf.

## Korrekturen

- Masser--Oesterle aktiv in der abc-Einführung zitiert.
- Freys Konstruktion aktiv beim Übergang zur Frey-Kurve zitiert.
- Mazurs modular-curve/Eisenstein-ideal framework in der Modularitätssektion verankert.
- Hoffstein--Ramakrishnan aktiv im Zero-Free-Region-Diagnostic ergänzt.
- `GeigerIUT2026` in EN/DE auf aktuellen Zenodo-Titel, Concept DOI `10.5281/zenodo.19960781` und latest checked record `10.5281/zenodo.20223276` aktualisiert.

## Verifikation

- `python _tools\check_refs.py ...`: EN/DE jeweils 35 Cite-Keys und 35 Bibitems; keine fehlenden oder unzitierten Keys.
- LaTeX: EN und DE jeweils zweimal mit `pdflatex -interaction=nonstopmode -halt-on-error` neu gebaut.
- Logscan: keine LaTeX-Fehler, Citation-Warnings, undefined references/citations, Rerun-Hinweise oder Overfull-HBoxen. Verbleibend sind nur Underfull-HBoxen, RevTeX-/nameref-Info und der lokale MiKTeX-Updatehinweis.
- Kombi-PDF per `pypdf` neu aus EN+DE gemergt und mit Metadaten versehen.
- Deutsche PDF-Textspur: keine typischen ASCII-Umlautersatzformen (`fuer`, `ueber`, `Fuehrer`, `Schluessel`, `Unabhaengig`) gefunden.

## Artefakte

- EN: 14 Seiten, 552356 B, MD5 `55DA4649408945C99BC54D0FDD508A49`.
- DE: 15 Seiten, 557306 B, MD5 `377574DBAB2F69F5DCD659C8A0F37919`.
- Kombi: 29 Seiten, 1055498 B, MD5 `D4CEAAC834696F3F869CCA3CFD0D6CF3`.

## Resthinweis

Die Inline-Bibliographie bleibt thematisch/chronologisch statt alphabetisch sortiert. Das wurde nicht als Zitationsfehler behandelt, weil der aktive Cite-/Bibitem-Abgleich vollständig grün ist.
