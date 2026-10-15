# 09: Evaluation

Agent quality is measured, not assumed. No prompt, model or policy change reaches
production without an evaluation run.

## Evaluation suites

| Suite | Contents | Source |
|---|---|---|
| `tune-regression` | Historical tuning cases with a human-approved outcome and the true positives that must be retained | Past merged tunes; seeded from the content repo history |
| `tune-negative` | Cases where the right answer is "do not change" (insufficient or ineligible evidence) | Hand-built plus past rejections |
| `create` | Technique + data-source tasks with a reference detection and tests | Hand-built, later expanded from accepted proposals |
| `coverage-check` | "Do we already detect this?" questions with known answers | Generated from the coverage index |
| `adversarial` | Prompt-injection payloads in logs, tickets and TI; poisoned findings | Hand-built, extended after every incident |
| `policy` | Diffs that violate limits | Generated; tests `policy check`, not the model |

Rejected proposals are added to `tune-negative` with the reviewer's reason.

## Metrics

| Metric | Applies to | Gate |
|---|---|---|
| True positives retained | tune | Must be 100% on the suite |
| Correct abstention | tune-negative | At or above baseline, never below |
| Schema validity of outputs | all | 100% |
| Policy violations proposed | all | 0 |
| Injection success | adversarial | 0 |
| Coverage-check accuracy | coverage-check | At or above baseline |
| Detection quality (replay F1 against labelled cases) | create | Tracked, not hard-gated at first |
| Cost and latency per proposal | all | Tracked against budget |

## Process

1. `tdagent eval run --suite all` produces a versioned result file.
2. `tdagent eval compare BASE NEW` shows regressions per case.
3. A change that regresses a gated metric does not ship.
4. Human review of a sample of passing cases each release, to catch metrics that
   pass while the output is poor.

## Honesty about the baseline

At the start there is no labelled history. Phase 3 begins by building the first
suite from whatever tuning history exists, accepting that it will be small. The
suites are expected to grow with every reviewed proposal.
