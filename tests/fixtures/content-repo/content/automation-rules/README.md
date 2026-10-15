# automation-rules

Folder per item, named exactly its ID (`AUTO-<NAME>-<nnn>`), containing:

- `manifest.yaml` (schema `content-manifest`, `type` set accordingly)
- the definition file named by `definitionFile` (exported ARM/JSON)

Automation rules can close incidents or change severity, so they are human-authored: the AI agent cannot modify this directory.

No examples are shipped yet. Add one with a real exported definition from a
non-production workspace, scrubbed of identifiers.
