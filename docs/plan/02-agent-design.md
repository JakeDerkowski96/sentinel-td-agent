# 02: Agent design

## Shape: a deterministic workflow with narrow model steps

Not a free-roaming agent. Each mode is a state machine whose states are either
deterministic code or a single constrained model call with a structured output
schema. Retries, timeouts and human wait states belong to the orchestrator.

## Deterministic versus model

| Deterministic code | Model (Claude via Bedrock) |
|---|---|
| Signal detection against policy thresholds | Hypothesise a root cause from gathered evidence |
| Coverage check ("do we already detect this?") | Draft or modify KQL |
| Evidence retrieval with fixed, parameterised queries | Draft a test plan for custom behaviour |
| Learning-eligibility filtering | Write the rationale and PR description |
| Policy and permission enforcement, path checks | Adversarial critique of its own proposal |
| Validation (static, replay) and result comparison | Summarise threat-intelligence relevance |
| PR creation, labelling, audit logging | |

If a step can be a function, it is a function.

## Modes

| Mode | Purpose | Entry | Allowed tools | Output | Human boundary |
|---|---|---|---|---|---|
| **TUNE** | Change an existing rule | Signal, Jira request | content read, telemetry read, findings read, model, replay | PR modifying the rule, tests, tuning-history | Review + merge; labels for severity decrease, disable, new exception |
| **CREATE** | Add a rule | Coverage gap, new source, TI hypothesis, hunt conversion | as TUNE + data-availability check | PR adding a rule folder | Review + merge; promotion to production is human-only |
| **RESEARCH** | Assess an opportunity | Any signal where a rule is premature | read-only | Research note (artefact), no PR unless requested | None needed; output informs a person |
| **VALIDATE** | Run candidate through validation layers | Called by TUNE/CREATE or manually | replay, sandbox (policy-gated) | Validation report | Sandbox execution needs policy approval of the plan |
| **COVERAGE ASSESSMENT** *(later)* | Find gaps without proposing rules | Schedule, request | read-only | Gap report | None |
| **DEPRECATE** *(later)* | Propose retiring obsolete rules | Silent/redundant signal | read-only | PR setting lifecycle to `retired` | Retirement of a production rule is human-only |

In every mode the agent never deploys.

## TUNE state machine

```text
INTAKE -> SELECT_RULE -> LOAD_CONTEXT -> GATHER_EVIDENCE -> ANALYSE -> PROPOSE
   -> STATIC_VALIDATE -> REPLAY -> CRITIQUE -> TEST_PLAN -> EVIDENCE_PACKAGE
   -> POLICY_CHECK -> OPEN_PR -> AWAIT_REVIEW -> INGEST_OUTCOME
```

| State | Kind | Stop / failure condition |
|---|---|---|
| INTAKE | code | Request unparseable or rule unknown: record and stop |
| SELECT_RULE | code | `agent.tuning` is `locked`: stop (`propose-only` continues but marks the PR) |
| LOAD_CONTEXT | code | Reads rule, metadata, tuning-history, exceptions, playbook |
| GATHER_EVIDENCE | code | Eligible findings below minimum count: stop with "insufficient evidence" |
| ANALYSE | model | Output schema violation: retry once, then stop |
| PROPOSE | model | Must express the change as a diff to allowed paths only |
| STATIC_VALIDATE | code | `dac-validate --strict` fails: one model repair attempt, then stop |
| REPLAY | code | Known true positives lost: reject the proposal, record why |
| CRITIQUE | model | "What true positives could this hide?" objections must each be answered with evidence or the proposal is downgraded |
| TEST_PLAN | model + policy | Plan rejected by policy: proposal continues without sandbox evidence and says so |
| EVIDENCE_PACKAGE | code | Missing required sections: stop |
| POLICY_CHECK | code | Size, path or label violation: stop (exit 4) |
| OPEN_PR | code | Branch/PR creation failure: retry with backoff, then alert |
| AWAIT_REVIEW | orchestrator | Wait for callback; timeout leaves the PR open and notifies |
| INGEST_OUTCOME | code | Merged/rejected/rolled back is written to tuning-history intent and the proposals store |

## CREATE state machine

```text
SIGNAL -> COVERAGE_CHECK -> HYPOTHESIS -> DATA_AVAILABILITY -> DRAFT -> STATIC_VALIDATE
   -> REPLAY -> CRITIQUE -> TEST_PLAN -> EVIDENCE_PACKAGE -> POLICY_CHECK -> OPEN_PR
```

`COVERAGE_CHECK` queries the coverage index. If an enabled rule already covers the
technique on the same data source, the mode converts to TUNE or stops with a
"covered" result. `DATA_AVAILABILITY` verifies tables and columns exist in the
target workspaces; the agent must not invent fields.

## Guardrails on every model call

- Structured output against a JSON Schema in `contracts/`; free text only in
  designated rationale fields.
- Untrusted text is passed as quoted data in labelled fields; the system prompt
  states that such fields are data and never instructions.
- Minimised context: aggregated patterns and redacted samples, not raw logs.
- Tool allow-list per state; the model cannot choose tools outside it.
- Token and cost budget per run; exceeding it stops the run.
- Model ID and region come from configuration (ADR 0005), never code.

## KQL safety

Generated or modified KQL is checked before it runs anywhere: read-only operators
only, a mandatory time bound, a row cap, and an allow-list of tables drawn from
`dataSources` and declared dependencies. Replay queries run with a query timeout
and a cost ceiling.

## Adversarial self-review

The CRITIQUE state exists because a proposal that reduces noise is easy to
justify and hard to verify. A separate model call is asked to find evidence that
would contradict the proposal, and its objections become required reading in the
evidence package. This mirrors the triage agent's contradiction-search discipline.
