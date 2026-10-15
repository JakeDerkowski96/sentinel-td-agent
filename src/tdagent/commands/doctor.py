"""`tdagent doctor`: check the local setup.

Required permissions: none (local reads only). Cloud checks (Bedrock, DynamoDB, Log
Analytics, GitHub App) are listed as skipped until the phases that need them land.

Usage:
    tdagent doctor
    tdagent doctor --content-repo ../sentinel-detection-as-code -v
"""

from __future__ import annotations

import argparse
import shutil
import sys

from dac_validate import __version__ as validator_version

from ..config import Config
from ..content_repo import open_content_repo
from ..errors import EXIT_FINDINGS, EXIT_OK, TdAgentError
from .common import GroupFactory

SKIPPED = (
    "Bedrock model access",
    "DynamoDB tables",
    "Log Analytics access",
    "GitHub App token",
)


def _doctor(_args: argparse.Namespace, cfg: Config) -> int:
    failures = 0

    def line(status: str, name: str, detail: str = "") -> None:
        print(f"{status:7} {name}" + (f": {detail}" if detail else ""))

    line("ok", "python", sys.version.split()[0])
    line(
        "ok" if shutil.which("git") else "warn",
        "git",
        "found" if shutil.which("git") else "not on PATH",
    )
    line("ok", "dac-validate", validator_version)
    line(
        "ok" if cfg.source else "info",
        "config",
        str(cfg.source) if cfg.source else "none found (defaults)",
    )
    try:
        content = open_content_repo(cfg.content_repo)
    except TdAgentError as exc:
        line("FAIL", "content repo", str(exc))
        failures += 1
    else:
        errors = sum(1 for i in content.issues if i.severity.value == "error")
        line("ok", "content repo", f"{content.root} @ {content.ref}")
        line(
            "ok" if errors == 0 else "FAIL",
            "content validation",
            f"{len(content.repo.rules)} rules, {errors} errors",
        )
        failures += 1 if errors else 0
    for name in SKIPPED:
        line("skipped", name, "not implemented yet")
    return EXIT_FINDINGS if failures else EXIT_OK


def register(group: GroupFactory) -> None:
    """Attach `doctor` as a top-level command."""
    parser = group("doctor", "check the local setup", leaf=True)
    parser.set_defaults(func=_doctor)
