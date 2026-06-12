# Review Chain — abc Paper v0.1 — Step 6 (Neutralisierung)

**Modell:** Opus 4.7
**Datum:** 2026-04-29
**Paper:** An Unconditional Eta Bound and the Period Reformulation of the abc Conjecture via Frey Curves
**Datei:** `abc_Theta_Tamagawa_EN.tex`
**Rolle:** Neutraler Experte (analytische Zahlentheorie / arithmetische Geometrie)

---

## Vorbemerkung

Step 5 hat 15 Angriffe formuliert, davon 4 als "toedlich" eingestuft. Step 6 prueft jeden Angriff sachlich gegen die seit Step 4 vorgenommenen Fixes und gegen die mathematische Realitaet. Ziel ist weder Rechtfertigung noch Verschaerfung, sondern eine ausgewogene Triage: Welche Befunde haben Bestand, welche sind durch die Fixes entschaerft, welche sind im adversariellen Register ueberzeichnet?

Befund vorab: Die seit Step 4 vorgenommenen Fixes (E1, E2, E3, E6, A1, A2, Goldfeld-Zitat, E4, E10) entschaerfen einen Teil der Angriffe substantiell, **erzeugen aber zugleich eine neue interne Inkonsistenz**: Cor 8.11 wurde korrekt auf "implies" / einseitig umgestellt, doch zwei nachgelagerte Remarks (`rem:significance`, `rem:reformulation_not_reduction`) und die Boxed-Gleichung `eq:abc_core` (Z. 1543-1547) tragen weiterhin Aequivalenz-Sprache. Diese Inkonsistenz verschaerft Angriff 15 und ist der erste Pflichtfix.

---

## A: Bewertung der 15 Angriffe

### Angriff 1 (Step 5: toedlich) — Cor 8.11 = Goldfeld 1988

**Bewertung: ABGESCHWAECHT, aber substanziell verbleibend.**

Goldfeld (1988/2002) hat die Periodenversion der Vermutung
$\min(|\Omega_1|,|\Omega_2|) \ge \kappa(\varepsilon)\,N^{-1/2-\varepsilon} \Longrightarrow \mathrm{abc}$
fuer Frey-Kurven publiziert. Das ist der wesentliche Inhalt, der Cor 8.11 zugrunde liegt. Step 5 hat zu Recht moniert, dass das Korollar ohne Goldfeld-Zitat als Eigenleistung praesentiert wurde.

Nach den Fixes (Goldfeld2002 als bibitem; Z. 1070-1077: "This is a quantitative refinement of Goldfeld's Period Conjecture"; explizite Zuschreibung im Korollar-Text) ist die Neuheits-Frage nicht mehr **Plagiats-Niveau**, sondern eine Frage nach dem Mass des inkrementellen Beitrags. Der echte Mehrwert ist:

1. Explizite Konstante 0.005 (vs. nicht-explizit bei Goldfeld);
2. $\lambda_1$-Formulierung in Gitter-Sprache (statt $\Omega_E$);
3. Expliziter Beweis ueber die $\eta$-Funktion und $\SL_2(\mathbb{Z})$-Reduktion.

Fuer eine **CRMath-Note** (8-12 Seiten) ist eine quantitative Verfeinerung mit expliziter Konstante prinzipiell publizierbar; entscheidend ist, dass der inkrementelle Charakter klar gerahmt wird. Der Angriff ist nicht mehr "toedlich", aber die Formulierung im Abstract und in `rem:significance` muss konsistent als "quantitative Verfeinerung" und nicht als "Reduktion auf eine einzige neue Ungleichung" auftreten.

### Angriff 2 (Step 5: toedlich) — Thm 8.10 ist Lehrbuch-Uebung

**Bewertung: BESTAETIGT IM KERN, ABGESCHWAECHT IM VERDIKT.**

Die Mathematik von Thm 8.10 ist tatsaechlich elementar: $\tau \in \mathcal{F} \Rightarrow \mathrm{Im}(\tau) \ge \sqrt{3}/2$, dann geometrische Reihe auf der $q$-Entwicklung. Der Beweis (Z. 1029-1050) umfasst neun Zeilen. Die Beschraenktheit von $|\eta(\tau)|^{24}$ auf $\mathcal{F}$ ist Standard, und die explizite Konstante 0.005 ist eine numerische Auswertung. Das ist sachlich richtig.

Was Step 5 jedoch unterspielt: Im **CRMath-Note-Format** ist nicht entscheidend, ob ein Schritt isoliert Lehrbuch-Niveau hat, sondern ob seine **Rolle in der Gesamtargumentation** neu ist. Thm 8.10 ist hier nicht das Kopf-Theorem, sondern technische Eingabe in Cor 8.11. Die headline ist die Reduktion auf $\lambda_1$ mit expliziter Konstante; Thm 8.10 ist der elementare Schritt, der diese Konstante liefert.

Empfehlung: Den elementaren Charakter im Beweistext **explizit anerkennen** (z.B. "elementary consequence of $\tau \in \mathcal{F}$"), statt ihn zu kaschieren. Das nimmt Reviewern den naheliegenden Einwand und positioniert Thm 8.10 ehrlich als "explicit numerical input" zu Cor 8.11.

### Angriff 3 (Step 5: toedlich) — $\lambda_1$ strikt schwieriger als $\Omega_E$

**Bewertung: BESTAETIGT, aber teilweise behoben durch rem:lambda1_omega.**

Die Mathematik des Angriffs ist korrekt: Im SL$_2(\mathbb{Z})$-reduzierten Basis ist $\lambda_1 = |\omega_2'|$ der kuerzeste Vektor. Wenn $\tau_\infty \notin \mathcal{F}$ (also $\mathrm{Im}(\tau_\infty) < \sqrt{3}/2$ oder $|\tau_\infty| < 1$), dann ist $\omega_2' \neq \omega_2$ eine Linearkombination, und $\lambda_1 \le \Omega_E$ mit moeglicher strikter Ungleichung. Eine untere Schranke an $\lambda_1$ ist also **stronger** als eine an $\Omega_E$ — das Paper beweist eine **hinreichende** Bedingung, die schaerfer ist als Goldfelds Originalbedingung.

Der Fix `rem:lambda1_omega` (Z. 1093-1111) macht dies offen, was Schritt 4 zu Recht als kritischen Fortschritt markiert. Damit ist der Angriff nicht mehr verheimlicht, aber substanziell verbleibt: Die Sprache "Reformulation" (in `rem:reformulation_not_reduction`, Z. 1122-1128) ist mathematisch falsch, **wenn** das Paper $\lambda_1$-Schranken statt $\Omega_E$-Schranken zur Reformulation erklaert. Es ist eine **strikt staerkere hinreichende Bedingung**, keine Aequivalenz zu Goldfeld.

Pflichtfix: Sprache "reformulation, not reduction" → "stronger sufficient condition than Goldfeld's, formulated in lattice-geometric terms".

### Angriff 4 (Step 5: schwer) — $\Delta_{\min}$ vs. $\Delta(\Lambda)$: 2-adische Faktoren

**Bewertung: TEILWEISE BESTAETIGT — Praezisierungspflicht, kein Show-Stopper.**

Die Beobachtung ist korrekt: Fuer Frey-Kurven gilt $\Delta_{\min} = (abc)^2 / 2^\delta$ mit $\delta \in \{0, 4, 8\}$, abhaengig von der 2-adischen Reduktion. Die Identitaet $|\Delta_{\min}| = (2\pi/|\omega_2'|)^{12} \cdot |\eta(\tau')|^{24}$ ist die analytische Diskriminanten-Formel; sie gilt fuer den Néron-Modell-Diskriminant **nach** korrekter Wahl der Néron-Differentiale, was bei Frey-Kurven 2-adische Korrekturen verlangt.

Fuer das Argument von Cor 8.11 ist dies jedoch **nicht** toedlich, weil:

1. Der 2-adische Faktor ist beschraenkt durch $2^8 = 256$, also eine $O(1)$-Konstante;
2. Die Konstante 0.005 in Thm 8.10 ist sowieso eine universelle Schranke, in der ein Faktor 256 in den Vorfaktor $c_\varepsilon$ absorbiert werden kann;
3. Der Skalenanteil (das $N^{6+\varepsilon}$-Verhalten) wird durch den 2-adischen Faktor nicht beruehrt.

Die Praezisierung ist trotzdem noetig fuer Reviewer-Haertung. Empfehlung: Bemerkung im Beweis von Cor 8.11, dass $|\Delta_{\min}| = |\Delta(\Lambda)|$ bis auf einen 2-adischen Faktor $\le 2^8$ gilt, der in der absoluten Konstante absorbiert wird.

### Angriff 5 (Step 5: schwer) — §4 falscher Beweis im Haupttext

**Bewertung: BESTAETIGT — strukturell unbefriedigend, A3 noch nicht behoben.**

Der Beweis von Prop 4.2 (Z. 412-438) enthaelt einen algebraischen Fehler ($|\eta(\ell\tau_p)| \ge c > 0$, korrekt: $|\eta(\ell\tau_p)|^2 \sim |q_p|^{\ell/12} \to 0$), der im Erratum `rem:erratum_gap` (Z. 441-459) explizit eingestanden wird. Step 4 hatte A3 bereits als Pflichtfix markiert: §4 in Anhang auslagern, Haupttext auf 3-5 Zeilen Skizze plus Verweis kuerzen.

Die Fix-Liste oben bestaetigt: A3 ist **noch nicht behoben**. Fuer ein Top-Journal-Format (CRMath, JTNB) ist ein expliziter Fehlbeweis im Haupttext ein desk-reject-Risiko, **selbst wenn** die Hauptresultate (Thm 8.10, Cor 8.11) davon unabhaengig sind. Der Reviewer sieht zuerst die Erratum-Bemerkung und schliesst auf mangelnde Sorgfalt.

Pflichtfix: §4-Beweis und Erratum in Anhang A; im Haupttext nur Proposition (mit Status-Marker "Conditional, proof gap") plus 2-3 Zeilen Plausibilitaet plus Pointer.

### Angriff 6 (Step 5: schwer) — Conj 4.1 nicht wohldefiniert

**Bewertung: BEREITS BEHOBEN — durch rem:conj_welldefined entschaerft.**

Step 5 monierte, dass Conj 4.1 in keiner der drei Lesarten (p-adisch, archimedisch, adelisch) sauber definiert ist. Der Fix E3 hat `rem:conj_welldefined` hinzugefuegt, der die drei Lesarten explizit diskutiert und festhaelt: p-adisch ist trivial erfuellt; archimedisch nicht wohldefiniert in der angegebenen Form; adelisch noch nicht ausgearbeitet.

Damit ist Conj 4.1 transparent als Heuristik / unausgearbeitete Vermutung markiert. Fuer ein CRMath-Note ist das akzeptabel, **wenn** der Status klar bleibt: Conj 4.1 ist nicht das tragende Glied der Argumentation, sondern eine motivierende Skizze fuer §4. Die tragende Argumentation laeuft archimedisch ueber Cor 8.11.

Empfehlung: Im Anhang (zusammen mit Fix A3) sollte der Status von Conj 4.1 als "exploratory" gekennzeichnet werden, damit Reviewer den Heuristik-Charakter sofort erkennen.

### Angriff 7 (Step 5: schwer) — Im(τ) < √3/2 in Tab 2 vs. Thm 8.10

**Bewertung: ABGESCHWAECHT — expositorisches Problem, nicht mathematisches.**

Der Beweis von Cor 8.11 (Z. 1081-1086) wendet Thm 8.10 korrekt auf das **reduzierte** $\tau' \in \mathcal{F}$ an, nicht auf das kanonische $\tau_\infty$ der Frey-Kurve. Die Identitaet $|\Delta_{\min}| = (2\pi/|\omega_2'|)^{12} \cdot |\eta(\tau')|^{24}$ ist $\SL_2(\mathbb{Z})$-invariant in der Diskriminante (linke Seite), wobei sich die rechte Seite konsistent mit dem Kuerzesten-Vektor-Wechsel transformiert.

Das mathematische Argument ist also **richtig**. Was bestaetigt bleibt: Tab 2 listet die unreduzierten $\mathrm{Im}(\tau_\infty)$-Werte (im Bereich [0.27, 0.91]), die im Allgemeinen NICHT die Voraussetzung von Thm 8.10 erfuellen. Eine Leserin, die nur Tab 2 anschaut, wuerde fragen: "Wie kann Thm 8.10 hier angewandt werden?"

Pflichtfix: Tab 2 um Spalte $\mathrm{Im}(\tau')$ (reduziert) ergaenzen, oder zumindest Tabellen-Caption/Begleittext erweitern: "$\tau_\infty$ unreduziert; nach $\SL_2(\mathbb{Z})$-Reduktion gilt $\mathrm{Im}(\tau') \ge \sqrt{3}/2$ und Thm 8.10 ist anwendbar."

### Angriff 8 (Step 5: heilbar) — Prop 3.1 letzter Schritt

**Bewertung: BESTAETIGT, leicht heilbar.**

Die Formulierung "at appropriate arguments" ist nicht hinreichend. Step 4 hat E5 (Apostol-Referenz) bereits als Empfehlung gefuehrt. Pflichtfix bei finaler Submission: Apostol §1.6 oder Köhler "Eta Products and Theta Series Identities" zitieren und den letzten Schritt explizit ausschreiben (eine Zeile).

### Angriff 9 (Step 5: schwer) — Prop 7.7 von Tab 2 widerlegt

**Bewertung: WIDERLEGT — Angriff beruht auf Fehllesung.**

Prop 7.7 (Diophantine reformulation, Z. 947-966) sagt: Die Bedingung $|\eta(\tau_\infty)|^{24} \ll N^\varepsilon$ ist **aequivalent** zu zwei Diophantine-Bedingungen, eine davon $\mathrm{Im}(\tau_\infty) \ge \varepsilon'/(2\pi) \cdot \log N$. Die zweite Bedingung (Approximationseigenschaft) ist gleichermassen erforderlich.

Tab 2 zeigt $\mathrm{Im}(\tau_\infty) \in [0.27, 0.91]$, was die erste Bedingung formal **nicht** erfuellt. Das ist jedoch **kein Widerspruch zu Prop 7.7**: Tab 2 zeigt empirisch, dass $|\eta(\tau_\infty)|^{24} < 1$ trotzdem gilt — naemlich weil die zweite Bedingung (Approximationsverhalten) fuer die getesteten Triples gut genug ist, dass das Produkt das fehlende Wachstum von $y$ kompensiert.

Mit anderen Worten: Prop 7.7 sagt $A \Leftrightarrow (B_1 \wedge B_2)$, und Tab 2 zeigt, dass $A$ empirisch gilt. Das impliziert $B_1 \wedge B_2$, nicht eine isolierte Verletzung von $B_1$.

Empfehlung: Prop 7.7 ist mathematisch sauber, aber das **Begleittext-Framing** ist missverstaendlich: Der Leser denkt, $B_1$ allein sei eine Voraussetzung fuer das abc-Argument. Klarstellung in `rem:numerical` oder einem zusaetzlichen Remark, dass die zwei Bedingungen interagieren und Tab 2 die Konjunktion testet, nicht $B_1$ isoliert.

### Angriff 10 (Step 5: heilbar) — Mining-Difficulty-Slogan

**Bewertung: BESTAETIGT — kosmetisch heilbar.**

Die Bemerkungen `rem:mining_difficulty`, `rem:poisson_regime`, `rem:katz_sarnak` sind heuristische Einordnung, kein Beweis. Step 4 hat B5 (Heuristik-Konsolidierung) bereits empfohlen. Fuer CRMath-Format gehoert das in einen einzigen "Heuristic remark" oder ganz heraus.

Empfehlung: Auf einen Absatz konsolidieren oder fuer die CRMath-Version komplett streichen. Heuristische Bemerkungen sind in einer 8-12-Seiten-Note Platzverschwendung und geben Reviewern Angriffsflaeche.

### Angriff 11 (Step 5: heilbar) — IUT-Vergleich praetentioes

**Bewertung: BESTAETIGT — kuerzen.**

§10 (IUT-Vergleich, Z. 1581-1611) stellt das Paper auf eine Stufe mit Mochizuki, ohne entsprechende Substanz zu liefern. Step 4 hat B4 (auf 3-4 Saetze kuerzen) empfohlen. Fuer CRMath ist das Pflicht: maximal 3-4 Saetze plus Verweis auf GeigerIUT2026.

### Angriff 12 (Step 5: schwer) — Self-Citation auf zirkulaeres Paper

**Bewertung: ABGESCHWAECHT — keine load-bearing Zitation.**

Der Self-Citation-Vorwurf zerfaellt in zwei Teile:

1. *Inhaltlich:* Wenn GeigerBSD2026 selbst eine Zirkularitaet bei Schritt B3 eingesteht, ist eine Berufung auf dieses Paper als "non-circularity"-Beleg substantiell schwach.
2. *Funktional:* Die Hauptresultate (Thm 8.10, Cor 8.11) haengen NICHT von GeigerBSD2026 ab. Die Self-Citations dienen Kontext-Setzung, nicht der Beweisfuehrung.

Solange das Paper klarstellt, dass GeigerBSD2026 und GeigerIUT2026 **kontextuell**, nicht load-bearing sind, ist dies eher kosmetisches Risiko als substantieller Angriff. Empfehlung: In den Self-Citations explizit "for context only, not used in proofs" anmerken.

### Angriff 13 (Step 5: heilbar) — Modulgrad ohne 4π²

**Bewertung: BESTAETIGT — leicht heilbar, Pflichtfix.**

Die korrekte Formel lautet: $\deg\varphi = (4\pi^2 \|f\|^2_{\mathrm{Pet}}) / (c_E^2 \cdot \mathrm{Vol}(E(\mathbb{C})))$, mit der Manin-Konstanten $c_E$. Die aktuelle Formulierung in `rem:modular_degree` (Z. 794-795) versteckt den $4\pi^2$-Faktor unter "up to the Manin constant", was **mathematisch falsch** ist (die Manin-Konstante ist eine separate Groesse, kein Synonym fuer $4\pi^2$).

Step 4 hat dies als B2 (E7) bereits gefuehrt. Pflichtfix vor Submission: Formel mit explizitem $4\pi^2$ und $c_E$.

### Angriff 14 (Step 5: schwer) — Petersson-Norm ohne Konvention

**Bewertung: BESTAETIGT — Pflichtfix.**

Die Asymptotik $\|f\|^2 \asymp L(\mathrm{Sym}^2 f, 1) / N$ haengt von der Volumen-Normierung auf $\Gamma_0(N)\backslash\mathfrak{H}$ ab (Iwaniec-Sarnak: hyperbolisches Volumen $[\Gamma(1):\Gamma_0(N)] \cdot \mathrm{Vol}(\Gamma(1)\backslash\mathfrak{H})$ vs. andere Konventionen; Faktor $N \log\log N$-Korrekturen je nach Konvention). Fuer einen Reviewer ist eine Asymptotik ohne Konvention **nicht nachvollziehbar**.

Pflichtfix: Iwaniec-Sarnak (2000) explizit zitieren mit Seitenangabe oder Formelnummer; Konvention angeben.

### Angriff 15 (Step 5: toedlich) — "Single bound" Marketing-Inflation

**Bewertung: BESTAETIGT, teilweise verschaerft durch interne Inkonsistenz.**

Dies ist der substanziellste verbleibende Angriff. Cor 8.11 wurde durch Fix A1 korrekt auf "implies" / einseitig umgestellt. Aber:

- **Z. 1116-1119** (`rem:significance`): "The entire content of the abc conjecture now resides in the single inequality~\eqref{eq:abc_lattice}". Nach A1-Fix ist nur eine Hinrichtung bewiesen, also residiert NICHT der "entire content" in eq:abc_lattice — sondern ein **hinreichendes** Kriterium.
- **Z. 1124-1128** (`rem:reformulation_not_reduction`): "The period lower bound ... and the abc conjecture are equivalent: proving either one yields the other." Direkter Widerspruch zum A1-Fix.
- **Z. 1543-1547** (`eq:abc_core`): Boxed-Gleichung mit "$\Longleftrightarrow$". Auch hier ist nur die Implikation $\Omega_E \ge \dots \Rightarrow \mathrm{abc}$ bewiesen.

Diese drei Stellen widersprechen direkt der A1-Korrektur. Solange das Paper an drei Stellen "Aequivalenz" sagt und an einer Stelle "implies", ist das nicht "Marketing-Inflation" im Sinne unbewiesener Behauptung, sondern **interne Inkonsistenz**, die jeden sorgfaeltigen Reviewer aufmerksam macht.

Pflichtfix: Konsistente Sprache "sufficient condition" / "implies" / "$\Rightarrow$" an allen drei Stellen. `rem:reformulation_not_reduction` muss umgeschrieben werden zu: "Corollary 8.11 establishes a *sufficient* condition for abc. The converse direction (abc $\Rightarrow$ eq.~\eqref{eq:abc_lattice}) is open." Ebenso `eq:abc_core` von "$\Longleftrightarrow$" auf "$\Longleftarrow$" oder "$\Leftarrow$" mit erlaeuterndem Text.

---

## B: Pflicht-Fixes vor CRMath-Einreichung

Konsolidierte Liste der Fixes, die **vor** Einreichung erforderlich sind:

| # | Fix | Bezug | Aufwand |
|---|-----|-------|---------|
| **P1** | `rem:significance` (Z. 1116-1119), `rem:reformulation_not_reduction` (Z. 1122-1128), `eq:abc_core` (Z. 1543-1547): Aequivalenzsprache durchgaengig auf "sufficient condition" / "implies" / "$\Rightarrow$" umstellen. Diese drei Stellen widersprechen direkt dem A1-Fix in Cor 8.11. | Angriff 15 + interne Inkonsistenz | klein, aber kritisch |
| **P2** | §4 (Prop 4.2-Beweis + Erratum) in Anhang A auslagern; im Haupttext nur Statement + 2-3 Zeilen Plausibilitaet + Pointer. | Angriff 5 (A3 Step 4) | mittel |
| **P3** | Tab 2: Spalte $\mathrm{Im}(\tau')$ (reduziert) hinzufuegen oder Caption-Hinweis: "$\tau_\infty$ unreduziert; nach $\SL_2(\mathbb{Z})$-Reduktion ist Thm 8.10 anwendbar." | Angriff 7 | klein |
| **P4** | `rem:modular_degree` (Z. 794-795): Korrekte Formel $\deg\varphi = (4\pi^2 \|f\|^2_{\mathrm{Pet}})/(c_E^2 \cdot \mathrm{Vol}(E(\mathbb{C})))$; Manin-Konstante $c_E$ explizit. | Angriff 13 (B2 Step 4) | klein |
| **P5** | `eq:petersson_sym2` (Z. 743-747): Iwaniec-Sarnak-Konvention explizit angeben (Seite/Formelnummer) | Angriff 14 | klein |
| **P6** | "Reformulation, not reduction"-Sprache in Cor 8.11 / `rem:reformulation_not_reduction` korrigieren: Es ist eine **stronger sufficient condition** als Goldfelds Originalform, keine Aequivalenz-Reformulierung. | Angriff 3 | klein |
| **P7** | `rem:lambda1_omega`: Klar machen, dass die "Translation lambda_1-Schranke -> Omega_E-Schranke" eine separate offene Frage ist; Frey-Kurven Néron-Differential-Normierung kurz benennen. | Angriff 3 (Verfeinerung) | klein |

**Aufwand insgesamt:** 1-2 Iterationen (1-2 Tage). Alle Pflichtfixes sind editorisch / lokal; keine neuen Beweise erforderlich.

---

## C: Empfohlene Fixes (nice-to-have, Reviewer-Haertung)

| # | Fix | Bezug |
|---|-----|-------|
| E1 | Prop 3.1 letzter Schritt: Apostol §1.6 oder Köhler-Referenz; Modulidentitaet explizit ausschreiben (1 Zeile). | Angriff 8 (B1 Step 4) |
| E2 | Cor 8.11 Beweis: 2-adischer Faktor $\Delta_{\min} = |\Delta(\Lambda)|/2^\delta$ ($\delta \le 8$) explizit erwaehnen, Absorption in der Konstante. | Angriff 4 |
| E3 | §10 (IUT-Vergleich) auf 3-4 Saetze + Verweis auf GeigerIUT2026 kuerzen. | Angriff 11 (B4 Step 4) |
| E4 | `rem:mining_difficulty`, `rem:poisson_regime`, `rem:katz_sarnak` zu einem einzigen "Heuristic remark" verdichten oder fuer CRMath-Version streichen. | Angriff 10 (B5 Step 4) |
| E5 | Self-Citations (GeigerBSD2026, GeigerIUT2026): explizit als "for context only, not used in proofs" markieren. | Angriff 12 |
| E6 | Conj 4.1 (in den Anhang, zusammen mit Fix P2): als "exploratory" markieren; Status klar kennzeichnen. | Angriff 6 (Verfeinerung) |
| E7 | Thm 8.10 Beweis: elementarer Charakter explizit anerkennen (z.B. "elementary consequence of $\tau \in \mathcal{F}$"). | Angriff 2 |
| E8 | Manin-Drinfeld-Luecke in Prop 7.5 (Rationalitaet $\neq$ Periodenformel direkt) explizieren. | B6 Step 4 |
| E9 | Numerische Tabelle: "16 representative cases" → "16 tested, 9 displayed" konsistent. | E10 Step 3 (bereits teilweise behoben) |

Diese Punkte sind nicht blockierend, schliessen aber die wahrscheinlichen Reviewer-Einwurfsflaechen.

---

## D: Einreichungsempfehlung CRMath

**Empfehlung:** **Bedingt einreichbar** nach Erledigung der Pflichtfixes P1-P7 (1-2 Iterationen).

**Begruendung:**

- **Pro CRMath:** Das Paper hat nach den Fixes E1-E10 + Goldfeld-Zitat einen klar identifizierbaren, modesten Beitrag: explizite Konstante 0.005, $\lambda_1$-Formulierung, expliziter $\eta$-Beweis. Fuer das Note-Format (8-12 Seiten) ist das im Bereich des Publizierbaren, wenn der inkrementelle Charakter ehrlich gerahmt ist und die internen Inkonsistenzen (P1) bereinigt sind.
- **Riskant fuer CRMath:** CRMath legt Wert auf Eleganz und Klarheit. Solange `rem:significance` + `rem:reformulation_not_reduction` + `eq:abc_core` Aequivalenz-Sprache tragen, wirkt das Paper unsauber. Ein sorgfaeltiger Reviewer (zwingend bei CRMath) wird diese Inkonsistenz innerhalb von 10 Minuten finden.
- **Backup-Journal:** **Journal de Théorie des Nombres de Bordeaux (JTNB)** — etwas weniger prestigetraechtig, aber stilistisch toleranter gegenueber inkrementellen Verfeinerungen mit ehrlichem Framing. Bei Ablehnung durch CRMath (oder zur Risikominimierung) ein moeglicher erster Versuch. Auch: **Acta Arithmetica** als zweite Backup-Option.

**Submission-Strategie:**

1. **Phase 1 (1-2 Tage):** Pflichtfixes P1-P7 umsetzen. Insbesondere die Sprach-Konsistenz (P1, P6) ist im jetzigen Zustand der wichtigste Schritt.
2. **Phase 2 (1 Tag):** Empfohlene Fixes E1-E5 umsetzen, sofern Platzbudget es erlaubt.
3. **Phase 3 (1 Tag):** CRMath-Format-Anpassung (8-12 Seiten, Heuristik kuerzen, KI-Disclosure L1 oder L2 in Acknowledgements).
4. **Submission an CRMath** mit kurzem Cover Letter, der den inkrementellen Charakter (quantitative Verfeinerung von Goldfeld 1988) explizit benennt.

Die "toedlich"-Verdikte aus Step 5 (Angriffe 1, 2, 3, 15) sind in dieser Form **nicht** alle haltbar:

- Angriff 1: ABGESCHWAECHT (Goldfeld-Zitat plus inkrementeller Beitrag);
- Angriff 2: BESTAETIGT IM KERN, ABGESCHWAECHT IM VERDIKT (elementar, aber als technische Eingabe in Cor 8.11 in Ordnung);
- Angriff 3: BESTAETIGT (rem:lambda1_omega macht es offen, "Reformulation"-Sprache muss aber raus);
- Angriff 15: BESTAETIGT und teilweise verschaerft durch interne Inkonsistenz nach A1-Fix.

Toedlich im Sinne von "desk-reject, kein Fix moeglich" ist **keiner**. Aber ohne Pflichtfixes P1-P7 ist die Submission riskant.

---

## E: Readiness-Score

| Zustand | Score | Begruendung |
|---------|-------|-------------|
| Aktueller Stand (nach Step-4-Fixes inkl. neuer Inkonsistenz) | **5.5/10** | Die A1-Korrektur in Cor 8.11 ist ein Fortschritt, aber `rem:significance`, `rem:reformulation_not_reduction`, `eq:abc_core` sind noch nicht angeglichen. Interne Inkonsistenz ist eine Regression gegenueber dem Step-4-Score. |
| + P1 (Sprach-Konsistenz) | **6.5/10** | Interne Inkonsistenz behoben, Marketing-Angriff entkraeftet. |
| + P1, P2 (§4 in Anhang) | **7.0/10** | Strukturelles Hauptrisiko (Erratum im Haupttext) entfernt. |
| + P1-P7 (alle Pflichtfixes) | **7.5/10** | Reviewer-fest. Modester, aber sauberer Beitrag. |
| + P1-P7 + E1-E5 (empfohlen) | **8.0/10** | Maximal erreichbarer Score fuer dieses Paper-Konzept. Nicht hoeher, weil die Neuheits-Frage (Goldfeld als Vorlage) ein strukturelles Limit fuer CRMath setzt. |

**Mein Kompass:** Ein 8.0-Paper ist publizierbar in CRMath / JTNB / Acta Arithmetica, aber nicht in einem A-Journal (Annals, JAMS, Inventiones). Das ist konsistent mit dem Anspruch einer Note: ein klarer, modester, sauber gerahmter Beitrag, kein Durchbruch.

---

## Score-Trajektorie

| Step | Score | Hauptbefund |
|------|-------|-------------|
| Step 1 (Konstruktiv 1) | 5.5/10 | §4 vs. §7 Inkonsistenz |
| Step 2 (Experte) | 4.5/10 | Thm 4.2 algebraisch falsch; Conj 4.1 nicht wohldefiniert |
| Step 3 (Konstruktiv 2) | 5.5/10 | E1-E6 Fixes; E6 unfixiert; Struktur-Probleme |
| Step 4 (Experte 2) | 6.0/10 | A1: nur Hinrichtung; Titel + §4-Struktur |
| Step 5 (Widerleger) | adversarial | 4 toedliche Angriffe (Goldfeld-Neuheit, Trivialitaet, $\lambda_1$, Marketing) |
| **Step 6 (Neutralisierung)** | **5.5/10 (aktuell) / 7.5/10 (nach P1-P7)** | **Interne Inkonsistenz nach A1-Fix; Step-5-Angriffe groesstenteils abgeschwaecht, Pflichtfixes klar.** |

---

## F: Pflichtfixes vor Step 7 (Abschluss)

1. **P1**: Aequivalenzsprache in `rem:significance`, `rem:reformulation_not_reduction`, `eq:abc_core` konsistent auf "sufficient condition" umstellen — **kritisch**, da interne Inkonsistenz nach A1-Fix.
2. **P2**: §4 in Anhang A auslagern.
3. **P3**: Tab 2 — Spalte $\mathrm{Im}(\tau')$ (reduziert) oder Caption-Klarstellung.
4. **P4-P5**: Modulgrad $4\pi^2$-Faktor; Petersson-Konvention.
5. **P6-P7**: "Reformulation, not reduction"-Sprache und `rem:lambda1_omega` praezisieren.

Empfohlene Folge-Iterationen (1-2 Tage Aufwand). Step 7 (Abschluss) sollte verifizieren, dass:

- Cor 8.11 + `rem:significance` + `rem:reformulation_not_reduction` + `eq:abc_core` durchgaengig "sufficient condition" sagen;
- §4-Beweis aus dem Haupttext entfernt ist;
- Tab 2 die $\SL_2(\mathbb{Z})$-Reduktion expliziert.

Dann ist das Paper bei einem Score von ca. 7.5/10 reif fuer CRMath-Submission (oder JTNB als Backup).
