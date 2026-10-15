# 0008: The content repository owns policy and schemas; the agent reads them

**Status:** accepted

## Context
If limits live in the agent repo, whoever changes the agent also changes its limits.

## Options
1. Policy in the agent repository.
2. Policy and schemas in the content repository, human-only paths.

## Decision
Option 2. See content repo ADR 0006.

## Consequences
- Limits change through reviewed content-repo PRs.
- The agent must read policy at run time and fail closed if it cannot.

## Alternatives rejected
Option 1 weakens the boundary.
