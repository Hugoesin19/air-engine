"""Integration tests for policy pack selection."""

from __future__ import annotations

from pathlib import Path

from air_engine.interfaces.library import verify

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
POLICIES_DIR = EXAMPLES_DIR / "policies"
VALID_TRACE = EXAMPLES_DIR / "trace_valid_minimal.json"


def test_valid_trace_passes_mvp_and_dev_policies() -> None:
    mvp = verify(VALID_TRACE, POLICIES_DIR / "mvp.yaml")
    dev = verify(VALID_TRACE, POLICIES_DIR / "dev.yaml")
    assert mvp.passed is True
    assert dev.passed is True


def test_valid_trace_fails_strict_policy() -> None:
    diagnostic = verify(VALID_TRACE, POLICIES_DIR / "strict.yaml")
    assert diagnostic.passed is False
    invariant_ids = {violation.invariant_id for violation in diagnostic.violations}
    assert invariant_ids == {"max_trace_duration", "token_budget"}


def test_same_trace_outcome_changes_by_policy_only() -> None:
    mvp = verify(VALID_TRACE, POLICIES_DIR / "mvp.yaml")
    strict = verify(VALID_TRACE, POLICIES_DIR / "strict.yaml")
    assert mvp.passed is True
    assert strict.passed is False


def test_semantic_failure_not_relaxed_by_dev_policy() -> None:
    diagnostic = verify(
        EXAMPLES_DIR / "trace_invalid_missing_tool_return.json",
        POLICIES_DIR / "dev.yaml",
    )
    assert diagnostic.passed is False
    assert any(
        violation.invariant_id == "tool_call_has_return"
        for violation in diagnostic.violations
    )
