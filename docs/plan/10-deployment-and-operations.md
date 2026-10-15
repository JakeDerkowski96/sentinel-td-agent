# 10: Deployment and operations

Nothing in this document is deployed yet. It is the plan for Phases 2 onward.

## AWS resources

| Resource | Purpose |
|---|---|
| Dedicated AWS account (per environment) | Isolation from anything that deploys detections |
| Step Functions state machines (one per mode) | Orchestration, retries, wait-for-callback |
| Lambda (short steps) / ECS Fargate (replay, long steps) | Workers running `tdagent` |
| EventBridge Scheduler | Daily signal scan; periodic coverage assessment |
| SQS + API Gateway (webhook) | Jira intake with a dead-letter queue |
| DynamoDB `tdagent-*` tables | Proposals, signals, runs, evals |
| S3 artefacts bucket (KMS, versioned, lifecycle) | Evidence packages, replay outputs, reports, run records |
| Secrets Manager | GitHub App key, Jira credential |
| KMS customer-managed key | Encrypt tables, bucket, logs |
| CloudWatch Logs, metrics, alarms | Operations |
| Bedrock model access + Guardrail | Reasoning |
| IAM roles | See [security](08-security-and-permissions.md) |

## Infrastructure as code

**Terraform**, because this spans AWS and Azure/Entra and GitHub (multi-cloud is the
case where Terraform is preferred over Bicep). Not scaffolded yet; it arrives with
Phase 2 in an `infra/` directory (review-log U17).

## Configuration

Behaviour that changes between environments lives in configuration, not code:
model ID and region, table names, bucket, content repo location, budgets, tenant
selection. Reference: [configuration](../configuration.md).

## Observability

| Signal | Where | Alarm |
|---|---|---|
| Run outcomes (success, stopped, failed) by mode | CloudWatch metric from run records | Failure rate above threshold |
| Cost per run and per day | Metric from token usage | Daily budget breach |
| Model call latency and errors | CloudWatch | Sustained errors |
| Queue age (Jira intake) | SQS metric | Messages older than N minutes |
| PRs open by agent | Content repo query | More than the configured cap open at once |
| Silent agent | Heartbeat from the scheduled scan | No scan in 36 hours |

## Cost controls

Per-run token/cost budget (`--max-cost` and config), concurrency cap on model
calls, candidate cap per scheduled scan, and a daily budget alarm. A run that
exceeds its budget stops and records why.

## Runbooks (to be written as features land)

| Situation | First response |
|---|---|
| Agent opened a bad proposal | Close the PR with a reason (feeds `tune-negative`); check the run record; if the cause is policy, tighten policy |
| Suspected prompt injection | Disable the trigger (EventBridge rule / webhook), preserve the run record, review recent proposals for the source |
| Bedrock throttling | Reduce concurrency; Step Functions retries with backoff |
| Content repo CI failing for agent PRs | Compare validator version pins between repos |
| Cost alarm | Check for a loop in run records; lower the candidate cap |

## Release

Semantic versions, annotated tags, `CHANGELOG.md`. The deployed state machines pin
a released `tdagent` version, and the content repository pins the validator by tag.
