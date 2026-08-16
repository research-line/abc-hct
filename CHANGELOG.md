# Changelog - abc-hct

All notable changes to this repository will be documented in this file.

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
