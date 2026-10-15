"""Coverage report: what do we detect, on which data, and where are the gaps?

Required permissions: none (derived from a local checkout).

Coverage here is *declared* coverage: a rule claims a technique. It does not prove
the rule fires on it; that needs test results and the performance report.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ..content_repo import ENV_STATES, ContentRepo
from ..errors import TdAgentError

LIMITATIONS = (
    "Declared coverage only: a rule claims a technique, which does not prove it fires on it. "
    "Use test results and the performance report to judge whether coverage works."
)


def read_techniques_file(path: Path) -> list[str]:
    """Read one technique ID per line; blank lines and '#' comments are ignored."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise TdAgentError(f"cannot read techniques file {path}: {exc}") from exc
    return sorted({ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")})


def build_coverage(
    content: ContentRepo,
    *,
    env: str,
    include_retired: bool,
    techniques_file: Path | None,
    now: datetime,
) -> dict[str, Any]:
    """Build the coverage report for the rules in ``env``."""
    rules = content.rules_in(env, include_retired=include_retired)
    techniques: dict[str, list[dict[str, Any]]] = defaultdict(list)
    tactics: dict[str, list[dict[str, Any]]] = defaultdict(list)
    tables: dict[str, list[str]] = defaultdict(list)
    by_life: Counter[str] = Counter()
    by_sev: Counter[str] = Counter()
    by_tier: Counter[str] = Counter()

    for bundle in rules:
        ref = {
            "id": bundle.rule_id,
            "lifecycle": bundle.metadata.get("lifecycle"),
            "enabled": bool(bundle.rule.get("enabled")),
        }
        for tech in bundle.rule.get("techniques", []):
            techniques[tech].append(ref)
        for tactic in bundle.rule.get("tactics", []):
            tactics[tactic].append(ref)
        for table in bundle.metadata.get("dataSources", {}).get("tables", []):
            tables[table].append(bundle.rule_id)
        by_life[str(bundle.metadata.get("lifecycle"))] += 1
        by_sev[str(bundle.rule.get("severity"))] += 1
        by_tier[str(bundle.metadata.get("confidenceTier"))] += 1

    # Weak coverage is judged against ALL live rules, not the --env slice: "only covered
    # by dev rules" is meaningless if the dev slice was filtered out of view.
    prod_states = ENV_STATES["prod"]
    covering: dict[str, list[Any]] = defaultdict(list)
    for bundle in content.rules_in("all"):
        for tech in bundle.rule.get("techniques", []):
            covering[tech].append(bundle)
    weak = []
    for tech, bundles in sorted(covering.items()):
        if not any(
            b.metadata.get("lifecycle") in prod_states and b.rule.get("enabled") for b in bundles
        ):
            weak.append(
                {
                    "technique": tech,
                    "reason": "no enabled rule in a production lifecycle state",
                    "rules": sorted(b.rule_id for b in bundles),
                }
            )

    uncovered: list[str] = []
    if techniques_file is not None:
        uncovered = [t for t in read_techniques_file(techniques_file) if t not in techniques]

    candidates = sorted(
        m.item_id
        for m in content.repo.manifests
        if m.data.get("type") == "hunting-query"
        and m.data.get("ruleConversion", {}).get("candidate")
    )
    return {
        "reportVersion": 1,
        "kind": "coverage",
        "generatedAt": now.isoformat(),
        "contentRepoRef": content.ref,
        "parameters": {
            "env": env,
            "includeRetired": include_retired,
            "techniquesFile": str(techniques_file) if techniques_file else None,
        },
        "summary": {
            "rules": len(rules),
            "byLifecycle": dict(sorted(by_life.items())),
            "bySeverity": dict(sorted(by_sev.items())),
            "byTier": dict(sorted(by_tier.items())),
        },
        "techniques": {k: sorted(v, key=lambda r: r["id"]) for k, v in sorted(techniques.items())},
        "tactics": {k: sorted(v, key=lambda r: r["id"]) for k, v in sorted(tactics.items())},
        "dataSources": {k: sorted(v) for k, v in sorted(tables.items())},
        "weakCoverage": weak,
        "uncoveredTechniques": uncovered,
        "conversionCandidates": candidates,
        "limitations": LIMITATIONS,
    }
