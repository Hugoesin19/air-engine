"""CLI integration tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from varly.interfaces.cli.main import run

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_cli_validate_success_on_valid_trace() -> None:
    exit_code = run(
        ["validate", str(EXAMPLES_DIR / "trace_valid_minimal.json")],
    )
    assert exit_code == 0


def test_cli_validate_failure_on_invalid_trace() -> None:
    exit_code = run(
        ["validate", str(EXAMPLES_DIR / "trace_invalid_cycle.json")],
    )
    assert exit_code == 1


def test_installed_entry_point_validates_trace() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "varly.interfaces.cli.main",
            "validate",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Valid AIR trace" in result.stdout
