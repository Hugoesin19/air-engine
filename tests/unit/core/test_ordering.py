"""Unit tests for canonical ordering over control causality."""

from __future__ import annotations

from pathlib import Path

from air_engine.core import (
    ControlEdge,
    ControlEdgeKind,
    EdgeId,
    Node,
    NodeId,
    Trace,
    TraceId,
)
from air_engine.core.ordering import (
    canonical_linear_extension,
    causal_closure,
    causally_precedes,
)
from air_engine.core.types import AIR_SCHEMA_VERSION

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def _load_trace(name: str) -> Trace:
    from air_engine.parser import parse_trace_file

    return parse_trace_file(EXAMPLES_DIR / name)


def test_canonical_order_preserves_linear_chain() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    ordered = canonical_linear_extension(trace, trace.node_ids)
    event_types = []
    for node_id in ordered:
        node = trace.node_by_id(node_id)
        assert node is not None
        event_types.append(node.labels["event_type"])
    assert event_types == [
        "run_start",
        "llm_invoke",
        "tool_call",
        "tool_return",
        "run_end",
    ]


def test_causal_closure_includes_target_node() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    tool_call = NodeId("01930000-0000-7000-8000-000000000012")
    closure = causal_closure(trace, tool_call)
    assert tool_call in closure
    assert NodeId("01930000-0000-7000-8000-000000000010") in closure


def test_concurrent_branches_use_lexicographic_tie_break() -> None:
    root = NodeId("n-root")
    left = NodeId("n-left")
    right = NodeId("n-right")
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-concurrent"),
        root_id=root,
        nodes=(
            Node(id=root, labels={"event_type": "run_start"}),
            Node(id=left, labels={"event_type": "left"}),
            Node(id=right, labels={"event_type": "right"}),
        ),
        control_edges=(
            ControlEdge(
                id=EdgeId("e-left"),
                source=root,
                target=left,
                kind=ControlEdgeKind.CAUSES,
            ),
            ControlEdge(
                id=EdgeId("e-right"),
                source=root,
                target=right,
                kind=ControlEdgeKind.CAUSES,
            ),
        ),
        referential_edges=(),
    )
    ordered = canonical_linear_extension(trace, {root, left, right})
    assert ordered[0] == root
    assert ordered[1:] == (left, right)


def test_causally_precedes_detects_reachability() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    root = NodeId("01930000-0000-7000-8000-000000000010")
    tool_call = NodeId("01930000-0000-7000-8000-000000000012")
    assert causally_precedes(trace, root, tool_call)
    assert not causally_precedes(trace, tool_call, root)
