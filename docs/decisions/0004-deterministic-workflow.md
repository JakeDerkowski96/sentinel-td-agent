# 0004: Deterministic workflow with narrow model steps

**Status:** accepted (review-log U10)

## Context
Detection changes are consequential and must be auditable and reproducible. Open-ended agent loops are hard to bound, test and cost-control.

## Options
1. A free-roaming tool-using agent.
2. A state machine per mode on Step Functions; the model is called for specific steps with structured output.
3. A managed agent runtime (Bedrock AgentCore or Agents).

## Decision
Option 2 to start. Option 3 remains open if its identity, memory or tool-gateway features become worth the lock-in.

## Consequences
- Explicit states, stop conditions, retries and human wait states.
- Less flexible than an open loop by design.
- Orchestrator choice is revisitable because workers just run the CLI (ADR 0007).

## Alternatives rejected
Option 1 cannot enforce the safety properties we need.
