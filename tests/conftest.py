"""Shared fixtures: a disposable copy of the vendored sample content repository.

Required permissions: none.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "content-repo"
CONTRACTS = REPO_ROOT / "contracts"


def copy_files(src: Path, dst: Path) -> None:
    """Copy files only. shutil.copytree also copies directory attributes, and OneDrive-synced
    checkouts carry read-only directory attributes that later make rmtree fail on Windows."""
    for path in src.rglob("*"):
        target = dst / path.relative_to(src)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


@pytest.fixture()
def content(tmp_path: Path) -> Path:
    """A throwaway copy of the sample content repository that tests may mutate."""
    root = tmp_path / "content-repo"
    copy_files(FIXTURE, root)
    return root


def load_contract(name: str) -> dict[str, Any]:
    """Load a JSON Schema from contracts/."""
    data: dict[str, Any] = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    return data
