#!/usr/bin/env python3
"""Build a portable Magma/Wiese handoff bundle.

The bundle contains the Magma handoff script, the parser, the runbook, and the
vendored Wiese/Kilford + ArtinAlgebras package directories. It is meant for a
machine that has Magma available, while this local machine does not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path


DEFAULT_NAME = f"magma_wiese_handoff_{date.today().isoformat()}.zip"

INCLUDE_FILES = [
    Path("_scripts/mstar_wiese_local_hecke_handoff.m"),
    Path("_scripts/mstar_wiese_diagnostic_ladder.m"),
    Path("_scripts/mstar_parse_wiese_output.py"),
    Path("_scripts/make_magma_wiese_bundle.py"),
    Path("_scripts/setup_magma_path.ps1"),
    Path("_handoffs/MAGMA_WIESE_RUNBOOK.md"),
    Path("_proof-notes/MG_wiese_local_hecke_handoff.md"),
]

INCLUDE_DIRS = [
    Path("_sources/ArtinAlgebras"),
    Path("_sources/HeckeAlgebra"),
]

SKIP_SUFFIXES = {".aux", ".log", ".out", ".toc", ".dvi"}
SKIP_DIRS = {"__pycache__"}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts) or path.suffix.lower() in SKIP_SUFFIXES


def iter_bundle_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for rel in INCLUDE_FILES:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append(path)

    for rel_dir in INCLUDE_DIRS:
        base = root / rel_dir
        if not base.is_dir():
            raise FileNotFoundError(base)
        for path in sorted(base.rglob("*")):
            if path.is_file() and not should_skip(path.relative_to(root)):
                files.append(path)
    return sorted(set(files), key=lambda p: p.relative_to(root).as_posix())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("_handoffs") / DEFAULT_NAME)
    args = parser.parse_args()

    root = project_root()
    out = args.out
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)

    files = iter_bundle_files(root)
    manifest_entries = []

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            rel = path.relative_to(root).as_posix()
            zf.write(path, rel)
            manifest_entries.append(
                {
                    "path": rel,
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )

        readme = "\n".join(
            [
                "# Magma/Wiese Handoff Bundle",
                "",
                "Run from the extracted bundle root on a machine with Magma:",
                "",
                "```bash",
                "magma _scripts/mstar_wiese_diagnostic_ladder.m 2>&1 | tee _results/mstar_wiese_diag.log",
                "python _scripts/mstar_parse_wiese_output.py _results/mstar_wiese_diag.log",
                "magma _scripts/mstar_wiese_local_hecke_handoff.m 2>&1 | tee _results/mstar_wiese_smoke.log",
                "python _scripts/mstar_parse_wiese_output.py _results/mstar_wiese_smoke.log",
                "```",
                "",
                "The script starts smoke-only by default. See `_handoffs/MAGMA_WIESE_RUNBOOK.md`.",
                "",
            ]
        )
        zf.writestr("README_RUN.md", readme)
        zf.writestr(
            "BUNDLE_MANIFEST.json",
            json.dumps(
                {
                    "created": date.today().isoformat(),
                    "file_count": len(manifest_entries),
                    "files": manifest_entries,
                },
                indent=2,
            )
            + "\n",
        )

    print(out)
    print(f"files={len(manifest_entries)} bytes={out.stat().st_size} sha256={sha256_file(out)}")


if __name__ == "__main__":
    main()
