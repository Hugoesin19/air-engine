"""Adapter tests for recorded real-shaped OpenAI and LangGraph fixtures."""

from __future__ import annotations

from pathlib import Path

from varly.adapters import adapt_json_file, adapt_langgraph_file, adapt_openai_file
from varly.analyzer import verify_trace
from varly.contracts import load_policy_file
from varly.core.ordering import canonical_linear_extension
from varly.core.trace import Trace

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"
RECORDED_DIR = EXAMPLES_DIR / "fixtures" / "recorded"
GOLDEN = EXAMPLES_DIR / "trace_valid_minimal.json"
POLICY = EXAMPLES_DIR / "policies" / "mvp.yaml"


def _event_sequence(trace: Trace) -> list[str]:
    node_ids = canonical_linear_extension(trace, (node.id for node in trace.nodes))
    nodes_by_id = {node.id: node for node in trace.nodes}
    return [str(nodes_by_id[node_id].labels.get("event_type")) for node_id in node_ids]


def test_recorded_openai_responses_matches_golden_sequence() -> None:
    canonical = adapt_json_file(GOLDEN)
    adapted = adapt_openai_file(RECORDED_DIR / "openai_responses_search.json")
    assert _event_sequence(adapted) == _event_sequence(canonical)


def test_recorded_langgraph_callbacks_matches_golden_sequence() -> None:
    canonical = adapt_json_file(GOLDEN)
    adapted = adapt_langgraph_file(RECORDED_DIR / "langgraph_callbacks_search.json")
    assert _event_sequence(adapted) == _event_sequence(canonical)


def test_recorded_openai_fixture_verifies_without_api() -> None:
    trace = adapt_openai_file(RECORDED_DIR / "openai_responses_search.json")
    diagnostic = verify_trace(trace, load_policy_file(POLICY))
    assert diagnostic.passed is True


def test_recorded_langgraph_fixture_verifies_without_api() -> None:
    trace = adapt_langgraph_file(RECORDED_DIR / "langgraph_callbacks_search.json")
    diagnostic = verify_trace(trace, load_policy_file(POLICY))
    assert diagnostic.passed is True
