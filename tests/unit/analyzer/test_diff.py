"""Unit tests for diagnostic regression diffs."""

from __future__ import annotations

from air_engine.analyzer.diagnostic import Diagnostic, Violation
from air_engine.analyzer.diff import compare_diagnostics
from air_engine.core.types import NodeId, TraceId


def _diagnostic(*violations: Violation, trace_id: str = "t") -> Diagnostic:
    return Diagnostic(
        trace_id=TraceId(trace_id),
        passed=len(violations) == 0,
        violations=violations,
    )


def test_identical_diagnostics_are_not_regression() -> None:
    violation = Violation(invariant_id="no_orphans", message="x", node_id=NodeId("n1"))
    diff = compare_diagnostics(
        _diagnostic(violation, trace_id="base"),
        _diagnostic(violation, trace_id="cur"),
    )
    assert diff.is_regression is False
    assert diff.added == ()
    assert diff.unchanged == (violation,)


def test_new_violation_is_regression() -> None:
    added = Violation(
        invariant_id="tool_call_has_return",
        message="missing",
        node_id=NodeId("n-12"),
    )
    diff = compare_diagnostics(_diagnostic(trace_id="base"), _diagnostic(added))
    assert diff.is_regression is True
    assert diff.added == (added,)
    assert diff.removed == ()


def test_resolved_violation_is_not_regression() -> None:
    removed = Violation(invariant_id="token_budget", message="over", node_id=None)
    diff = compare_diagnostics(_diagnostic(removed, trace_id="base"), _diagnostic())
    assert diff.is_regression is False
    assert diff.removed == (removed,)


def test_diff_order_is_deterministic() -> None:
    first = Violation(invariant_id="b", message="m2", node_id=None)
    second = Violation(invariant_id="a", message="m1", node_id=NodeId("n"))
    left = compare_diagnostics(_diagnostic(), _diagnostic(first, second))
    right = compare_diagnostics(_diagnostic(), _diagnostic(second, first))
    assert left.added == right.added
    assert [violation.invariant_id for violation in left.added] == ["a", "b"]
