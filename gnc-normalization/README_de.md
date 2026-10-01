# Global Normalization Contract Lemma — Reparaturfassung v1.2

[English](README.md)

Autor: Lukas Geiger. Manuskriptdatum: 2. Oktober 2026. Der bisherige Zenodo-
Record ist [v1.1](https://doi.org/10.5281/zenodo.21924254); die Versionsfamilie
ist [10.5281/zenodo.21924253](https://doi.org/10.5281/zenodo.21924253).

Dieses Paket enthält das englische Manuskript (24 Seiten), das deutsche
Manuskript (26 Seiten), ihre LaTeX-Quellen und die beiden KI-Offenlegungen.
Version 1.2 ist ein korrigierter Entwurf; die Veröffentlichung des neuen
Zenodo-Records erfolgt in einem getrennten Schritt.

Die Reparatur korrigiert die ATS-IV-Domäne zum vervollständigten Körper und
stellt die äußeren Betragsstriche im logarithmischen Volumenvergleich wieder
her. Sie trennt Absolutbetragsnormierung, Haar-Maß und Modul und zieht die
allgemeine Gleichsetzung von algebraischer Hülle und konvexer Hülle zurück.
Der rahmenübergreifende Maßvergleich bleibt in jedem diagnostischen Zweig
offen. Der benannte Transport ist ein möglicher hinreichender Weg, keine
notwendige Bedingung. Das elementare Produktformel-Multiplikatorlemma und die
bedingte F1/F2-Herleitung bleiben erhalten. Dieses Paper beweist weder E2 noch
die abc-Vermutung.

Die 14 Literaturangaben des Manuskripts benennen die Primärliteratur. Das
Paket enthält keine kopierten Primärquellen-PDFs und kein neues Rechenexperiment
oder rechnerisches Beweiszertifikat.

Beide Sprachen mit pdfLaTeX aus diesem Verzeichnis bauen, jeweils drei Läufe:

```sh
pdflatex -interaction=nonstopmode -halt-on-error GNC_Assessment_v1_2_en.tex
pdflatex -interaction=nonstopmode -halt-on-error GNC_Assessment_v1_2_ger.tex
```

Beide geprüften PDFs wurden erfolgreich und ohne abschließende Warnungen
gebaut. Alle 50 Seiten wurden anhand von Kontaktbögen auf Layoutfehler geprüft.
Das Manifest bindet die konkreten Quell- und PDF-Bytes; PDF-Metadaten können
sich bei erneutem Bauen ändern.

Copyright © 2026 Lukas Geiger. Dieses Paper-Paket steht unter
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Für die Software des
Repositorys gilt weiterhin MIT; dieses Verzeichnis benennt die Paper-Lizenz.
Zitate Dritter bleiben ihren ursprünglichen Autoren zugeordnet.
