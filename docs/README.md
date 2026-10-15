# Documentation index

| Document | Description |
|---|---|
| [review-log.md](review-log.md) | Uncertainties, options considered and choices made while building this. Start here when reviewing |
| [plan/00-vision-and-scope.md](plan/00-vision-and-scope.md) | Mission, principles, scope, non-goals, success measures |
| [plan/01-system-architecture.md](plan/01-system-architecture.md) | Components, triggers, trust zones, cross-cloud identity flow |
| [plan/02-agent-design.md](plan/02-agent-design.md) | Operating modes, workflow state machines, LLM versus deterministic split |
| [plan/03-cli.md](plan/03-cli.md) | Complete command reference with implementation status |
| [plan/04-reports.md](plan/04-reports.md) | Audit, coverage and performance (dev and prod) reports |
| [plan/05-data-and-storage.md](plan/05-data-and-storage.md) | DynamoDB design, and the justification for when Postgres would be worth adding |
| [plan/06-triage-integration.md](plan/06-triage-integration.md) | Working with the existing triage agent |
| [plan/07-validation-and-promotion.md](plan/07-validation-and-promotion.md) | Evidence package, validation layers, review and feedback |
| [plan/08-security-and-permissions.md](plan/08-security-and-permissions.md) | Identities, least-privilege matrix, threat model |
| [plan/09-evaluation.md](plan/09-evaluation.md) | How agent quality is measured and gated |
| [plan/10-deployment-and-operations.md](plan/10-deployment-and-operations.md) | AWS resources, environments, observability, runbooks |
| [plan/11-roadmap.md](plan/11-roadmap.md) | Phased delivery with checklists |
| [plan/12-feature-detection-inventory.md](plan/12-feature-detection-inventory.md) | Planned feature: ingest the rule inventory into Log Analytics |
| [configuration.md](configuration.md) | Configuration file and environment variable reference |
| [troubleshooting.md](troubleshooting.md) | Symptom, cause, fix for the implemented CLI |
| [decisions/](decisions/) | Architecture decision records |

The standard `architecture.md`, `deployment.md` and `operations.md` documents are
covered by `plan/01`, `plan/10` and `plan/10` respectively, because this repository
is at the plan stage and keeps them in one numbered sequence.
