"""Tests for batch verify CI helper."""

from __future__ import annotations

from pathlib import Path

from scripts.ci.verify_batch import run_batch

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
POLICY = EXAMPLES / "policies" / "mvp.yaml"
VALID = EXAMPLES / "trace_valid_minimal.json"
INVALID = EXAMPLES / "trace_invalid_missing_tool_return.json"


def test_batch_verify_all_pass() -> None:
    results = run_batch([VALID], contract=POLICY, source="air")
    assert len(results) == 1
    assert results[0].exit_code == 0


def test_batch_verify_fails_when_any_trace_fails() -> None:
    results = run_batch([VALID, INVALID], contract=POLICY, source="air")
    assert results[0].exit_code == 0
    assert results[1].exit_code == 1
