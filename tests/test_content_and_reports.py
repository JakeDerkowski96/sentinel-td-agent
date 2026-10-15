"""Content commands and the audit/coverage reports, including contract conformance.

Required permissions: none.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tdagent.cli import main
from tdagent.content_repo import open_content_repo
from tdagent.reports.audit import build_audit
from tdagent.reports.coverage import build_coverage

from .conftest import load_contract

NOW = datetime(2026, 10, 15, tzinfo=UTC)


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _meta(content: Path, rule: str) -> Path:
    return next((content / "content/analytics-rules").glob(f"{rule}-*")) / "metadata.yaml"


def test_content_list_json(content: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--content-repo", str(content), "content", "list", "--format", "json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert {r["id"] for r in rows} >= {"DET-ENTRA-0001", "WL-PRIVILEGED-ACCOUNTS"}


def test_content_list_filters(content: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = ["--content-repo", str(content), "content", "list", "--type", "rule", "--env", "dev"]
    assert main([*args, "--format", "json"]) == 0
    ids = {r["id"] for r in json.loads(capsys.readouterr().out)}
    assert ids == {
        "DET-ENTRA-0001",
        "DET-MDE-0001",
        "DET-LINUX-0001",
    }  # all three are dev lifecycle
    assert (
        main(
            [
                "--content-repo",
                str(content),
                "content",
                "list",
                "--env",
                "prod",
                "--type",
                "rule",
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out) == []


def test_content_show_rule_and_item_and_unknown(
    content: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = ["--content-repo", str(content), "content", "show"]
    assert main([*base, "DET-MDE-0001"]) == 0
    rule = json.loads(capsys.readouterr().out)
    assert rule["dependencies"] == ["FUNC-NORMALIZE-PROCESS-001"]
    assert rule["tenantOverrides"] == ["contoso"]
    assert main([*base, "FUNC-NORMALIZE-PROCESS-001"]) == 0
    assert json.loads(capsys.readouterr().out)["usedBy"] == ["DET-MDE-0001"]
    assert main([*base, "DET-NOPE-0001"]) == 2


def test_content_validate_exit_codes(content: Path) -> None:
    base = ["--content-repo", str(content), "content", "validate"]
    assert main([*base, "--strict"]) == 0
    rule = next((content / "content/analytics-rules").glob("DET-ENTRA-0001-*")) / "rule.yaml"
    with rule.open("a", encoding="utf-8") as handle:
        handle.write("unexpectedField: 1\n")
    assert main(base) == 1


def test_content_index_dry_run_and_write(content: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    base = ["--content-repo", str(content), "content", "index", "--out", str(out)]
    assert main([*base, "--dry-run"]) == 0
    assert not out.exists()
    assert main(base) == 0
    assert (
        json.loads((out / "coverage-index.json").read_text(encoding="utf-8"))["counts"]["rules"]
        == 3
    )


def test_content_index_refuses_invalid_repo(content: Path, tmp_path: Path) -> None:
    (next((content / "content/analytics-rules").glob("DET-LINUX-0001-*")) / "query.kql").unlink()
    assert (
        main(["--content-repo", str(content), "content", "index", "--out", str(tmp_path / "o")])
        == 1
    )


def test_audit_report_matches_contract(content: Path) -> None:
    report = build_audit(open_content_repo(content), env="all", include_retired=False, now=NOW)
    errors = list(
        Draft202012Validator(load_contract("report-audit.v1.schema.json")).iter_errors(report)
    )
    assert errors == []
    assert report["summary"]["rules"] == 3
    assert report["contentRepoRef"] == "unknown"  # a temp copy is not a git checkout
    assert report["agentControls"] == {"allowed": 3}


def test_audit_flags_stale_review_expired_exception_and_override(content: Path) -> None:
    exc = next((content / "content/analytics-rules").glob("DET-MDE-0001-*")) / "exceptions.yaml"
    exc.write_text(
        "schemaVersion: 1\nid: DET-MDE-0001\nexceptions:\n"
        "  - id: EXC-001\n    description: scanner\n    reason: known scanner\n    owner: team\n"
        '    approvedBy: lead\n    approvedOn: "2026-01-01"\n    expires: "2026-06-01"\n'
        "    implementation: kql-exclusion\n",
        encoding="utf-8",
    )
    _replace(
        content / "tenants/overrides/contoso/DET-MDE-0001.yaml", '"2027-04-15"', '"2026-10-30"'
    )
    later = datetime(2027, 6, 1, tzinfo=UTC)
    report = build_audit(open_content_repo(content), env="all", include_retired=False, now=later)
    assert [e["id"] for e in report["exceptions"]["expired"]] == ["EXC-001"]
    assert report["overrides"]["expired"][0]["tenant"] == "contoso"
    assert len(report["ownership"]["notReviewed"]["rules"]) == 3  # created 2026-10-15, now 2027-06


def test_audit_expiring_soon(content: Path) -> None:
    _replace(
        content / "tenants/overrides/contoso/DET-MDE-0001.yaml", '"2027-04-15"', '"2026-10-30"'
    )
    report = build_audit(open_content_repo(content), env="all", include_retired=False, now=NOW)
    assert report["overrides"]["expiringSoon"][0]["rule"] == "DET-MDE-0001"


def test_audit_flags_experimental_in_production(content: Path) -> None:
    _replace(_meta(content, "DET-ENTRA-0001"), "lifecycle: validated", "lifecycle: production")
    report = build_audit(open_content_repo(content), env="prod", include_retired=False, now=NOW)
    assert report["maturity"]["experimentalInProduction"] == ["DET-ENTRA-0001"]
    assert report["summary"]["rules"] == 1


def test_coverage_report_matches_contract(content: Path) -> None:
    report = build_coverage(
        open_content_repo(content), env="all", include_retired=False, techniques_file=None, now=NOW
    )
    errors = list(
        Draft202012Validator(load_contract("report-coverage.v1.schema.json")).iter_errors(report)
    )
    assert errors == []
    assert set(report["techniques"]) == {"T1027", "T1059.001", "T1110", "T1110.001"}
    assert report["dataSources"]["SigninLogs"] == ["DET-ENTRA-0001"]
    assert report["conversionCandidates"] == ["HUNT-IDENTITY-0001"]


def test_coverage_env_slices_and_weak_coverage(content: Path) -> None:
    repo = open_content_repo(content)
    prod = build_coverage(repo, env="prod", include_retired=False, techniques_file=None, now=NOW)
    assert prod["summary"]["rules"] == 0
    assert len(prod["weakCoverage"]) == 4  # everything is dev-only, judged against all live rules

    _replace(_meta(content, "DET-ENTRA-0001"), "lifecycle: validated", "lifecycle: production")
    repo = open_content_repo(content)
    prod = build_coverage(repo, env="prod", include_retired=False, techniques_file=None, now=NOW)
    assert list(prod["techniques"]) == ["T1110"]
    assert "T1110" not in {w["technique"] for w in prod["weakCoverage"]}


def test_coverage_uncovered_techniques_from_file(content: Path, tmp_path: Path) -> None:
    wanted = tmp_path / "t.txt"
    wanted.write_text("# comment\nT1110\nT1566\n\nT1110\n", encoding="utf-8")
    report = build_coverage(
        open_content_repo(content),
        env="all",
        include_retired=False,
        techniques_file=wanted,
        now=NOW,
    )
    assert report["uncoveredTechniques"] == ["T1566"]


def test_coverage_missing_techniques_file_is_clean_error(content: Path, tmp_path: Path) -> None:
    code = main(
        [
            "--content-repo",
            str(content),
            "report",
            "coverage",
            "--techniques",
            str(tmp_path / "no.txt"),
        ]
    )
    assert code == 2


def test_report_cli_formats_and_output_file(content: Path, tmp_path: Path) -> None:
    out = tmp_path / "r" / "audit.json"
    base = ["--content-repo", str(content), "report"]
    assert main([*base, "audit", "--format", "json", "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["kind"] == "audit"
    md = tmp_path / "cov.md"
    assert main([*base, "coverage", "--output", str(md)]) == 0
    assert md.read_text(encoding="utf-8").startswith("# Coverage report")


def test_unwritable_output_is_clean_error(content: Path, tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    code = main(
        ["--content-repo", str(content), "report", "audit", "--output", str(blocker / "x.md")]
    )
    assert code == 2
