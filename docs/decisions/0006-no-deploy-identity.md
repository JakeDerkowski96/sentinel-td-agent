# 0006: The agent holds no deploy or merge identity; sandbox access only after policy approval

**Status:** accepted

## Context
A compromised or manipulated agent must not be able to change production detections.

## Options
1. Give the agent deployment credentials but instruct it not to use them.
2. Never issue such credentials; sandbox execution through a separate identity reachable only after policy validation of the test plan.

## Decision
Option 2.

## Consequences
- Prompt injection can at worst produce a bad PR, which review and CI catch.
- Sandbox test execution (Phase 5) needs its own approval path.

## Alternatives rejected
Option 1 relies on the model following instructions.
