"""CLI tests for render flags."""

from __future__ import annotations

from pathlib import Path

from _pytest.capture import CaptureFixture

from air_engine.interfaces.cli.main import run

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_validate_show_dag_exits_zero(capsys: CaptureFixture[str]) -> None:
    exit_code = run(
        [
            "validate",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--show-dag",
        ],
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "control_dag:" in captured.out
    assert "tool_call (search)" in captured.out


def test_verify_show_metrics_exits_zero(capsys: CaptureFixture[str]) -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policy_mvp.yaml"),
            "--show-metrics",
        ],
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "duration_ms: 600" in captured.out
    assert "total_tokens: 150" in captured.out
