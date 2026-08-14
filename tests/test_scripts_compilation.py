"""Compilation and syntax integrity tests for abc-hct research scripts."""

import compileall
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_scripts_syntax_compilation():
    """Verify that all Python scripts under _scripts/ compile without syntax errors."""
    scripts_dir = REPO_ROOT / "_scripts"
    assert scripts_dir.exists(), "_scripts directory must exist"

    # compileall returns True on success, False on error
    success = compileall.compile_dir(str(scripts_dir), quiet=1, force=False)
    assert success, "One or more scripts in _scripts/ failed Python compilation"


def test_compute_queue_scripts_compilation():
    """Verify that compute queue scripts compile if the directory exists."""
    cq_scripts_dir = REPO_ROOT / "_compute_queue" / "scripts"
    if cq_scripts_dir.exists():
        success = compileall.compile_dir(str(cq_scripts_dir), quiet=1, force=False)
        assert success, "One or more scripts in _compute_queue/scripts/ failed Python compilation"
