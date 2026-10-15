# 03: CLI reference

`tdagent` is the single interface to the agent. The orchestrator invokes the same
commands a person runs, so behaviour is reproducible and testable offline.

## Conventions

| Item | Behaviour |
|---|---|
| Global flags | `--config PATH`, `--content-repo PATH`, `-v/--verbose`, `--version` |
| State-changing commands | Support `--dry-run`: report exactly what would change, change nothing |
| Output | `--format md|json` on reports; results to stdout, diagnostics to stderr |
| `--output FILE` | Write the result to a file instead of stdout |
| Exit codes | `0` ok; `1` findings/failure; `2` usage or runtime error; `3` planned, not implemented; `4` denied by policy |

Config lookup order: `--config`, then `$TDAGENT_CONFIG`, then `./tdagent.yaml`.
`--content-repo` overrides `content_repo` in config. See [configuration](../configuration.md).

## Command tree and status

Legend: **implemented** works now and offline; *planned (Phase N)* prints what it will do and exits 3.

### content: manage detection content

| Command | Status | Purpose |
|---|---|---|
| `content validate [--strict]` | implemented | Schema + cross-reference validation (wraps `dac-validate`) |
| `content index [--out DIR] [--dry-run]` | implemented | Build the coverage/dependency index |
| `content list [--type T] [--lifecycle S] [--env E]` | implemented | List rules/content with key attributes |
| `content show ID` | implemented | Show a rule or content item with its metadata, history and dependencies |
| `content new --type T --domain D --name N` | *planned (Phase 2)* | Scaffold a new rule/content folder from templates |
| `content deps ID` | *planned (Phase 2)* | Dependency graph: what ID needs and what needs ID |
| `content set-lifecycle ID STATE` | *planned (Phase 3)* | Propose a lifecycle transition as a PR (policy-checked) |
| `content set-agent-mode ID MODE` | *planned (Phase 3)* | Change `agent.tuning` for a rule (human-labelled PR) |
| `content retire ID` | *planned (Phase 7)* | Propose retirement |

### report: generate reports

| Command | Status | Purpose |
|---|---|---|
| `report audit [--format] [--output]` | implemented | Content integrity, ownership, exceptions, test and playbook gaps |
| `report coverage [--env dev|prod|all] [--techniques FILE]` | implemented | Technique, tactic and data-source coverage; gaps |
| `report performance --env dev|prod|all [--tenant T] [--window P30D]` | *planned (Phase 2)* | Alert volume, false-positive rate, health, cost per rule |

See [reports](04-reports.md).

### signals and findings

| Command | Status | Purpose |
|---|---|---|
| `signals scan [--tenant T]` | *planned (Phase 2)* | Evaluate `tuning-thresholds.yaml`; list tuning candidates |
| `findings query --rule ID [--eligible-only]` | *planned (Phase 2)* | Query triage findings from the shared store |
| `findings show ID` | *planned (Phase 2)* | Show one finding |

### propose: run an agent mode

| Command | Status | Purpose |
|---|---|---|
| `propose tune --rule ID` | *planned (Phase 3)* | TUNE state machine |
| `propose create --from {hunt,ti,gap,request} REF` | *planned (Phase 4)* | CREATE state machine |
| `propose research --topic TEXT` | *planned (Phase 4)* | RESEARCH |
| `propose coverage-assess [--scope S]` | *planned (Phase 7)* | COVERAGE ASSESSMENT |
| `propose deprecate --rule ID` | *planned (Phase 7)* | DEPRECATE |

All `propose` commands accept `--dry-run` (run to the end, open no PR) and
`--max-cost USD`.

### test: validation layers

| Command | Status | Purpose |
|---|---|---|
| `test replay --rule ID [--window P30D] [--tenant T]` | *planned (Phase 3)* | Replay current vs candidate over history |
| `test synthetic --rule ID` | *planned (Phase 3)* | Run fixture-based cases |
| `test atomic --rule ID` | *planned (Phase 5)* | Atomic Red Team via the sandbox identity |
| `test sandbox --rule ID` | *planned (Phase 5)* | End-to-end alert/incident validation |

### pr, policy, eval, inventory, doctor

| Command | Status | Purpose |
|---|---|---|
| `pr open --proposal ID` | *planned (Phase 3)* | Open the PR for a stored proposal |
| `pr status --proposal ID` | *planned (Phase 3)* | Review state and CI result |
| `policy show` | *planned (Phase 2)* | Print effective policy |
| `policy check --diff REF` | *planned (Phase 3)* | Check a diff against `proposal-limits.yaml` (also run in CI) |
| `eval run [--suite S]` | *planned (Phase 3)* | Run the evaluation suite |
| `eval compare A B` | *planned (Phase 3)* | Compare two eval runs |
| `inventory flatten` / `inventory ingest` | *planned (Phase 6)* | See [the inventory feature](12-feature-detection-inventory.md) |
| `doctor` | implemented (local checks) | Check config, content repo, validator version; cloud checks added per phase |

## Required permissions per command

| Commands | Permission |
|---|---|
| implemented commands | Read access to the local content checkout |
| `report performance`, `signals`, `test replay` | Log Analytics Reader on target workspaces |
| `findings *` | DynamoDB read on the triage findings table |
| `propose *` | Bedrock `InvokeModel`, DynamoDB read/write on agent tables |
| `pr *` | GitHub App token (see security plan) |
| `test atomic`, `test sandbox` | Sandbox-only identity |
| `inventory ingest` | Monitoring Metrics Publisher on the DCR |
