# Decisions

Architecture decision records. Never deleted; superseded ones get a note.

- [0001](0001-two-repositories.md): Two repositories: the agent and the content
- [0002](0002-dynamodb-shared-store.md): DynamoDB as the shared store; PostgreSQL deferred
- [0003](0003-triage-and-td-separate.md): Triage and threat detection are separate agents, joined by a learning gate
- [0004](0004-deterministic-workflow.md): Deterministic workflow with narrow model steps
- [0005](0005-bedrock-converse-config-model.md): Claude via the Bedrock Converse API; model ID in configuration
- [0006](0006-no-deploy-identity.md): The agent holds no deploy or merge identity; sandbox access only after policy approval
- [0007](0007-cli-single-interface.md): The CLI is the single interface; the orchestrator runs the same commands
- [0008](0008-content-repo-owns-policy.md): The content repository owns policy and schemas; the agent reads them
- [0009](0009-pin-validator-vendor-fixture.md): Pin the content validator by tag; vendor a sample content repo for tests
