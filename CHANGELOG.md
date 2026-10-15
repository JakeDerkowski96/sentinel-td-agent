# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Full plan for the Threat Detection agent in `docs/plan/` (vision, architecture, agent design,
  CLI, reports, storage, triage integration, validation and promotion, security, evaluation,
  deployment and operations, roadmap, the detection-inventory feature).
- Review log recording every uncertainty, the options considered and the choice made.
- Architecture decision records.
- JSON Schema contracts: triage finding, proposal evidence package, run record, audit and
  coverage reports, configuration.
- `tdagent` CLI: implemented `content list|show|validate|index`, `report audit`,
  `report coverage` and `doctor`; the rest of the command tree is stubbed with a documented
  exit code and the phase that delivers it.
- Vendored sample content repository for tests, with `scripts/refresh_fixture.py` to update it.
- `scripts/check_links.py` documentation link checker.
- CI workflow with a single gate job; repository settings script.

[Unreleased]: https://github.com/JakeDerkowski96/sentinel-td-agent/commits/main
