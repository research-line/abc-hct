# Changelog - abc-hct

All notable changes to this repository will be documented in this file.

## [0.1.7] - 2026-08-21

### Added
- Added bilingual `SECURITY.md` defining Zero-Egress, Local-First, unprivileged User-Mode operation, confidentiality of working drafts/proof notes, and responsible disclosure guidelines.
- Added CI workflow badge, Platform (`Linux | Windows | macOS`), Privacy (`100% Offline | Zero-Egress`), and Security (`Local-First | Deterministic`) badges to `README.md` & `README_de.md`.
- Added second interactive bilingual Mermaid sequence diagram illustrating the Curated Verification & Reproducibility Lifecycle (modular symbol engine -> Hecke annihilators -> deterministic certificate ledger -> test gate validation).
- Expanded Sibling Research & Ecosystem Matrix with `rh-even-dominance` (Riemann Hypothesis even dominance) and `open-bricks` umbrella links.
- Added PEP 621 classifiers (Python 3.13, OS Independent, Linux, Windows, MacOS, Physics) and project URLs ("Bug Tracker", "Changelog") in `pyproject.toml`.
- Expanded automated metadata test suite in `tests/test_metadata.py` to 10 comprehensive contract tests (total 15 automated tests).

### Changed
- Discoverability, README-Design, Badges, Security Parity & Metadata Parity Check (Pfad B, 2026-08-21).
- Updated `llms.txt` header `Last-checked` timestamp to `2026-08-21`, added `SECURITY.md` link, and updated test suite count (15 automated tests).
- Bumped version to `0.1.7` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suite.
- Verified all 270 research scripts under `_scripts/` via Python syntax compilation (`compileall`), `ruff check .`, and `pytest` suite.

### 2026-08-18 -- Public release

#### Changed
- **Repository made public** (user-approved release gate: Paper A live since 2026-08-13, DOI 10.5281/zenodo.21916900). Verified reachable anonymously (`raw.githubusercontent.com`, HTTP 200) immediately after the switch.
- Zenodo record 21964107 (Paper A, v1.2) now carries a related identifier `isSupplementedBy -> https://github.com/research-line/abc-hct` (in-place metadata edit via `paper_publisher.py --modify-last --github-url`, no new version; before/after metadata diff confirmed this was the only field that changed; the tool's built-in live-verification passed).
- Removed now-stale "private repository" wording from `README.md`, `README_de.md`, and `llms.txt` (self-description must match reality once public).
- `.LAB/.HCT/abc/GITHUB_REPO.md` (project-internal status doc) updated to record the public switch and the new related identifier.

#### Deferred (documented, not executed)
- Code-Availability section in Paper A/B LaTeX sources: prepared text ready, insertion deferred to each paper's next due version (a pure link addition does not by itself justify a new Zenodo version per pipeline policy).
- Individual proof-note curation under `_proof-notes/` (>1000 candidates): out of scope for this pass, tracked as a follow-up.

### 2026-08-17 -- Public-readiness curation

#### Fixed
- **Privacy leak (host paths):** 8 tracked `_results/*.json` files leaked the absolute local path in JSON-escaped form (`source`/`case_dir`/`file`/`scripts` provenance fields); 2 further tracked `.status.json` files leaked the absolute Windows-Store Python interpreter path in a logged `cmd` array. Redacted all 10 files (relative paths / generic `"python"`); hardened `LOCAL_PATH_TOKENS` with the JSON-escaped token so this class of leak is now caught going forward.
- **Stray cross-host duplicates:** 106 untracked `*-WORKSTATION-LG.*` files removed from the local working copy; `.gitignore` now excludes `*-WORKSTATION-LG.*`/`*-ASUS-GEI.*` and the OneDrive<->local-clone mirror descriptors `README_MIRROR.md` / `REPO.pointer.json`.

#### Added
- Evidence-mapping section ("Evidence Mapping: Result <-> Reproducer <-> Paper") in `README.md` & `README_de.md`: ties result categories to their reproducer scripts, `_results/` files, citing paper section, and Zenodo DOI.
- 2 result files explicitly cited by exact filename in Paper B ("Beneath the *abc* Landscape") but missing from the repo: `r1_faithful_al_80224_raw_field_check_2026-06-27.{json,md}` added; `MAC_COMPUTE_STATUS_2026-06-27.md` deliberately not added (internal operational status log with Tailscale IP/Mac paths — flagged for paper-text review).

## [0.1.6] - 2026-08-16

### Added
- Synchronized Shields.io badges in `README.md` & `README_de.md` (Tests: 10 Passed, Version: 0.1.6, Python >=3.10, SageMath 10.x, PARI/GP 2.15, LLM-Ready, research-line ecosystem, open-bricks umbrella).
- Added comprehensive Sibling Research & Ecosystem Matrix across `research-line` (`functional-stability-theory`, `fst-nash`, `economic-sanctions-coercive-diplomacy`, `prompt-archaeology-casestudy2`, `CultureEvolution`, `connes-cvs`, `direct-beam`) and `open-bricks` developer tools (`DevCenter`, `CodeBox`) in both English and German documentation.
- Enhanced automated metadata & manifest parity test suite in `tests/test_metadata.py` with version synchronization, sibling matrix checks, and UTF-8 document encoding verification (10/10 passed).
- Added per-file ignore rules for research script suites in `pyproject.toml` (`[tool.ruff]`), achieving 100% clean linter status.

### Changed
- Discoverability, README-Design, Badges & Metadata Parity Check (Pfad B, 2026-08-16).
- Updated `llms.txt` header `Last-checked` timestamp to `2026-08-16` and updated test interface count.
- Bumped version to `0.1.6` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and `tests/test_metadata.py`.
- Verified Python script syntax compilation and pytest test suite (100% PASS).

## [0.1.5] - 2026-08-14

### Added
- Added automated pytest test suite in `tests/` (`test_policy.py`, `test_metadata.py`, `test_scripts_compilation.py`) covering repository hygiene, privacy boundaries, metadata sync, and Python syntax compilation.
- Added `[tool.ruff]` and updated `[tool.pytest.ini_options]` configuration in `pyproject.toml`.
- Added pytest verification step to GitHub Actions CI workflow (`.github/workflows/abc-hct-hygiene.yml`).

### Changed
- Technical hygiene & maintenance check (Pfad A, 2026-08-14).
- Updated `llms.txt` header `Last-checked` date to `2026-08-14`.
- Updated `README.md` and `README_de.md` LLM-Ready status badges to `2026-08-14`.
- Verified Python script syntax compilation across all 270 research scripts under `_scripts/`.
- Verified automated pytest suite (100% PASS).

## [0.1.4] - 2026-08-05

### Added
- Created `README_de.md` for full German documentation parity with language switcher navigation.
- Added `research-line` Ecosystem and `open-bricks` Umbrella Shields.io badges to `README.md` and `README_de.md`.

### Changed
- Discoverability, SEO & README design maintenance check (Pfad B, 2026-08-05).
- Updated `llms.txt` header `Last-checked` date to `2026-08-05` and added German documentation link.
- Updated `README.md` LLM-Ready status badge timestamp to `2026-08-05`.
- Verified Python script syntax compilation (`python -m compileall _scripts`).
- Technical hygiene and documentation maintenance check (2026-08-10).
- Verified Python script syntax compilation (`python -m compileall -q _scripts _compute_queue/scripts`).

### Changed
- Technical hygiene and documentation maintenance check.
- Updated the `llms.txt` `Last-checked` header and the README LLM-Ready badge to `2026-08-01`.
- Verified syntax-only Python compilation for `_scripts/` and `_compute_queue/scripts/`.

## [0.1.2] - 2026-07-30

### Changed
- Technical hygiene & documentation maintenance check (Pfad A, 2026-07-30).
- Updated `llms.txt` header `Last-checked` date to `2026-07-30`.
- Updated `README.md` LLM-Ready status badge timestamp to `2026-07-30`.
- Verified Python script syntax compilation (`python -m compileall _scripts`, 270 scripts clean).

## [0.1.1] - 2026-07-29

### Changed
- Discoverability, SEO & README design maintenance check (Pfad B, 2026-07-29).
- Updated `llms.txt` header `Last-checked` date to `2026-07-29`.
- Updated `README.md` status badge timestamp to `2026-07-29` and added Quick Navigation table.
- Added Mermaid System Architecture & Calculation Pipeline diagram to `README.md`.
- Verified Python script syntax compilation (`python -m compileall _scripts`).

## [0.1.0] - 2026-07-27

### Changed
- Technical hygiene & documentation maintenance check (2026-07-27).
- Updated `llms.txt` header `Last-checked` date to `2026-07-27`.
- Updated `README.md` status badge timestamp to `2026-07-27`.
- Verified Python script syntax compilation (`python -m compileall _scripts`).

## [0.1.0] - 2026-07-25

## [0.1.0] - 2026-07-22

### Changed
- Initial technical hygiene & documentation maintenance check.
- Updated `llms.txt` header `Last-checked` date to `2026-07-22`.
- Verified Python script syntax compilation (`python -m compileall _scripts`).
