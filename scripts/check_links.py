#!/usr/bin/env python3
"""Check that relative links in Markdown files point at files that exist.

Purpose:
    Docs rot silently when files move. This fails CI on a broken relative link so
    an unlinked or renamed document is caught in the PR that caused it.

Required permissions: none (reads the local checkout only).

Usage:
    python scripts/check_links.py
    python scripts/check_links.py --root . --verbose

Notes:
    External (http/https/mailto) links and pure in-page anchors are skipped.
    Anchors on file links are stripped; only the file's existence is checked.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Vendored fixtures are snapshots of another repo; their relative links are not ours to check.
SKIP_DIRS = {".git", ".venv", "node_modules", "build", "fixtures"}
log = logging.getLogger("check_links")


def markdown_files(root: Path) -> list[Path]:
    """Return every Markdown file under ``root`` outside ignored directories."""
    return [p for p in root.rglob("*.md") if not SKIP_DIRS.intersection(p.relative_to(root).parts)]


def broken_links(path: Path, root: Path) -> list[str]:
    """Return a message for each broken relative link in ``path``."""
    problems: list[str] = []
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            if not resolved.exists():
                problems.append(
                    f"{path.relative_to(root).as_posix()}:{number}: broken link '{target}'"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")
    root = args.root.resolve()
    try:
        files = markdown_files(root)
        problems = [msg for f in files for msg in broken_links(f, root)]
    except OSError as exc:
        log.error("cannot read files under %s: %s", root, exc)
        return 2
    log.debug("checked %d Markdown files", len(files))
    for msg in problems:
        print(msg)
    print(f"checked {len(files)} Markdown files: {len(problems)} broken links")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
