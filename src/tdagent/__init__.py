"""tdagent: CLI for the Sentinel Threat Detection agent.

Offline commands (content management, audit and coverage reports) work against a
local checkout of the content repository. Commands that need AWS, Bedrock or a
Sentinel workspace are documented in docs/plan/03-cli.md and stubbed here.

Required permissions: none for the implemented commands (local file reads only).
"""

__version__ = "0.1.0"
