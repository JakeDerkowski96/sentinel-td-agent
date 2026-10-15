"""Load `tdagent.yaml` plus environment overrides.

Required permissions: none (reads one local file).

Lookup order for the file: explicit path, then $TDAGENT_CONFIG, then
./tdagent.yaml. A missing file is fine for offline commands; defaults apply.
Credentials never belong here -- see docs/plan/08-security-and-permissions.md.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError

log = logging.getLogger(__name__)


@dataclass
class Config:
    """Effective configuration. Only `content_repo` is used by implemented commands."""

    content_repo: Path = Path(".")
    bedrock: dict[str, Any] = field(default_factory=dict)
    stores: dict[str, Any] = field(default_factory=dict)
    budgets: dict[str, Any] = field(default_factory=dict)
    source: Path | None = None


def _find(explicit: Path | None) -> Path | None:
    if explicit is not None:
        if not explicit.is_file():
            raise ConfigError(f"config file not found: {explicit}")
        return explicit
    env = os.environ.get("TDAGENT_CONFIG")
    if env:
        path = Path(env)
        if not path.is_file():
            raise ConfigError(f"$TDAGENT_CONFIG points at a missing file: {path}")
        return path
    default = Path("tdagent.yaml")
    return default if default.is_file() else None


def load_config(explicit: Path | None = None, content_repo: Path | None = None) -> Config:
    """Return the effective configuration.

    Precedence for the content repository: ``content_repo`` argument (the CLI flag),
    then $TDAGENT_CONTENT_REPO, then the file, then the current directory.
    """
    cfg = Config()
    path = _find(explicit)
    if path is not None:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigError(f"cannot read config {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"config {path} must be a mapping at the top level")
        cfg.source = path
        cfg.bedrock = dict(raw.get("bedrock") or {})
        cfg.stores = dict(raw.get("stores") or {})
        cfg.budgets = dict(raw.get("budgets") or {})
        if raw.get("content_repo"):
            # Relative paths are relative to the config file, not the shell's cwd.
            cfg.content_repo = (path.parent / str(raw["content_repo"])).resolve()
    env_repo = os.environ.get("TDAGENT_CONTENT_REPO")
    if env_repo:
        cfg.content_repo = Path(env_repo)
    if content_repo is not None:
        cfg.content_repo = content_repo
    log.debug("config source=%s content_repo=%s", cfg.source, cfg.content_repo)
    return cfg
