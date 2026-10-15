"""Audit report: is the content healthy, owned, tested and compliant?

Required permissions: none (derived from a local checkout).
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Any

from ..content_repo import ContentRepo

NOT_REVIEWED_DAYS = 180
EXPIRING_SOON_DAYS = 30


def _days_until(value: Any, today: date) -> int | None:
    try:
        return (date.fromisoformat(str(value)) - today).days
    except ValueError:
        return None


def build_audit(
    content: ContentRepo, *, env: str, include_retired: bool, now: datetime
) -> dict[str, Any]:
    """Build the audit report for the rules in ``env``.

    Validation findings are repository-wide regardless of ``env``; everything else
    is limited to the selected rules so a prod audit is not cluttered by drafts.
    """
    today = now.date()
    rules = content.rules_in(env, include_retired=include_retired)
    index = content.index()

    missing_owner: list[str] = []
    not_reviewed: list[str] = []
    no_tests: list[str] = []
    no_playbook: list[str] = []
    experimental_prod: list[str] = []
    exc_expired: list[dict[str, Any]] = []
    exc_soon: list[dict[str, Any]] = []
    controls: Counter[str] = Counter()
    by_lifecycle: Counter[str] = Counter()

    for bundle in rules:
        meta, rid = bundle.metadata, bundle.rule_id
        by_lifecycle[str(meta.get("lifecycle"))] += 1
        controls[str(meta.get("agent", {}).get("tuning"))] += 1
        if not meta.get("owner"):
            missing_owner.append(rid)
        # A rule never reviewed is aged from its creation date.
        until = _days_until(meta.get("lastReviewed") or meta.get("created"), today)
        if until is not None and -until > NOT_REVIEWED_DAYS:
            not_reviewed.append(rid)
        if not bundle.tests:
            no_tests.append(rid)
        playbook = meta.get("documentation", {}).get("analystPlaybook")
        if not playbook or not (bundle.directory / playbook).exists():
            no_playbook.append(rid)
        if (
            meta.get("lifecycle") in {"approved", "production"}
            and meta.get("confidenceTier") == "Experimental"
        ):
            experimental_prod.append(rid)
        for exc in (bundle.exceptions or {}).get("exceptions", []):
            left = _days_until(exc.get("expires"), today)
            entry = {"rule": rid, "id": exc.get("id"), "expires": exc.get("expires")}
            if left is not None and left < 0:
                exc_expired.append(entry)
            elif left is not None and left <= EXPIRING_SOON_DAYS:
                exc_soon.append(entry)

    in_scope = {b.rule_id for b in rules}
    ov_expired: list[dict[str, Any]] = []
    ov_soon: list[dict[str, Any]] = []
    for _path, data in content.repo.overrides:
        if data.get("rule") not in in_scope:
            continue
        left = _days_until(data.get("expires"), today) if data.get("expires") else None
        entry = {
            "tenant": data.get("tenant"),
            "rule": data.get("rule"),
            "expires": data.get("expires"),
        }
        if left is not None and left < 0:
            ov_expired.append(entry)
        elif left is not None and left <= EXPIRING_SOON_DAYS:
            ov_soon.append(entry)

    errors = sum(1 for i in content.issues if i.severity.value == "error")
    return {
        "reportVersion": 1,
        "kind": "audit",
        "generatedAt": now.isoformat(),
        "contentRepoRef": content.ref,
        "parameters": {"env": env, "includeRetired": include_retired},
        "summary": {
            "rules": len(rules),
            "content": len(content.repo.manifests),
            "errors": errors,
            "warnings": len(content.issues) - errors,
            "byLifecycle": dict(sorted(by_lifecycle.items())),
        },
        "validation": [
            {"severity": i.severity.value, "code": i.code, "path": i.path, "message": i.message}
            for i in content.issues
        ],
        "ownership": {
            "missingOwner": sorted(missing_owner),
            "notReviewed": {"thresholdDays": NOT_REVIEWED_DAYS, "rules": sorted(not_reviewed)},
        },
        "maturity": {
            "noTests": sorted(no_tests),
            "noPlaybook": sorted(no_playbook),
            "experimentalInProduction": sorted(experimental_prod),
        },
        "exceptions": {"expired": exc_expired, "expiringSoon": exc_soon},
        "overrides": {"expired": ov_expired, "expiringSoon": ov_soon},
        "agentControls": dict(sorted(controls.items())),
        "unusedContent": list(index.get("unusedContent", [])),
    }
