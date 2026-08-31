"""E2E: cookbook tool argument policy gates."""

from __future__ import annotations

from pathlib import Path

from varly.interfaces.cli.main import run

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "examples" / "cookbook" / "artifacts" / "tool_args_valid.json"
INVALID = ROOT / "examples" / "cookbook" / "artifacts" / "tool_args_invalid.json"
POLICY = ROOT / "examples" / "policies" / "api-guard.yaml"


def test_cookbook_tool_args_valid_passes() -> None:
    exit_code = run(
        [
            "verify",
            str(VALID),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 0


def test_cookbook_tool_args_invalid_fails() -> None:
    exit_code = run(
        [
            "verify",
            str(INVALID),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 1
