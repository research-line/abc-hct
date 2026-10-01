"""Metadata, security, documentation, and Pfad B contract parity tests for abc-hct."""

import re
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_toml_structure():
    """Verify that pyproject.toml exists and contains valid metadata and PEP 621 classifiers."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert "project" in data
    project = data["project"]
    assert project.get("name") == "abc-hct"
    assert project.get("version") == "0.1.13"
    assert "description" in project
    assert project.get("requires-python") == ">=3.10"
    assert "license" in project

    classifiers = project.get("classifiers", [])
    assert "Programming Language :: Python :: 3.13" in classifiers
    assert "Operating System :: OS Independent" in classifiers
    assert "Topic :: Scientific/Engineering :: Mathematics" in classifiers

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Documentation" in urls
    assert "Bug Tracker" in urls
    assert "Changelog" in urls
    assert "Security" in urls
    assert "Parent Organization" in urls
    assert "Umbrella Ecosystem" in urls
    assert "Third-Party Licenses" in urls
    assert "Marketing Log" in urls
    assert "LLM Ready" in urls


def test_pep621_ecosystem_urls():
    """Verify that PEP 621 project URLs link to the research-line org, security policy, and open-bricks umbrella."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})

    assert urls.get("Parent Organization") == "https://github.com/research-line"
    assert urls.get("Umbrella Ecosystem") == "https://github.com/open-bricks"
    assert urls.get("Security") == "https://github.com/research-line/abc-hct/blob/main/SECURITY.md"
    assert urls.get("Third-Party Licenses") == "https://github.com/research-line/abc-hct/blob/main/THIRD_PARTY_LICENSES.md"
    assert urls.get("Marketing Log") == "https://github.com/research-line/abc-hct/blob/main/MARKETING-LOG.txt"
    assert urls.get("LLM Ready") == "https://github.com/research-line/abc-hct/blob/main/llms.txt"


def test_llms_txt_structure_and_timestamp():
    """Verify that llms.txt contains required sections, canonical links, and current check timestamp."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.exists(), "llms.txt must exist in repo root"
    content = llms_path.read_text(encoding="utf-8")

    assert "# abc-hct" in content
    assert "## Last-checked: 2026-09-19" in content
    assert "## Canonical Links" in content
    assert "SECURITY.md" in content
    assert "THIRD_PARTY_LICENSES.md" in content
    assert "MARKETING-LOG.txt" in content
    assert "## Summary" in content
    assert "## Interfaces" in content
    assert "## Safety & Governance Invariants" in content
    assert "## Safety Boundaries" in content
    assert "## Search Phrases" in content


def test_readme_and_readme_de_parity():
    """Verify that README.md and README_de.md are present with synchronized badges and cross-links."""
    readme_en = REPO_ROOT / "README.md"
    readme_de = REPO_ROOT / "README_de.md"

    assert readme_en.exists(), "README.md must exist"
    assert readme_de.exists(), "README_de.md must exist"

    en_content = readme_en.read_text(encoding="utf-8")
    de_content = readme_de.read_text(encoding="utf-8")

    # Both must reference each other
    assert "README_de.md" in en_content
    assert "README.md" in de_content

    # Both must link to llms.txt, SECURITY.md, CHANGELOG.md, THIRD_PARTY_LICENSES.md, and MARKETING-LOG.txt
    for doc in ["llms.txt", "SECURITY.md", "CHANGELOG.md", "THIRD_PARTY_LICENSES.md", "MARKETING-LOG.txt", "LICENSE"]:
        assert doc in en_content, f"Missing {doc} in README.md"
        assert doc in de_content, f"Missing {doc} in README_de.md"

    # Check status badges
    assert "Version-0.1.13-blue.svg" in en_content
    assert "Version-0.1.13-blue.svg" in de_content
    assert ("Tests-58%20Passed" in en_content or "Tests-54%20Passed" in en_content or "Tests-42%20Passed" in en_content)
    assert ("Tests-58%20Passed" in de_content or "Tests-54%20Passed" in de_content or "Tests-42%20Passed" in de_content)
    assert "LLM--Ready-2026--09--19" in en_content
    assert "LLM--Ready-2026--09--19" in de_content
    assert "Ecosystem-research--line-blue.svg" in en_content
    assert "Ecosystem-research--line-blue.svg" in de_content
    assert "Umbrella-open--bricks-purple.svg" in en_content
    assert "Umbrella-open--bricks-purple.svg" in de_content
    assert "Zero--Egress" in en_content
    assert "Zero--Egress" in de_content
    assert "Security%20SLA-48h%20Response%20%7C%205d%20Triage" in en_content
    assert "Security%20SLA-48h%20Response%20%7C%205d%20Triage" in de_content


def test_readme_navigation_and_mermaid_parity():
    """Verify that both READMEs contain quick navigation and both Mermaid architecture diagrams."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "Quick Navigation" in en_content
    assert "Schnellnavigation" in de_content

    # Pipeline diagram
    assert "flowchart TD" in en_content
    assert "flowchart TD" in de_content

    # Verification lifecycle diagram
    assert "sequenceDiagram" in en_content
    assert "sequenceDiagram" in de_content



def test_18_point_navigation_parity():
    """Verify that both READMEs contain all 18 quick navigation points with identical anchors."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_anchors = [
        "quick-reference",
        "key-scientific-findings",
        "target-personas--discoverability",
        "comparative-matrix-vs-alternatives",
        "dual-mermaid-diagrams",
        "system-architecture--pipeline",
        "curated-verification-lifecycle",
        "core-capabilities--research-invariants",
        "evidence-mapping--paper-references",
        "computational-milestones--batches",
        "basket-kill--modular-symbol-artifacts",
        "repository-policy--staged-disclosure",
        "sibling-research--ecosystem-matrix",
        "discovery--llm-context",
        "project-structure",
        "testing--verification",
        "third-party-licenses",
        "security--license",
    ]

    for anchor in expected_anchors:
        assert f"#{anchor}" in en_content, f"Missing anchor #{anchor} in README.md navigation"
        assert f'id="{anchor}"' in en_content, f"Missing anchor id='{anchor}' in README.md body"
        assert f'id="{anchor}"' in de_content, f"Missing anchor id='{anchor}' in README_de.md body"


def test_security_policy_structure():
    """Verify that SECURITY.md exists, contains English and German sections, and valid contacts."""
    sec_path = REPO_ROOT / "SECURITY.md"
    assert sec_path.exists(), "SECURITY.md must exist in repo root"
    content = sec_path.read_text(encoding="utf-8")

    assert "# Security Policy / Sicherheitsrichtlinie" in content
    assert "## English" in content
    assert "## Deutsch" in content
    assert "Zero-Egress" in content
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "https://github.com/research-line/abc-hct/security/advisories/new" in content


def test_security_policy_supported_versions_sla_and_contacts():
    """Verify that SECURITY.md defines supported versions matrix, 48h response SLA, and ecosystem contacts."""
    sec_path = REPO_ROOT / "SECURITY.md"
    content = sec_path.read_text(encoding="utf-8")

    assert "Supported Versions" in content
    assert "0.1.x" in content
    assert "48 hours" in content
    assert "48 Stunden" in content
    assert "5 business days" in content
    assert "5 Werktagen" in content
    assert "security@open-bricks.org" in content
    assert "lukas@open-bricks.org" in content


def test_sibling_research_matrix_parity():
    """Verify that all 16 sibling repositories are correctly linked in both README files."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_slugs = [
        "functional-stability-theory",
        "fst-nash",
        "economic-sanctions-coercive-diplomacy",
        "prompt-archaeology-casestudy2",
        "connes-cvs",
        "direct-beam",
        "rh-even-dominance",
        "CultureEvolution",
        "DevCenter",
        "CodeBox",
        "automation-master",
        "cleaner-tree",
        "SoftwareCenter",
        "USR_pic2pic",
        "ellmos-installer",
        "open-bricks",
    ]
    for slug in expected_slugs:
        assert slug in en_content, f"Missing sibling link {slug} in README.md"
        assert slug in de_content, f"Missing sibling link {slug} in README_de.md"


def test_invariants_table_parity():
    """Verify that all 10 invariants (INV-DET-01 to INV-SLA-10) are defined across READMEs and MARKETING-LOG.txt."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    mkt_content = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    for i in range(1, 11):
        inv_pattern = rf"INV-[A-Z0-9]+-{i:02d}"
        assert re.search(inv_pattern, en_content), f"Invariant index {i:02d} missing in README.md"
        assert re.search(inv_pattern, de_content), f"Invariant index {i:02d} missing in README_de.md"
        assert re.search(inv_pattern, mkt_content), f"Invariant index {i:02d} missing in MARKETING-LOG.txt"


def test_license_file_mit():
    """Verify that LICENSE exists and contains standard MIT terms."""
    lic_path = REPO_ROOT / "LICENSE"
    assert lic_path.exists(), "LICENSE must exist in repo root"
    content = lic_path.read_text(encoding="utf-8")
    assert "MIT License" in content
    assert "Copyright (c) 2026 HCT Research Line Team / research-line / open-bricks" in content


def test_third_party_licenses_inventory():
    """Verify that THIRD_PARTY_LICENSES.md exists and inventories all computational and QA dependencies."""
    tpl_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl_path.exists(), "THIRD_PARTY_LICENSES.md must exist in repo root"
    content = tpl_path.read_text(encoding="utf-8")

    assert "Python Standard Library" in content
    assert "SageMath" in content
    assert "PARI/GP" in content
    assert "pytest" in content
    assert "Ruff" in content
    assert "Zero-Egress" in content


def test_marketing_log_audit():
    """Verify that MARKETING-LOG.txt exists and contains required marketing sections and personas."""
    mkt_path = REPO_ROOT / "MARKETING-LOG.txt"
    assert mkt_path.exists(), "MARKETING-LOG.txt must exist in repo root"
    content = mkt_path.read_text(encoding="utf-8")

    assert "1. EXECUTIVE SUMMARY & VALUE PROPOSITION" in content
    assert "2. TARGET AUDIENCES & PERSONAS" in content
    assert "3. SEARCH PHRASES & DISCOVERABILITY KEYWORDS" in content
    assert "4. GOVERNANCE & RUNTIME INVARIANTS (10 GUARANTEES)" in content
    assert "5. ECOSYSTEM SIBLINGS & CROSS-ORGANIZATION MATRIX" in content
    assert "6. STRATEGIC ROADMAP & FUTURE DISCOVERABILITY" in content


def test_changelog_structure():
    """Verify that CHANGELOG.md contains the latest release entry."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md must exist"
    content = changelog_path.read_text(encoding="utf-8")

    assert "## [0.1.10] - 2026-09-10" in content


def test_ci_workflow_integrity():
    """Verify that GitHub Actions workflow file exists and defines required test and linting steps."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "abc-hct-hygiene.yml"
    assert workflow_path.exists(), "Hygiene workflow file must exist"
    content = workflow_path.read_text(encoding="utf-8")

    assert "pytest" in content
    assert "ruff check ." in content
    assert "python -m compileall" in content


def test_ci_concurrency_and_action_versions():
    """Verify that GitHub Actions workflow defines concurrency group, cancel-in-progress, and standard actions."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "abc-hct-hygiene.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content
    assert "actions/checkout@v4" in content
    assert "actions/setup-python@v5" in content


def test_gitignore_hygiene_patterns():
    """Verify that .gitignore excludes sync conflicts, lockfiles, and test/linter caches."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore must exist"
    content = gitignore_path.read_text(encoding="utf-8")

    assert "*-conflict-*" in content
    assert "*.sync-conflict-*" in content
    assert "*.conflict" in content
    assert "*-CONFLIT-*" in content
    assert "*.sync-temp-*" in content
    assert "LOCK" in content
    assert "LOCK.*" in content
    assert "*.lock" in content
    assert "LOCK*.txt" in content
    assert ".ruff_cache/" in content
    assert ".pytest_cache/" in content
    assert ".coverage" in content
    assert "coverage/" in content
    assert "htmlcov/" in content
    assert "wheelhouse/" in content
    assert ".wheel-smoke/" in content


def test_utf8_encoding_all_docs():
    """Verify that all documentation and text files decode strictly as UTF-8."""
    doc_files = [
        "README.md",
        "README_de.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "llms.txt",
        "CHANGELOG.md",
        "pyproject.toml",
        "LICENSE",
        "THIRD_PARTY_LICENSES.md",
        "MARKETING-LOG.txt",
        "REPRODUCIBILITY_H3A_2026-05-17.md",
    ]
    for rel_path in doc_files:
        doc_file = REPO_ROOT / rel_path
        if doc_file.exists():
            doc_file.read_text(encoding="utf-8")


def test_version_parity_across_all_manifests():
    """Verify that version 0.1.13 is synchronized across pyproject.toml, READMEs, and CHANGELOG."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    version = data["project"]["version"]

    assert version == "0.1.13"
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert f"## [{version}] - 2026-09-19" in (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


def test_extended_ruff_linter_compliance():
    """Verify that ruff linter select configuration covers all standard rule sets."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    select_rules = set(data.get("tool", {}).get("ruff", {}).get("lint", {}).get("select", []))
    expected_rule_sets = {"E", "F", "W", "I", "UP", "B", "SIM", "C4", "PT", "RUF"}
    assert expected_rule_sets.issubset(select_rules), f"Missing ruff rule sets: {expected_rule_sets - select_rules}"


def test_ci_timeout_minutes_guardrail():
    """Verify that CI hygiene workflow defines runaway timeout-minutes guardrail."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "abc-hct-hygiene.yml"
    content = workflow_path.read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in content
    assert "python -m pytest -ra -v" in content


def test_pep621_extended_urls():
    """Verify that PEP 621 URLs in pyproject.toml define LLM Ready canonical manifest link."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})
    assert "LLM Ready" in urls
    assert urls["LLM Ready"] == "https://github.com/research-line/abc-hct/blob/main/llms.txt"


def test_multi_host_git_exclusions():
    """Verify that .gitignore excludes multi-host sync conflicts, agent locks, and tox/mypy caches."""
    gitignore_path = REPO_ROOT / ".gitignore"
    content = gitignore_path.read_text(encoding="utf-8")
    for pattern in [
        "*-WORKSTATION*",
        "*-ASUS-GEI*",
        "* (kopie)*",
        "* (copy)*",
        "uv.lock",
        "LOCK.permissions.json",
        ".tox/",
        ".mypy_cache/",
        ".coverage.*",
    ]:
        assert pattern in content, f"Missing gitignore exclusion pattern: {pattern}"


def test_marketing_log_recent_hygiene_entry():
    """Verify that MARKETING-LOG.txt documents the latest technical hygiene audit for 2026-09-18."""
    mkt_path = REPO_ROOT / "MARKETING-LOG.txt"
    content = mkt_path.read_text(encoding="utf-8")
    assert "2026-09-18" in content
    assert "8. TECHNICAL HYGIENE & MAINTENANCE AUDIT" in content


def test_changelog_recent_pfad_a_entry():
    """Verify that CHANGELOG.md documents the 0.1.12 release and Pfad A hygiene improvements."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    content = changelog_path.read_text(encoding="utf-8")
    assert "## [0.1.12] - 2026-09-18" in content
    assert "Pfad A" in content


def test_ci_stale_workflow_present_and_hardened():
    """Verify that GitHub Actions stale workflow exists and defines schedule, timeouts, and permissions."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert workflow_path.exists(), "stale.yml workflow must exist"
    content = workflow_path.read_text(encoding="utf-8")

    assert "actions/stale@v9" in content
    assert "cron: '30 1 * * *'" in content
    assert "timeout-minutes: 10" in content
    assert "cancel-in-progress: true" in content
    assert "issues: write" in content
    assert "pull-requests: write" in content


def test_ci_welcome_workflow_present_and_hardened():
    """Verify that GitHub Actions welcome workflow exists and defines timeout and first-interaction action."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "welcome.yml"
    assert workflow_path.exists(), "welcome.yml workflow must exist"
    content = workflow_path.read_text(encoding="utf-8")

    assert "actions/first-interaction@v3" in content
    assert "timeout-minutes: 5" in content
    assert "cancel-in-progress: true" in content
    assert "issues: write" in content
    assert "pull-requests: write" in content


def test_pyproject_license_files_and_norecursedirs():
    """Verify that pyproject.toml defines license-files and norecursedirs configuration."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    license_files = data.get("project", {}).get("license-files", [])
    assert "LICENSE" in license_files
    assert "THIRD_PARTY_LICENSES.md" in license_files

    norecursedirs = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("norecursedirs", [])
    assert ".git" in norecursedirs
    assert ".pytest_cache" in norecursedirs
    assert "_compute_queue" in norecursedirs


def test_gitignore_expanded_multihost_and_lock_rules():
    """Verify that .gitignore defines expanded multi-host sync patterns and canonical lock rules."""
    gitignore_path = REPO_ROOT / ".gitignore"
    content = gitignore_path.read_text(encoding="utf-8")

    for pattern in [
        "*conflicted copy*",
        "* (Kopie)*",
        "* (Copy)*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        "*-MacBook*",
        "LOCK.user.*",
        "LOCK.until.*",
        "LOCK.condition.*",
        "uv.lock",
        "!package-lock.json",
        ".hypothesis/",
        ".turbo/",
        ".nyc_output/",
        "*.orig",
        "*.rej",
    ]:
        assert pattern in content, f"Missing expanded gitignore pattern: {pattern}"


def test_third_party_licenses_governance_invariants():
    """Verify that THIRD_PARTY_LICENSES.md asserts RunAsInvoker, Zero-Copyleft, and INV-DET-01..INV-SLA-10."""
    tpl_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    content = tpl_path.read_text(encoding="utf-8")

    assert "2026-09-19" in content
    assert "RunAsInvoker" in content
    assert "Zero-Copyleft" in content
    assert "INV-DET-01" in content
    assert "INV-SLA-10" in content


def test_release_manifest_cross_document_parity():
    """Verify that version 0.1.13 and date 2026-09-19 maintain cross-document parity across all documentation."""
    pyproject_data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject_data["project"]["version"]
    assert version == "0.1.13"

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    llms = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")

    assert f"Version-{version}-blue.svg" in readme_en
    assert f"Version-{version}-blue.svg" in readme_de
    assert f"## [{version}] - 2026-09-19" in changelog
    assert f"Active Version: {version}" in marketing
    assert "Last-checked: 2026-09-19" in llms


def test_target_personas_and_seo_parity():
    """Verify that both READMEs contain the 4 research personas and discovery phrases."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for persona_id in ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]:
        assert persona_id in readme_en, f"Missing {persona_id} in README.md"
        assert persona_id in readme_de, f"Missing {persona_id} in README_de.md"

    assert "abc conjecture computational verification python sagemath" in readme_en
    assert "reproduzierbare arithmetische geometrie open science zenodo" in readme_de


def test_comparative_matrix_vs_alternatives_parity():
    """Verify that both READMEs contain the 10-dimension comparative matrix benchmarking against alternatives."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for doc in [readme_en, readme_de]:
        assert "Proprietary Magma Scripts" in doc or "Proprietäre Magma-Skripte" in doc
        assert "INV-DET-01" in doc
        assert "INV-ZE-02" in doc
        assert "INV-MSTAR-06" in doc
        assert "INV-SLA-10" in doc


def test_statutory_disclaimer_bgb521_parity():
    """Verify that both READMEs contain the statutory liability notice (§ 521 BGB Gefälligkeitsrecht)."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "§ 521 BGB" in readme_en
    assert "Section 521 of the German Civil Code" in readme_en
    assert "§ 521 BGB" in readme_de
    assert "Haftung des Schenkers" in readme_de


def test_dual_mermaid_diagrams_parity():
    """Verify that both READMEs feature 5-tier flowchart TD and sequenceDiagram with autonumber."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for doc in [readme_en, readme_de]:
        assert "flowchart TD" in doc
        assert "subgraph T1" in doc
        assert "subgraph T5" in doc
        assert "sequenceDiagram" in doc
        assert "autonumber" in doc


def test_third_party_licenses_sbom_matrix_parity():
    """Verify that THIRD_PARTY_LICENSES.md includes the Level 1 SBOM Invariant Cross-Reference Matrix."""
    content = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "Level 1 SBOM Invariant Cross-Reference Matrix" in content
    for inv in [
        "INV-DET-01",
        "INV-ZE-02",
        "INV-CUR-03",
        "INV-CERT-04",
        "INV-ENV-05",
        "INV-MSTAR-06",
        "INV-SEC-07",
        "INV-LIC-08",
        "INV-DOC-09",
        "INV-SLA-10",
    ]:
        assert inv in content, f"Missing {inv} in Level 1 SBOM Matrix"


def test_changelog_and_marketing_pfad_b_parity():
    """Verify that CHANGELOG.md and MARKETING-LOG.txt document the Pfad B 2026-09-19 release."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    assert "## [0.1.13] - 2026-09-19" in changelog
    assert "18-point bilingual Pfad B standards" in changelog
    assert "9. TECHNICAL HYGIENE & MARKETING-DESIGN PARITY AUDIT (PFAD B — 2026-09-19)" in marketing


def test_ci_auto_assign_workflow_present_and_hardened():
    """Verify that auto-assign workflow exists and defines least-privilege permissions and timeout."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "auto-assign.yml"
    assert workflow_path.exists(), "auto-assign.yml workflow must exist"
    content = workflow_path.read_text(encoding="utf-8")

    assert "actions/github-script@v7" in content
    assert "timeout-minutes: 5" in content
    assert "cancel-in-progress: true" in content
    assert "issues: write" in content
    assert "pull-requests: write" in content


def test_ci_label_sync_workflow_and_labels_config():
    """Verify that label-sync workflow and labels.yml exist with 11 standard governance labels."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "label-sync.yml"
    assert workflow_path.exists(), "label-sync.yml workflow must exist"
    wf_content = workflow_path.read_text(encoding="utf-8")

    assert "EndBug/label-sync@v2" in wf_content
    assert "timeout-minutes: 5" in wf_content
    assert "cancel-in-progress: true" in wf_content
    assert "issues: write" in wf_content

    labels_path = REPO_ROOT / ".github" / "labels.yml"
    assert labels_path.exists(), "labels.yml must exist"
    labels_content = labels_path.read_text(encoding="utf-8")

    for label in [
        "bug",
        "enhancement",
        "good first issue",
        "help wanted",
        "documentation",
        "duplicate",
        "wontfix",
        "priority: high",
        "priority: low",
        "needs-triage",
        "stale",
    ]:
        assert f"name: {label}" in labels_content or f"name: '{label}'" in labels_content, f"Missing label: {label}"


def test_notice_attribution_file():
    """Verify that canonical NOTICE attribution file exists in repository root."""
    notice_path = REPO_ROOT / "NOTICE"
    assert notice_path.exists(), "NOTICE file must exist in repo root"
    content = notice_path.read_text(encoding="utf-8")

    assert "abc-hct" in content
    assert "Copyright (c) 2026 Lukas Geiger" in content
    assert "research-line" in content
    assert "open-bricks" in content
    assert "MIT License" in content


def test_level1_sbom_text_inventory():
    """Verify that THIRD_PARTY_LICENSES.txt Level 1 SBOM companion file exists and documents invariants."""
    sbom_path = REPO_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert sbom_path.exists(), "THIRD_PARTY_LICENSES.txt must exist in repo root"
    content = sbom_path.read_text(encoding="utf-8")

    assert "Audited: 2026-09-26" in content
    assert "RunAsInvoker" in content
    assert "Zero-Copyleft Isolation" in content
    assert "Python Standard Library" in content
    assert "SageMath" in content
    assert "PARI/GP" in content
    assert "INV-DET-01" in content
    assert "INV-SLA-10" in content


def test_gitignore_lock_defense_and_temp_caches():
    """Verify that .gitignore defines multi-host patterns, lock defense, and temporary test caches."""
    gitignore_path = REPO_ROOT / ".gitignore"
    content = gitignore_path.read_text(encoding="utf-8")

    for pattern in [
        "*-IDEAPAD*",
        "*_WORKSTATION*",
        "*_WORKSTATION-LG*",
        "*-WORKSTATION.*",
        "*-WORKSTATION-LG.*",
        ".automation-lock",
        ".pytest_temp/",
        ".pytest_tmp*/",
        "Desktop.ini",
        "*.swo",
    ]:
        assert pattern in content, f"Missing pattern in .gitignore: {pattern}"


def test_pyproject_extended_license_files_and_notice_url():
    """Verify that pyproject.toml defines NOTICE and THIRD_PARTY_LICENSES.txt in license-files and URLs."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    license_files = data.get("project", {}).get("license-files", [])
    assert "NOTICE" in license_files
    assert "THIRD_PARTY_LICENSES.txt" in license_files

    urls = data.get("project", {}).get("urls", {})
    assert "Notice" in urls
    assert "Third-Party Licenses (Text)" in urls

    ini_options = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "--basetemp=.pytest_temp" in ini_options.get("addopts", "")
    assert ".pytest_temp" in ini_options.get("norecursedirs", [])


def test_sec_dual_html_anchors_parity():
    """Verify that both README.md and README_de.md contain sec-01 through sec-18 dual reciprocal HTML anchors."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        anchor_tag = f'<a id="sec-{i:02d}"></a>'
        nav_ref = f"#sec-{i:02d}"
        assert anchor_tag in readme_en, f"Missing {anchor_tag} in README.md"
        assert anchor_tag in readme_de, f"Missing {anchor_tag} in README_de.md"
        assert nav_ref in readme_en, f"Missing navigation reference {nav_ref} in README.md"
        assert nav_ref in readme_de, f"Missing navigation reference {nav_ref} in README_de.md"


def test_ascii_architectural_topology_projection():
    """Verify that both READMEs contain the ASCII 4-view architectural topology projection."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### ASCII Architectural Topology Projection" in readme_en
    assert "[VIEW 1: CLI DRIVERS & COMPUTATION HARNESSES]" in readme_en
    assert "[VIEW 2: NO-MAGMA ALGEBRAIC QUOTIENT ENGINE CORE]" in readme_en
    assert "[VIEW 3: PROOF & CERTIFICATE VERIFICATION]" in readme_en
    assert "[VIEW 4: OPEN-SCIENCE LEDGER & CITATION]" in readme_en

    assert "### ASCII-Projektion der System- und Verifikationstopologie" in readme_de
    assert "[SICHT 1: CLI-TREIBER & RECHEN-HARNESSES]" in readme_de
    assert "[SICHT 2: NO-MAGMA ALGEBRAISCHER QUOTIENTENKERN]" in readme_de
    assert "[SICHT 3: BEWEIS- & ZERTIFIKATSVERIFIKATION]" in readme_de
    assert "[SICHT 4: OPEN-SCIENCE-LEDGER & ZITATE]" in readme_de


def test_pep621_20_keywords_saturation():
    """Verify that pyproject.toml has 20/20 keyword saturation matching GitHub topics."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    keywords = data.get("project", {}).get("keywords", [])

    assert len(keywords) == 20, f"Expected 20 keywords, found {len(keywords)}: {keywords}"
    expected_sample = [
        "abc-conjecture",
        "modular-forms",
        "modular-curves",
        "sagemath",
        "pari-gp",
        "manin-symbols",
        "hecke-algebra",
        "zenodo",
        "no-magma",
        "frey-curves",
    ]
    for kw in expected_sample:
        assert kw in keywords, f"Missing keyword '{kw}' in pyproject.toml"


def test_plain_text_licenses_urls_in_pyproject():
    """Verify that pyproject.toml registers Plain-Text Licenses and Level 1 SBOM under project.urls."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})

    assert "Plain-Text Licenses" in urls
    assert "Level 1 SBOM" in urls
    assert "THIRD_PARTY_LICENSES.txt" in urls["Plain-Text Licenses"]
    assert "THIRD_PARTY_LICENSES.md" in urls["Level 1 SBOM"]


def test_changelog_recent_pfad_b_unreleased_entry():
    """Verify that CHANGELOG.md documents the Pfad B discoverability & navigation additions under [Unreleased]."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "Reciprocal Dual HTML Anchors Parity" in changelog
    assert "ASCII Four-View Architectural Topology Projection" in changelog
    assert "Pfad B Marketing, Discoverability & Navigation Parity" in changelog


def test_marketing_log_pfad_b_entry_20260928():
    """Verify that MARKETING-LOG.txt contains Section 11 documenting the 2026-09-28 Pfad B audit."""
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "11. PATH B DISCOVERABILITY, 18-POINT NAVIGATION PARITY" in marketing
    assert "2026-09-28" in marketing
    assert "ASCII Four-View Architectural Topology Projection" in marketing
    assert "PEP 621 20/20 Keyword Saturation" in marketing


def test_contributing_file_exists_and_bilingual_structure():
    """Verify that CONTRIBUTING.md exists in repo root with bilingual structure and quality gates."""
    contrib_path = REPO_ROOT / "CONTRIBUTING.md"
    assert contrib_path.exists(), "CONTRIBUTING.md must exist in repo root"
    content = contrib_path.read_text(encoding="utf-8")

    assert "# Contributing to abc-hct / Mitwirken an abc-hct" in content
    assert "## English" in content
    assert "## Deutsch" in content

    # Check invariant references
    assert "INV-DET-01" in content
    assert "INV-ZE-02" in content
    assert "INV-SEC-07" in content
    assert "INV-SLA-10" in content
    assert "RunAsInvoker" in content

    # Check version freeze and ticket reference
    assert "0.1.13" in content
    assert "T-20260920-167562623" in content

    # Check pre-commit quality gates
    assert "pytest" in content
    assert "ruff check ." in content
    assert "compileall" in content
    assert "git diff --check" in content

    # Check zero-copyleft and offline guarantees
    assert "Zero-Copyleft" in content
    assert "SECURITY.md" in content


def test_pyproject_contributing_url():
    """Verify that pyproject.toml defines Contributing URL under [project.urls]."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})

    assert "Contributing" in urls
    assert urls["Contributing"] == "https://github.com/research-line/abc-hct/blob/main/CONTRIBUTING.md"


def test_readme_and_readme_de_contributing_parity():
    """Verify that README.md and README_de.md include synchronized Contributing badges and documentation links."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "Contributing-Welcome-brightgreen.svg" in readme_en
    assert "Mitwirken-Willkommen-brightgreen.svg" in readme_de
    assert "Verified-2026--10--01" in readme_en
    assert "Geprüft-2026--10--01" in readme_de

    assert "CONTRIBUTING.md" in readme_en
    assert "CONTRIBUTING.md" in readme_de


def test_sbom_and_marketing_audit_20261001():
    """Verify that Level 1 SBOM companion and MARKETING-LOG.txt document the 2026-10-01 Pfad A audit."""
    sbom_txt = (REPO_ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    sbom_md = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    assert "2026-10-01" in sbom_txt
    assert "2026-10-01" in sbom_md
    assert "12. TECHNICAL HYGIENE, CONTRIBUTING GUIDELINES" in marketing
    assert "2026-10-01" in marketing
    assert "CONTRIBUTING.md" in marketing
