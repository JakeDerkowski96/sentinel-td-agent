# Configuration reference

`tdagent` reads YAML configuration. Lookup order: `--config PATH`, then
`$TDAGENT_CONFIG`, then `./tdagent.yaml`. A missing file is not an error for
offline commands; defaults apply.

Never put credentials in this file. Credentials come from the environment or the
platform's identity (IAM role, federation); see the security plan.

```yaml
content_repo: ../sentinel-detection-as-code   # path to a checkout

bedrock:                      # planned (Phase 3)
  region: us-east-1
  model_id: ""                # set per environment; never hard-coded in code
  guardrail_id: ""

stores:                       # planned (Phase 1)
  findings_table: ""
  proposals_table: tdagent-proposals
  runs_table: tdagent-runs
  artefacts_bucket: ""

budgets:                      # planned (Phase 3)
  max_cost_per_run_usd: 5.0
  max_candidates_per_scan: 10
```

| Key | Used by | Default |
|---|---|---|
| `content_repo` | all content and report commands | current directory |
| `bedrock.*` | `propose *`, `eval *` | unset |
| `stores.*` | `findings *`, `propose *`, `signals *` | unset |
| `budgets.*` | `propose *` | see above |

Environment variable overrides: `TDAGENT_CONFIG`, `TDAGENT_CONTENT_REPO`.
The schema is `contracts/agent-config.v1.schema.json`; an example is
`config/tdagent.example.yaml`.
