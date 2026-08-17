"""CLI rendering helpers for trace inspection."""

from __future__ import annotations

from collections.abc import Mapping

from air_engine.core.trace import Trace
from air_engine.core.types import LabelValue, NodeId

_LLM_INVOKE = "llm_invoke"
_TIMESTAMP_KEY = "timestamp_ms"
_TOKENS_KEY = "tokens"


def render_control_dag(trace: Trace) -> str:
    """Render the control-flow graph as an ASCII tree from the root."""
    nodes_by_id = {node.id: node for node in trace.nodes}
    adjacency: dict[NodeId, list[NodeId]] = {}
    for edge in trace.control_edges:
        adjacency.setdefault(edge.source, []).append(edge.target)

    lines: list[str] = []

    def format_node(node_id: NodeId) -> str:
        node = nodes_by_id[node_id]
        event_type = node.labels.get("event_type", "?")
        name = node.labels.get("name")
        if isinstance(event_type, str) and isinstance(name, str) and name:
            return f"{event_type} ({name})"
        return str(event_type)

    def walk(node_id: NodeId, prefix: str = "", is_last: bool = True) -> None:
        connector = "+-- " if is_last else "|-- "
        lines.append(f"{prefix}{connector}{format_node(node_id)} [{node_id}]")
        children = adjacency.get(node_id, [])
        child_prefix = prefix + ("    " if is_last else "|   ")
        for index, child in enumerate(children):
            walk(child, child_prefix, index == len(children) - 1)

    walk(trace.root_id)
    return "\n".join(lines)


def summarize_trace_metrics(trace: Trace) -> str:
    """Summarize duration and token metrics derived from node labels."""
    timestamps = [
        value
        for node in trace.nodes
        if (value := _numeric_label(node.labels, _TIMESTAMP_KEY)) is not None
    ]
    total_tokens = 0.0
    token_nodes = 0
    for node in trace.nodes:
        if node.labels.get("event_type") != _LLM_INVOKE:
            continue
        tokens = _numeric_label(node.labels, _TOKENS_KEY)
        if tokens is None:
            continue
        total_tokens += tokens
        token_nodes += 1

    lines = [
        f"  nodes: {len(trace.nodes)}",
        f"  control_edges: {len(trace.control_edges)}",
        f"  referential_edges: {len(trace.referential_edges)}",
    ]
    if timestamps:
        duration_ms = max(timestamps) - min(timestamps)
        lines.append(f"  duration_ms: {duration_ms}")
    if token_nodes:
        token_display = int(total_tokens) if total_tokens.is_integer() else total_tokens
        lines.append(f"  total_tokens: {token_display}")
    return "\n".join(lines)


def _numeric_label(labels: Mapping[str, LabelValue], key: str) -> float | None:
    value = labels.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)
