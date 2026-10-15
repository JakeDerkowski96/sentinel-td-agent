# DET-ENTRA-0001: analyst playbook

## What fired
A user had at least the threshold number of failed password sign-ins, then a
successful sign-in, inside one query window.

## First checks
1. Is `IsPrivileged` true? If so, treat as higher priority.
2. Compare the success `IPAddress` with `FailedIPs`. The same address for
   failures and the success points to a single client retrying.
3. Check the sign-in's `AppDisplayName`, user agent and location against the
   user's normal pattern.
4. Check for MFA completion on the successful sign-in.

## Likely benign
- A user who forgot their password, then reset or remembered it.
- A client application retrying with a stale cached password.

## Escalate when
- The success comes from an IP never seen for the user, and MFA was not
  satisfied or was satisfied from an unusual device.
- Failures came from many addresses (spray) and the success came from one.
