"""Unit tests for diagnostic JSON export."""

from __future__ import annotations

import json
from pathlib import Path

from air_engine.analyzer.diagnostic import Diagnostic, Violation
from air_engine.analyzer.export import (
    DIAGNOSTIC_SCHEMA_VERSION,
    diagnostic_to_dict,
    diagnostic_to_json,
    write_diagnostic_json,
)
from air_engine.core.types import NodeId, TraceId


def test_diagnostic_to_dict_passed() -> None:
    diagnostic = Diagnostic(
        trace_id=TraceId("trace-001"),
        passed=True,
        violations=(),
    )
    payload = diagnostic_to_dict(diagnostic)
    assert payload == {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "trace_id": "trace-001",
        "passed": True,
        "violation_count": 0,
        "violations": [],
    }


def test_diagnostic_to_dict_with_violations() -> None:
    diagnostic = Diagnostic(
        trace_id=TraceId("trace-002"),
        passed=False,
        violations=(
            Violation(
                invariant_id="tool_call_has_return",
                message="ToolCall at node: n-12 has no reachable ToolReturn via E_c",
                node_id=NodeId("n-12"),
            ),
            Violation(
                invariant_id="max_trace_duration",
                message="Trace duration 600ms exceeds limit 500ms",
                node_id=None,
            ),
        ),
    )
    payload = diagnostic_to_dict(diagnostic)
    assert payload["passed"] is False
    assert payload["violation_count"] == 2
    assert payload["violations"][0]["node_id"] == "n-12"
    assert payload["violations"][1]["node_id"] is None


def test_write_diagnostic_json_round_trip(tmp_path: Path) -> None:
    diagnostic = Diagnostic(
        trace_id=TraceId("trace-003"),
        passed=True,
        violations=(),
    )
    output = tmp_path / "nested" / "artifacts" / "diagnostic.json"
    write_diagnostic_json(diagnostic, output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["trace_id"] == "trace-003"
    assert payload["passed"] is True
    assert diagnostic_to_json(diagnostic).endswith("}")
