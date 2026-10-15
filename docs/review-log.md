# Review log

Everything I was unsure about while building these repositories, why, what I
could have done instead, and what I chose. Written for your review.

- **Format:** each entry has *Uncertainty*, *Options*, *Choice and why*, and
  *Follow-up for you*. Numbers (U1...) are referenced from ADRs and plan documents.
- The content repository's ADRs are in [`sentinel-detection-as-code`](https://github.com/JakeDerkowski96/sentinel-detection-as-code/tree/main/docs/decisions).

## Quick view: decisions that need you

| # | Decision for you |
|---|---|
| U1 | What to do with the empty existing `detection-as-code` repo |
| U2 | Confirm the employer is fine with a generic public design |
| U4 | Share the triage table shape; decide who sets the eligibility index attribute |
| U6 | What did `non-standard` rules mean? |
| U9 | Does `canary` count as prod? |
| U12 | Verify telemetry columns and how rules are named when deployed |
| U13 | Tenant scoping rule for evidence |
| U14 | Customer data and Bedrock position |
| U22 | Central versus per-tenant inventory workspace |
| U16 | Test the example KQL before trusting it |

---

## U1: Repository topology, names and the existing placeholder repo

**Uncertainty.** The request mentioned 'a public repo' for the plan and then 'within this repo' a DaC repo, but also asked for a changelog for 'both repos'. A `detection-as-code` repo already exists on the account (created 2026-10-08, README only, default branch `uno`).

**Options considered.**

1. One repo containing both the plan and the DaC content tree.
2. Two new repos: agent/plan and DaC content.
3. Reuse the existing empty `detection-as-code` repo for the DaC content.

**Choice and why.** Two new repos: `sentinel-td-agent` and `sentinel-detection-as-code`. 'Both repos' only makes sense with two, and the permission boundary between agent and content (ADR 0001) needs two. I did not touch the existing placeholder because I could not tell whether it was intended for this, and writing to it would have been irreversible-ish for a public repo.

**Follow-up for you.** Decide whether to rename, archive or delete the empty `detection-as-code` repo. If you wanted the DaC content there, the repo can be renamed or content pushed; nothing else depends on the name.

---

## U2: Publishing a work-adjacent design publicly

**Uncertainty.** The design derives from a work project's Notion pages and notes. Your standards say public repos must contain no employer-derived content, tenant/workspace identifiers or proprietary process, and that portable repos state this in `CONTRIBUTING.md`.

**Options considered.**

1. Reproduce the Notion material closely.
2. Re-author it generically, with fictional tenants and reserved example data.
3. Keep the repos private.

**Choice and why.** Re-authored generically. Tenants are `contoso`; domains are `*.example`; IPs are documentation ranges; no employer names or identifiers appear (I searched for GUIDs and employer terms before committing). `CONTRIBUTING.md` states the portable-repo rule in both repos. You explicitly asked for public, so I did not make them private.

**Follow-up for you.** Before relying on this publicly, confirm your employer is comfortable with the architecture being public even though it is generic. The earlier public gist covers similar ground.

---

## U3: DynamoDB versus PostgreSQL

**Uncertainty.** You asked for Postgres to be documented if there is a good enough case. I had earlier suggested Aurora PostgreSQL before I knew the triage agent uses DynamoDB.

**Options considered.**

1. DynamoDB only.
2. PostgreSQL for the TD agent, reading findings from DynamoDB.
3. Migrate everything to PostgreSQL.

**Choice and why.** DynamoDB (ADR 0002, plan/05). All known access patterns are key-based, integration with the triage store is the stated goal, and a sparse GSI turns the learning gate into a structural property. I am **revising my earlier Aurora recommendation** because the new fact (existing DynamoDB) outweighs it. Plan/05 documents where Postgres genuinely wins and the triggers that should reopen the decision.

**Follow-up for you.** Check whether the triage team has relational query needs I do not know about. If they do, the third trigger in plan/05 may already be met.

---

## U4: The real triage finding shape, and who computes learning eligibility

**Uncertainty.** I never saw the existing triage agent's DynamoDB item shape. `TriageFinding v1` comes from the design notes, not from the real table. Attribute names in the GSI design are assumptions.

**Options considered.**

1. Treat the design-note shape as the truth.
2. Define a target contract and read through an adapter, reconciling in Phase 1.
3. Block until the schema is shared.

**Choice and why.** Target contract plus adapter (plan/06). The contract is labelled 'target'; the first Phase 1 task is a field-by-field reconciliation. This avoids both blocking and pretending to know.

**Follow-up for you.** Share the triage table's item shape and GSIs. Decide whether triage or a stream function sets the `eligible` index attribute.

---

## U5: Rule source format: YAML plus KQL instead of ARM JSON

**Uncertainty.** The prior pattern stored rules as ARM templates with a metadata sidecar. ARM is what Sentinel deploys, but it embeds the query as an escaped string.

**Options considered.**

1. Keep ARM JSON as the source.
2. YAML properties plus a `.kql` file; generate ARM at deploy time.
3. Sentinel's content-hub YAML format.

**Choice and why.** Option 2 (content repo ADR 0001). Readable diffs, real KQL files, and fewer escaping errors for an agent. Cost: a compile step does not exist yet, and existing ARM rules would need a converter.

**Follow-up for you.** Confirm you are happy to adopt a compile-to-ARM step. If not, `rule.yaml` could be replaced by ARM with the same sidecar approach; the validator and index would need small changes.

---

## U6: Lifecycle in metadata, not folder paths

**Uncertainty.** The prior inventory tooling derived `environment` and `standard` from folders (`prod`/`dev`/`archived`, `standard`/`non-standard`). You asked for one folder per rule under `content`.

**Options considered.**

1. Keep environment folders.
2. Flat folders; lifecycle as a metadata field.

**Choice and why.** Flat (content repo ADR 0003 and 0004). Promotion becomes a one-line change and history follows the rule. `standard` versus `non-standard` has no equivalent yet; if it meant something operational it should become a metadata field.

**Follow-up for you.** Tell me what 'non-standard' meant. If it is a real category I will add it to `metadata.yaml`.

---

## U7: Generated coverage index is not committed

**Uncertainty.** An agent benefits from a precomputed index, but committing it creates conflicts and staleness.

**Options considered.**

1. Commit it.
2. Build on demand and publish as a CI artefact.

**Choice and why.** On demand (content repo ADR 0005). One fast offline command before reasoning.

**Follow-up for you.** If cold-start latency matters, publish it from `main` to a release asset or bucket.

---

## U8: CLI language and how much to implement

**Uncertainty.** The control plane's deployment engine was described as PowerShell; the prior inventory scripts were Python; the agent calls Bedrock (boto3). You asked for a plan and scaffold, not a finished agent.

**Options considered.**

1. PowerShell CLI.
2. Python CLI, all commands stubbed.
3. Python CLI with the offline commands implemented and the rest stubbed with exit code 3.

**Choice and why.** Python with the offline commands implemented (`content *`, `report audit`, `report coverage`, `doctor`) and everything needing cloud access stubbed with a clear message (ADR 0007). The offline commands are useful immediately, give the report framework a real test, and exercise the contracts. Stubs exit 3 so automation cannot mistake them for success.

**Follow-up for you.** If you want the deployment engine and the agent CLI in the same language, tell me before Phase 2.

---

## U9: What 'dev' and 'prod' mean for reports

**Uncertainty.** You asked for rule performance reports for both dev and prod. Environments are not folders any more (U6), so 'dev' needs a definition.

**Options considered.**

1. Dev = sandbox workspace telemetry only.
2. Derive from lifecycle states.
3. Both: lifecycle for content reports, workspace for telemetry.

**Choice and why.** Lifecycle-derived for the offline reports: dev = draft/validated/sandbox-passed; prod = canary/approved/production (plan/04). For the performance report the workspace the telemetry comes from is the real environment boundary; that will be added when the report is built.

**Follow-up for you.** Confirm the mapping, in particular whether `canary` counts as prod (I assumed yes, because it runs in production tenants at reduced severity).

---

## U10: Orchestration runtime

**Uncertainty.** Options: Step Functions, Bedrock AgentCore, Bedrock Agents, or plain Lambda chains. No requirement was given.

**Options considered.**

1. Step Functions + Lambda/Fargate.
2. Bedrock AgentCore.
3. Bedrock Agents.

**Choice and why.** Step Functions (ADR 0004): explicit states, retries, human wait states and execution history match the safety properties we want. Workers just run the CLI, so changing the orchestrator later is cheap.

**Follow-up for you.** If your organisation has a standard agent platform, that may override this.

---

## U11: Model selection and API

**Uncertainty.** Which Claude model and which Bedrock API surface to use.

**Options considered.**

1. Hard-code a model.
2. Configuration-driven model ID with the Converse API.

**Choice and why.** Configuration-driven (ADR 0005). I deliberately did not pick a model ID: availability varies by region and account, and changes should be gated by the evaluation suite.

**Follow-up for you.** Choose the model per mode once the evaluation harness exists.

---

## U12: Joining Git rule IDs to Sentinel telemetry

**Uncertainty.** Sentinel alerts and health records identify rules by resource GUID, not `DET-...`. Performance reports must join them. I did not verify the exact telemetry columns against a live workspace.

**Options considered.**

1. Deterministic GUID derived from the Git ID (UUIDv5).
2. Stamp the Git ID into a custom detail.
3. Maintain a mapping table.

**Choice and why.** Proposed deterministic GUID with the custom-detail stamp as a fallback (plan/04). It needs no lookup table. This is a requirement on the (unbuilt) deployment engine.

**Follow-up for you.** Verify the column names (`SecurityAlert`, `SecurityIncident`, `SentinelHealth`) in a real workspace and confirm how the existing deployment names rules.

---

## U13: Tenant scoping of evidence

**Uncertainty.** The design notes say nothing about how far one tenant's evidence may reach. This matters for a multi-tenant operator.

**Options considered.**

1. Global learning from any tenant.
2. Tenant-local only.
3. Tenant-local by default; global needs multi-tenant evidence.

**Choice and why.** The third: evidence from tenant A may justify a change for tenant A only (as an override); a global change needs validated evidence from several tenants. It is a proposal, recorded in the content repo's tenancy doc and the security threat model.

**Follow-up for you.** Confirm. The threshold ('several') needs a number.

---

## U14: Customer data and Bedrock

**Uncertainty.** Whether customer contracts allow telemetry-derived content to be processed by a model in AWS, and where.

**Options considered.**

1. Assume it is fine.
2. Design for minimisation and flag it as a precondition.

**Choice and why.** Flagged as a precondition (plan/08, Phase 1) and designed for minimisation: aggregates, redacted samples, hashed identifiers, Guardrails, no unmanaged prompt logging.

**Follow-up for you.** Check contracts and regions before any production run.

---

## U15: Numeric defaults in policy

**Uncertainty.** Thresholds such as 100 alerts per week or 5 validated findings are invented starting points. No real alert-volume data was available.

**Options considered.**

1. Leave the values blank.
2. Ship plausible defaults clearly marked as uncalibrated.

**Choice and why.** Defaults, marked as uncalibrated in the policy README and `docs/policy.md`, with a calibration procedure. Blank values would make the example fail validation and teach nothing.

**Follow-up for you.** Calibrate against your real alert distribution before enabling any scheduled scan.

---

## U16: What was and was not verified

**Uncertainty.** This is the most important caveat. Nothing was run against Sentinel, Azure, AWS, Bedrock or GitHub Apps.

**Choice and why.** **Verified (run here):** the content repo validator, schemas, example content and its 18 tests; lint, type checks and CI on both repos; contract schemas are valid JSON Schema; the agent CLI's implemented commands against the vendored sample. **Not verified:** that the example KQL runs or produces the intended results (including the regexes and the `_GetWatchlist`/function usage); table and column names; Sentinel's ARM mapping of `rule.yaml`; that entity-mapping identifiers are accepted; DynamoDB design against the real table; telemetry columns; Atomic Red Team test selection (left `pending`); Bedrock behaviour; IAM and federation details.

**Follow-up for you.** Example rules and everything in plan/05, plan/08 and plan/10 should be treated as design, not tested fact. Run the example KQL in a sandbox before trusting it.

---

## U17: Infrastructure as code not scaffolded

**Uncertainty.** Your standards prefer Bicep, with Terraform for multi-cloud. This spans AWS, Entra and GitHub.

**Options considered.**

1. Bicep.
2. Terraform.
3. Defer.

**Choice and why.** Terraform chosen in the plan, but no `infra/` directory yet: an empty IaC folder is worse than none (your standards), and the resource list will change when Phase 1 reconciles the stores.

**Follow-up for you.** Confirm Terraform is acceptable in your environment.

---

## U18: Branch protection, reviews and the GitHub App

**Uncertainty.** Solo maintainer: required approvals cannot be satisfied by the author. The agent's GitHub App does not exist.

**Options considered.**

1. Require approvals.
2. Require PR + status check, no approvals (your standard).
3. No protection.

**Choice and why.** Option 2, scripted (`scripts/apply_repo_settings.sh`), admins not exempt, linear history, conversation resolution. Note CODEOWNERS only enforces review once a second maintainer exists; until then the `validate-gate` check is the control. The App's permissions and branch restriction to `agent/*` are designed (plan/08) but unbuilt.

**Follow-up for you.** Create the GitHub App in Phase 3 and add a ruleset restricting its pushes to `agent/*`.

---

## U19: Notion pages were not updated

**Uncertainty.** The original architecture lives in Notion. I worked from the local export and edited only the local export copies earlier in this session.

**Options considered.**

1. Update Notion via its connector.
2. Leave Notion; the repos are now the more detailed plan.

**Choice and why.** Left Notion alone: writing to a shared workspace was not requested. The Notion pages and these repos now diverge (the repos are more detailed and adjusted for DynamoDB and Bedrock).

**Follow-up for you.** Decide whether Notion links to the repos or is updated. I can push the Control Plane page edits if you want.

---

## U20: Validator dependency and test fixture

**Uncertainty.** The agent depends on the content repo's validator. A tag exists only after the content repo's first release.

**Options considered.**

1. Depend on `main`.
2. Pin a tag; vendor a sample content snapshot for tests.

**Choice and why.** Tagged `v0.1.0` on the content repo, pinned here; sample content vendored under `tests/fixtures` (ADR 0009). The fixture can drift until refreshed.

**Follow-up for you.** Add a scheduled job to check the pin and fixture against the latest content release.

---

## U21: Jira and threat-intelligence integrations

**Uncertainty.** No details were available: ticket format, labels, RSS sources, scoring.

**Options considered.**

1. Invent specifics.
2. Describe the interface and mark details open.

**Choice and why.** Described triggers and trust handling only (plan/01, plan/08). No Jira schema or feed list is invented.

**Follow-up for you.** Provide the ticket template and the feed list when Phase 3 and 4 start.

---

## U22: Scope of the detection-inventory feature

**Uncertainty.** You described `/bak` as reference for an additional feature. I read the scripts and templates but not their live behaviour.

**Options considered.**

1. Implement now.
2. Design now, implement in Phase 6.

**Choice and why.** Designed only (plan/12), adapted to the new content model, with the differences listed. Implementing it needs infrastructure decisions (central versus per-tenant workspace) that are yours.

**Follow-up for you.** Decide the central versus per-tenant question and the table retention.

---

## U23: Deployment engine boundary

**Uncertainty.** The control plane describes a PowerShell deployment engine; the content repo's model assumes it will compile `rule.yaml` to ARM.

**Options considered.**

1. Build it here.
2. Document the contract and leave it out.

**Choice and why.** Left out and documented (content repo architecture doc): it has different permissions and cadence. Requirements it must honour are listed (compile to ARM, deterministic rule GUIDs, canary override at deploy time, tenant overrides).

**Follow-up for you.** Decide when to scope it; it blocks Phase 5 sandbox validation and production canaries.

---

## U24: Windows and OneDrive friction

**Uncertainty.** Minor: the working tree is on OneDrive, causing CRLF warnings and read-only directory attributes that broke test cleanup.

**Options considered.**

1. Ignore.
2. Work around it.

**Choice and why.** Added `.gitattributes` (`eol=lf`) to both repos and made the test fixture copy files only. No behaviour impact.

**Follow-up for you.** Consider keeping git repos out of OneDrive, which can also corrupt `.git` directories.

---
