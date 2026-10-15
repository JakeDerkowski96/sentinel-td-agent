# 0007: The CLI is the single interface; the orchestrator runs the same commands

**Status:** accepted (review-log U8)

## Context
Behaviour that only exists inside an orchestrator cannot be reproduced locally or tested offline.

## Options
1. Orchestrator-specific code per state.
2. Workers invoke `tdagent` commands that a person can also run.

## Decision
Option 2, in Python.

## Consequences
- Any proposal step can be re-run from a terminal with `--dry-run`.
- Offline commands (content, audit, coverage) are useful without AWS.

## Alternatives rejected
Option 1 splits the logic and makes debugging a deployment exercise.
