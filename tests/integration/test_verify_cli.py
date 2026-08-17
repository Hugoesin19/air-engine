"""CLI integration tests for verify command."""

from __future__ import annotations

from pathlib import Path

from air_engine.interfaces.cli.main import run

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_cli_verify_passes_on_valid_trace() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policy_mvp.yaml"),
        ],
    )
    assert exit_code == 0


def test_cli_verify_fails_on_missing_contract() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "does_not_exist.yaml"),
        ],
    )
    assert exit_code == 1
