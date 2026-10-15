# 0005: Claude via the Bedrock Converse API; model ID in configuration

**Status:** accepted (review-log U11)

## Context
The organisation runs Claude on AWS Bedrock. Model versions change often.

## Options
1. Hard-code a model ID.
2. Configuration-driven model ID and region; Converse API with tool use and structured output.

## Decision
Option 2.

## Consequences
- Model upgrades are config changes gated by the evaluation suite.
- Different modes can use different models if evaluation justifies it.

## Alternatives rejected
Option 1 turns every model change into a code change.
