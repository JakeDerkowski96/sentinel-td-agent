# Troubleshooting

Covers the implemented commands. Symptom, cause, fix.

| Symptom | Cause | Fix |
|---|---|---|
| `does not look like a DaC repository root (no schemas/ directory)` | `--content-repo` points at the wrong folder | Point it at the root of a `sentinel-detection-as-code` checkout |
| Exit code `3`, "planned, not implemented" | The command exists in the plan but not in code yet | Read the phase named in the message; see the roadmap |
| `content validate` exits `1` | The content repo has schema or cross-reference errors | Read the listed codes; each is documented in the content repo's `docs/validation.md` |
| `report coverage` is empty | `--env` filter excludes every rule (for example `--env prod` while all rules are `draft`) | Use `--env all` or check lifecycle states |
| `ModuleNotFoundError: dac_validate` | Dependency not installed | `pip install -e ".[dev]"`; the pinned tag must be reachable |
| `content index` refuses to run | The repository has validation errors | Fix them first; an index built from invalid metadata would look authoritative and be wrong |
| Config not found | Wrong working directory or path | Pass `--config`, or set `TDAGENT_CONFIG` |
