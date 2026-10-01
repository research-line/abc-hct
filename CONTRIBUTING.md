# Contributing to abc-hct / Mitwirken an abc-hct

[![English](https://img.shields.io/badge/Language-English-blue.svg)](#english)
[![Deutsch](https://img.shields.io/badge/Sprache-Deutsch-yellow.svg)](#deutsch)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security Policy](https://img.shields.io/badge/Security-SECURITY.md-blue.svg)](SECURITY.md)

---

<a id="english"></a>
## English

Thank you for your interest in contributing to **abc-hct** (`research-line/abc-hct`). This repository hosts curated calculation scripts, reproduction harnesses, and machine-readable result certificates for Hecke curves and Manin-Hecke quotients.

To preserve scientific rigor, deterministic reproducibility, and repository hygiene, all contributions must adhere to the standards and quality gates described below.

### 1. Architectural Principles & Invariants

All contributions must strictly conform to our ten foundational governance and research invariants:
- **`INV-DET-01` Deterministic Verification**: Zero stochastic variance; mathematical computations must produce identical algebraic output on every run.
- **`INV-ZE-02` 100% Offline & Zero-Egress**: Computations, harnesses, and test suites must operate completely offline with zero telemetry or network calls.
- **`INV-CUR-03` Curated Evidence & Non-Pollution**: Working notes (`BEWEISNOTIZ*.md`), raw logs, and intermediate state must never be committed; only finalized certificates belong under `_results/`.
- **`INV-CERT-04` Machine-Readable Certificate Ledger**: Result certificates must be formatted as deterministic JSON/Markdown.
- **`INV-ENV-05` Environment Isolation**: Clean execution queue with bounded timeouts and robust fallback handling across supported environments (Python 3.10-3.13, SageMath 10.x, PARI/GP 2.15).
- **`INV-MSTAR-06` No-Magma Modular Symbol Engine**: All modular symbol pairings over GF(3863) use open-source SageMath and Python tooling, eliminating commercial CAS reliance.
- **`INV-SEC-07` Local-First Sandboxing & RunAsInvoker**: All scripts and harnesses operate strictly within unprivileged user-mode boundaries (`RunAsInvoker`) without requiring administrative or root elevation.
- **`INV-LIC-08` Permissive Open-Science Licensing**: Codebase is licensed under the permissive MIT License to foster open science and peer verification.
- **`INV-DOC-09` Bilingual & LLM-Ready Parity**: 100% reciprocal bilingual parity between English and German documentation, and machine-readable manifests (`llms.txt`).
- **`INV-SLA-10` Security SLA**: Strict adherence to our 48-hour response SLA and 5-day triage commitment.

### 2. Zero-Copyleft Isolation Boundary

External computational engines (SageMath, PARI/GP) are licensed under GPL-2.0+. To ensure zero-copyleft contamination of the MIT-licensed research codebase, all interactions with SageMath and PARI/GP must execute exclusively through out-of-process CLI interfaces and subprocess execution boundaries.

### 3. Version Freeze Discipline (v0.1.13)

Under engineering ticket `T-20260920-167562623`, the active package version is frozen at **`0.1.13`**.
- Do **not** increment or modify the version in `pyproject.toml`, documentation badges, or release manifests.
- All new features, hygiene updates, and fixes must be recorded under the `## [Unreleased]` section of [`CHANGELOG.md`](CHANGELOG.md).

### 4. Development Workflow & Local Isolation (Plan D)

1. **Clone & Branching**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   pip install pytest ruff
   ```
3. **Execution Safety**:
   - Always run with unprivileged user permissions. Never run scripts with `sudo` or elevated administrator rights.
   - Do not hardcode local machine paths (e.g., home directory paths) in tracked files.

### 5. Pre-Commit Quality Gates

Before opening a pull request, run and pass all mandatory quality gates locally:

```bash
# 1. Automated test suite (all contract, metadata, and policy tests)
pytest

# 2. Fast code linter
ruff check .

# 3. Syntax compilation check across scripts and tests
python -m compileall _scripts tests

# 4. Git whitespace and hygiene check
git diff --check
```

### 6. Pull Request Guidelines

- Ensure your branch is rebased onto the latest `main`.
- Document your changes in `CHANGELOG.md` under `## [Unreleased]`.
- Provide atomic, descriptive commit messages following the Conventional Commits specification (e.g., `chore(hygiene): ...`, `test(contract): ...`).
- Verify that no untracked artifacts, temporary files, or local logs are staged.

### 7. Responsible Security Disclosure

Do **not** report security vulnerabilities via public GitHub issues. Please follow the instructions in [`SECURITY.md`](SECURITY.md) to report security concerns privately via GitHub Security Advisories or to the designated security team (`security@ellmos.ai` / `security@open-bricks.org`).

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse an einer Mitarbeit an **abc-hct** (`research-line/abc-hct`). Dieses Repository enthält kuratierte Berechnungsskripte, Reproduktions-Harnesses und maschinenlesbare Ergebniszertifikate für Hecke-Kurven und Manin-Hecke-Quotienten.

Zur Wahrung wissenschaftlicher Verlässlichkeit, deterministischer Reproduzierbarkeit und Code-Hygiene müssen alle Beiträge den folgenden Standards und Qualitätsprüfungen genügen.

### 1. Architekturprinzipien & Invarianten

Alle Beiträge müssen die zehn zentralen Governance- und Forschungsinvarianten strikt einhalten:
- **`INV-DET-01` Deterministische Verifikation**: Keine stochastische Varianz; mathematische Berechnungen müssen bei jedem Durchlauf identische algebraische Resultate liefern.
- **`INV-ZE-02` 100% Offline & Zero-Egress**: Berechnungen, Test-Suites und Skripte laufen vollständig offline ohne Telemetrie oder Netzwerkabrufe.
- **`INV-CUR-03` Kuratierte Evidenz & Nicht-Kontamination**: Arbeitsnotizen (`BEWEISNOTIZ*.md`), Rohlogs und Zwischenzustände verbleiben lokal; nur finalisierte Zertifikate werden unter `_results/` abgelegt.
- **`INV-CERT-04` Maschinenlesbares Zertifikatsledger**: Ergebniszertifikate liegen als deterministisches JSON/Markdown vor.
- **`INV-ENV-05` Isolierte Rechenumgebungen**: Saubere Rechenqueue mit definierten Timeouts und Fallbacks über alle unterstützten Umgebungen (Python 3.10-3.13, SageMath 10.x, PARI/GP 2.15).
- **`INV-MSTAR-06` No-Magma Modular-Symbol-Engine**: Alle modularen Symbol-Paarungen über GF(3863) nutzen Open-Source-Werkzeuge (SageMath/Python) ohne proprietäre CAS-Abhängigkeiten.
- **`INV-SEC-07` Lokales Sandboxing & RunAsInvoker**: Alle Skripte laufen streng in unprivilegierten Benutzermodi (`RunAsInvoker`) ohne Administrator- oder Root-Rechte.
- **`INV-LIC-08` Freie Open-Science-Lizenz**: Der Code steht unter der permissiven MIT-Lizenz zur Förderung offener Wissenschaft.
- **`INV-DOC-09` Bilinguale & LLM-Parität**: 100% wechselseitige Parität zwischen englischer und deutscher Dokumentation sowie maschinenlesbaren Manifesten (`llms.txt`).
- **`INV-SLA-10` Sicherheits-SLA**: Verbindliche Einhaltung der 48-Stunden-Reaktionszeit und 5-tägigen Triage-Frist.

### 2. Zero-Copyleft-Isolationsgrenze

Externe Computeralgebrasysteme (SageMath, PARI/GP) stehen unter GPL-2.0+. Um eine Copyleft-Kontamination der MIT-lizenzierten Forschungsbasis auszuschließen, dürfen Aufrufe dieser Systeme ausschließlich über Out-of-Process-CLI-Schnittstellen und Subprozess-Grenzen erfolgen.

### 3. Versions-Freeze-Disziplin (v0.1.13)

Gemäß Ticket `T-20260920-167562623` ist die Versionsnummer auf **`0.1.13`** eingefroren.
- Bitte ändern oder erhöhen Sie die Versionsnummer in `pyproject.toml`, Badges oder Release-Manifesten **nicht**.
- Alle neuen Features, Hygiene-Updates und Fixes werden im Abschnitt `## [Unreleased]` der Datei [`CHANGELOG.md`](CHANGELOG.md) dokumentiert.

### 4. Lokaler Entwicklungsworkflow (Plan D)

1. **Branch erstellen**:
   ```bash
   git checkout -b feature/mein-beitrag
   ```
2. **Virtuelle Umgebung einrichten**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate
   pip install -e .
   pip install pytest ruff
   ```
3. **Sicherheit im Entwicklungsprozess**:
   - Skripte stets mit regulären Benutzerrechten ausführen. Niemals administrative Rechte anfordern.
   - Keine lokalen Benutzerpfade (z. B. Home-Verzeichnisse) in getrackte Dateien schreiben.

### 5. Lokale Qualitätsprüfungen (Quality Gates)

Vor dem Erstellen eines Pull Requests müssen alle lokalen Prüfungen erfolgreich bestanden werden:

```bash
# 1. Test-Suite ausführen
pytest

# 2. Linter ausführen
ruff check .

# 3. Python-Syntax kompilieren
python -m compileall _scripts tests

# 4. Whitespace- und Git-Prüfung
git diff --check
```

### 6. Pull-Request-Richtlinien

- Stellen Sie sicher, dass Ihr Branch auf den aktuellen Stand von `main` rebased ist.
- Dokumentieren Sie alle Anpassungen in `CHANGELOG.md` unter `## [Unreleased]`.
- Nutzen Sie atomare Commits mit präzisen Beschreibungen gemäß Conventional Commits (`chore(hygiene): ...`, `test(contract): ...`).
- Prüfen Sie vor dem Commit, dass keine temporären Dateien oder lokalen Logs gestaged werden.

### 7. Sicherheitsmeldungen

Sicherheitsrelevante Schwachstellen bitte **nicht** über öffentliche GitHub-Issues melden. Nutzen Sie stattdessen die in [`SECURITY.md`](SECURITY.md) beschriebenen privaten GitHub Security Advisories oder wenden Sie sich direkt an `security@ellmos.ai` bzw. `security@open-bricks.org`.
