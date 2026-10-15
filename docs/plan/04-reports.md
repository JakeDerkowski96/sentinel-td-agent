# 04: Reports

Three report families. All are **derived**: from the content repository and,
for performance, from Sentinel telemetry. Reports are never hand-maintained and
the outputs are versioned JSON (`contracts/report-*.v1.schema.json`) plus rendered
Markdown.

## Environments: what "dev" and "prod" mean

The repository has no `dev/` or `prod/` folders (ADR 0004 in the content repo).
Environment is derived from the lifecycle state:

| `--env` | Lifecycle states included | Meaning |
|---|---|---|
| `dev` | `draft`, `validated`, `sandbox-passed` | Not yet deployed to production tenants |
| `prod` | `canary`, `approved`, `production` | Deployed to production tenants (canary at reduced severity) |
| `all` | all except `retired` | Everything live or in progress |

`--include-retired` adds retired content. This mapping is an assumption; see
review-log U9.

## 1. Audit report (implemented)

**Question answered:** is the content healthy, owned, tested and compliant?

| Section | Source | Flags |
|---|---|---|
| Validation | `dac-validate` output | any error |
| Ownership and review | `metadata.owner`, `lastReviewed` | no owner; not reviewed in 180 days |
| Maturity gaps | tests, playbook, history | no tests; no playbook; Experimental tier in production |
| Exceptions | `exceptions.yaml` | expired; expiring within 30 days |
| Overrides | `tenants/overrides` | expired; expiring within 30 days |
| Agent controls | `agent.tuning` | counts of `allowed`, `propose-only`, `locked` |
| Unused content | index `unusedContent` | functions/parsers/watchlists nothing depends on |

Later phases add: git-derived change history and SentinelAudit deployment events.

## 2. Coverage report (implemented)

**Question answered:** what do we detect, on which data, and where are the gaps?

| Section | Source |
|---|---|
| Summary | counts by lifecycle, severity, tier |
| Technique coverage | techniques -> rules (with lifecycle, enabled) |
| Tactic coverage | tactics -> rules |
| Data-source coverage | tables -> rules |
| Weak coverage | techniques covered only by non-production or disabled rules |
| Uncovered techniques of interest | from `--techniques FILE` (one technique per line) |
| Conversion candidates | hunting queries flagged `ruleConversion.candidate` |
| Tenant capability gaps *(planned)* | rules whose `requirements` tables are missing per tenant |

Coverage here means **declared** coverage. It says a rule claims a technique, not
that it fires on it. The performance report and test results are what show whether
it works; the report states this limitation in its header.

## 3. Performance report (planned, Phase 2)

**Question answered:** how is each rule behaving in practice, in dev (sandbox) and
prod (per tenant)?

| Metric | Definition | Source |
|---|---|---|
| Alerts | Count in window | `SecurityAlert` |
| Incidents | Incidents created from the rule | `SecurityIncident` |
| Closure mix | True positive / benign positive / false positive / undetermined | `SecurityIncident.Classification` |
| False-positive rate | validated benign / (validated benign + validated true), only over classified incidents | derived; reported with the classified fraction |
| Volume trend | Window vs previous window | derived |
| Execution health | Failures, delays, partial results | `SentinelHealth` |
| Query cost | Duration/data scanned where available | query logs where enabled |
| Silent-rule flag | Zero alerts while source tables ingest | derived |
| Triage-finding eligible count | Eligible findings referencing the rule | findings store |
| Canary state | Start, duration, volume at reduced severity | metadata + alerts |

Dimensions: rule ID, tenant, severity, lifecycle, `--window`.

### Joining telemetry to Git IDs

Sentinel telemetry identifies a rule by its resource GUID, not `DET-...`. The
proposal (needs the deployment engine to honour it): deploy each rule under a
**deterministic GUID derived from its Git ID** (UUIDv5 over a fixed namespace), so
the join is computable without a lookup table. Fallback: stamp the Git ID into a
custom detail column. Both are documented in review-log U12; the exact telemetry
column names should be verified against a live workspace before implementation.

## Output contract

Each report JSON carries `reportVersion`, `generatedAt`, `contentRepoRef`,
parameters, and its sections, and validates against its schema in `contracts/`.
Markdown is rendered from the JSON, never the other way round.
