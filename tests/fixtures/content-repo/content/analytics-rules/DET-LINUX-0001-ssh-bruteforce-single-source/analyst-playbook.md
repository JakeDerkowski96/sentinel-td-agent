# DET-LINUX-0001: analyst playbook

## What fired
One source IP produced at least the threshold number of failed SSH password
attempts against a single host in the window.

## First checks
1. Is the source IP internal, a known scanner, or a known jump host?
2. Was there an `Accepted` login from the same source after the failures
   (query `SyslogSshdAuth()` for that host and source)?
3. Is the host expected to expose SSH to the internet?

## Likely benign
- Authorised vulnerability scanning.
- Automation with an out-of-date credential.

## Escalate when
- A successful login follows the failures from the same source.
- The target user is a privileged account.
