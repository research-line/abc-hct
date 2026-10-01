# Global Normalization Contract Lemma — corrective manuscript v1.2

[Deutsch](README_de.md)

Author: Lukas Geiger. Manuscript date: 2 October 2026. The preceding Zenodo
record is [v1.1](https://doi.org/10.5281/zenodo.21924254); the version family is
[10.5281/zenodo.21924253](https://doi.org/10.5281/zenodo.21924253).

This package contains the English manuscript (24 pages), the German manuscript
(26 pages), their LaTeX sources and the two AI-disclosure inputs. Version 1.2
is a corrective draft; publication of the new Zenodo record is a separate step.

The repair corrects the overlined ATS IV domain and restores the
outer absolute-value bars in the logarithmic-volume comparison. It separates
absolute-value normalization, Haar measure and the module, and retracts the
generic identification of the algebraic hull with the convex hull. The
cross-frame measure comparison remains open in every diagnostic branch.
The named transport is a possible sufficient route, not a necessary condition.
The elementary product-formula multiplier lemma and the conditional F1/F2
derivation remain; neither E2 nor the abc conjecture is proved by this paper.

The manuscript's 14 bibliography entries identify the primary literature.
This package contains no copied primary-source PDFs and no new computational
experiment or computational proof certificate.

Build each language with pdfLaTeX from this directory, three passes:

```sh
pdflatex -interaction=nonstopmode -halt-on-error GNC_Assessment_v1_2_en.tex
pdflatex -interaction=nonstopmode -halt-on-error GNC_Assessment_v1_2_ger.tex
```

Both checked PDFs compiled successfully with no final warnings. All 50 pages
were inspected for layout using contact sheets. The manifest binds the exact
source and PDF bytes; PDF metadata may vary on rebuild.

Copyright © 2026 Lukas Geiger. This paper package is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The repository's MIT
license continues to apply to its software; this directory specifies the paper
license. Third-party quotations remain attributed to their original authors.
