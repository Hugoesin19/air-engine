"""Unit tests for business-rule contract invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from air_engine.analyzer import verify_trace
from air_engine.contracts import Contract, InvalidInvariantParamError, InvariantSpec
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


def _valid_trace() -> Trace:
    return parse_trace_file(EXAMPLES_DIR / "trace_valid_minimal.json")


def _linear_trace(event_types: tuple[str, ...], *, tool_name: str = "search") -> Trace:
    node_ids = tuple(NodeId(f"n-{index:02d}") for index in range(len(event_types)))
    nodes = []
    for node_id, event_type in zip(node_ids, event_types, strict=True):
        labels: dict[str, str] = {"event_type": event_type}
        if event_type in {"tool_call", "tool_return"}:
            labels["name"] = tool_name
        nodes.append(Node(id=node_id, labels=labels))
    edges = tuple(
        ControlEdge(
            id=EdgeId(f"e-{index}"),
            source=node_ids[index],
            target=node_ids[index + 1],
            kind=ControlEdgeKind.CAUSES,
        )
        for index in range(len(node_ids) - 1)
    )
    return Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-business"),
        root_id=node_ids[0],
        nodes=tuple(nodes),
        control_edges=edges,
        referential_edges=(),
    )


def test_valid_trace_passes_business_rules() -> None:
    trace = _valid_trace()
    contract = Contract.with_defaults(
        (
            InvariantSpec(id="max_llm_invocations", params={"max": 1}),
            InvariantSpec(id="max_tool_calls", params={"max": 1}),
            InvariantSpec(id="tool_name_allowlist", params={"allowed": ("search",)}),
            InvariantSpec(
                id="required_event_sequence",
                params={"sequence": ("run_start", "tool_call", "run_end")},
            ),
        ),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_max_llm_invocations_fails_when_exceeded() -> None:
    trace = _linear_trace(("run_start", "llm_invoke", "llm_invoke", "run_end"))
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_llm_invocations", params={"max": 1}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "max_llm_invocations"
    assert diagnostic.violations[0].node_id == NodeId("n-02")


def test_max_tool_calls_fails_when_exceeded() -> None:
    trace = _linear_trace(
        ("run_start", "tool_call", "tool_return", "tool_call", "tool_return"),
    )
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_tool_calls", params={"max": 1}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "max_tool_calls"


def test_tool_name_allowlist_rejects_unknown_tool() -> None:
    trace = _linear_trace(
        ("run_start", "tool_call", "tool_return", "run_end"),
        tool_name="shell",
    )
    contract = Contract.with_defaults(
        (InvariantSpec(id="tool_name_allowlist", params={"allowed": ("search",)}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "tool_name_allowlist"
    assert "shell" in diagnostic.violations[0].message


def test_required_event_sequence_fails_on_wrong_order() -> None:
    trace = _linear_trace(("run_start", "tool_call", "llm_invoke", "run_end"))
    contract = Contract.with_defaults(
        (
            InvariantSpec(
                id="required_event_sequence",
                params={"sequence": ("run_start", "llm_invoke", "tool_call")},
            ),
        ),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "required_event_sequence"


def test_business_invariants_require_params() -> None:
    trace = _valid_trace()
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_llm_invocations", params={}),),
    )
    with pytest.raises(InvalidInvariantParamError, match="max"):
        verify_trace(trace, contract)
