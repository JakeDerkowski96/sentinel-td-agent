# analytics-rules/

One folder per rule: `<ID>-<slug>/`. See
[`docs/content-model.md`](../../docs/content-model.md) for the file set.

To add a rule:

1. Pick the next number for its domain (`DET-<DOMAIN>-<nnnn>`).
2. Create `rule.yaml`, `query.kql`, `metadata.yaml`, `tuning-history.yaml` with a
   `create` entry.
3. Declare every function, parser and watchlist the query calls.
4. Run `dac-validate validate --strict`.
