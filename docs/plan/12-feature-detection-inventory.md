# 12: Planned feature: detection rule inventory in Log Analytics

**Status: planned (Phase 6).** Not implemented. This design adapts an earlier
pipeline pattern to the new content model.

## What it is

On every merge to `main` (and after production deployment), flatten every rule in
the content repository into one row and ingest the rows into a Log Analytics
custom table, so rule metadata can be queried and joined to alerts, incidents and
health data **in KQL**, next to the telemetry it describes.

## Why

- Performance and coverage questions become KQL: "alerts per rule by lifecycle",
  "rules with no tests that generate the most incidents", "techniques covered only
  by Experimental rules".
- Gives dashboards and the CISO reporting a single queryable inventory, without
  each consumer reading Git.
- Lets the performance report join metadata to telemetry inside the workspace.

## Design

```text
content repo (merge to main / after prod deploy)
   -> tdagent inventory flatten          one JSON row per rule
   -> tdagent inventory ingest           Logs Ingestion API (token via OIDC)
   -> DCE -> DCR (ingestion-time transform casts types)
   -> DetectionInventory_CL custom table
```

Deployment order for the infrastructure matters: **table, then DCE, then DCR**
(the DCR references both). Parameters only; no names, workspaces or locations are
hard-coded, so the same templates serve every tenant.

## Row shape (proposed)

Columns are named after the final table columns so the transform only casts types.

| Group | Columns |
|---|---|
| Identity | `RuleId`, `DisplayName`, `Kind`, `FolderPath`, `ContentRef` (commit SHA) |
| Deployable | `Severity`, `Enabled`, `Query`, `QueryFrequency`, `QueryPeriod`, `TriggerOperator`, `TriggerThreshold`, `SuppressionEnabled`, `SuppressionDuration` |
| Structured (`dynamic`) | `Tactics`, `Techniques`, `EntityMappings`, `CustomDetails`, `IncidentConfiguration`, `AlertDetailsOverride`, `EventGroupingSettings` |
| Metadata | `Lifecycle`, `ConfidenceTier`, `Owner`, `Package`, `Scope`, `AgentTuning`, `DataSourceTables`, `Dependencies` |
| Derived flags | `HasEntityMappings`, `HasCustomDetails`, `HasIncidentGrouping`, `HasAlertDetailsOverride`, `HasEventGrouping`, `HasSuppression`, `HasTests`, `HasPlaybook`, `HasExceptions`, `HistoryEntries` |
| Freshness | `RuleLastModified`, `MetadataLastModified` (last git commit touching each file) |

`TimeGenerated` is the ingestion time. Each ingestion run appends a snapshot; the
latest state is `DetectionInventory_CL | summarize arg_max(TimeGenerated, *) by RuleId`.

## What differs from the earlier pattern

| Earlier pattern | New design | Why |
|---|---|---|
| Path-derived `environment` (`prod/dev/archived`) and `standard` | `Lifecycle` from `metadata.yaml` | No environment folders (content repo ADR 0004) |
| Sidecar `dataSourceDependency`, `confidenceTier` | Same ideas, richer `metadata.yaml` | Already part of the content model |
| Rows read from ARM templates | Rows read from `rule.yaml` + `metadata.yaml` | ARM is generated, not the source |
| One workspace | One central workspace or per-tenant, to be decided | Open (review-log U22) |

## Permissions

| Role | Scope | Reason |
|---|---|---|
| Monitoring Metrics Publisher | The inventory DCR | Ingest rows (CI identity, federated) |
| Contributor-equivalent for infra deployment (narrower role to be identified) | The resource group holding table/DCE/DCR | One-time infrastructure deployment |

## Open items

- Single central inventory workspace versus per-tenant ingestion.
- Retention for the table (inherit workspace retention initially).
- Whether `Query` should be ingested in full (useful, large) or hashed with a length.
