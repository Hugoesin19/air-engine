"""Programmatic API for loading, inspecting, and verifying AIR traces."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from air_engine.adapters import (
    adapt_capture_file,
    adapt_json_file,
    adapt_langgraph_file,
    adapt_openai_file,
)
from air_engine.analyzer import verify_trace
from air_engine.analyzer.diagnostic import Diagnostic
from air_engine.analyzer.export import (
    diagnostic_to_dict,
    diagnostic_to_json,
    write_diagnostic_json,
)
from air_engine.analyzer.state_builder import build_state_at_node
from air_engine.contracts import load_policy_file
from air_engine.core.state import ExecutionState
from air_engine.core.trace import Trace
from air_engine.core.types import NodeId

TraceSource = Literal["air", "capture", "langgraph", "openai"]

__all__ = [
    "TraceSource",
    "diagnostic_to_dict",
    "diagnostic_to_json",
    "load_trace",
    "state_at",
    "verify",
    "write_diagnostic_json",
]


def load_trace(path: Path | str, *, source: TraceSource = "air") -> Trace:
    """Load external telemetry or a canonical AIR trace from disk."""
    resolved = Path(path)
    if source == "air":
        return adapt_json_file(resolved)
    if source == "capture":
        return adapt_capture_file(resolved)
    if source == "langgraph":
        return adapt_langgraph_file(resolved)
    if source == "openai":
        return adapt_openai_file(resolved)
    msg = f"Unsupported trace source: {source!r}"
    raise ValueError(msg)


def verify(
    trace_path: Path | str,
    contract_path: Path | str,
    *,
    source: TraceSource = "air",
) -> Diagnostic:
    """Verify a trace file against a contract policy."""
    trace = load_trace(trace_path, source=source)
    contract = load_policy_file(Path(contract_path))
    return verify_trace(trace, contract)


def state_at(trace: Trace, node_id: NodeId | str) -> ExecutionState:
    """Reconstruct execution state at a node."""
    return build_state_at_node(trace, NodeId(str(node_id)))
