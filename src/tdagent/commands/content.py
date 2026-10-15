"""`tdagent content ...`: inspect, validate and index detection content.

Required permissions: none (local reads; `content index` writes only into --out unless
--dry-run).

Usage:
    tdagent content list --env prod
    tdagent content show DET-ENTRA-0001
    tdagent content validate --strict
    tdagent content index --dry-run -v
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from dac_validate.index import write_index
from dac_validate.report import render_json, render_markdown, render_text, summarize

from ..config import Config
from ..content_repo import ENV_STATES, ContentRepo, open_content_repo
from ..errors import EXIT_ERROR, EXIT_FINDINGS, EXIT_OK
from .common import GroupFactory, emit

log = logging.getLogger(__name__)

TYPES = (
    "rule",
    "function",
    "parser",
    "watchlist",
    "automation-rule",
    "playbook",
    "workbook",
    "hunting-query",
)


def _rows(content: ContentRepo, args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if args.type in (None, "rule"):
        for b in content.rules_in(args.env, include_retired=args.include_retired):
            rows.append(
                {
                    "id": b.rule_id,
                    "type": "rule",
                    "lifecycle": b.metadata.get("lifecycle"),
                    "severity": b.rule.get("severity"),
                    "tier": b.metadata.get("confidenceTier"),
                    "agent": b.metadata.get("agent", {}).get("tuning"),
                    "name": b.rule.get("displayName"),
                }
            )
    for m in content.repo.manifests:
        kind = m.data.get("type")
        if args.type not in (None, kind):
            continue
        rows.append(
            {
                "id": m.item_id,
                "type": kind,
                "lifecycle": m.data.get("lifecycle"),
                "severity": "",
                "tier": "",
                "agent": "",
                "name": m.data.get("displayName"),
            }
        )
    if args.lifecycle:
        rows = [r for r in rows if r["lifecycle"] == args.lifecycle]
    return sorted(rows, key=lambda r: str(r["id"]))


def _list(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    rows = _rows(content, args)
    if args.format == "json":
        emit(json.dumps(rows, indent=2), None)
        return EXIT_OK
    cols = ["id", "type", "lifecycle", "severity", "tier", "agent", "name"]
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) if rows else len(c) for c in cols}
    print("  ".join(c.upper().ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))
    print(f"{len(rows)} items")
    return EXIT_OK


def _show(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    index = content.index()
    target = args.id
    for b in content.repo.rules:
        if b.rule_id != target:
            continue
        overrides = [
            f"{d.get('tenant')}" for _p, d in content.repo.overrides if d.get("rule") == target
        ]
        detail = {
            "id": target,
            "type": "rule",
            "path": b.directory.relative_to(content.root).as_posix(),
            "displayName": b.rule.get("displayName"),
            "severity": b.rule.get("severity"),
            "enabled": b.rule.get("enabled"),
            "lifecycle": b.metadata.get("lifecycle"),
            "confidenceTier": b.metadata.get("confidenceTier"),
            "owner": b.metadata.get("owner"),
            "agent": b.metadata.get("agent"),
            "tactics": b.rule.get("tactics"),
            "techniques": b.rule.get("techniques"),
            "tables": b.metadata.get("dataSources", {}).get("tables"),
            "dependencies": index["rules"][target]["dependencies"],
            "package": b.metadata.get("package"),
            "scope": b.metadata.get("deployment", {}).get("scope"),
            "tenantOverrides": overrides,
            "historyEntries": [
                {k: e.get(k) for k in ("version", "date", "type", "outcome", "summary")}
                for e in (b.history or {}).get("entries", [])
            ],
            "exceptions": len((b.exceptions or {}).get("exceptions", [])),
            "testCases": len((b.tests or {}).get("cases", [])),
        }
        emit(json.dumps(detail, indent=2), None)
        return EXIT_OK
    for m in content.repo.manifests:
        if m.item_id == target:
            detail = {
                "id": target,
                "type": m.data.get("type"),
                "path": m.directory.relative_to(content.root).as_posix(),
                "displayName": m.data.get("displayName"),
                "lifecycle": m.data.get("lifecycle"),
                "alias": m.data.get("alias"),
                "tables": m.data.get("tables"),
                "usedBy": index["content"].get(target, {}).get("usedBy", []),
            }
            emit(json.dumps(detail, indent=2), None)
            return EXIT_OK
    log.error("no rule or content item with id %s", target)
    return EXIT_ERROR


def _validate(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    rules, items = len(content.repo.rules), len(content.repo.manifests)
    renderers = {"text": render_text, "json": render_json, "markdown": render_markdown}
    emit(renderers[args.format](content.issues, rules, items), args.output)
    errors, warnings = summarize(content.issues)
    return EXIT_FINDINGS if errors or (args.strict and warnings) else EXIT_OK


def _index(args: argparse.Namespace, cfg: Config) -> int:
    content = open_content_repo(cfg.content_repo)
    # An index built from invalid metadata would look authoritative and be wrong.
    errors, _ = summarize(content.issues)
    if errors:
        log.error("content has %d validation errors; fix them before building the index", errors)
        return EXIT_FINDINGS
    target = write_index(content.index(), args.out, dry_run=args.dry_run)
    print(f"{'would write' if args.dry_run else 'wrote'} {target}")
    return EXIT_OK


def register(group: GroupFactory) -> None:
    """Attach the implemented `content` subcommands."""
    sub = group("content", "manage detection content")

    p = sub.add_parser("list", help="list rules and content items")
    p.add_argument("--type", choices=TYPES, help="restrict to one content type")
    p.add_argument("--lifecycle", help="restrict to one lifecycle state")
    p.add_argument(
        "--env", choices=sorted(ENV_STATES), default="all", help="rules only: dev, prod or all"
    )
    p.add_argument("--include-retired", action="store_true")
    p.add_argument("--format", choices=("table", "json"), default="table")
    p.set_defaults(func=_list)

    p = sub.add_parser("show", help="show one rule or content item")
    p.add_argument("id", help="e.g. DET-ENTRA-0001")
    p.set_defaults(func=_show)

    p = sub.add_parser("validate", help="validate schemas and cross-references")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    p.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    p.add_argument("--output", type=Path)
    p.set_defaults(func=_validate)

    p = sub.add_parser("index", help="build the coverage/dependency index")
    p.add_argument(
        "--out", type=Path, default=Path("build"), help="output directory (default: build)"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="report what would be written without writing"
    )
    p.set_defaults(func=_index)
