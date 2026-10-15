# sentinel-td-agent

The plan, contracts and CLI for an AI **Threat Detection (TD) agent** that proposes
Microsoft Sentinel detection changes as pull requests. Claude runs on Amazon
Bedrock; the detections live in a separate Git repository,
[`sentinel-detection-as-code`](https://github.com/JakeDerkowski96/sentinel-detection-as-code).

> **Status: plan plus scaffold.** The plan in [`docs/plan/`](docs/plan/) is complete.
> The CLI implements offline content management and the audit and coverage
> reports; everything that needs AWS, Bedrock or a Sentinel workspace is a
> documented, stubbed command. See the [roadmap](docs/plan/11-roadmap.md).

## Purpose

Detection quality decays: rules get noisy, data sources change, new techniques
appear, and tuning is slow manual work. This agent turns signals (tuning
thresholds, analyst requests, coverage gaps, threat intelligence, validated triage
findings) into **reviewed, tested, evidence-backed pull requests**, and gives the
team reports on audit status, coverage and rule performance.

The guiding rule: **AI proposes. Git records. CI validates. Deployment automation
executes. Humans authorise consequential changes.** The agent never deploys.

## What's here

| Path | Contents |
|---|---|
| `docs/plan/` | The full plan: vision, architecture, agent design, CLI, reports, storage, security, evaluation, roadmap |
| `docs/review-log.md` | Every uncertainty hit while writing this, the options, and why each choice was made. **Read this first when reviewing.** |
| `docs/decisions/` | Architecture decision records |
| `contracts/` | JSON Schemas for data crossing a boundary (triage finding, evidence package, run record, reports, config) |
| `config/` | Example configuration |
| `src/tdagent/` | The `tdagent` CLI |
| `tests/` | Tests, including a vendored sample content repository |
| `scripts/` | Operational scripts |

## Prerequisites

- Python 3.11 or later
- Git
- A checkout of [`sentinel-detection-as-code`](https://github.com/JakeDerkowski96/sentinel-detection-as-code) (or its path in config)
- For planned features only: an AWS account with Bedrock model access, and Azure access via federation (see [security](docs/plan/08-security-and-permissions.md))

## Required permissions

| Role / permission | Scope | Reason |
|---|---|---|
| None | n/a | The implemented commands (`content *`, `report audit`, `report coverage`, `doctor`) read a local checkout only |
| *Planned* Bedrock `InvokeModel` on the configured model | AWS account | Agent reasoning steps |
| *Planned* Log Analytics Reader | Per-tenant workspace | Signals, replay, performance report |
| *Planned* GitHub App: contents write on `agent/*`, pull requests write | Content repository | Open proposals |

The full least-privilege matrix is in [`docs/plan/08-security-and-permissions.md`](docs/plan/08-security-and-permissions.md).

## Usage

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"

tdagent --content-repo ../sentinel-detection-as-code content list
tdagent --content-repo ../sentinel-detection-as-code report coverage --env all --format md
tdagent --content-repo ../sentinel-detection-as-code report audit --format json
tdagent propose tune --rule DET-LINUX-0001      # planned: prints what it will do, exits 3
```

Exit codes: `0` ok, `1` findings or failure, `2` usage or runtime error,
`3` command is planned but not implemented, `4` denied by policy.

## Documentation

Start at [`docs/README.md`](docs/README.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Conventional Commits, squash merge,
protected `main`.

## License

MIT. See [`LICENSE`](LICENSE).
