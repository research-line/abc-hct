# Bridge Certificate — corrective version 0.3

Part 3 of the abc Gap Series. Published bilingual preprint: [Zenodo 0.3](https://zenodo.org/records/23090371), DOI **10.5281/zenodo.23090371**. English: 35 pages; German: 37 pages. License: CC BY 4.0.

The revision separates the prospective application recipe from partial historical cases, corrects the ATS IV v2 §6.10/Theorem 6.10.1 reference, restores the LANA eta notation, and limits the role crosswalk and seven obligations to the proposed audit specification. It asserts no mathematical error, proof or disproof of abc. The typed LANA bridge, C7 positive control, full source/formula review and independent method validation remain open.

The English and German sources share 38 labels, 11 citations and 15 bibliography keys. Six final compiler runs succeeded; all 72 pages were visually checked. Published downloads match the local PDFs by SHA-256 and Zenodo MD5. Independent reviews accepted the bounded scientific correction and the final technical changes; this does not constitute whole-paper acceptance.

Build each manuscript from this directory with a standard pdfLaTeX installation (including `glyphtounicode`). The disclosure include is bundled. Run each command three times to settle cross-references:

```sh
pdflatex -interaction=nonstopmode -halt-on-error BRIDGE_CERTIFICATE_v0_3_en.tex
pdflatex -interaction=nonstopmode -halt-on-error BRIDGE_CERTIFICATE_v0_3_ger.tex
```

`release-v0.3.json` records the exact source/PDF hashes and limitations. The published Zenodo filenames are `BRIDGE_CERTIFICATE_3_en.pdf` and `BRIDGE_CERTIFICATE_3_ger.pdf`; this source bundle retains the local `v0_3` filenames.
