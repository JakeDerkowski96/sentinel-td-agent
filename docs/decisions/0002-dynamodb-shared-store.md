# 0002: DynamoDB as the shared store; PostgreSQL deferred

**Status:** accepted (review-log U3)

## Context
The triage agent already stores findings in DynamoDB, and seamless integration is a goal. Full comparison and reasoning are in plan/05.

## Options
1. DynamoDB for findings and TD-agent state.
2. PostgreSQL for TD-agent state, reading findings from DynamoDB.
3. Migrate everything to PostgreSQL.

## Decision
Option 1, with GSIs (including a sparse `eligible` index) on the findings table, `tdagent-*` tables alongside it, S3 for large artefacts, and Athena over exports for ad hoc analysis. Repository interfaces make a later backend addition cheap.

## Consequences
- No second operational database, no migration of the triage agent's data.
- Ad hoc relational questions need exports or new GSIs.
- Documented triggers say when to revisit.

## Alternatives rejected
Option 2 adds an always-on database for access patterns that are all key-based. Option 3 forces a migration on another team for benefits we cannot yet demonstrate.
