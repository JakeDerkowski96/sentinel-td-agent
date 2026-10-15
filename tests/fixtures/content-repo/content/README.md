# content/

Everything that deploys to Sentinel, grouped by type. Each item has a stable ID;
see [`docs/conventions.md`](../docs/conventions.md) and
[`docs/content-model.md`](../docs/content-model.md).

| Directory | Holds |
|---|---|
| `analytics-rules/` | One folder per rule, `<ID>-<slug>/` |
| `functions/` | Workspace functions (`FUNC-...`) |
| `parsers/` | Parser functions (`PARSER-...`) |
| `watchlists/` | Watchlists (`WL-...`) |
| `automation-rules/` | Automation rules (`AUTO-...`); human-authored |
| `playbooks/` | Playbooks (`PB-...`); human-authored |
| `workbooks/` | Workbooks (`WB-...`) |
| `hunting-queries/` | Hunting queries (`HUNT-...`), some flagged as rule candidates |
| `packages/` | Groups that deploy together (`PKG-...`) |
