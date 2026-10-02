# Changelog - abc-hct

All notable changes to this repository will be documented in this file.

## [Unreleased]

### Research manuscript corrections
- Add the bilingual Part 6 ATS height-subchain v0.3 corrective paper package: R18 linear-class, full-place and arithmetic-domain fixes with unchanged core proofs and explicit open measure/extension gates. Package version 0.1.13 remains frozen.

### Added
- **Bilingual Contributing Guidelines (`CONTRIBUTING.md`)**: Authored comprehensive English and German contribution guidelines detailing Plan D local development workflow, strict Version Freeze discipline (`0.1.13` per `T-20260920-167562623`), mandatory pre-commit quality gates (`pytest`, `ruff check .`, `compileall`, `git diff --check`), unprivileged `RunAsInvoker` user-mode execution, zero-copyleft subprocess isolation, zero-egress offline privacy, and responsible vulnerability disclosure per `SECURITY.md`.
- **PEP 621 Contributing URL**: Registered canonical `Contributing` URL (`https://github.com/research-line/abc-hct/blob/main/CONTRIBUTING.md`) under `[project.urls]` in `pyproject.toml`.
- **Level 1 SBOM Companion Re-Audit (2026-10-01)**: Re-audited `THIRD_PARTY_LICENSES.txt` and `THIRD_PARTY_LICENSES.md` validating runtime invariant cross-reference matrix, unprivileged non-elevation boundaries, and mathematical engine licenses.
- **Contract Test Suite Expansion (58 Tests)**: Added 4 new automated contract tests in `tests/test_metadata.py` asserting `CONTRIBUTING.md` presence and bilingual invariants, PEP 621 Contributing URL registration, README Contributing/Verified badge parity, and 2026-10-01 SBOM/Marketing audit synchronization.
- **Reciprocal Dual HTML Anchors Parity**: Embedded `<a id="sec-01"></a>` through `<a id="sec-18"></a>` across all 18 sections of both `README.md` and `README_de.md`, providing bulletproof dual-anchor linking alongside semantic slug anchors (`#quick-reference`, `#sec-01`).
- **ASCII Four-View Architectural Topology Projection**: Integrated ASCII system topology in Section 6 across both documentation files (`[VIEW 1: CLI DRIVERS & COMPUTATION HARNESSES]`, `[VIEW 2: NO-MAGMA ALGEBRAIC QUOTIENT ENGINE CORE]`, `[VIEW 3: PROOF & CERTIFICATE VERIFICATION]`, `[VIEW 4: OPEN-SCIENCE LEDGER & CITATION]`).
- **PEP 621 20/20 Keyword Saturation & Plain-Text URLs**: Saturated `keywords` array to 20/20 items matching remote GitHub topics; registered canonical URLs for `"Plain-Text Licenses"` and `"Level 1 SBOM"` under `[project.urls]` in `pyproject.toml`.
- **Level 1 SBOM Re-Audit**: Re-audited `THIRD_PARTY_LICENSES.txt` and `THIRD_PARTY_LICENSES.md` (2026-09-28) validating runtime invariant matrix against Level 1 SBOM requirements and unprivileged `RunAsInvoker` mode.
- **Contract Test Expansion (54 Tests)**: Added 6 new automated contract tests in `tests/test_metadata.py` asserting reciprocal dual HTML anchors (`sec-01`..`sec-18`), ASCII topology projection, PEP 621 20 keywords saturation, Plain-Text/SBOM URLs, changelog unreleased notes, and marketing log Section 11.
- **CI Lifecycle Workflows**: Provisioned `auto-assign.yml` (least-privilege `pull-requests: write`, `issues: write`, concurrency cancel-in-progress, 5m timeout) and `label-sync.yml` with `.github/labels.yml` containing 11 canonical governance labels. Hardened `welcome.yml` and `stale.yml` concurrency groups to `${{ github.workflow }}-${{ github.ref }}`.
- **Canonical NOTICE Attribution**: Created standard Open-Source `NOTICE` file in repository root establishing clear copyright attribution (c) 2026 Lukas Geiger, HCT Research Line Team under research-line and open-bricks umbrella.
- **Level 1 SBOM Text Inventory**: Added `THIRD_PARTY_LICENSES.txt` companion file documenting direct build and offline algebra engine dependencies with unprivileged `RunAsInvoker` non-elevation, zero-copyleft guarantees, and 10 research governance invariants (`INV-DET-01` through `INV-SLA-10`).

### Changed
- **Technical Repository Hygiene (Pfad A — 2026-10-01)**: Routine Pfad A maintenance run (Version 0.1.13 frozen per T-20260920-167562623). Synchronized Shields.io badges (`Verified-2026--10--01`, `Geprüft-2026--10--01`, `Contributing-Welcome`, `Tests-58%20Passed`) across `README.md` and `README_de.md`. Updated `llms.txt` and `MARKETING-LOG.txt`.
- **Pfad B Marketing, Discoverability & Navigation Parity**: Routine Pfad B audit (2026-09-28, Version 0.1.13 frozen per T-20260920-167562623). Verified 18-point dual anchor parity, ASCII topology projection, Shields.io badges (`Verified-2026--09--28`, `Level 1 SBOM`, `54 Passed`), and updated `llms.txt`.
- **Technical Repository Hygiene**: Pfad A CI lifecycle hardening, lock defense, PEP 621 standardization, and contract test expansion (2026-09-26, Version 0.1.13 frozen per T-20260920-167562623).
- **Multi-Host Lock Defense & Sync Hygiene**: Extended `.gitignore` with multi-host cloud-sync patterns (`*-IDEAPAD*`, `*_WORKSTATION*`, `*_WORKSTATION-LG*`, `*-WORKSTATION.*`, `*-WORKSTATION-LG.*`), lock defense (`.automation-lock`), test caches (`.pytest_temp/`, `.pytest_tmp*/`), and OS/editor artifacts (`Desktop.ini`, `*.swo`).
- **PEP 621 Standardisation & Pytest Hardening**: Standardized `license-files` in `pyproject.toml` to include `NOTICE` and `THIRD_PARTY_LICENSES.txt`; added `Notice` and `Third-Party Licenses (Text)` URLs; hardened pytest options with `--basetemp=.pytest_temp` and extended `norecursedirs`.

## [0.1.13] - 2026-09-19

### Added
- Elevated repository discoverability, visual architecture, and documentation to modern 18-point bilingual Pfad B standards (2026-09-19).
- Added Section 3 (Target Personas & Discoverability) with 4 structured personas (`[PERSONA-01]` Arithmetic Geometer & Number Theorist, `[PERSONA-02]` Computational Algebraist & Open-Science Researcher, `[PERSONA-03]` Mathematical Software Engineer & Proof Engineer, `[PERSONA-04]` Research Program Evaluator & Zenodo Archival Auditor) and high-intent discovery search queries in both `README.md` and `README_de.md`.
- Added Section 4 (Comparative Matrix vs. Computational Frameworks) benchmarking `abc-hct` against 4 alternative frameworks (Proprietary Magma Scripts, Raw Ad-Hoc PARI/GP Scripts, Cloud CAS / CoCalc Notebooks, General CAS Mathematica/Maple) across all 10 invariants (`INV-DET-01` through `INV-SLA-10`).
- Upgraded System Architecture to modern `flowchart TD` 5-tier topology and preserved sequence diagram verification flow with `autonumber` and 0 semicolons.
- Added Section 11 (Modular Symbol Pairing & Basket Elimination Artifacts) detailing the GF(3863) quotient elimination across levels `60168`, `80224`, `120336`, and `240672`.
- Added Section 18 statutory liability disclaimer according to German law (§ 521 BGB Gefälligkeitsrecht) in both `README.md` and `README_de.md`.
- Added Level 1 SBOM Invariant Cross-Reference Matrix table in `THIRD_PARTY_LICENSES.md` auditing all 10 governance invariants and unprivileged `RunAsInvoker` non-elevation boundaries.
- Enriched GitHub repository topics to full 20/20 topics via GitHub CLI.
- Added 6 new automated contract tests in `tests/test_metadata.py` (verifying 18-point navigation parity, target personas, comparative matrix, statutory disclaimer § 521 BGB, Level 1 SBOM invariant table, and version 0.1.13 cross-document parity; total 42 tests).
- Added Section 9 (Pfad B Discoverability & Visual Architecture Audit) in `MARKETING-LOG.txt`.

### Changed
- Bumped version to `0.1.13` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suites.
- Synchronized Shields.io badges (`Version-0.1.13-blue.svg`, test count badge, and `LLM--Ready-2026--09--19`) across both `README.md` and `README_de.md`.
- Updated `llms.txt` header `Last-checked` timestamp to `2026-09-19` and updated interface test count to 42 automated tests.

## [0.1.12] - 2026-09-18

### Added
- Provisioned standard automated GitHub Actions workflows:
  * `.github/workflows/stale.yml`: automated issue and pull request stale lifecycle management with `actions/stale@v9`, daily schedule (`cron: '30 1 * * *'`), `timeout-minutes: 10`, concurrency group, and least-privilege permissions (`issues: write`, `pull-requests: write`).
  * `.github/workflows/welcome.yml`: automated greeting and contribution guidelines for first-time contributors with `actions/first-interaction@v3`, `timeout-minutes: 5`, concurrency group, and least-privilege permissions (`issues: write`, `pull-requests: write`).
- Declared PEP 621 `license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]` in `pyproject.toml`.
- Configured `norecursedirs` under `[tool.pytest.ini_options]` in `pyproject.toml` to guard against traversal into version control, cache directories, compute queues, and raw research state.
- Expanded multi-host sync conflict protection and canonical agent locks in `.gitignore` (`*conflicted copy*`, `* (Kopie)*`, `* (Copy)*`, `*-LAPTOP*`, `*-Mac Studio*`, `*-MacBook*`, `LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `!package-lock.json`, `.hypothesis/`, `.turbo/`, `.nyc_output/`, `*.orig`, `*.rej`).
- Added 6 new automated contract tests in `tests/test_metadata.py` verifying stale & welcome CI workflows, pyproject license files & norecursedirs, expanded gitignore patterns, and release synchronization (elevating test suite to 36 tests).
- Added Section 8 (Technical Hygiene & Maintenance Audit) to `MARKETING-LOG.txt`.

### Changed
- Technical repository hygiene, CI workflow provisioning, multi-host defense, and contract test expansion (Pfad A, 2026-09-18).
- Updated `THIRD_PARTY_LICENSES.md` with 2026-09-18 verification date, explicitly asserting unprivileged `RunAsInvoker` execution, zero-copyleft boundaries, and 10 research governance invariants.
- Updated `llms.txt` header `Last-checked` timestamp to `2026-09-18` and updated interface test count to 36 automated tests.
- Bumped version to `0.1.12` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suites.
- Synchronized Shields.io version badge to `Version-0.1.12-blue.svg`, test badge to `Tests-36%20Passed`, and LLM-Ready badge to `2026-09-18` across `README.md` and `README_de.md`.

## [0.1.11] - 2026-09-11

### Added
- Added PEP 621 canonical `"LLM Ready"` URL in `pyproject.toml` pointing to `llms.txt`.
- Added `timeout-minutes: 15` runaway guardrail to GitHub Actions CI workflow (`.github/workflows/abc-hct-hygiene.yml`).
- Added multi-host conflict patterns (`*-WORKSTATION*`, `*-ASUS-GEI*`, `* (kopie)*`, `* (copy)*`), multi-agent lockfiles (`uv.lock`, `LOCK.permissions.json`), and test caches (`.tox/`, `.mypy_cache/`, `.coverage.*`) to `.gitignore`.
- Added 6 new automated contract tests in `tests/test_metadata.py` verifying extended ruff linter rule compliance, CI timeout guardrails, PEP 621 extended URLs, multi-host git exclusions, recent changelog entries, and recent marketing log hygiene audits (bringing suite to 30 automated tests).
- Added Section 7 (Technical Hygiene & Maintenance Audit) to `MARKETING-LOG.txt`.

### Changed
- Technical repository hygiene, CI hardening, PEP 621 URLs, and contract test expansion (Pfad A, 2026-09-11).
- Expanded `[tool.ruff.lint].select` to 10 standard rule sets (`E`, `F`, `W`, `I`, `UP`, `B`, `SIM`, `C4`, `PT`, `RUF`) with clean zero-error compliance across the entire repository.
- Standardized test runner command in GitHub Actions CI workflow to `python -m pytest -ra -v`.
- Standardized import sorting across test modules with automatic isort formatting.
- Updated `llms.txt` header `Last-checked` timestamp to `2026-09-11` and synchronized test baseline to 30 automated tests.
- Bumped version to `0.1.11` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suites.
- Synchronized Shields.io version badge to `Version-0.1.11-blue.svg`, test badge to `Tests-30%20Passed`, and LLM-Ready badge to `2026-09-11` in both `README.md` and `README_de.md`.

## [0.1.10] - 2026-09-10

### Added
- Created `THIRD_PARTY_LICENSES.md` detailing open-science software licenses and copyrights for SageMath, PARI/GP, Python stdlib, pytest, and ruff.
- Created `MARKETING-LOG.txt` outlining executive value propositions, 4 research personas, high-intent discovery search queries, 10 governance invariants, and cross-organizational sibling synergies.
- Created standard MIT `LICENSE` file for the HCT Research Line Team and open-bricks umbrella.
- Added comprehensive table of 10 Governance & Research Invariants (`INV-DET-01` through `INV-SLA-10`) to both `README.md` and `README_de.md`.
- Expanded Sibling Research & Ecosystem Matrix to 16 cross-organization partner repositories.
- Added PEP 621 URLs for `Third-Party Licenses` and `Marketing Log` in `pyproject.toml`.
- Added Security SLA badge (`48h Response | 5d Triage`) to both `README.md` and `README_de.md`.
- Expanded automated contract test suite in `tests/test_metadata.py` with 5 new tests verifying `THIRD_PARTY_LICENSES.md`, `MARKETING-LOG.txt`, `LICENSE`, 14-point navigation parity, and 10 research invariants.

### Changed
- Elevated repository discoverability, bilingual architecture, and documentation to modern Pfad B standards (Pfad B, 2026-09-10).
- Standardized 14-point Quick Navigation / Schnellnavigation across `README.md` and `README_de.md` with 100% reciprocal anchor parity.
- Synchronized `llms.txt` header to `Last-checked: 2026-09-10`, added canonical links to `MARKETING-LOG.txt` and `THIRD_PARTY_LICENSES.md`, and updated interface test count.
- Synchronized version to `0.1.10` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suites.
- Synchronized Shields.io version badge to `Version-0.1.10-blue.svg` and LLM-Ready badge to `2026-09-10`.

## [0.1.9] - 2026-09-09

### Added
- Added PEP 621 `Security` URL pointing to `SECURITY.md` in `pyproject.toml`.
- Hardened bilingual `SECURITY.md` with explicit 5-business-day / 5-Werktage triage and assessment commitment complementing the 48-hour initial response SLA.
- Hardened `.gitignore` with comprehensive multi-host conflict patterns (`*-conflict-*`, `*-CONFLIT-*`, `*.sync-temp-*`), multi-agent locks (`LOCK`, `LOCK.*`, `*.lock`), packaging/coverage caches (`.coverage`, `coverage/`, `htmlcov/`, `wheelhouse/`, `.wheel-smoke/`), and temp files (`*.tmp`, `*.bak`, `*.swp`, `*~`).
- Hardened GitHub Actions CI workflow (`.github/workflows/abc-hct-hygiene.yml`) by including `tests` in compileall check and standardizing pytest execution to `pytest -v`.

### Changed
- Technical repository hygiene, PEP 621 Security URL, SLA triage hardening, `.gitignore` patterns, and contract test expansion (Pfad A, 2026-09-09).
- Standardized `pyproject.toml` pytest `addopts` to `-ra -v`.
- Updated `llms.txt` header `Last-checked` timestamp to `2026-09-09`.
- Bumped version to `0.1.9` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suite.
- Synchronized Shields.io version badge to `Version-0.1.9-blue.svg` and LLM-Ready badge to `2026-09-09` in both `README.md` and `README_de.md`.

## [0.1.8] - 2026-08-25

### Added
- Hardened GitHub Actions CI workflow (`.github/workflows/abc-hct-hygiene.yml`) with workflow concurrency grouping (`cancel-in-progress: true`) and standardized on `actions/checkout@v4` and `actions/setup-python@v5`.
- Added PEP 621 ecosystem URLs (`Parent Organization = https://github.com/research-line`, `Umbrella Ecosystem = https://github.com/open-bricks`) in `pyproject.toml`.
- Hardened bilingual `SECURITY.md` with structured Supported Versions matrix (`0.1.x`), 48-hour response SLA, and official ecosystem contacts (`security@open-bricks.org`, `lukas@open-bricks.org`).
- Hardened `.gitignore` with synchronization conflict patterns (`*.sync-conflict-*`, `*.conflict`), temporary lockfiles (`LOCK*.txt`), and test/linter caches (`.ruff_cache/`, `.pytest_cache/`).
- Added 4 new contract tests to `tests/test_metadata.py` verifying CI concurrency & action versions, PEP 621 ecosystem URLs, security policy SLA/matrix/contacts, and gitignore hygiene patterns (14 metadata contract tests, 19 total automated tests).

### Changed
- Technical repository hygiene, CI concurrency hardening, PEP 621 ecosystem URLs, and contract test expansion (Pfad A, 2026-08-25).
- Updated `llms.txt` header `Last-checked` timestamp to `2026-08-25` and updated interface test count (19 automated tests).
- Bumped version to `0.1.8` across `pyproject.toml`, `README.md`, `README_de.md`, `llms.txt`, and test suite.
- Synchronized Shields.io test badge to `Tests-19 Passed` and LLM-Ready badge to `2026-08-25` in both `README.md` and `README_de.md`.

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
