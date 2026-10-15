# 06: Working with the existing triage agent

The triage agent investigates incidents and writes findings. The TD agent consumes
validated findings as one input among several. They are deliberately separate
(ADR 0003 in the decision log): triage says **what happened**, TD decides **what
that implies for detection logic**.

## Contract

`contracts/triage-finding.v1.schema.json` is the proposed shape, derived from the
design notes. It separates facts, inferences, knowledge-base guidance,
threat-intelligence and assumptions, carries **two** confidence dimensions
(`assessment_confidence`, `evidence_completeness`), and a `learning_eligibility`
block.

**Important:** the real triage agent already has a stored shape. This contract is
a *target*, not a claim about what exists. Phase 1 begins with a field-by-field
reconciliation (review-log U4):

| Outcome | Action |
|---|---|
| Field exists with the same meaning | Map it |
| Field exists with a different name | Add an adapter in the TD agent's read layer |
| Field missing | Agree with the triage team whether to add it or derive it |
| Triage field the TD agent does not need | Ignore it |

The TD agent reads through an adapter so the two schemas can evolve
independently.

## What the TD agent requires from a finding

| Need | Why |
|---|---|
| Rule ID(s) and tenant | Attribute evidence to the right rule and scope |
| Verdict and `analyst_validated` | Only validated conclusions may drive tuning |
| `evidence_completeness`, `assessment_confidence` | Do not learn from confident-but-incomplete work |
| Trigger condition / distinguishing features | The raw material for an exclusion or threshold |
| Entities (redacted/hashed where possible) | Pattern detection without raw identifiers in prompts |
| `missing_evidence` with reason and impact | Understand blind spots |

## The learning gate, structurally

`learning_eligibility.eligible_for_detection_learning` is true only when the
analyst validated the verdict **and** evidence completeness and confidence meet the
thresholds in `policy/tuning-thresholds.yaml`. Who computes the flag, and when, is
open (review-log U4); the preferred answer is the triage side, writing the sparse
index attribute described in [05](05-data-and-storage.md), so ineligible findings
are unreadable by the TD agent rather than merely filtered out.

## Flow back to triage

The relationship is two-way, and the second direction is cheap and valuable:

- The content repository's `analyst-playbook.md` per rule is guidance the triage
  agent can read when investigating that rule's incidents.
- When a tune merges, the rule's `tuning-history.yaml` entry explains what
  changed; triage can retrieve it so a later incident is judged against the
  current logic, not the old.

Neither requires new infrastructure: the triage agent reads the content repo
(or its CI artefacts) read-only.

## Safety property

If the triage agent is wrong, the damage is limited to: a finding that is not
validated (ignored), or a validated-but-wrong finding (one human mistake, caught by
the replay and review stages). A systematically wrong triage agent cannot silently
degrade detections, because the gate requires human validation.
