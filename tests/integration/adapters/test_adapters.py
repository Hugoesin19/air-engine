"""Integration tests for adapter modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from air_engine.adapters import (
    adapt_json_file,
    adapt_langgraph_file,
    adapt_openai_file,
)
from air_engine.adapters.errors import UnsupportedFormatError
from air_engine.analyzer import verify_trace
from air_engine.contracts import load_policy_file
from air_engine.core.ordering import canonical_linear_extension
from air_engine.core.trace import Trace

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def _event_sequence(trace: Trace) -> list[str]:
    node_ids = canonical_linear_extension(trace, (node.id for node in trace.nodes))
    nodes_by_id = {node.id: node for node in trace.nodes}
    return [str(nodes_by_id[node_id].labels.get("event_type")) for node_id in node_ids]


def _verify_full_policy(trace: Trace) -> None:
    contract = load_policy_file(EXAMPLES_DIR / "policy_mvp.yaml")
    diagnostic = verify_trace(trace, contract)
    assert diagnostic.passed is True


def test_json_adapter_loads_canonical_trace() -> None:
    trace = adapt_json_file(EXAMPLES_DIR / "trace_valid_minimal.json")
    assert trace.trace_id == "01930000-0000-7000-8000-000000000001"
    _verify_full_policy(trace)


def test_langgraph_adapter_produces_equivalent_flow() -> None:
    canonical = adapt_json_file(EXAMPLES_DIR / "trace_valid_minimal.json")
    adapted = adapt_langgraph_file(EXAMPLES_DIR / "langgraph_run_minimal.json")
    assert _event_sequence(adapted) == _event_sequence(canonical)
    _verify_full_policy(adapted)


def test_openai_adapter_produces_equivalent_flow() -> None:
    canonical = adapt_json_file(EXAMPLES_DIR / "trace_valid_minimal.json")
    adapted = adapt_openai_file(EXAMPLES_DIR / "openai_run_minimal.json")
    assert _event_sequence(adapted) == _event_sequence(canonical)
    _verify_full_policy(adapted)


def test_langgraph_adapter_rejects_unknown_format() -> None:
    with pytest.raises(UnsupportedFormatError, match="format_version"):
        adapt_langgraph_file(EXAMPLES_DIR / "trace_valid_minimal.json")
