"""CLI behaviour: help, exit codes, planned stubs, configuration precedence.

Required permissions: none.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tdagent.cli import build_parser, main
from tdagent.commands.planned import PLANNED
from tdagent.config import load_config
from tdagent.errors import EXIT_ERROR, EXIT_OK, EXIT_PLANNED, ConfigError

from .conftest import FIXTURE


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "content" in capsys.readouterr().out


def test_every_planned_command_is_registered_and_exits_3(caplog: pytest.LogCaptureFixture) -> None:
    assert PLANNED, "plan lists planned commands"
    for item in PLANNED:
        caplog.clear()
        # Extra flags are accepted: the stub must be reachable with its eventual arguments.
        code = main([item.group, item.name, "--rule", "DET-X"])
        assert code == EXIT_PLANNED, f"{item.group} {item.name}"
        assert f"Phase {item.phase}" in caplog.text


def test_unknown_argument_rejected_for_implemented_command() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--content-repo", str(FIXTURE), "content", "list", "--nope"])
    assert exc.value.code == 2


def test_missing_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["content"])
    assert exc.value.code == 2


def test_not_a_content_repo_exits_2(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    assert main(["--content-repo", str(tmp_path), "content", "list"]) == EXIT_ERROR
    assert "does not look like a DaC repository root" in caplog.text


def test_planned_commands_do_not_shadow_implemented_ones() -> None:
    parser = build_parser()
    args = parser.parse_args(["--content-repo", str(FIXTURE), "content", "list"])
    assert not getattr(args, "planned", False)


def test_doctor_ok_on_sample_and_fails_on_bad_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--content-repo", str(FIXTURE), "doctor"]) == EXIT_OK
    out = capsys.readouterr().out
    assert "content validation" in out and "skipped" in out
    assert main(["--content-repo", str(tmp_path), "doctor"]) == 1


def test_config_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg_file = tmp_path / "cfg" / "tdagent.yaml"
    cfg_file.parent.mkdir()
    cfg_file.write_text("content_repo: ../from-file\n", encoding="utf-8")
    monkeypatch.delenv("TDAGENT_CONTENT_REPO", raising=False)
    monkeypatch.delenv("TDAGENT_CONFIG", raising=False)

    # file value is resolved relative to the config file, not the shell's cwd
    assert load_config(cfg_file).content_repo == (tmp_path / "from-file").resolve()
    monkeypatch.setenv("TDAGENT_CONTENT_REPO", "/from/env")
    assert load_config(cfg_file).content_repo == Path("/from/env")
    assert load_config(cfg_file, Path("/from/flag")).content_repo == Path("/from/flag")


def test_missing_config_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(tmp_path / "nope.yaml")


def test_invalid_config_shape_is_an_error(tmp_path: Path) -> None:
    bad = tmp_path / "tdagent.yaml"
    bad.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(bad)


def test_env_config_pointing_at_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TDAGENT_CONFIG", str(tmp_path / "missing.yaml"))
    with pytest.raises(ConfigError):
        load_config()
