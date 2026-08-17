"""Unit tests for contract evaluation and diagnostics."""

from __future__ import annotations

from pathlib import Path

import pytest

from air_engine.analyzer import verify_trace
from air_engine.contracts import (
    Contract,
    InvariantSpec,
    UnknownInvariantError,
    load_policy_file,
)
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


def _load_trace(name: str) -> Trace:
    return parse_trace_file(EXAMPLES_DIR / name)


def _cycle_trace() -> Trace:
    root = NodeId("n-root")
    mid = NodeId("n-mid")
    leaf = NodeId("n-leaf")
    return Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-cycle"),
        root_id=root,
        nodes=(
            Node(id=root, labels={"event_type": "run_start"}),
            Node(id=mid, labels={"event_type": "step_a"}),
            Node(id=leaf, labels={"event_type": "step_b"}),
        ),
        control_edges=(
            ControlEdge(
                id=EdgeId("e1"),
                source=root,
                target=mid,
                kind=ControlEdgeKind.CAUSES,
            ),
            ControlEdge(
                id=EdgeId("e2"),
                source=mid,
                target=leaf,
                kind=ControlEdgeKind.CAUSES,
            ),
            ControlEdge(
                id=EdgeId("e3"),
                source=leaf,
                target=mid,
                kind=ControlEdgeKind.CAUSES,
            ),
        ),
        referential_edges=(),
    )


def _orphan_trace() -> Trace:
    root = NodeId("n-root")
    child = NodeId("n-child")
    orphan = NodeId("n-orphan")
    return Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-orphan"),
        root_id=root,
        nodes=(
            Node(id=root, labels={"event_type": "run_start"}),
            Node(id=child, labels={"event_type": "step"}),
            Node(id=orphan, labels={"event_type": "orphan"}),
        ),
        control_edges=(
            ControlEdge(
                id=EdgeId("e1"),
                source=root,
                target=child,
                kind=ControlEdgeKind.CAUSES,
            ),
        ),
        referential_edges=(),
    )


def test_load_policy_mvp_yaml() -> None:
    contract = load_policy_file(EXAMPLES_DIR / "policy_mvp.yaml")
    assert len(contract.invariants) == 6
    invariant_ids = [spec.id for spec in contract.invariants]
    assert invariant_ids == [
        "no_causal_cycles",
        "root_reachability",
        "no_orphans",
        "tool_call_has_return",
        "max_trace_duration",
        "token_budget",
    ]


def test_verify_valid_trace_passes() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    contract = load_policy_file(EXAMPLES_DIR / "policy_mvp.yaml")
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True
    assert diagnostic.violations == ()


def test_verify_cycle_trace_fails_no_causal_cycles() -> None:
    trace = _cycle_trace()
    contract = Contract.with_defaults(
        (InvariantSpec(id="no_causal_cycles", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert len(diagnostic.violations) == 1
    assert diagnostic.violations[0].invariant_id == "no_causal_cycles"
    assert diagnostic.violations[0].node_id == NodeId("n-mid")


def test_verify_orphan_trace_fails_root_reachability() -> None:
    trace = _orphan_trace()
    contract = Contract.with_defaults(
        (InvariantSpec(id="root_reachability", params={}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert len(diagnostic.violations) == 1
    assert diagnostic.violations[0].invariant_id == "root_reachability"
    assert diagnostic.violations[0].node_id == NodeId("n-orphan")


def test_diagnostic_is_deterministic() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    contract = load_policy_file(EXAMPLES_DIR / "policy_mvp.yaml")
    first = verify_trace(trace, contract)
    second = verify_trace(trace, contract)
    assert first == second


def test_unknown_invariant_raises() -> None:
    trace = _load_trace("trace_valid_minimal.json")
    contract = Contract.with_defaults(
        (InvariantSpec(id="unknown_rule", params={}),),
    )
    with pytest.raises(UnknownInvariantError, match="Unknown invariant"):
        verify_trace(trace, contract)
