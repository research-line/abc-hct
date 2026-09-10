# Third-Party Licenses & Dependency Inventory

This document provides a comprehensive inventory of all third-party software libraries, mathematical engines, toolchains, and runtime environments utilized or referenced by **abc-hct** (`research-line/abc-hct`), including their respective licenses, copyright holders, and usage scopes.

Last updated: **2026-09-10**

---

## 1. Computational Algebra & Number Theory Engines

### Python Standard Library
- **Project:** Python Software Foundation
- **Scope:** Runtime execution, test automation, modular script execution, JSON certificate serialization, and path canonicalization
- **License:** Python Software Foundation License Version 2 (PSFL-2.0)
- **Copyright:** (c) 2001-2026 Python Software Foundation; All Rights Reserved.
- **Notice:**
  > Permission is hereby granted to copy, modify, and distribute this software and its documentation for any purpose and without fee, provided that the above copyright notice appear in all copies and that both that copyright notice and this permission notice appear in supporting documentation...

### SageMath
- **Project:** [SageMath Open-Source Mathematics Software System](https://www.sagemath.org/)
- **Scope:** Modular symbol pairing engines, Hecke algebra operators ($T_5, T_7$), quotient dimension verification, and arithmetic geometry routines
- **License:** GNU General Public License Version 2 or later (GPL-2.0+)
- **Copyright:** (c) 2005-2026 The Sage Developers
- **Usage Scope:** Invoked as an external offline command-line and library execution environment (`sage _scripts/...`). All custom research algorithms, certifier scripts, and reproducibility harnesses in this repository remain independent original works distributed under the MIT License.

### PARI/GP
- **Project:** [PARI/GP Mathematics System](https://pari.math.u-bordeaux.fr/)
- **Scope:** High-precision polynomial arithmetic, Frey-Watkins saturation verification, and elliptic curve conductor calculations (`_scripts/frey_watkins_phase2.gp`)
- **License:** GNU General Public License Version 2 or later (GPL-2.0+)
- **Copyright:** (c) 1989-2026 The PARI Group, Bordeaux
- **Usage Scope:** Standalone script execution via `gp` CLI. Standalone scripts emit machine-readable results without linking proprietary or closed-source extensions.

---

## 2. Quality Assurance, Linting & Contract Tooling

### pytest
- **Project:** [pytest-dev/pytest](https://github.com/pytest-dev/pytest)
- **Scope:** Automated repository metadata, policy hygiene, security parity, and Python syntax compilation contract testing
- **License:** MIT License
- **Copyright:** (c) 2004-2026 Holger Krekel and pytest-dev contributors
- **Notice:**
  > Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction...

### Ruff
- **Project:** [astral-sh/ruff](https://github.com/astral-sh/ruff)
- **Scope:** Fast Python linter and code hygiene gatekeeper in local development and CI workflows
- **License:** MIT License / Apache License 2.0
- **Copyright:** (c) 2023-2026 Astral Software Inc.

---

## 3. Compliance & Governance Assurance

1. **Permissive Repository Licensing**: All original research code, scripts, verification harnesses, and documentation in this repository are licensed under the permissive **MIT License**, facilitating open science and unrestricted scholarly reproducibility.
2. **Offline Local-First Execution**: All mathematical calculations, Sage/GP script invocations, and test suites execute strictly locally with zero outbound network egress.
3. **Zero-Egress & Privacy**: No calculation telemetry, analytics, tracking tokens, or private proof logs are transmitted outside the local machine.
4. **Staged Disclosure & Boundary Discipline**: Internal working notes (`BEWEISNOTIZ*.md`) and raw data snapshots remain isolated by strict `.gitignore` rules, ensuring version control contains only vetted, reproducible certificates.
