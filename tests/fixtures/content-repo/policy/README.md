# Policy

Machine-readable rules that govern how detection content changes. They are
**read by the AI agent and enforced by CI, but not editable by the agent**
(`/policy/` is a forbidden path in `proposal-limits.yaml`).

| File | Purpose |
|---|---|
| `tuning-thresholds.yaml` | When a rule becomes a tuning candidate; what makes a triage finding usable as evidence |
| `proposal-limits.yaml` | What the agent may touch, how big a proposal may be, what needs a human label |
| `lifecycle.yaml` | Lifecycle states and the transitions allowed between them |
| `taxonomy.yaml` | ID prefixes per content type, confidence tiers, domains |

Thresholds live here, not in prompts, so a change to agent behaviour is a
reviewed diff with history.

> **Every numeric value in these files is a starting default, not a measured
> optimum.** Tune them against your own alert volumes before relying on them.
> See `docs/policy.md`.
