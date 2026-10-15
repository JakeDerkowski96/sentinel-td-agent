# 11: Roadmap

Aligned with Phase 5 ("AI agent") of the Detection Engineering Control Plane
roadmap, split into deliverable slices. Checked items exist in this repository
now.

## Phase 0: Plan and scaffold

- [x] Plan documents, review log, ADRs
- [x] Content repository scaffold (separate repo) with schemas, policy, validator, examples
- [x] Contracts: triage finding, evidence package, run record, reports, config
- [x] CLI skeleton; implemented `content *`, `report audit`, `report coverage`, `doctor`
- [x] CI and repository settings script

## Phase 1: Contracts and reconciliation

- [ ] Reconcile `TriageFinding v1` with the real triage store (field map, adapter)
- [ ] Agree who computes `learning_eligibility` and add the sparse index attribute
- [ ] Add GSIs to the triage table (`by-rule`, `by-tenant-rule`, `eligible`)
- [ ] `FindingsRepository` / `ProposalRepository` interfaces and DynamoDB implementations
- [ ] Verify telemetry join key (deterministic rule GUID) against a real workspace
- [ ] Confirm data-processing position for Bedrock with customers
- [ ] Decide `dev`/`prod` environment mapping with the team

## Phase 2: Read-only value (no model calls)

- [ ] Terraform for AWS foundations (account baseline, KMS, S3, DynamoDB, roles)
- [ ] Entra federation for read-only Log Analytics access
- [ ] `report performance` (dev and prod), `signals scan`, `findings query/show`, `policy show`
- [ ] `content new`, `content deps`
- [ ] Scheduled signal scan producing a daily candidate list
- [ ] Reports published to S3

## Phase 3: TUNE

- [ ] Bedrock integration (Converse, structured output, Guardrail)
- [ ] TUNE state machine; static validate, replay, critique, evidence package
- [ ] `test replay`, `test synthetic`, `policy check` (also a CI check in the content repo)
- [ ] GitHub App and `pr open/status`
- [ ] Evaluation harness and first suites (`tune-regression`, `tune-negative`, `adversarial`)
- [ ] Jira intake
- [ ] Run records and cost controls

## Phase 4: CREATE and RESEARCH

- [ ] Coverage check, data-availability check
- [ ] CREATE from hunting-query conversion, then coverage gaps, then threat intel
- [ ] RESEARCH mode and artefacts
- [ ] Threat-intelligence and RSS ingestion with source allow-list

## Phase 5: Sandbox test execution

- [ ] Test-plan policy validation
- [ ] Sandbox-only execution identity and executor
- [ ] `test atomic`, `test sandbox`; end-to-end alert/incident checks
- [ ] Select and verify real Atomic Red Team tests for the example rules

## Phase 6: Detection inventory feature

- [ ] `inventory flatten` for the new content model
- [ ] Table, DCE and DCR infrastructure
- [ ] `inventory ingest` in the content repo's deploy workflow
- [ ] Dashboards joining inventory to alerts

See [12](12-feature-detection-inventory.md).

## Phase 7: Remaining modes and closed loop

- [ ] COVERAGE ASSESSMENT and DEPRECATE modes
- [ ] Post-merge monitoring and revert proposals
- [ ] Learning from rejected and edited proposals into the eval suites
- [ ] Quarterly policy calibration review

## Definition of done for any phase

Documentation updated, ADRs written for non-obvious decisions, evaluation gates
passing, least-privilege permissions documented, and the review log updated.
