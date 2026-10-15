# 0003: Triage and threat detection are separate agents, joined by a learning gate

**Status:** accepted

## Context
One process deciding a verdict and also optimising the detector that produced the incident can reinforce its own errors.

## Options
1. A single agent investigates and tunes.
2. Separate agents; findings flow one way through a validated, evidence-complete gate.

## Decision
Option 2.

## Consequences
- A systematically wrong triage agent cannot silently degrade detections: the gate needs human validation.
- Requires a stable finding contract and reconciliation with the existing triage store.

## Alternatives rejected
Option 1 removes the independent check.
