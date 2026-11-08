# No Positive Margin from Pencils — companion paper v0.1

[Deutsch](README_de.md)

**No Positive Margin from Pencils: Xiao's Lemma, a Rank-r Margin Identity, and the Nef Barrier in Parshin–Moret-Bailly Height Arguments**, by Lukas Geiger. Version 0.1, 8 November 2026.

- Zenodo record (v0.1): [10.5281/zenodo.24046160](https://doi.org/10.5281/zenodo.24046160)
- Concept DOI (all versions, use for citation): [10.5281/zenodo.24046159](https://doi.org/10.5281/zenodo.24046159)
- Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

This is a companion paper to Paper A ([10.5281/zenodo.21916900](https://doi.org/10.5281/zenodo.21916900)). It shows that the geometric margin in the pencil step of Parshin–Moret-Bailly height arguments is never positive: in rank two via Xiao's lemma for pencils, in rank r via a margin identity and a nef lemma. As an application, Proposition 9 vi) of arXiv:2611.05217v1 (Soulé) is shown to be false.

Claim boundary: the paper makes no statement about the abc conjecture, and the arithmetic side of the Harder–Narasimhan-unstable case for r ≥ 3 is left open.

## Files

- [English PDF](pmb_pencil_nogo_v0.1_en.pdf), 12 pages, and [source](pmb_pencil_nogo_v0.1_en.tex).
- [German PDF](pmb_pencil_nogo_v0.1_de.pdf), 13 pages, and [source](pmb_pencil_nogo_v0.1_de.tex).
- AI-disclosure inputs: [EN](ai_disclosure_STANDARD_en.tex), [DE](ai_disclosure_STANDARD_de.tex).
- [manifest.json](manifest.json) with SHA-256 and byte counts of all files.

The TeX sources differ from the compiled PDFs only in the `\input` path of the AI-disclosure file, which points to the local copy in this directory. The PDFs are unchanged.

## Build

Run pdfLaTeX from this directory, three passes per language:

```sh
pdflatex -interaction=nonstopmode -halt-on-error pmb_pencil_nogo_v0.1_en.tex
pdflatex -interaction=nonstopmode -halt-on-error pmb_pencil_nogo_v0.1_de.tex
```

PDF metadata may vary on rebuild; the manifest binds the published PDF bytes.

## Citation

Please cite the concept DOI [10.5281/zenodo.24046159](https://doi.org/10.5281/zenodo.24046159), which always resolves to the latest version.

Copyright © 2026 Lukas Geiger. This paper package is licensed under CC BY 4.0. The repository's MIT licence continues to apply to its software; this directory specifies the paper licence. Third-party results remain attributed to their original authors.
