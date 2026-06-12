# Quellencheck Paper B (Beneath the abc Landscape) — 2026-05-27

**Paper:** `PAPER_B__beneath_abc_landscape/beneath_abc_landscape_EN.tex` (Mai 2026, EN-only)
**Geprüft:** 6 Bibitems in `thebibliography` + Body-Zitations-Check
**Methodik:** WebSearch + WebFetch gegen Primärquellen (Springer, Cambridge Core, Project Euclid, ADS, EUDML, Zenodo, arXiv).
**Legende:** ✓ = vollständig korrekt; ⚠ = kleinere Abweichung/Hinweis; ❌ = Fehler.

---

## Befund pro Bibitem

### Ribet1990
- **Status:** ✓
- **Quellen:**
  - <https://eudml.org/doc/143793>
  - <https://link.springer.com/article/10.1007/BF01231195>
  - <https://ui.adsabs.harvard.edu/abs/1990InMat.100..431R/abstract>
  - <https://math.berkeley.edu/~ribet/Articles/invent_100.pdf>
- **Verifizierte Daten:**
  - Autor: K. A. Ribet ✓
  - Titel: "On modular representations of Gal(Q̄/Q) arising from modular forms" ✓
  - Journal: Invent. Math. ✓
  - Volume 100, pp. 431–476, Jahr 1990 ✓
  - DOI 10.1007/BF01231195 ✓
- **Korrektur:** Keine. Der LaTeX-Eintrag verwendet `\Gal(\overline{\mathbb Q}/\mathbb Q)` korrekt.

### Goldfeld2002
- **Status:** ⚠ (kleinere Titel-Formvariante; sachlich korrekt)
- **Quellen:**
  - <https://www.cambridge.org/core/books/abs/panorama-of-number-theory-or-the-view-from-bakers-garden/modular-forms-elliptic-curves-and-the-abcconjecture/53251777764D05438AE3C7C846FADCB4>
  - <https://www.math.columbia.edu/~goldfeld/ABC-Conjecture.pdf>
- **Verifizierte Daten:**
  - Autor: Dorian Goldfeld ✓
  - Chapter-Titel auf Cambridge Core: **"Modular Forms, Elliptic Curves and the ABC-Conjecture"** (mit Bindestrich "ABC-Conjecture", OHNE Oxford-Komma vor "and"). Im Paper: "Modular forms, elliptic curves, and the ABC conjecture" (mit Komma, ohne Bindestrich).
  - Book: *A Panorama of Number Theory or The View from Baker's Garden*, ed. G. Wüstholz ✓
  - Cambridge Univ. Press, 2002, pp. 128–147 ✓
  - DOI 10.1017/CBO9780511542961.010 ✓
- **Korrektur (optional, kosmetisch):** Titel an Originalform anpassen: `Modular forms, elliptic curves and the ABC-conjecture` (Komma vor "and" entfernen, Bindestrich in "ABC-conjecture" einfügen) — entspricht aber gängiger Zitierpraxis auch ohne Anpassung. Substanzielle Daten alle korrekt.

### Watkins2002
- **Status:** ✓
- **Quellen:**
  - <https://projecteuclid.org/journals/experimental-mathematics/volume-11/issue-4/Computing-the-Modular-Degree-of-an-Elliptic-Curve/em/1057864659.full>
  - <https://www.tandfonline.com/doi/abs/10.1080/10586458.2002.10504701>
- **Verifizierte Daten:**
  - Autor: Mark Watkins ✓
  - Titel: "Computing the Modular Degree of an Elliptic Curve" ✓
  - Journal: Experimental Mathematics ✓
  - Volume 11(4), Jahr 2002, pp. 487–502 ✓
  - DOI 10.1080/10586458.2002.10504701 ✓
- **Korrektur:** Keine.

### Cesnavicius2018
- **Status:** ✓ (Issue-Nummer optional)
- **Quellen:**
  - <https://www.cambridge.org/core/journals/compositio-mathematica/article/abs/manin-constant-in-the-semistable-case/42D5D9E3E5F758E35C12E5FB5BA1781E>
  - <https://arxiv.org/abs/1703.02951>
- **Verifizierte Daten:**
  - Autor: Kęstutis Česnavičius ✓ (LaTeX `\v{C}esnavi\v{C}ius` korrekt)
  - Titel: "The Manin constant in the semistable case" ✓
  - Journal: Compositio Math. (Compositio Mathematica) ✓
  - Volume 154, Issue 9, Jahr 2018, pp. 1889–1920 ✓
  - DOI 10.1112/S0010437X18007273 ✓
- **Korrektur (optional):** Im Paper ist die Issue-Nummer (9) nicht angegeben. Üblich/akzeptabel; bei strikter Bibliographie ggf. ergänzen: `\textbf{154}(9), 1889--1920.`

### GeigerBSD2026
- **Status:** ✓
- **Quellen:**
  - <https://zenodo.org/records/19106186>
  - <https://doi.org/10.5281/zenodo.19106186>
- **Verifizierte Daten:**
  - Autor: Lukas Geiger ✓
  - Titel: "The BSD Conjecture as a Positivity Normal-Form Theorem" ✓ (1:1 wie im Paper)
  - Jahr: 2026 (publiziert 19. März 2026, v1.1 vom 3. April 2026) ✓
  - DOI: 10.5281/zenodo.19106186 — auf Zenodo als Version-DOI v1.1 aufgelöst; in der LaTeX-Bibitem als „DOI" geführt. Funktioniert als persistenter Link. Falls bewusst Concept-DOI gewünscht: ggf. prüfen, ob 19106186 die Concept- oder eine Version-DOI ist (Webseite zeigt direkt v1.1 + Hinweis auf neuere Version — d.h. der Link ist nicht "concept", sondern entweder die initiale Version-DOI mit Auto-Forward auf Konzept, oder bereits eine Version).
- **Korrektur:** Keine zwingende. Falls strikte Concept-DOI gewünscht: User-seits prüfen, ob für BSD-Paper eine separate Concept-DOI vergeben ist (vgl. CLAUDE.md: Concept-DOI ist die Zahl aus `links.versions` der Zenodo-API).

### GeigerIUT2026
- **Status:** ⚠ (Titel-Suffix "(DRAFT)" fehlt; Versionsstatus DRAFT)
- **Quellen:**
  - <https://zenodo.org/records/19960781> → redirected zu v6 = <https://zenodo.org/records/20223276>
- **Verifizierte Daten:**
  - Autor: Lukas Geiger ✓
  - Titel auf Zenodo (verbatim, aktuellste Version v6, Mai 2026): **"The Gap in IUTchIII, Corollary 3.12: From Attempted Repair to Structural Diagnosis (DRAFT)"**
  - Im Paper: "The Gap in IUTchIII, Corollary~3.12: From Attempted Repair to Structural Diagnosis" — **"(DRAFT)" fehlt**.
  - Concept-DOI 10.5281/zenodo.19960781 ✓ (resolviert auf aktuelle Version)
  - Jahr 2026 ✓
- **Korrektur (Empfehlung):**
  - Entweder Suffix "(DRAFT)" im Bibitem ergänzen, um Zenodo-Form 1:1 zu treffen
  - ODER auf Zenodo-Seite den Titel ohne "(DRAFT)" setzen (in-place via API edit, vgl. `_templates/ZENODO_CREDENTIALS_TEMPLATE.md`), wenn der Status nicht mehr DRAFT sein soll
  - Hinweis: Eine als Referenz in einem publizierten Paper genannte Zenodo-Quelle mit „DRAFT"-Status ist semantisch heikel. Empfehlung: Vor Submission von Paper B den IUT-Eintrag entweder aus dem DRAFT-Status nehmen oder im Bibitem als „Preprint (Draft)" markieren, damit das Zitationsverhalten zur Quelle passt.

---

## Body-Zitations-Check

### Fehlende Bibliographie für eine prominent zitierte Quelle: Iyengar–Khare–Manning, arXiv:2510.05418

Im Body wird **ohne `\cite{}` und ohne entsprechenden Bibitem-Eintrag** an mehreren zentralen Stellen auf Iyengar–Khare–Manning, arXiv:2510.05418 referenziert:

- **Zeile 681:** Sektionsüberschrift `\subsection*{Declared Proof Target: Route A via IKM 2510.05418}`
- **Zeile 683:** "The IKM-S2 specialisation …"
- **Zeile 694–695:** "The relevant tool is Iyengar--Khare--Manning, arXiv:2510.05418."
- **Zeile 695:** "IKM Theorem 2.30 …"
- **Zeile 701, 706, 711:** explizite Verweise auf "*Theorem 2.20*", "*Theorem 2.32*", "*Theorem 3.5*"
- **Zeile 775:** "IKM, §5 provides the local Cohen--Macaulay model …"

**Verifikation der Quelle:** ✓
- arXiv 2510.05418: Srikanth B. Iyengar, Chandrashekhar B. Khare, Jeffrey Manning, **"The commutative algebra of congruence ideals and applications to number theory"**, Oktober 2025.
- Quelle: <https://arxiv.org/abs/2510.05418>

**Schweregrad:** ❌ Fehlende Bibliographie-Eintrag. In einem wissenschaftlichen Paper sollten konkrete Verweise auf Theorem 2.20/2.30/2.32/3.5 und §5 einer externen Arbeit einen Bibitem haben. Das ist eine **substantielle Lücke**, weil die Beweistargets von Route A direkt von dieser Arbeit abhängen ("The central analytic load is H3-eq …").

**Empfohlene Korrektur:** Bibitem ergänzen, z. B.:

```latex
\bibitem{IKM2025}
S.~B. Iyengar, C.~B. Khare, and J. Manning (2025).
The commutative algebra of congruence ideals and applications
to number theory.
Preprint, arXiv:2510.05418.
\url{https://arxiv.org/abs/2510.05418}
```

Und im Body an den IKM-Referenzstellen `\cite{IKM2025}` einfügen, mindestens an Zeile 694 ("Iyengar--Khare--Manning, arXiv:2510.05418") und bei den Theorem-Zitaten (2.20, 2.30, 2.32, 3.5) als `\cite[Thm.~2.20]{IKM2025}` etc.

### Weitere Body-Checks

- **`\cite{}`-Befehle im Body:** Alle vorkommenden `\cite{}`-Argumente (Goldfeld2002, Watkins2002, Ribet1990, Cesnavicius2018, GeigerBSD2026, GeigerIUT2026) haben ein passendes `\bibitem`. Keine "?"-Referenzen oder broken cites.
- **Ungenutzte Bibitems:** Keine. Alle 6 Bibitems werden im Body verwendet.
- **Autor-/Personennamen ohne Bibitem:** Im Body sind keine weiteren personennamen-basierten Quellenverweise sichtbar (außer Goldfeld, Watkins, Ribet, Frey, Manin — alle als Methoden-/Theorienamen verwendet; nicht alle erfordern Bibitem). Frey-Konstruktion, Manin-Symbole, Atkin-Lehner, Wiedemann, Berlekamp-Massey, Cohen-Macaulay, Wiles-Lenstra-Diamond, Gorenstein sind Standard-Konzeptnamen und brauchen keinen separaten Bibitem.

---

## Gesamt-Befund

| Eintrag | Status |
|---|---|
| Ribet1990 | ✓ |
| Goldfeld2002 | ⚠ (Titel-Formvariante, kosmetisch) |
| Watkins2002 | ✓ |
| Cesnavicius2018 | ✓ (Issue-Nr. fehlt, kosmetisch) |
| GeigerBSD2026 | ✓ |
| GeigerIUT2026 | ⚠ (Titel-Suffix "(DRAFT)" fehlt; Zenodo-Status DRAFT) |
| **IKM (arXiv:2510.05418)** | **❌ Fehlender Bibitem** |

**Keine Halluzinationen entdeckt.** Alle 6 vorhandenen Bibitems sind reale, verifizierte Publikationen mit korrekten Autoren-, Titel- und Bibliographie-Daten. Kleinere Abweichungen (Goldfeld-Titel-Formatierung, Cesnavicius-Issue) sind kosmetisch und entsprechen üblicher Zitierpraxis.

## Empfehlungen (Priorität)

1. **P0 (vor Submission/Zenodo-Push):**
   - **IKM-Bibitem ergänzen** (`\bibitem{IKM2025}` für Iyengar–Khare–Manning, arXiv:2510.05418) und im Body alle IKM-Referenzen mit `\cite{IKM2025}` (oder `\cite[Thm.~2.X]{IKM2025}` an den präzisen Theorem-Stellen) auszeichnen.
   - **GeigerIUT2026:** Entscheidung treffen: (a) Suffix "(DRAFT)" im Titel ergänzen, ODER (b) Zenodo-Record aus DRAFT-Status nehmen (Title via `paper_publisher.py --modify-last <RECORD_ID> --title "…"`), damit Paper-Bibitem und Zenodo-Quelle synchron sind. Empfehlung: Status klären, dann Bibitem oder Zenodo-Titel anpassen.

2. **P1 (optional, Qualitätsverbesserung):**
   - **Goldfeld2002:** Titel an Cambridge-Originalform anpassen ("Modular Forms, Elliptic Curves and the ABC-Conjecture") — kosmetisch.
   - **Cesnavicius2018:** Issue-Nummer (9) ergänzen: `\textbf{154}(9), 1889--1920.` — strikt.
   - **GeigerBSD2026:** Prüfen, ob 10.5281/zenodo.19106186 die Concept-DOI ist oder eine Version-DOI; bei Concept-DOI ist die Referenz langlebiger.

3. **P2 (kein Handlungsbedarf):**
   - Ribet1990, Watkins2002: keine Korrekturen nötig.

---

*Erstellt durch Quellencheck-Agent (L.G., 2026-05-27).*
*Methodik: Pro Bibitem mindestens eine WebSearch + ein WebFetch gegen die Originalquelle (Verlags-Webseite oder Repository). Keine geratenen Daten.*
