"""Helpers shared by command modules.

Required permissions: none.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..config import Config
from ..errors import TdAgentError

log = logging.getLogger(__name__)

Handler = Callable[[argparse.Namespace, Config], int]
# group(name, help, leaf=False): returns the subparsers action for a command group,
# or (leaf=True) a standalone top-level parser.
GroupFactory = Callable[..., Any]


def emit(text: str, output: Path | None) -> None:
    """Write a result to ``output`` or stdout. Results go to stdout; diagnostics to logging."""
    if output is None:
        print(text)
        return
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    except OSError as exc:
        raise TdAgentError(f"cannot write {output}: {exc}") from exc
    log.info("wrote %s", output)
