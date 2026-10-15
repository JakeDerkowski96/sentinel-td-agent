"""Commands described in the plan but not implemented yet.

Each one is registered so `--help` shows the full command tree, and running it prints
what it will do, which phase delivers it, and where it is specified, then exits with
code 3 so automation can never mistake a stub for success.

Required permissions: none.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass

from ..config import Config
from ..errors import EXIT_PLANNED
from .common import GroupFactory, Handler

log = logging.getLogger(__name__)
PLAN = "docs/plan/03-cli.md"


@dataclass(frozen=True)
class Planned:
    """One stubbed command."""

    group: str
    name: str
    help: str
    phase: int
    spec: str  # document that specifies it


PLANNED: tuple[Planned, ...] = (
    Planned("content", "new", "scaffold a new rule or content folder from templates", 2, PLAN),
    Planned("content", "deps", "dependency graph: what an item needs and what needs it", 2, PLAN),
    Planned("content", "set-lifecycle", "propose a lifecycle transition as a PR", 3, PLAN),
    Planned(
        "content", "set-agent-mode", "change a rule's agent.tuning (human-labelled PR)", 3, PLAN
    ),
    Planned("content", "retire", "propose retiring a rule", 7, PLAN),
    Planned(
        "report",
        "performance",
        "alert volume, false-positive rate, health, cost (dev and prod)",
        2,
        "docs/plan/04-reports.md",
    ),
    Planned(
        "signals",
        "scan",
        "evaluate tuning thresholds and list tuning candidates",
        2,
        "docs/plan/02-agent-design.md",
    ),
    Planned(
        "findings",
        "query",
        "query triage findings from the shared store",
        2,
        "docs/plan/06-triage-integration.md",
    ),
    Planned("findings", "show", "show one triage finding", 2, "docs/plan/06-triage-integration.md"),
    Planned(
        "propose",
        "tune",
        "TUNE: propose a change to an existing rule",
        3,
        "docs/plan/02-agent-design.md",
    ),
    Planned("propose", "create", "CREATE: propose a new rule", 4, "docs/plan/02-agent-design.md"),
    Planned(
        "propose",
        "research",
        "RESEARCH: assess a detection opportunity",
        4,
        "docs/plan/02-agent-design.md",
    ),
    Planned(
        "propose",
        "coverage-assess",
        "COVERAGE ASSESSMENT: find gaps without proposing rules",
        7,
        "docs/plan/02-agent-design.md",
    ),
    Planned(
        "propose",
        "deprecate",
        "DEPRECATE: propose retiring obsolete rules",
        7,
        "docs/plan/02-agent-design.md",
    ),
    Planned(
        "test",
        "replay",
        "replay current vs candidate logic over history",
        3,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned(
        "test",
        "synthetic",
        "run fixture-based test cases",
        3,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned(
        "test",
        "atomic",
        "run Atomic Red Team via the sandbox identity",
        5,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned(
        "test",
        "sandbox",
        "end-to-end alert and incident validation in the sandbox",
        5,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned(
        "pr",
        "open",
        "open the pull request for a stored proposal",
        3,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned(
        "pr",
        "status",
        "review state and CI result of a proposal's PR",
        3,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned("policy", "show", "print the effective policy", 2, "docs/plan/03-cli.md"),
    Planned(
        "policy",
        "check",
        "check a diff against proposal-limits.yaml",
        3,
        "docs/plan/07-validation-and-promotion.md",
    ),
    Planned("eval", "run", "run the evaluation suites", 3, "docs/plan/09-evaluation.md"),
    Planned("eval", "compare", "compare two evaluation runs", 3, "docs/plan/09-evaluation.md"),
    Planned(
        "inventory",
        "flatten",
        "flatten rules into inventory rows",
        6,
        "docs/plan/12-feature-detection-inventory.md",
    ),
    Planned(
        "inventory",
        "ingest",
        "ingest inventory rows into Log Analytics",
        6,
        "docs/plan/12-feature-detection-inventory.md",
    ),
)


def _stub(item: Planned) -> Handler:
    def run(_args: argparse.Namespace, _cfg: Config) -> int:
        log.error(
            "'%s %s' is planned for Phase %d and is not implemented yet: %s. Specified in %s.",
            item.group,
            item.name,
            item.phase,
            item.help,
            item.spec,
        )
        return EXIT_PLANNED

    return run


def register(group: GroupFactory) -> None:
    """Attach every planned command under its group."""
    for item in PLANNED:
        sub = group(item.group, f"{item.group} commands")
        parser = sub.add_parser(item.name, help=f"[planned, phase {item.phase}] {item.help}")
        parser.set_defaults(func=_stub(item), planned=True)
