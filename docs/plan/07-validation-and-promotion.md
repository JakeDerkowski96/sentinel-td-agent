# 07: Validation and promotion

The agent's job ends at a well-evidenced pull request. Promotion beyond the PR is
the existing pipeline's job and a human's decision.

## Validation layers and who runs them

| Layer | Runs | Agent's role |
|---|---|---|
| 1. Static | In the agent (before opening the PR) and in CI | Runs `dac-validate --strict`; repairs once if it fails |
| 2. Historical replay | In the agent | Runs current vs candidate over representative history; compares |
| 3. Synthetic cases | In the agent | Runs fixture-based cases in the rule's `tests/` |
| 4. Atomic Red Team | Sandbox identity, policy-gated | Selects a test, produces a plan; execution only after policy approval |
| 5. Sandbox end-to-end | Sandbox workspace | Verifies alert, incident, entity mapping, custom details, grouping |
| 6. Production canary | Deployment pipeline | Not the agent; it reads canary results afterwards |
| 7. Human approval | People | Not the agent |

Any failed required layer blocks the proposal. Warnings may proceed but are listed
in the evidence package.

## Replay design

For TUNE, replay compares the **current** and **candidate** logic over the same
data:

| Window | Purpose |
|---|---|
| 7 days | Recent behaviour, closest to current noise |
| 30 days | Seasonality-light baseline |
| 90 days (where retention allows) | Rare true positives |

Measured per window and tenant: alerts (before, after), entities affected,
**known true positives retained** (from validated findings and `tests/`), alerts
removed and their characterisation, and query duration. The pass condition is
policy-defined: `max_coverage_regression_pct: 0` means no known true positive may
be lost.

Replay cannot validate incident pipeline behaviour (grouping, automation); that is
what the sandbox layer is for.

## Evidence package

`contracts/proposal-evidence-package.v1.schema.json`. Required sections:

| Section | Content |
|---|---|
| `proposal` | ID, mode, rule IDs, origin, model ID, run ID |
| `trigger` | The signal or request, with identifiers |
| `evidence` | Findings used (IDs, eligibility), telemetry summaries, with provenance |
| `analysis` | Root cause hypothesis; facts and inferences kept distinct |
| `change` | What changed and why, as a diff summary |
| `validation` | Result of each layer, including warnings and skipped layers with reasons |
| `critique` | Objections raised by the adversarial review and the response to each |
| `risk` | Coverage impact, blind spots introduced, rollback note |
| `policy` | Limits checked, labels required |

The PR body is rendered from the package; the JSON is stored with the proposal.

## Pull request rules (from policy)

Branch `agent/*`, label `ai-proposed`, at most `max_rules_changed_per_pr` rules,
only `allowed_paths`, plus the human labels required by
`require_human_label_for`. CI additionally re-runs `dac-validate` and (Phase 3)
`tdagent policy check` on the diff, so the limits are enforced by something other
than the agent's goodwill.

## Review feedback

| Outcome | Recorded as |
|---|---|
| Merged | `tuning-history.yaml` entry `outcome: merged` (written by the PR itself) and proposal status `merged` |
| Merged with edits | Same, plus a note of what the reviewer changed (a learning signal for evals) |
| Rejected | Proposal status `rejected` with the reviewer's reason; a `rejected` entry is added to `tuning-history.yaml` in a follow-up so the agent does not re-propose the same change |
| Rolled back after merge | `rolled-back` entry; counts against the regression-rate measure |

Rejection reasons are valuable: they feed the evaluation set (see
[09](09-evaluation.md)).

## Rollback

Rollback is a normal revert PR. The agent may *propose* a revert when post-merge
monitoring shows a regression (new silent-rule signal, a missed incident linked
to the rule) but never performs one.
