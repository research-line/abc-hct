# abc-hct

Private working repository for the HCT/abc research line.

Current scope:

- bilingual abc/HCT paper drafts,
- reproducible scripts for the no-Magma Manin-Hecke quotient route,
- curated machine-readable result artifacts needed for verification,
- publication-ready supplements after curation.

Repository policy:

- Keep this repository private until the corresponding DOI/public release gate is reached.
- GitHub normally receives computation scripts and reproducible results, not internal proof notebooks.
- Do not push `BEWEISNOTIZ*`, `_proof-notes/`, handoffs, raw agent transcripts, credentials, or proof scratch by default.
- Internal proof notes become repo-publishable only after journal publication and explicit release as attached notes.
- Public release should contain only curated paper files, reproducibility scripts, selected results, and a clean disclosure/status note.

Primary local project path:

```text
C:\Users\User\OneDrive\.TOPICS\.RESEARCH\.LAB\.HCT\abc
```

Current computational milestone:

The no-Magma Sage/Python Manin-Hecke quotient over `GF(3863)` has killed the mapped basket `60168/80224/120336/240672` in both `raw` and `anc` modes. The remaining work is theoretical embedding, rank certification, and uniform FAQS/M* transfer.