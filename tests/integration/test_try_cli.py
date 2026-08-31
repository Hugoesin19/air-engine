"""CLI integration tests for try command."""

from __future__ import annotations

from varly.interfaces.cli.main import run


def test_cli_try_runs_pass_fail_and_regression() -> None:
    exit_code = run(["try"])
    assert exit_code == 0
