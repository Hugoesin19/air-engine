"""Unit tests for JUnit and SARIF diagnostic reports."""

from __future__ import annotations

import json
from xml.etree.ElementTree import fromstring

from air_engine.analyzer.diagnostic import Diagnostic, Violation
from air_engine.analyzer.reports import (
    diagnostic_to_junit,
    diagnostic_to_sarif,
    github_error_annotations,
)
from air_engine.core.types import NodeId, TraceId


def _failed() -> Diagnostic:
    return Diagnostic(
        trace_id=TraceId("trace-fail"),
        passed=False,
        violations=(
            Violation(
                invariant_id="tool_call_has_return",
                message="missing return",
                node_id=NodeId("n-12"),
            ),
        ),
    )


def test_junit_pass_has_zero_failures() -> None:
    diagnostic = Diagnostic(
        trace_id=TraceId("trace-ok"),
        passed=True,
        violations=(),
    )
    root = fromstring(diagnostic_to_junit(diagnostic))
    assert root.get("failures") == "0"
    assert root.get("tests") == "1"
    assert root.find("testcase") is not None
    assert root.find("testcase/failure") is None


def test_junit_failure_contains_invariant() -> None:
    root = fromstring(diagnostic_to_junit(_failed()))
    assert root.get("failures") == "1"
    failure = root.find("testcase/failure")
    assert failure is not None
    assert failure.get("type") == "tool_call_has_return"
    assert "missing return" in (failure.get("message") or "")


def test_sarif_results_match_violations() -> None:
    payload = json.loads(diagnostic_to_sarif(_failed()))
    assert payload["version"] == "2.1.0"
    results = payload["runs"][0]["results"]
    assert results[0]["ruleId"] == "tool_call_has_return"
    assert results[0]["level"] == "error"
    assert payload["runs"][0]["invocations"][0]["executionSuccessful"] is False


def test_github_annotations_on_failure() -> None:
    lines = github_error_annotations(_failed())
    assert len(lines) == 1
    assert lines[0].startswith("::error title=tool_call_has_return::")
    assert "missing return" in lines[0]


def test_github_annotations_empty_on_pass() -> None:
    diagnostic = Diagnostic(trace_id=TraceId("ok"), passed=True, violations=())
    assert github_error_annotations(diagnostic) == ()
