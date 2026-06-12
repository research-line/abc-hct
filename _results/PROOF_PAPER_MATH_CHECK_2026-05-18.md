# Proof/Paper-Math-Check 2026-05-18

## Projekt

- Projekt: HCT/abc Eta Bound / Period Reformulation
- Pfad: `.LAB/.HCT/abc/`
- Automation: `research-proof-paper-parallel-math-check`
- Auswahlgrund: Für das Root-Paper gab es am 2026-05-17 einen Zitationscheck und am 2026-05-18 einen GitHub-Check, aber noch keinen dedizierten Proof/Paper-Math-Check. Die jüngsten FWS-/ANC-/Q_B-Notizen machten einen Abgleich zwischen BEWEISNOTIZ und Paper sinnvoll.

## Geprüfte Dateien

- `BEWEISNOTIZ_2.md`
- `abc_Theta_Tamagawa_EN.tex`
- `abc_Theta_Tamagawa_DE.tex`
- `AKTIONSPLAN.md`
- `abc_Theta_Tamagawa_DE.pdf`
- `abc_Theta_Tamagawa_kombi.pdf`

## Befund

1. EN-Paper und BEWEISNOTIZ führen bereits die korrekte Hauptlinie: Die Eta-Schranke ist unbedingtes Theorem; die Periodenuntergrenze bleibt der offene Kern.
2. Die deutsche Paperfassung hatte in einer Bemerkung noch die ältere Lesart, nach der die Eta-Schranke selbst als offene Zutat erschien. Das war mathematisch stale.
3. `AKTIONSPLAN.md` enthielt im Abstract noch `The converse direction remains open`, obwohl Paper und BEWEISNOTIZ die AGM-Konverse für Frey-Kurven bereits nachgezogen hatten.
4. `BEWEISNOTIZ_2.md` enthielt in Loop 328 die verkürzte Formel `Q_B(φ_N)=β_N(G_N^{-1})_{d,d}`. Korrekt ist wegen der Koordinatenprojektion `Q_B(φ_N)=β_N²(G_N^{-1})_{d,d}`.
5. Die FWS-h-Abschnitte verwendeten teilweise `h_F/logN` für die Diskriminantenhöhe. Für die proof-relevante Szpiro-Größe muss hier `H_delta/logN = log|Δ_min|/(12 log N)` stehen; die echte normalisierte Faltings-Höhe enthält archimedische Terme.
6. Eine ältere 2026-04-30-Checknotiz in `BEWEISNOTIZ_2.md` sagte noch aktiv, die Umkehrrichtung bleibe offen. Diese historische Stelle war seit Loop 20/AGM-Konverse überholt.

## Korrekturen

- `abc_Theta_Tamagawa_DE.tex`: Bemerkung zur Eta-/Perioden-Schranke synchronisiert. Die Eta-Schranke wird jetzt als unbedingtes Theorem geführt; die Periodenuntergrenze ist der verbleibende offene Kern. Die deutsche Dezimalschreibweise wurde als `0{,}005` gesetzt.
- `BEWEISNOTIZ_2.md`: Q_B-Formel auf `β_N²` korrigiert; FWS-h/FWS-h_delta-Abschnitte auf `H_delta/logN` und die Guardrail `c_low>=1/4 => q<=2+ε`, nicht volle abc-Linie, bereinigt; eigener Check-Abschnitt Loop 329 ergänzt.
- `BEWEISNOTIZ_2.md`: ältere 2026-04-30-Formulierung zur offenen Umkehrrichtung mit einem Nachtrag versehen: Für Frey-Kurven ist die Rückrichtung inzwischen via AGM-Konverse nachgezogen; offen bleibt der unbedingte Beweis der Periodenuntergrenze.
- `AKTIONSPLAN.md`: Abstract auf AGM-Konverse für Frey-Kurven aktualisiert; Projektinfo, PDF-Größen und Status-Log auf v0.1-mathsync gesetzt.

## Mathematische Konsequenz

- Das Root-Paper und die BEWEISNOTIZ sind wieder synchron: kein abc-Beweisclaim, sondern unbedingte Eta-Schranke plus äquivalente bzw. hinreichende Frey-Periodenreformulierung.
- FWS-h_delta bleibt als robuste Diagnostik wertvoll, liefert aber keine unabhängige Verstärkung über Szpiro hinaus.
- Der nächste produktive Beweisschritt bleibt Q_B-3: `B_AL`/Intersection-Pairing zuerst für `80224/raw` pilotieren und danach auf die großen raw/anc-Level übertragen.

## Verifikation

- `pdflatex -interaction=nonstopmode -halt-on-error abc_Theta_Tamagawa_DE.tex` zweimal erfolgreich.
- Kombi-PDF aus EN+DE mit `pypdf` neu gemergt.
- Logscan: keine Treffer für LaTeX Error, Undefined control sequence, undefined references/citations, Rerun-Hinweise oder Overfull `\hbox`.
- Seitenzahlen: EN 14, DE 15, Kombi 29.
- SHA256 EN: `CD11B2989297565B4E10ACEBF8D72EA32E894BDB3FDEA2D998C7E3EDA6ECB430`
- SHA256 DE: `85EE7584913CFF71C1372CF8FF10ADEDA774F23E3D9AC31090554FB6975A5F8F`
- SHA256 Kombi: `60A1A3892643E089003DA0A86F7B5D60CC9915C93513AC2D45DB7E4855C19B05`
- Umlaute/Deutsch: Die geänderten deutschen TeX-Stellen verwenden echte Umlaute und die deutsche Dezimalschreibweise `0{,}005`; `pdftotext` bestätigt die korrigierte Passage in der PDF-Textspur mit `0,005`, `Perioden-Untergrenze`, `unbedingt`, `Cremona` und `Manin`.
