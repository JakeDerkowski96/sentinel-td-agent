"""Render report dictionaries as Markdown. JSON is the source; Markdown is derived.

Required permissions: none.
"""

from __future__ import annotations

from typing import Any


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return ["_None._", ""]
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return [*out, ""]


def _kv(mapping: dict[str, Any]) -> str:
    return ", ".join(f"{k}: {v}" for k, v in mapping.items()) or "none"


def _header(report: dict[str, Any], title: str) -> list[str]:
    ref, when, env = report["contentRepoRef"], report["generatedAt"], report["parameters"]["env"]
    return [f"# {title}", "", f"Content ref `{ref}` | generated {when} | env `{env}`", ""]


def render_audit(r: dict[str, Any]) -> str:
    """Render the audit report."""
    s, own, mat = r["summary"], r["ownership"], r["maturity"]
    exc, ovr = r["exceptions"], r["overrides"]
    out = [
        *_header(r, "Audit report"),
        "## Summary",
        "",
        f"- Rules in scope: **{s['rules']}** ({_kv(s['byLifecycle'])})",
        f"- Other content items: {s['content']}",
        f"- Validation: **{s['errors']} errors, {s['warnings']} warnings**",
        f"- Agent controls: {_kv(r['agentControls'])}",
        "",
        "## Validation findings",
        "",
        *_table(
            ["Severity", "Code", "Path", "Message"],
            [
                [i["severity"], f"`{i['code']}`", f"`{i['path']}`", i["message"]]
                for i in r["validation"]
            ],
        ),
        "## Ownership and review",
        "",
        f"- Missing owner: {', '.join(own['missingOwner']) or 'none'}",
        f"- Not reviewed in {own['notReviewed']['thresholdDays']} days: "
        f"{', '.join(own['notReviewed']['rules']) or 'none'}",
        "",
        "## Maturity gaps",
        "",
        f"- No tests: {', '.join(mat['noTests']) or 'none'}",
        f"- No analyst playbook: {', '.join(mat['noPlaybook']) or 'none'}",
        "- Experimental tier in production: "
        f"{', '.join(mat['experimentalInProduction']) or 'none'}",
        "",
        "## Exceptions",
        "",
        *_table(
            ["State", "Rule", "Exception", "Expires"],
            [["expired", e["rule"], e["id"], e["expires"]] for e in exc["expired"]]
            + [["expiring soon", e["rule"], e["id"], e["expires"]] for e in exc["expiringSoon"]],
        ),
        "## Tenant overrides",
        "",
        *_table(
            ["State", "Tenant", "Rule", "Expires"],
            [["expired", e["tenant"], e["rule"], e["expires"]] for e in ovr["expired"]]
            + [
                ["expiring soon", e["tenant"], e["rule"], e["expires"]] for e in ovr["expiringSoon"]
            ],
        ),
        "## Unused content",
        "",
        ", ".join(r["unusedContent"]) or "_None._",
        "",
    ]
    return "\n".join(out)


def render_coverage(r: dict[str, Any]) -> str:
    """Render the coverage report."""
    s = r["summary"]

    def refs(items: list[dict[str, Any]]) -> str:
        return ", ".join(
            f"{x['id']} ({x['lifecycle']}, {'on' if x['enabled'] else 'off'})" for x in items
        )

    out = [
        *_header(r, "Coverage report"),
        f"> {r['limitations']}",
        "",
        "## Summary",
        "",
        f"- Rules: **{s['rules']}** ({_kv(s['byLifecycle'])})",
        f"- Severity: {_kv(s['bySeverity'])}",
        f"- Confidence tier: {_kv(s['byTier'])}",
        "",
        "## Techniques",
        "",
        *_table(
            ["Technique", "Rules (lifecycle, enabled)"],
            [[f"`{t}`", refs(v)] for t, v in r["techniques"].items()],
        ),
        "## Tactics",
        "",
        *_table(
            ["Tactic", "Rules"],
            [[t, ", ".join(x["id"] for x in v)] for t, v in r["tactics"].items()],
        ),
        "## Data sources",
        "",
        *_table(
            ["Table", "Rules"], [[f"`{t}`", ", ".join(v)] for t, v in r["dataSources"].items()]
        ),
        "## Weak coverage",
        "",
        *_table(
            ["Technique", "Reason", "Rules"],
            [
                [f"`{w['technique']}`", w["reason"], ", ".join(w["rules"])]
                for w in r["weakCoverage"]
            ],
        ),
        "## Uncovered techniques of interest",
        "",
        ", ".join(f"`{t}`" for t in r["uncoveredTechniques"])
        or "_None (or no techniques file given)._",
        "",
        "## Rule-conversion candidates",
        "",
        ", ".join(r["conversionCandidates"]) or "_None._",
        "",
    ]
    return "\n".join(out)
