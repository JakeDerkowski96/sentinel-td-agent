"""Exceptions and process exit codes shared across the CLI.

Required permissions: none.
"""

from __future__ import annotations

EXIT_OK = 0
EXIT_FINDINGS = 1  # validation errors, or a check that failed on purpose
EXIT_ERROR = 2  # usage or runtime failure
EXIT_PLANNED = 3  # command exists in the plan but is not implemented
EXIT_POLICY_DENIED = 4  # reserved for policy enforcement (Phase 3)


class TdAgentError(Exception):
    """Base class: a failure the CLI should report cleanly without a traceback."""


class ConfigError(TdAgentError):
    """Configuration is missing, unreadable or invalid."""


class ContentRepoError(TdAgentError):
    """The content repository path is missing or is not a DaC repository."""
