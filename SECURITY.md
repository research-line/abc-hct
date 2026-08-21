# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

### Security & Privacy Commitments

`abc-hct` is an open-science computational arithmetic geometry research repository within the `research-line` ecosystem. We maintain strict security, confidentiality, and data integrity standards across all calculation pipelines, modular curve algorithms, and result certificates.

#### 1. Local-First & Zero-Egress Execution
- All calculation scripts (`_scripts/`), SageMath routines, PARI/GP procedures, and Manin-Hecke quotient certifiers execute **100% locally and offline**.
- The repository contains zero telemetry, zero background network calls, and zero external analytical tracking.

#### 2. Non-Elevation & Subprocess Isolation
- Scripts and verification harnesses run exclusively in **unprivileged user mode** without requiring administrative (`sudo` / Administrator) rights.
- Subprocess invocations (e.g., calling `gp`, `sage`, or Python workers) are strictly bounded to repository-local relative paths.

#### 3. Research Confidentiality & Boundary Protection
- Internal working drafts, active proof logs (`BEWEISNOTIZ*.md`), raw database snapshots (`_data/`), and transient compute states (`_compute_queue/logs/`) are strictly filtered and excluded via `.gitignore`.
- Only curated, finalized, and machine-verifiable calculation certificates (`_results/*.json`, `_results/*.md`) are admitted to the version control tree.
- Absolute host system paths and credential keys are systematically forbidden and guarded by automated repository policy tests.

#### 4. Deterministic Reproducibility & Certificate Verification
- Machine-readable result certificates are deterministically generated and verified through reproducible mathematical pipelines.
- Test suites enforce syntactic, semantic, and structural parity across all public releases.

### Reporting Security Concerns

If you discover any security, privacy, or leak vulnerabilities within this repository, please report them responsibly:

- **Primary Contact:** `security@ellmos.ai`
- **Secondary Contact:** `support@lukasgeiger.com`
- **GitHub Security Advisories:** [Report a Vulnerability](https://github.com/research-line/abc-hct/security/advisories/new)

Please do not open public issues for sensitive security or credential disclosures until coordinated disclosure has occurred.

---

<a name="deutsch"></a>
## Deutsch

### Sicherheits- & Datenschutz-Garantien

`abc-hct` ist ein Open-Science-Forschungsrepository für rechnergestützte arithmetische Geometrie im `research-line`-Ökosystem. Wir wahren strikte Sicherheits-, Vertraulichkeits- und Datenintegritätsstandards über alle Berechnungs-Pipelines, Modulkurven-Algorithmen und Ergebnis-Zertifikate.

#### 1. Local-First & Zero-Egress Ausführung
- Sämtliche Berechnungsskripte (`_scripts/`), SageMath-Routinen, PARI/GP-Prozeduren und Manin-Hecke-Quotienten-Zertifizierer laufen **100% lokal und offline**.
- Das Repository enthält keinerlei Telemetrie, keine Hintergrund-Netzwerkaufrufe und kein externes Tracking.

#### 2. Non-Elevation & Subprozess-Sicherheit
- Skripte und Verifikations-Harnesses arbeiten ausschließlich im **nicht-privilegierten Benutzermodus** ohne administrative Rechte (`sudo` / Administrator).
- Subprozess-Aufrufe (`gp`, `sage`, Python) sind strikt auf relative Repository-Pfade begrenzt.

#### 3. Forschungsintegrität & Vertraulichkeitsgrenzen
- Interne Arbeitsentwürfe, aktive Beweisnotizen (`BEWEISNOTIZ*.md`), rohe Datenbank-Snapshots (`_data/`) und transiente Berechnungszustände (`_compute_queue/logs/`) werden durch `.gitignore` strikt isoliert.
- Nur kuratierte, finalisierte und maschinenlesbare Ergebnis-Zertifikate (`_results/*.json`, `_results/*.md`) werden in die Versionskontrolle übernommen.
- Absolute Systempfade des Hosts und Zugangsdaten sind verboten und werden durch automatisierte Richtlinien-Tests abgesichert.

#### 4. Deterministische Reproduzierbarkeit & Zertifikatsprüfung
- Maschinenlesbare Resultatszertifikate werden deterministisch generiert und über reproduzierbare mathematische Pipelines verifiziert.
- Testsuiten stellen syntaktische und strukturelle Parität über alle Releases sicher.

### Sicherheitsmeldungen

Sollten Sie Sicherheits-, Datenschutz- oder Informationsleck-Schwachstellen entdecken, bitten wir um verantwortungsvolle Meldung:

- **Primäre Kontaktadresse:** `security@ellmos.ai`
- **Sekundäre Kontaktadresse:** `support@lukasgeiger.com`
- **GitHub Security Advisories:** [Schwachstelle melden](https://github.com/research-line/abc-hct/security/advisories/new)

Bitte eröffnen Sie keine öffentlichen Issues für vertrauliche Sicherheits- oder Leak-Meldungen vor Abschluss der koordinierten Behebung.
