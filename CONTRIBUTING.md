# Contributing

## Portable-repo rule

This repository contains **generic, independently authored patterns only**. It
must never contain employer-specific detections, tenant, subscription, workspace
or account identifiers, internal architecture or proprietary process. Examples use
fictional names (`contoso`), reserved example domains and documentation IP ranges.

## Workflow

1. Branch from `main`: `<type>/<short-kebab-description>`
   (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `infra`).
2. Commit with [Conventional Commits](https://www.conventionalcommits.org/):
   imperative subject, 72 characters maximum, body explaining *why*.
3. Run `ruff check .`, `ruff format --check .`, `mypy` and `pytest` locally.
4. Open a PR using the template. Squash-merge; delete the branch.

Never commit directly to `main`.

## Changing the plan

A change to behaviour described in `docs/plan/` updates the plan in the same PR. A
change to a decision updates or supersedes its ADR (never delete one) and adds an
entry to `docs/review-log.md` if it resolves or creates an uncertainty.

## Changing a contract

Files in `contracts/` are versioned (`...v1...`). A backwards-compatible addition
(new optional field) stays in `v1`. Anything else creates `v2` alongside `v1`.
