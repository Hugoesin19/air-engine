"""Unit tests for AIR structural topology validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from air_engine.core import (
    AIR_SCHEMA_VERSION,
    ControlEdge,
    ControlEdgeKind,
    CycleDetectedError,
    DuplicateIdError,
    EdgeId,
    InvalidRootError,
    Node,
    NodeId,
    ReferentialEdge,
    ReferentialEdgeKind,
    Trace,
    TraceId,
    UnknownNodeReferenceError,
    UnreachableNodeError,
    validate_trace_structure,
)
from air_engine.core.topology import causal_ancestors

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def _node(node_id: str, event_type: str) -> Node:
    return Node(
        id=NodeId(node_id),
        labels={"semantic_type": "semantic", "event_type": event_type},
    )


def _control_edge(
    edge_id: str,
    source: str,
    target: str,
    kind: ControlEdgeKind = ControlEdgeKind.CAUSES,
) -> ControlEdge:
    return ControlEdge(
        id=EdgeId(edge_id),
        source=NodeId(source),
        target=NodeId(target),
        kind=kind,
    )


def _trace_from_payload(payload: dict[str, Any]) -> Trace:
    nodes = tuple(
        Node(id=NodeId(node["id"]), labels=dict(node["labels"]))
        for node in payload["nodes"]
    )
    control_edges = tuple(
        ControlEdge(
            id=EdgeId(edge["id"]),
            source=NodeId(edge["source"]),
            target=NodeId(edge["target"]),
            kind=ControlEdgeKind(edge["kind"]),
        )
        for edge in payload["control_edges"]
    )
    referential_edges = tuple(
        ReferentialEdge(
            id=EdgeId(edge["id"]),
            source=NodeId(edge["source"]),
            target=NodeId(edge["target"]),
            kind=ReferentialEdgeKind(edge["kind"]),
        )
        for edge in payload["referential_edges"]
    )
    return Trace(
        air_schema_version=payload["air_schema_version"],
        trace_id=TraceId(payload["trace_id"]),
        root_id=NodeId(payload["root_id"]),
        nodes=nodes,
        control_edges=control_edges,
        referential_edges=referential_edges,
    )


def _load_example(name: str) -> Trace:
    payload = json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
    return _trace_from_payload(payload)


def test_valid_minimal_trace_passes_validation() -> None:
    trace = _load_example("trace_valid_minimal.json")
    validate_trace_structure(trace)


def test_valid_minimal_example_matches_schema_version() -> None:
    trace = _load_example("trace_valid_minimal.json")
    assert trace.air_schema_version == AIR_SCHEMA_VERSION


def test_invalid_cycle_example_raises() -> None:
    trace = _load_example("trace_invalid_cycle.json")
    with pytest.raises(CycleDetectedError):
        validate_trace_structure(trace)


def test_invalid_orphan_example_raises() -> None:
    trace = _load_example("trace_invalid_orphan.json")
    with pytest.raises(UnreachableNodeError):
        validate_trace_structure(trace)


def test_referential_cycles_do_not_break_control_validation() -> None:
    root = "n-root"
    child = "n-child"
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-ref-cycle"),
        root_id=NodeId(root),
        nodes=(
            _node(root, "run_start"),
            _node(child, "step"),
        ),
        control_edges=(_control_edge("e1", root, child),),
        referential_edges=(
            ReferentialEdge(
                id=EdgeId("r1"),
                source=NodeId(child),
                target=NodeId(root),
                kind=ReferentialEdgeKind.READS,
            ),
            ReferentialEdge(
                id=EdgeId("r2"),
                source=NodeId(root),
                target=NodeId(child),
                kind=ReferentialEdgeKind.WRITES,
            ),
        ),
    )
    validate_trace_structure(trace)


def test_duplicate_node_id_raises() -> None:
    duplicate = "n-dup"
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-dup-node"),
        root_id=NodeId(duplicate),
        nodes=(
            _node(duplicate, "run_start"),
            _node(duplicate, "duplicate"),
        ),
        control_edges=(),
        referential_edges=(),
    )
    with pytest.raises(DuplicateIdError):
        validate_trace_structure(trace)


def test_unknown_edge_endpoint_raises() -> None:
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-unknown-node"),
        root_id=NodeId("n-root"),
        nodes=(_node("n-root", "run_start"),),
        control_edges=(_control_edge("e1", "n-root", "n-missing"),),
        referential_edges=(),
    )
    with pytest.raises(UnknownNodeReferenceError):
        validate_trace_structure(trace)


def test_invalid_root_with_incoming_control_edge_raises() -> None:
    root = "n-root"
    child = "n-child"
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-bad-root"),
        root_id=NodeId(root),
        nodes=(_node(root, "run_start"), _node(child, "step")),
        control_edges=(_control_edge("e1", child, root),),
        referential_edges=(),
    )
    with pytest.raises((InvalidRootError, UnreachableNodeError)):
        validate_trace_structure(trace)


def test_causal_ancestors_returns_upstream_control_nodes() -> None:
    trace = _load_example("trace_valid_minimal.json")
    tool_call = NodeId("01930000-0000-7000-8000-000000000012")
    ancestors = causal_ancestors(trace, tool_call)
    assert NodeId("01930000-0000-7000-8000-000000000010") in ancestors
    assert NodeId("01930000-0000-7000-8000-000000000011") in ancestors
    assert tool_call not in ancestors
