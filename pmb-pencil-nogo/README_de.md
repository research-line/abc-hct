# Kein positiver Spielraum aus Büschelargumenten — Begleitarbeit v0.1

[English](README.md)

**Kein positiver Spielraum aus Büschelargumenten: Xiaos Lemma, eine Spielraumidentität in Rang r und die Nef-Barriere in Höhenargumenten nach Parshin und Moret-Bailly** von Lukas Geiger. Version 0.1, 8. November 2026.

- Zenodo-Eintrag (v0.1): [10.5281/zenodo.24046160](https://doi.org/10.5281/zenodo.24046160)
- Concept-DOI (alle Versionen, zum Zitieren): [10.5281/zenodo.24046159](https://doi.org/10.5281/zenodo.24046159)
- Lizenz: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Dies ist eine Begleitarbeit zu Paper A ([10.5281/zenodo.21916900](https://doi.org/10.5281/zenodo.21916900)). Sie zeigt, dass der geometrische Spielraum im Büschelschritt von Höhenargumenten nach Parshin und Moret-Bailly nie positiv ist: in Rang zwei über Xiaos Lemma für Büschel, in Rang r über eine Spielraumidentität und ein Nef-Lemma. Als Anwendung erweist sich Proposition 9 vi) aus arXiv:2611.05217v1 (Soulé) als falsch.

Claim-Grenze: Die Arbeit macht keine Aussage über die abc-Vermutung, und die arithmetische Seite des Harder-Narasimhan-instabilen Falls für r ≥ 3 bleibt offen.

## Dateien

- [Englisches PDF](pmb_pencil_nogo_v0.1_en.pdf), 12 Seiten, und [Quelle](pmb_pencil_nogo_v0.1_en.tex).
- [Deutsches PDF](pmb_pencil_nogo_v0.1_de.pdf), 13 Seiten, und [Quelle](pmb_pencil_nogo_v0.1_de.tex).
- Eingaben der KI-Offenlegung: [EN](ai_disclosure_STANDARD_en.tex), [DE](ai_disclosure_STANDARD_de.tex).
- [manifest.json](manifest.json) mit SHA-256 und Bytezahl aller Dateien.

Die TeX-Quellen unterscheiden sich von den übersetzten PDFs nur im `\input`-Pfad der KI-Offenlegung, der auf die lokale Kopie in diesem Ordner zeigt. Die PDFs sind unverändert.

## Bauen

pdfLaTeX aus diesem Ordner starten, je Sprache drei Durchläufe:

```sh
pdflatex -interaction=nonstopmode -halt-on-error pmb_pencil_nogo_v0.1_en.tex
pdflatex -interaction=nonstopmode -halt-on-error pmb_pencil_nogo_v0.1_de.tex
```

PDF-Metadaten können beim Neubau abweichen; das Manifest bindet die veröffentlichten PDF-Bytes.

## Zitieren

Bitte die Concept-DOI [10.5281/zenodo.24046159](https://doi.org/10.5281/zenodo.24046159) zitieren, sie führt stets zur neuesten Version.

Copyright © 2026 Lukas Geiger. Dieses Papierpaket steht unter CC BY 4.0. Für die Software des Repositorys gilt weiterhin die MIT-Lizenz; dieser Ordner legt die Papierlizenz fest. Fremde Ergebnisse bleiben ihren ursprünglichen Autoren zugeordnet.
