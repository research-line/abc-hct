"""Metadata, security, and documentation parity tests for abc-hct."""

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
    assert project.get("version") == "0.1.7"
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


def test_llms_txt_structure_and_timestamp():
    """Verify that llms.txt contains required sections, SECURITY.md link, and current check timestamp."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.exists(), "llms.txt must exist in repo root"
    content = llms_path.read_text(encoding="utf-8")

    assert "# abc-hct" in content
    assert "## Last-checked: 2026-08-21" in content
    assert "## Canonical Links" in content
    assert "SECURITY.md" in content
    assert "## Summary" in content
    assert "## Interfaces" in content
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

    # Both must link to llms.txt, SECURITY.md, and CHANGELOG.md
    assert "llms.txt" in en_content
    assert "llms.txt" in de_content
    assert "SECURITY.md" in en_content
    assert "SECURITY.md" in de_content
    assert "CHANGELOG.md" in en_content
    assert "CHANGELOG.md" in de_content

    # Check status badges
    assert "Version-0.1.7-blue.svg" in en_content
    assert "Version-0.1.7-blue.svg" in de_content
    assert "Tests-15%20Passed" in en_content
    assert "Tests-15%20Passed" in de_content
    assert "LLM--Ready-2026--08--21" in en_content
    assert "LLM--Ready-2026--08--21" in de_content
    assert "Ecosystem-research--line-blue.svg" in en_content
    assert "Ecosystem-research--line-blue.svg" in de_content
    assert "Umbrella-open--bricks-purple.svg" in en_content
    assert "Umbrella-open--bricks-purple.svg" in de_content
    assert "Zero--Egress" in en_content
    assert "Zero--Egress" in de_content


def test_readme_navigation_and_mermaid_parity():
    """Verify that both READMEs contain quick navigation and both Mermaid architecture diagrams."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## Quick Navigation" in en_content
    assert "## Schnellnavigation" in de_content

    # Pipeline diagram
    assert "graph TD" in en_content
    assert "graph TD" in de_content

    # Verification lifecycle diagram
    assert "sequenceDiagram" in en_content
    assert "sequenceDiagram" in de_content


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


def test_sibling_research_matrix_parity():
    """Verify that all sibling repositories are correctly linked in both README files."""
    en_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_content = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_slugs = [
        "functional-stability-theory",
        "fst-nash",
        "economic-sanctions-coercive-diplomacy",
        "prompt-archaeology-casestudy2",
        "CultureEvolution",
        "connes-cvs",
        "direct-beam",
        "rh-even-dominance",
        "DevCenter",
        "CodeBox",
        "open-bricks",
    ]
    for slug in expected_slugs:
        assert slug in en_content, f"Missing sibling link {slug} in README.md"
        assert slug in de_content, f"Missing sibling link {slug} in README_de.md"


def test_changelog_structure():
    """Verify that CHANGELOG.md contains the latest release entry."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md must exist"
    content = changelog_path.read_text(encoding="utf-8")

    assert "## [0.1.7] - 2026-08-21" in content


def test_ci_workflow_integrity():
    """Verify that GitHub Actions workflow file exists and defines required test and linting steps."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "abc-hct-hygiene.yml"
    assert workflow_path.exists(), "Hygiene workflow file must exist"
    content = workflow_path.read_text(encoding="utf-8")

    assert "pytest" in content
    assert "ruff check ." in content
    assert "python -m compileall" in content


def test_utf8_encoding_all_docs():
    """Verify that all documentation and text files decode strictly as UTF-8."""
    doc_files = [
        "README.md",
        "README_de.md",
        "SECURITY.md",
        "llms.txt",
        "CHANGELOG.md",
        "pyproject.toml",
        "REPRODUCIBILITY_H3A_2026-05-17.md",
    ]
    for rel_path in doc_files:
        doc_file = REPO_ROOT / rel_path
        if doc_file.exists():
            doc_file.read_text(encoding="utf-8")


def test_version_parity_across_all_manifests():
    """Verify that version 0.1.7 is synchronized across pyproject.toml, READMEs, and CHANGELOG."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    version = data["project"]["version"]

    assert version == "0.1.7"
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Version-{version}-blue.svg" in (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert f"## [{version}] - 2026-08-21" in (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

