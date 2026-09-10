"""Metadata, security, documentation, and Pfad B contract parity tests for abc-hct."""

from pathlib import Path
import re
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
    assert project.get("version") == "0.1.10"
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


def test_llms_txt_structure_and_timestamp():
    """Verify that llms.txt contains required sections, canonical links, and current check timestamp."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.exists(), "llms.txt must exist in repo root"
    content = llms_path.read_text(encoding="utf-8")

    assert "# abc-hct" in content
    assert "## Last-checked: 2026-09-10" in content
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
    assert "Version-0.1.10-blue.svg" in en_content
    assert "Version-0.1.10-blue.svg" in de_content
    assert "Tests-24%20Passed" in en_content
    assert "Tests-24%20Passed" in de_content
    assert "LLM--Ready-2026--09--10" in en_content
    assert "LLM--Ready-2026--09--10" in de_content
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
    assert "graph TD" in en_content
    assert "graph TD" in de_content

    # Verification lifecycle diagram
    assert "sequenceDiagram" in en_content
    assert "sequenceDiagram" in de_content


def test_14_point_navigation_parity():
    """Verify that both READMEs contain all 14 quick navigation points with identical anchors."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_anchors = [
        "quick-reference",
        "key-scientific-findings",
        "system-architecture--pipeline",
        "curated-verification-lifecycle",
        "core-capabilities--research-invariants",
        "evidence-mapping--paper-references",
        "computational-milestones--batches",
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
        assert f"#{anchor}" in de_content, f"Missing anchor #{anchor} in README_de.md navigation"
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
    """Verify that version 0.1.10 is synchronized across pyproject.toml, READMEs, and CHANGELOG."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    version = data["project"]["version"]

    assert version == "0.1.10"
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert f"## [{version}] - 2026-09-10" in (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
