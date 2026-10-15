"""Command-line entry point for `tdagent`.

Argument parsing and dispatch only; the work lives in the command modules so it can be
tested without invoking the CLI.

Required permissions: none for the implemented commands (local reads).

Usage:
    tdagent --content-repo ../sentinel-detection-as-code content list
    tdagent report coverage --env prod --format json
    tdagent propose tune --rule DET-LINUX-0001     # planned: prints status, exits 3

Exit codes: 0 ok, 1 findings or failure, 2 usage or runtime error, 3 planned (not
implemented), 4 denied by policy.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .commands import content, doctor, planned, report
from .config import load_config
from .errors import EXIT_ERROR, TdAgentError


def build_parser() -> argparse.ArgumentParser:
    """Build the full command tree (implemented and planned commands)."""
    parser = argparse.ArgumentParser(
        prog="tdagent",
        description="Sentinel Threat Detection agent CLI. Planned commands are marked [planned].",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug detail on stderr")
    parser.add_argument("--config", type=Path, help="path to tdagent.yaml")
    parser.add_argument("--content-repo", type=Path, help="path to the content repository checkout")
    top = parser.add_subparsers(dest="group", required=True, metavar="COMMAND")
    groups: dict[str, Any] = {}

    def group(name: str, help_text: str, *, leaf: bool = False) -> Any:
        if leaf:
            return top.add_parser(name, help=help_text)
        if name not in groups:
            groups[name] = top.add_parser(name, help=help_text).add_subparsers(
                dest="command", required=True, metavar="SUBCOMMAND"
            )
        return groups[name]

    for module in (content, report, doctor, planned):
        module.register(group)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    # Planned commands accept (and ignore) the flags they will eventually have, so
    # `tdagent propose tune --rule X` reaches the stub instead of failing to parse.
    args, extras = parser.parse_known_args(argv)
    if extras and not getattr(args, "planned", False):
        parser.error(f"unrecognized arguments: {' '.join(extras)}")
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )
    try:
        cfg = load_config(args.config, args.content_repo)
        return int(args.func(args, cfg))
    except TdAgentError as exc:
        logging.getLogger("tdagent").error("%s", exc)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
