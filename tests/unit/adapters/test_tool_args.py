"""Adapter tests for tool args propagation into AIR labels."""

from __future__ import annotations

from pathlib import Path

from varly.adapters.capture.adapter import adapt_file

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def test_capture_adapter_maps_tool_args_to_args_json_label() -> None:
    trace = adapt_file(EXAMPLES_DIR / "cookbook" / "artifacts" / "tool_args_valid.json")
    tool_nodes = [
        node for node in trace.nodes if node.labels.get("event_type") == "tool_call"
    ]
    assert len(tool_nodes) == 1
    assert tool_nodes[0].labels.get("args_json") == (
        '{"endpoint":"https://api.example.com/search","query":"capital of France"}'
    )
