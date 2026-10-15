"""Access to a local checkout of the content repository.

Wraps the `dac_validate` library (pinned by tag) so the rest of the CLI deals
with one small surface: load, validate, index, and environment filtering.

Required permissions: none (local file reads; `git rev-parse` for the ref).
"""

from __future__ import annotations

import logging
import subprocess  # noqa: S404 - used only to read the checkout's HEAD
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dac_validate.checks import run_checks
from dac_validate.index import build_index
from dac_validate.loader import load_repository
from dac_validate.models import Issue, Repository, RuleBundle
from dac_validate.schema_check import validate_schemas

from .errors import ContentRepoError

log = logging.getLogger(__name__)

# Environment is derived from lifecycle because the content repo has no dev/prod
# folders (content ADR 0004). `canary` counts as prod: it runs in production
# tenants at reduced severity. See docs/review-log.md U9.
ENV_STATES: dict[str, frozenset[str]] = {
    "dev": frozenset({"draft", "validated", "sandbox-passed"}),
    "prod": frozenset({"canary", "approved", "production"}),
    "all": frozenset({"draft", "validated", "sandbox-passed", "canary", "approved", "production"}),
}


@dataclass
class ContentRepo:
    """A loaded content repository and its validation findings."""

    root: Path
    repo: Repository
    issues: list[Issue]

    @property
    def ref(self) -> str:
        """Short git commit of the content checkout.

        Returns 'unknown' unless the content root is itself the top level of a git
        repository. Without that check a vendored copy inside another repo (the test
        fixture) would report the *enclosing* repository's commit, which is misleading.
        """
        try:
            top = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(self.root), "rev-parse", "--show-toplevel"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if top.returncode != 0 or Path(top.stdout.strip()).resolve() != self.root:
                return "unknown"
            head = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(self.root), "rev-parse", "--short", "HEAD"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return "unknown"
        return head.stdout.strip() if head.returncode == 0 and head.stdout.strip() else "unknown"

    def index(self) -> dict[str, Any]:
        """Derived coverage/dependency index (always rebuilt; never cached)."""
        return build_index(self.repo)  # type: ignore[no-any-return]

    def rules_in(self, env: str, *, include_retired: bool = False) -> list[RuleBundle]:
        """Rules whose lifecycle belongs to ``env``; retired rules only on request."""
        states = set(ENV_STATES[env])
        if include_retired:
            states.add("retired")
        return [r for r in self.repo.rules if r.metadata.get("lifecycle") in states]


def open_content_repo(root: Path) -> ContentRepo:
    """Load and validate the repository at ``root``.

    Raises ContentRepoError when ``root`` is not a DaC repository, so every command
    reports the same clear message instead of a stack trace.
    """
    root = root.resolve()
    if not (root / "schemas").is_dir() or not (root / "content").is_dir():
        raise ContentRepoError(
            f"{root} does not look like a DaC repository root (needs schemas/ and content/). "
            "Pass --content-repo or set content_repo in tdagent.yaml."
        )
    try:
        repo = load_repository(root)
        issues = [*repo.load_issues, *validate_schemas(repo), *run_checks(repo)]
    except ValueError as exc:
        raise ContentRepoError(str(exc)) from exc
    log.debug("opened %s: %d rules, %d issues", root, len(repo.rules), len(issues))
    return ContentRepo(root=root, repo=repo, issues=issues)
