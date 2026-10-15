#!/usr/bin/env python3
"""Refresh the vendored sample content repository used by the tests.

Purpose:
    Tests need realistic content without network access to the content repository
    (ADR 0009). This copies a checkout of sentinel-detection-as-code into
    tests/fixtures/content-repo so the snapshot only changes when you decide it should.

Required permissions: none (local file copy).

Usage:
    python scripts/refresh_fixture.py ../sentinel-detection-as-code
    python scripts/refresh_fixture.py ../sentinel-detection-as-code --dry-run -v

Notes:
    Copies files only (not directory attributes): OneDrive-synced checkouts carry
    read-only directory attributes that make later cleanup fail on Windows.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

PARTS = ("content", "schemas", "policy", "tenants")
DEST = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "content-repo"
log = logging.getLogger("refresh_fixture")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", type=Path, help="path to a sentinel-detection-as-code checkout")
    parser.add_argument("--dry-run", action="store_true", help="show what would be copied")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    source = args.source.resolve()
    missing = [p for p in PARTS if not (source / p).is_dir()]
    if missing:
        log.error(
            "%s is not a content repository checkout (missing: %s)", source, ", ".join(missing)
        )
        return 2
    try:
        if DEST.exists() and not args.dry_run:
            shutil.rmtree(DEST)
        count = 0
        for part in PARTS:
            for path in sorted((source / part).rglob("*")):
                if path.is_dir() or "__pycache__" in path.parts:
                    continue
                target = DEST / path.relative_to(source)
                log.debug("%s -> %s", path, target)
                count += 1
                if not args.dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, target)
    except OSError as exc:
        log.error("copy failed: %s", exc)
        return 2
    log.info("%s %d files into %s", "would copy" if args.dry_run else "copied", count, DEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
