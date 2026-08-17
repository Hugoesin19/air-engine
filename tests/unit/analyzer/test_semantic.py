"""Unit tests for semantic contract invariants."""

from __future__ import annotations

from pathlib import Path

from air_engine.analyzer import verify_trace
from air_engine.contracts import Contract, InvariantSpec
from air_engine.core import (
    AIR_SCHEMA_VERSION,
    ControlEdge,
    ControlEdgeKind,
    EdgeId,
    Node,
    NodeId,
    Trace,
    TraceId,
)
from air_engine.parser import parse_trace_file

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def _tool_call_without_return_trace() -> Trace:
    root = NodeId("n-root")
    llm = NodeId("n-llm")
    tool_call = NodeId("n-call")
    run_end = NodeId("n-end")
    return Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-no-return"),
        root_id=root,
        nodes=(
            Node(id=root, labels={"event_type": "run_start"}),
            Node(id=llm, labels={"event_type": "llm_invoke"}),
            Node(
                id=tool_call,
                labels={"event_type": "tool_call", "name": "search"},
            ),
            Node(id=run_end, labels={"event_type": "run_end"}),
        ),
        control_edges=(
            ControlEdge(
                id=EdgeId("e1"),
                source=root,
                target=llm,
                kind=ControlEdgeKind.CAUSES,
            ),
            ControlEdge(
                id=EdgeId("e2"),
                source=llm,
                target=tool_call,
                kind=ControlEdgeKind.INVOKES,
            ),
            ControlEdge(
                id=EdgeId("e3"),
                source=tool_call,
                target=run_end,
                kind=ControlEdgeKind.CAUSES,
            ),
        ),
        referential_edges=(),
    )


def test_valid_trace_passes_tool_call_has_return() -> None:
    trace = parse_trace_file(EXAMPLES_DIR / "trace_valid_minimal.json")
    contract = Contract.with_defaults(
        (InvariantSpec(id="tool_call_has_return", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_missing_tool_return_example_fails_semantic_rule() -> None:
    trace = parse_trace_file(EXAMPLES_DIR / "trace_invalid_missing_tool_return.json")
    contract = Contract.with_defaults(
        (InvariantSpec(id="tool_call_has_return", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert len(diagnostic.violations) == 1
    assert diagnostic.violations[0].invariant_id == "tool_call_has_return"
    assert diagnostic.violations[0].node_id == NodeId(
        "01930000-0000-7000-8000-000000000012"
    )


def test_tool_call_without_return_in_memory_trace_fails() -> None:
    trace = _tool_call_without_return_trace()
    contract = Contract.with_defaults(
        (InvariantSpec(id="tool_call_has_return", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].node_id == NodeId("n-call")


def test_mismatched_tool_name_does_not_count_as_return() -> None:
    root = NodeId("n-root")
    tool_call = NodeId("n-call")
    tool_return = NodeId("n-return")
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-name-mismatch"),
        root_id=root,
        nodes=(
            Node(id=root, labels={"event_type": "run_start"}),
            Node(
                id=tool_call,
                labels={"event_type": "tool_call", "name": "search"},
            ),
            Node(
                id=tool_return,
                labels={"event_type": "tool_return", "name": "other"},
            ),
        ),
        control_edges=(
            ControlEdge(
                id=EdgeId("e1"),
                source=root,
                target=tool_call,
                kind=ControlEdgeKind.CAUSES,
            ),
            ControlEdge(
                id=EdgeId("e2"),
                source=tool_call,
                target=tool_return,
                kind=ControlEdgeKind.PRODUCES,
            ),
        ),
        referential_edges=(),
    )
    contract = Contract.with_defaults(
        (InvariantSpec(id="tool_call_has_return", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].node_id == tool_call
