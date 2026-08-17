"""Unit tests for functional state reconstruction."""

from __future__ import annotations

from pathlib import Path

from air_engine.analyzer import build_state_at_node
from air_engine.core import NodeId, Trace, reconstruct_state
from air_engine.core.state import reduce_state
from air_engine.parser import parse_trace_file

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def _load_trace(name: str) -> Trace:
    return parse_trace_file(EXAMPLES_DIR / name)


def test_empty_state_has_no_events() -> None:
    from air_engine.core import empty_state

    assert empty_state().events == ()


def test_reconstruct_state_at_tool_call_node() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    tool_call = NodeId("01930000-0000-7000-8000-000000000012")
    state = reconstruct_state(trace, tool_call)
    event_types = [event.labels["event_type"] for event in state.events]
    assert event_types == ["run_start", "llm_invoke", "tool_call"]


def test_state_reconstruction_is_deterministic() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    tool_return = NodeId("01930000-0000-7000-8000-000000000013")
    first = reconstruct_state(trace, tool_return)
    second = reconstruct_state(trace, tool_return)
    assert first == second


def test_build_state_at_node_matches_core_reconstruction() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    run_end = NodeId("01930000-0000-7000-8000-000000000014")
    assert build_state_at_node(trace, run_end) == reconstruct_state(trace, run_end)


def test_reduce_state_appends_events_in_order() -> None:
    from air_engine.core.state import ExecutionState, ProjectedEvent

    state = ExecutionState(
        events=(
            ProjectedEvent(
                node_id=NodeId("a"),
                labels={"event_type": "first"},
            ),
        )
    )
    next_state = reduce_state(
        state,
        ProjectedEvent(node_id=NodeId("b"), labels={"event_type": "second"}),
    )
    assert [event.labels["event_type"] for event in next_state.events] == [
        "first",
        "second",
    ]
