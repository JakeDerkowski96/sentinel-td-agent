#!/usr/bin/env bash
# apply_repo_settings.sh
#
# Purpose:
#   Apply the standard repository settings and `main` branch protection with the
#   GitHub CLI. GitHub's template mechanism does not copy these, and scripting
#   them keeps every repository identical and reviewable.
#
# Required permissions:
#   GitHub: repository admin on the target repository (gh auth login with the
#   `repo` scope). No Azure or AWS access.
#
# Usage:
#   scripts/apply_repo_settings.sh OWNER/REPO [REQUIRED_CHECK]
#   scripts/apply_repo_settings.sh OWNER/REPO validate-gate --dry-run
#   VERBOSE=1 scripts/apply_repo_settings.sh OWNER/REPO validate-gate
#
# Prerequisites: gh authenticated; the required status check must have run at
# least once on the repo (GitHub only offers checks it has seen).
#
# Notes:
#   * A pull request is required, but approvals are deliberately NOT: as a solo maintainer you
#     cannot approve your own PR, which pushes people to disable protection under
#     time pressure. Required status checks are the real control. Enable reviews
#     when a second contributor exists.
#   * Admins are NOT exempt (enforce_admins) so the protection always applies.
#   * Push protection and secret scanning are set best-effort: they are free on
#     public repositories but need Advanced Security on private ones.

set -euo pipefail

REPO="${1:-}"
CHECK="${2:-validate-gate}"
DRY_RUN=0
for arg in "$@"; do [ "$arg" = "--dry-run" ] && DRY_RUN=1; done
[ "$CHECK" = "--dry-run" ] && CHECK="validate-gate"

if [ -z "$REPO" ] || [ "$REPO" = "--dry-run" ]; then
  echo "usage: $0 OWNER/REPO [REQUIRED_CHECK] [--dry-run]" >&2
  exit 2
fi

log() { [ "${VERBOSE:-0}" = "1" ] && echo "[verbose] $*" >&2 || true; }

run() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] $*"
  else
    log "$*"
    "$@"
  fi
}

echo "Applying settings to $REPO (required check: $CHECK, dry-run: $DRY_RUN)"

# Squash-only merges with the PR title and body as the commit message, branches
# deleted on merge, wiki and discussions off (docs live in docs/).
run gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
  -F delete_branch_on_merge=true -F has_wiki=false -F has_discussions=false >/dev/null

# Best effort: not all of these exist on every plan.
run gh api -X PATCH "repos/$REPO" \
  -F 'security_and_analysis[secret_scanning][status]=enabled' \
  -F 'security_and_analysis[secret_scanning_push_protection][status]=enabled' >/dev/null \
  || echo "warning: could not enable secret scanning / push protection (check plan or permissions)" >&2

run gh api -X PUT "repos/$REPO/vulnerability-alerts" >/dev/null \
  || echo "warning: could not enable Dependabot alerts" >&2

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] would PUT branch protection on main requiring status check '$CHECK'"
  exit 0
fi

gh api -X PUT "repos/$REPO/branches/main/protection" --input - >/dev/null <<JSON
{
  "required_status_checks": { "strict": true, "contexts": ["$CHECK"] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
echo "Done."
