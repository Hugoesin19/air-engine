"""CLI tests for the diff regression gate."""

from __future__ import annotations

from pathlib import Path

from air_engine.interfaces.cli.main import run
from air_engine.interfaces.library import compare_traces

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
POLICY = EXAMPLES_DIR / "policies" / "mvp.yaml"
BASELINE = EXAMPLES_DIR / "trace_valid_minimal.json"
BROKEN = EXAMPLES_DIR / "trace_invalid_missing_tool_return.json"


def test_cli_diff_same_trace_is_not_regression() -> None:
    exit_code = run(
        [
            "diff",
            str(BASELINE),
            str(BASELINE),
            "--contract",
            str(POLICY),
        ],
    )
    assert exit_code == 0


def test_cli_diff_broken_fixture_is_regression() -> None:
    exit_code = run(
        [
            "diff",
            str(BASELINE),
            str(BROKEN),
            "--contract",
            str(POLICY),
        ],
    )
    assert exit_code == 1


def test_library_compare_traces_detects_new_violations() -> None:
    same = compare_traces(BASELINE, BASELINE, POLICY)
    worse = compare_traces(BASELINE, BROKEN, POLICY)
    assert same.is_regression is False
    assert worse.is_regression is True
    assert worse.added_count >= 1
