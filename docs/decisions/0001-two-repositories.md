# 0001: Two repositories: the agent and the content

**Status:** accepted (review-log U1)

## Context
The agent's code, prompts and infrastructure change on a different cadence, with different reviewers and permissions, from detection content. Detection content needs a repository an agent can be fenced out of parts of.

## Options
1. One repository for both.
2. Two repositories: agent (this) and content.
3. Agent code inside the content repository.

## Decision
Option 2. The agent works in the content repository only through pull requests from `agent/*` branches.

## Consequences
- The content repo can hold human-only paths (`policy/`, `schemas/`) the agent cannot modify, enforced by a GitHub App with narrow permissions.
- Policy and schemas are owned by the content repo; the agent repo pins versions of the validator and reads policy at run time.
- Two release trains to keep compatible; mitigated by pinning (ADR 0009).

## Alternatives rejected
Option 1 couples agent releases to content PRs and removes the permission boundary. Option 3 lets the agent edit its own limits.
