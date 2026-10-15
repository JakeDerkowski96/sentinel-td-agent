# 0009: Pin the content validator by tag; vendor a sample content repo for tests

**Status:** accepted (review-log U20)

## Context
The agent depends on the validator and needs realistic content in tests without network access to the content repo.

## Options
1. Depend on the content repo's main branch.
2. Pin a release tag; vendor a small snapshot as a test fixture.

## Decision
Option 2, with `scripts/refresh_fixture.py` to update the snapshot deliberately.

## Consequences
- Reproducible builds; schema changes arrive as an explicit version bump.
- The fixture can drift from the content repo until refreshed.

## Alternatives rejected
Option 1 makes builds non-reproducible.
