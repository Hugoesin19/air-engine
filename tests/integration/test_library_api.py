"""Integration tests for the programmatic library API."""

from __future__ import annotations

from pathlib import Path

from air_engine.interfaces.library import (
    load_trace,
    state_at,
    verify,
    write_diagnostic_json,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_library_verify_air_trace() -> None:
    diagnostic = verify(
        EXAMPLES_DIR / "trace_valid_minimal.json",
        EXAMPLES_DIR / "policy_mvp.yaml",
        source="air",
    )
    assert diagnostic.passed is True


def test_library_verify_langgraph_trace() -> None:
    diagnostic = verify(
        EXAMPLES_DIR / "langgraph_run_minimal.json",
        EXAMPLES_DIR / "policy_mvp.yaml",
        source="langgraph",
    )
    assert diagnostic.passed is True


def test_library_state_at_node() -> None:
    trace = load_trace(EXAMPLES_DIR / "trace_valid_minimal.json")
    state = state_at(trace, "01930000-0000-7000-8000-000000000012")
    assert [event.labels["event_type"] for event in state.events] == [
        "run_start",
        "llm_invoke",
        "tool_call",
    ]


def test_library_write_diagnostic_json(tmp_path: Path) -> None:
    diagnostic = verify(
        EXAMPLES_DIR / "trace_valid_minimal.json",
        EXAMPLES_DIR / "policies" / "mvp.yaml",
    )
    output = tmp_path / "diagnostic.json"
    write_diagnostic_json(diagnostic, output)
    assert output.exists()
    assert '"passed": true' in output.read_text(encoding="utf-8").lower()
