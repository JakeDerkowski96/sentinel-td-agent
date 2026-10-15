"""`tdagent report audit|coverage`: reports derived from the content repository.

Required permissions: none (local reads only). `report performance` is planned and needs
Log Analytics Reader; see commands/planned.py.

Usage:
    tdagent report audit --env prod --format json --output audit.json
    tdagent report coverage --env all --techniques techniques-of-interest.txt
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from ..config import Config
from ..content_repo import ENV_STATES, open_content_repo
from ..errors import EXIT_OK
from ..reports.audit import build_audit
from ..reports.coverage import build_coverage
from ..reports.render import render_audit, render_coverage
from .common import GroupFactory, emit


def _audit(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    report = build_audit(
        content, env=args.env, include_retired=args.include_retired, now=datetime.now(UTC)
    )
    emit(
        json.dumps(report, indent=2) if args.format == "json" else render_audit(report), args.output
    )
    return EXIT_OK


def _coverage(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    report = build_coverage(
        content,
        env=args.env,
        include_retired=args.include_retired,
        techniques_file=args.techniques,
        now=datetime.now(UTC),
    )
    emit(
        json.dumps(report, indent=2) if args.format == "json" else render_coverage(report),
        args.output,
    )
    return EXIT_OK


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env", choices=sorted(ENV_STATES), default="all", help="dev, prod or all")
    parser.add_argument("--include-retired", action="store_true")
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument("--output", type=Path, help="write to a file instead of stdout")


def register(group: GroupFactory) -> None:
    """Attach the implemented `report` subcommands."""
    sub = group("report", "generate audit, coverage and performance reports")

    p = sub.add_parser("audit", help="content integrity, ownership, exceptions, maturity gaps")
    _common(p)
    p.set_defaults(func=_audit)

    p = sub.add_parser("coverage", help="technique, tactic and data-source coverage and gaps")
    _common(p)
    p.add_argument(
        "--techniques", type=Path, help="file of technique IDs of interest, one per line"
    )
    p.set_defaults(func=_coverage)
