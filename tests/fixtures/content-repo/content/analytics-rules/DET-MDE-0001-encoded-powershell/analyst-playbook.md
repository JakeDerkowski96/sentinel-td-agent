# DET-MDE-0001: analyst playbook

## What fired
`powershell.exe` or `pwsh.exe` started with `-enc`, `-ec` or `-encodedcommand`
followed by a long base64-looking payload.

## First checks
1. Decode the payload (base64, UTF-16LE) and read it.
2. Look at `InitiatingProcessFileName`: an office application, browser or
   script host as parent is more suspicious than a management agent.
3. Check whether the same host ran other unusual processes in the same period.

## Likely benign
- Endpoint management or deployment tooling that passes encoded commands.

## Escalate when
- The decoded content downloads or executes remote content, or disables security tooling.
- The parent process is unexpected for the user or device.
