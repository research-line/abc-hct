"""Policy and repository hygiene tests for abc-hct research line."""

from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_IGNORE_RULES = [
    "BEWEISNOTIZ*.md",
    "_proof-notes/",
    "_handoffs/",
    "_data/",
    "logs/",
    "_results/*.log",
    "_compute_queue/logs/",
    "_compute_queue/state/*.json",
    "_results/*.pid",
    "_results/PROOF_PAPER_MATH_CHECK_*.md",
    "_results/REVIEW_CHAIN_*.md",
]

FORBIDDEN_EXACT_FILES = {
    "BEWEISNOTIZ.md",
    "GAPS.md",
    "TODO.md",
    "MEMORY.md",
    "AKTIONSPLAN.md",
}

FORBIDDEN_PREFIXES = (
    "_proof-notes/",
    "_handoffs/",
    "_data/",
    "logs/",
    "_logs/",
)

FORBIDDEN_GLOBS = (
    "_results/PROOF_PAPER_MATH_CHECK_*.md",
    "_results/REVIEW_CHAIN_*.md",
)

LOCAL_PATH_TOKENS = (
    r"C:\Users\User\\",
    "C:/Users/User/",
    "/c/Users/User/",
    "/mnt/c/Users/User/",
)

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".ps1",
    ".json",
    ".jsonl",
    ".yml",
    ".yaml",
    ".toml",
}


def test_gitignore_required_rules():
    """Verify that all required privacy/hygiene ignore rules are present in .gitignore."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file must exist in repository root"
    content = gitignore_path.read_text(encoding="utf-8")
    missing = [rule for rule in REQUIRED_IGNORE_RULES if rule not in content]
    assert not missing, f"Missing required .gitignore rules: {', '.join(missing)}"


def test_no_forbidden_tracked_files():
    """Verify that internal draft, state, and private notes are not tracked in git."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    tracked_files = result.stdout.splitlines()

    violations = []
    for rel_path in tracked_files:
        p = Path(rel_path)
        if p.name in FORBIDDEN_EXACT_FILES:
            violations.append(f"Forbidden exact file tracked: {rel_path}")
        if rel_path.replace("\\", "/").startswith(FORBIDDEN_PREFIXES):
            violations.append(f"Forbidden prefix file tracked: {rel_path}")
        if any(p.match(pattern) for pattern in FORBIDDEN_GLOBS):
            violations.append(f"Forbidden glob pattern match tracked: {rel_path}")

    assert not violations, "Forbidden internal files are tracked:\n" + "\n".join(violations)


def test_no_host_path_leaks():
    """Verify that tracked text files do not contain host-specific absolute paths."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    tracked_files = result.stdout.splitlines()

    # Workflow file defines regex/search tokens as string literals and is exempted
    exempt_files = {
        ".github/workflows/abc-hct-hygiene.yml",
        "tests/test_policy.py",
    }

    path_leaks = []
    for rel_path in tracked_files:
        norm_path = rel_path.replace("\\", "/")
        if norm_path in exempt_files:
            continue
        p = REPO_ROOT / rel_path
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for token in LOCAL_PATH_TOKENS:
            if token in content:
                path_leaks.append(f"{rel_path} (contains token: '{token}')")

    assert not path_leaks, "Tracked files contain host-specific absolute paths:\n" + "\n".join(path_leaks)
