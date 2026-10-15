# 01: System architecture

## Component view

```text
 TRIGGERS                       ORCHESTRATION                   TOOLS / STORES
 --------                       -------------                   --------------
 EventBridge schedule --+
 Jira webhook (via SQS)-+--> Step Functions state machine --+--> content repo (git clone, read)
 Manual: tdagent CLI ---+     one per mode (TUNE, CREATE..)  +--> Log Analytics query API (read)
                                       |                     +--> DynamoDB (findings read, runs/proposals rw)
                                       v                     +--> Bedrock Converse API (Claude)
                              Task workers (Lambda /         +--> threat-intel + RSS fetchers
                              Fargate) run tdagent steps     +--> sandbox executor (policy-gated)
                                       |
                                       v
                          GitHub App --> pull request (agent/* branch)
                          S3 --> reports, run records, evidence artefacts
```

The workers run the **same `tdagent` commands** a human can run. One code path
means what the agent does is reproducible from a terminal and testable without AWS.

## Triggers

| Trigger | Mode started | Notes |
|---|---|---|
| Schedule (daily) | `signals scan` -> TUNE per candidate | Bounded by a per-run candidate cap |
| Jira ticket labelled for tuning | TUNE for the named rule | Ticket text is untrusted input |
| New log source detected | RESEARCH / CREATE | From telemetry inventory change |
| Threat-intel item scored relevant | RESEARCH | Produces a hypothesis, not a rule |
| Hunting query flagged `ruleConversion.candidate` | CREATE | |
| Manual CLI | any | Same state machines, run locally with `--dry-run` support |

## Trust zones

```text
 [ UNTRUSTED ]            [ AGENT ZONE (AWS) ]            [ HUMAN-CONTROLLED ]
 logs, incident text,     orchestrator, workers,          content repo main branch,
 TI content, Jira text,   Bedrock calls, stores           policy/, schemas/, CI,
 analyst comments                                         approvals, deployment
        |                       |                                  ^
        +---- sanitised/ ------>+------- PR only -----------------+
              quoted as data
```

Untrusted content is only ever passed to the model as quoted data in a field of a
structured prompt, never as instructions, and the model has no tool that can write
anywhere except through the proposal pipeline.

## Cross-cloud identity

```text
 AWS worker role (IAM) --OIDC federation--> Entra app registration (read-only)
                                              |-> Log Analytics query (per-tenant, via Lighthouse delegation)
 AWS worker role --------GitHub App token---> content repo (branch push + PR only)
 Sandbox executor role --federation--------> sandbox Entra identity (sandbox workspace only)
```

No long-lived secret crosses the boundary. The sandbox identity is reachable only
after the policy-validation step approves a test plan (ADR 0006).

## Environments

| Environment | Purpose | Notes |
|---|---|---|
| Local | Development and dry runs | Offline commands need no cloud |
| AWS dev account | Integration testing | Mock/sandbox Sentinel only |
| AWS prod account | Real signals, real PRs | Separate account from anything that deploys |

## Failure posture

Every state in a workflow has a stop condition and a recorded failure reason. When
evidence is unavailable (a table is empty, a query times out) the agent records the
gap in the evidence package and stops or downgrades the proposal; it does not
proceed on assumptions.
