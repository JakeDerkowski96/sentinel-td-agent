# 05: Data and storage

## Constraint

The existing triage agent already stores its findings in **DynamoDB**. The TD
agent should fit in with that as seamlessly as possible. This document sets out
the storage design on that basis, and then answers the explicit question: *is
there a good enough case to use PostgreSQL instead?*

## What the TD agent stores

| Data | Written by | Read by | Access pattern |
|---|---|---|---|
| Triage findings | Triage agent | TD agent (read-only) | By rule ID, by time, only learning-eligible, by tenant |
| Signals | TD agent | TD agent, reports | By rule ID + signal type, newest first |
| Proposals | TD agent | TD agent, humans, reports | By ID, by rule ID, by status |
| Run records (audit) | TD agent | Humans, reports, evals | By run ID, by time; expire after retention |
| Evaluation results | Eval harness | Humans | By suite + run |
| Content, policy, history | **Git** (not a database) | Everyone | n/a |

Git remains the source of truth for content and policy. The stores hold
operational state only.

## Recommended design: DynamoDB

### Triage findings (existing table, read-only to the TD agent)

The TD agent needs three access paths the triage agent may not have built yet.
Each is a **global secondary index (GSI)** on the existing table. Adding a GSI
does not change the table's primary key or existing items.

| Index | Partition key | Sort key | Purpose |
|---|---|---|---|
| `by-rule` | `detection_rule_id` | `created_time` | All findings for a rule, newest first |
| `by-tenant-rule` | `tenant#detection_rule_id` | `created_time` | Tenant-scoped evidence |
| `eligible` (**sparse**) | `detection_rule_id` | `created_time` | Only findings with `eligible_for_detection_learning = true` |

The sparse index is the key idea: the triage agent (or a small stream-triggered
function) sets an attribute `eligible_gsi_pk` **only** on findings that satisfy
the learning gate. DynamoDB indexes only items that have the index key, so the
TD agent literally cannot read an ineligible finding through this index. That
turns the learning gate from a convention into a structural property.

The exact attribute names above are **assumed** (the table schema was not
available while planning). Phase 1 reconciles them with the real shape; see
review-log U4.

### TD agent tables

Separate tables with a `tdagent-` prefix, in the same account and region as the
triage table so IAM, KMS and tooling are shared.

| Table | PK | SK | GSIs | Notes |
|---|---|---|---|---|
| `tdagent-proposals` | `proposal_id` | n/a | `by-rule` (rule_id, created), `by-status` (status, created) | Stores state, PR URL, evidence-package S3 pointer |
| `tdagent-signals` | `rule_id#signal_type` | `window_end` | none | Latest signal per rule is a query with `Limit=1` |
| `tdagent-runs` | `run_id` | n/a | `by-day` (day, started) | **TTL** for retention; large payloads in S3, pointer here |
| `tdagent-eval` | `suite#run_id` | `case_id` | none | |

Large artefacts (evidence packages, replay outputs, model transcripts) go to S3 with
the pointer and a content hash in the item. DynamoDB items stay small.

### Other choices

- **On-demand capacity.** Load is bursty and low; no capacity planning.
- **Point-in-time recovery** on proposals and findings access; **KMS** CMK.
- **IAM scoping.** The TD agent role gets `Query`/`GetItem` on the findings table
  restricted to the `eligible` index ARN (`dynamodb:LeadingKeys` can further
  restrict by tenant), full access to `tdagent-*` tables only.
- **Reporting.** Ad hoc analysis uses DynamoDB export to S3 queried by Athena
  (no impact on live tables, no second operational database).

## Should we use PostgreSQL instead?

**Recommendation: no, not for v1. Use DynamoDB.** The case for Postgres is real
but not yet strong enough to justify a second datastore or a migration of the
triage agent's data. The triggers below say when that should change.

### Comparison

| Concern | DynamoDB | PostgreSQL (e.g. Aurora) | Verdict here |
|---|---|---|---|
| Fit with the existing triage store | Same service, same IAM/KMS, no migration | Second store, or migrate the triage agent | **DynamoDB** (the deciding factor) |
| Our known access patterns | All are key-based (by rule, tenant, time, status) | Handles them, plus anything else | Tie: DynamoDB suffices |
| Ad hoc relational queries and joins | Weak; needs a GSI per question | Strong | Postgres, **but** Athena over exports covers reporting |
| Reporting across findings x rules x performance | Join happens in the report code against Git + Log Analytics | Could join in SQL | Our joins span Git and Log Analytics, which neither database holds |
| Vector / semantic search | Not supported | `pgvector` | Not needed in v1 (see below) |
| Operations | None (serverless) | Instance sizing, patching, connection management | **DynamoDB** |
| Cost at our scale | Pay per request, near zero idle | Always-on instance | **DynamoDB** |
| Schema evolution | Flexible items; versioned attributes | Migrations | Tie |
| Transactions across entities | Limited (TransactWriteItems up to 100 items) | Full | Not a requirement |
| Local development and tests | DynamoDB Local / moto | Any Postgres | Tie |

### Where Postgres would genuinely win

1. **Unforeseen analytical questions** over findings and proposals that do not
   map to a key (for example "which analyst-validated benign findings share a
   trigger condition across more than three rules?"). In DynamoDB each such question
   needs a new GSI or an export-and-query step.
2. **Semantic retrieval co-located with structured filters** (`pgvector`), if
   retrieval over findings, runbooks and rule documentation becomes central.
3. **Strong cross-entity consistency** if proposals, signals and approvals later
   need multi-row invariants.

### Triggers that would change this recommendation

Revisit when **any** of these holds:

- Three or more recurring report questions need a new GSI each, or a person is
  running Athena exports weekly just to answer routine questions.
- Semantic retrieval over findings becomes a core agent step (not just rule
  documentation), and the managed alternatives (Bedrock Knowledge Bases with a
  vector store) are not meeting filtering needs.
- The triage team independently wants relational queries and is willing to
  co-migrate, removing the main cost of the second store.

### Mitigation if Postgres is added later

Keep access behind a small repository interface (`FindingsRepository`,
`ProposalRepository`) in the agent code, so swapping or adding a backend does not
touch the workflow code. The interface is part of Phase 1.

## Semantic retrieval (deferred)

v1 retrieval is exact: by rule ID, technique, table and tenant, all answered from
the coverage index and the findings indexes. Free-text retrieval (runbooks, rule
documentation, past rationale) is deferred. When needed, prefer **Bedrock
Knowledge Bases** (managed, same account) over a self-managed vector database,
because it removes an operational burden and keeps IAM in one place. Embeddings
are an access mechanism only; the system of record stays DynamoDB and Git.
