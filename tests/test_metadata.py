"""Metadata and documentation parity tests for abc-hct."""

from pathlib import Path
import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_toml_structure():
    """Verify that pyproject.toml exists and contains valid metadata."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert "project" in data
    project = data["project"]
    assert project.get("name") == "abc-hct"
    assert project.get("version") == "0.1.6"
    assert "description" in project
    assert project.get("requires-python") == ">=3.10"
    assert "license" in project


def test_llms_txt_structure_and_timestamp():
    """Verify that llms.txt contains required sections and current check timestamp."""
    llms_path = REPO_ROOT / "llms.txt"
    assert llms_path.exists(), "llms.txt must exist in repo root"
    content = llms_path.read_text(encoding="utf-8")

    assert "# abc-hct" in content
    assert "## Last-checked: 2026-08-16" in content
    assert "## Canonical Links" in content
    assert "## Summary" in content
    assert "## Interfaces" in content
    assert "## Safety Boundaries" in content
    assert "## Search Phrases" in content


def test_readme_and_readme_de_parity():
    """Verify that README.md and README_de.md are present with synchronized badges and sibling matrix."""
    readme_en = REPO_ROOT / "README.md"
    readme_de = REPO_ROOT / "README_de.md"

    assert readme_en.exists(), "README.md must exist"
    assert readme_de.exists(), "README_de.md must exist"

    en_content = readme_en.read_text(encoding="utf-8")
    de_content = readme_de.read_text(encoding="utf-8")

    # Both must reference each other
    assert "README_de.md" in en_content
    assert "README.md" in de_content

    # Both must link to llms.txt and CHANGELOG.md
    assert "llms.txt" in en_content
    assert "llms.txt" in de_content
    assert "CHANGELOG.md" in en_content
    assert "CHANGELOG.md" in de_content

    # Check status badges
    assert "Version-0.1.6-blue.svg" in en_content
    assert "Version-0.1.6-blue.svg" in de_content
    assert "LLM--Ready-2026--08--16" in en_content
    assert "LLM--Ready-2026--08--16" in de_content
    assert "Ecosystem-research--line-blue.svg" in en_content
    assert "Ecosystem-research--line-blue.svg" in de_content
    assert "Umbrella-open--bricks-purple.svg" in en_content
    assert "Umbrella-open--bricks-purple.svg" in de_content

    # Sibling research matrix links
    for slug in [
        "functional-stability-theory",
        "fst-nash",
        "economic-sanctions-coercive-diplomacy",
        "prompt-archaeology-casestudy2",
        "CultureEvolution",
        "connes-cvs",
        "direct-beam",
        "DevCenter",
        "CodeBox",
    ]:
        assert slug in en_content, f"Missing sibling link {slug} in README.md"
        assert slug in de_content, f"Missing sibling link {slug} in README_de.md"


def test_changelog_structure():
    """Verify that CHANGELOG.md contains the latest release entry."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md must exist"
    content = changelog_path.read_text(encoding="utf-8")

    assert "## [0.1.6] - 2026-08-16" in content


def test_utf8_encoding_all_docs():
    """Verify that all documentation and text files decode strictly as UTF-8."""
    for rel_path in ["README.md", "README_de.md", "llms.txt", "CHANGELOG.md", "pyproject.toml"]:
        doc_file = REPO_ROOT / rel_path
        if doc_file.exists():
            doc_file.read_text(encoding="utf-8")
