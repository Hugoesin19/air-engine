"""Unit tests for metric contract invariants."""

from __future__ import annotations

import pytest

from varly.analyzer import verify_trace
from varly.contracts import Contract, InvalidInvariantParamError, InvariantSpec
from varly.core import (
    AIR_SCHEMA_VERSION,
    Node,
    NodeId,
    Trace,
    TraceId,
)


def _trace_with_metrics(duration_ms: float, tokens: float) -> Trace:
    root = NodeId("n-root")
    llm = NodeId("n-llm")
    end = NodeId("n-end")
    return Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-metrics"),
        root_id=root,
        nodes=(
            Node(
                id=root,
                labels={"event_type": "run_start", "timestamp_ms": 0},
            ),
            Node(
                id=llm,
                labels={
                    "event_type": "llm_invoke",
                    "timestamp_ms": duration_ms / 2,
                    "tokens": tokens,
                },
            ),
            Node(
                id=end,
                labels={"event_type": "run_end", "timestamp_ms": duration_ms},
            ),
        ),
        control_edges=(),
        referential_edges=(),
    )


def test_max_trace_duration_passes_within_limit() -> None:
    trace = _trace_with_metrics(duration_ms=500, tokens=10)
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_trace_duration", params={"max_ms": 1000}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_max_trace_duration_fails_when_exceeded() -> None:
    trace = _trace_with_metrics(duration_ms=5000, tokens=10)
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_trace_duration", params={"max_ms": 1000}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "max_trace_duration"


def test_max_trace_duration_skips_when_no_timestamps() -> None:
    root = NodeId("n-root")
    trace = Trace(
        air_schema_version=AIR_SCHEMA_VERSION,
        trace_id=TraceId("trace-no-time"),
        root_id=root,
        nodes=(Node(id=root, labels={"event_type": "run_start"}),),
        control_edges=(),
        referential_edges=(),
    )
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_trace_duration", params={"max_ms": 1000}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_token_budget_passes_within_limit() -> None:
    trace = _trace_with_metrics(duration_ms=100, tokens=50)
    contract = Contract.with_defaults(
        (InvariantSpec(id="token_budget", params={"max_tokens": 100}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_token_budget_fails_when_exceeded() -> None:
    trace = _trace_with_metrics(duration_ms=100, tokens=500)
    contract = Contract.with_defaults(
        (InvariantSpec(id="token_budget", params={"max_tokens": 100}),),
    )
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is False
    assert diagnostic.violations[0].invariant_id == "token_budget"


def test_metric_invariant_requires_params() -> None:
    trace = _trace_with_metrics(duration_ms=100, tokens=10)
    contract = Contract.with_defaults(
        (InvariantSpec(id="max_trace_duration", params={}),),
    )
    with pytest.raises(InvalidInvariantParamError, match="max_ms"):
        verify_trace(trace, contract)
