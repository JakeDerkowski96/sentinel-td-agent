# 00: Vision and scope

## Mission

Run detection engineering as a continuous, measurable, human-accountable loop,
with an AI agent doing the investigative and drafting work that is slow for people
and cheap for software, and people keeping every consequential decision.

## Principles

1. **The agent proposes; it never deploys.** Its only write path to anything that
   matters is a pull request in a separate repository it cannot merge to.
2. **Limits are data.** What the agent may touch, how big a change may be and when
   it should act are machine-readable policy in the content repository, editable
   only by humans.
3. **Evidence over assertion.** A proposal carries the signals, findings, replay
   results and test results that justify it, and the reasoning is reproducible
   from the run record.
4. **Deterministic by default.** Code does everything that does not need judgement;
   the model is called for narrow steps with structured outputs.
5. **Do not learn from unvalidated conclusions.** Only analyst-validated,
   evidence-complete triage findings may drive tuning.
6. **Less noise is not better detection.** A tuning proposal must show known true
   positives are retained.
7. **Everything is auditable.** Every run, tool call and model invocation is
   recorded with enough context to explain a proposal months later.

## Actors

| Actor | Role |
|---|---|
| Detection engineer | Owns policy, reviews and merges proposals, authors rules |
| SOC analyst | Files tuning requests, validates triage findings |
| Triage agent (existing) | Investigates incidents, writes `TriageFinding` records |
| **TD agent (this project)** | Detects signals, drafts and tests proposals, opens PRs, produces reports |
| CI | Validates every PR |
| Deployment automation (separate) | Deploys approved content |

## In scope

- Operating modes TUNE, CREATE, RESEARCH, VALIDATE, COVERAGE ASSESSMENT, DEPRECATE.
- A CLI covering content management and audit, coverage and performance reports.
- Reading triage findings, Sentinel telemetry, the content repository, threat
  intelligence and Jira requests.
- Opening PRs with an evidence package.
- Replay validation against historical telemetry; sandbox test execution through a
  policy-controlled identity (later phase).

## Out of scope

- Deploying content to Sentinel (separate deployment engine).
- Triaging incidents (existing triage agent).
- Response actions of any kind: closing incidents, changing severity or owner,
  suppressing alerts, running playbooks.
- Authoring automation rules or playbooks (human-only).
- Replacing analyst judgement on what is benign.

## Success measures

| Measure | Target direction | Notes |
|---|---|---|
| Proposal acceptance rate | Up, but not to 100% | 100% suggests rubber-stamping |
| Post-merge regression rate | Down | Merged tunes later rolled back or found to have lost a true positive |
| Time from signal to PR | Down | Median hours |
| Analyst time per tuning request | Down | Survey plus ticket timestamps |
| Techniques with production coverage | Up | From the coverage report |
| Rules with tests | Up | From the audit report |
| Noise on tuned rules | Down, **only counted if no coverage was lost** | See principle 6 |

## Glossary

- **Signal:** a condition from `policy/tuning-thresholds.yaml` that makes a rule a candidate.
- **Proposal:** a PR plus its evidence package.
- **Finding:** a structured triage result (`TriageFinding`).
- **Learning eligibility:** the gate deciding whether a finding may be used as evidence.
- **Replay:** running candidate logic over historical telemetry.
