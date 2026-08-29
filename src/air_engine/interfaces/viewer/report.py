"""Build enriched JSON reports for the local diagnostic viewer."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from air_engine.analyzer.diagnostic import Diagnostic
from air_engine.analyzer.export import diagnostic_to_dict
from air_engine.core.trace import Trace
from air_engine.core.types import LabelValue, NodeId

_LLM_INVOKE = "llm_invoke"
_TOOL_CALL = "tool_call"
_TIMESTAMP_KEY = "timestamp_ms"
_TOKENS_KEY = "tokens"


def _numeric_label(labels: Mapping[str, LabelValue], key: str) -> float | None:
    value = labels.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def trace_summary(trace: Trace) -> dict[str, object]:
    """Minimal run metrics for the viewer (not a full DAG)."""
    timestamps = [
        value
        for node in trace.nodes
        if (value := _numeric_label(node.labels, _TIMESTAMP_KEY)) is not None
    ]
    total_tokens = 0.0
    for node in trace.nodes:
        if node.labels.get("event_type") != _LLM_INVOKE:
            continue
        tokens = _numeric_label(node.labels, _TOKENS_KEY)
        if tokens is not None:
            total_tokens += tokens

    summary: dict[str, object] = {
        "steps": len(trace.nodes),
        "llm_calls": sum(
            1 for node in trace.nodes if node.labels.get("event_type") == _LLM_INVOKE
        ),
        "tool_calls": sum(
            1 for node in trace.nodes if node.labels.get("event_type") == _TOOL_CALL
        ),
        "control_edges": len(trace.control_edges),
    }
    if timestamps:
        summary["duration_ms"] = round(max(timestamps) - min(timestamps), 3)
    if total_tokens > 0:
        if total_tokens.is_integer():
            summary["total_tokens"] = int(total_tokens)
        else:
            summary["total_tokens"] = total_tokens
    return summary


def trace_timeline(trace: Trace) -> list[dict[str, object]]:
    """Ordered execution steps as a simple list (not a graph widget)."""
    nodes_by_id = {node.id: node for node in trace.nodes}
    adjacency: dict[NodeId, list[NodeId]] = {}
    for edge in trace.control_edges:
        adjacency.setdefault(edge.source, []).append(edge.target)

    items: list[dict[str, object]] = []

    def walk(node_id: NodeId) -> None:
        node = nodes_by_id[node_id]
        event_type = node.labels.get("event_type", "unknown")
        name = node.labels.get("name")
        tokens = _numeric_label(node.labels, _TOKENS_KEY)
        item: dict[str, object] = {
            "step": len(items) + 1,
            "event_type": str(event_type),
            "node_id": str(node_id),
        }
        if isinstance(name, str) and name:
            item["name"] = name
        if tokens is not None:
            item["tokens"] = int(tokens) if tokens.is_integer() else tokens
        items.append(item)
        for child in adjacency.get(node_id, []):
            walk(child)

    walk(trace.root_id)
    return items


def build_viewer_report(
    diagnostic: Diagnostic,
    trace: Trace,
    *,
    trace_file: Path | None = None,
    contract_file: Path | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Diagnostic JSON plus summary and timeline for the HTML viewer."""
    report: dict[str, Any] = dict(diagnostic_to_dict(diagnostic))
    report["summary"] = trace_summary(trace)
    report["timeline"] = trace_timeline(trace)
    meta: dict[str, str] = {}
    if trace_file is not None:
        meta["trace_file"] = str(trace_file)
    if contract_file is not None:
        meta["contract_file"] = str(contract_file)
    if source is not None:
        meta["source"] = source
    if meta:
        report["meta"] = meta
    return report


def write_viewer_report(
    diagnostic: Diagnostic,
    trace: Trace,
    path: Path,
    *,
    trace_file: Path | None = None,
    contract_file: Path | None = None,
    source: str | None = None,
) -> None:
    """Write an enriched viewer report to disk."""
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_viewer_report(
        diagnostic,
        trace,
        trace_file=trace_file,
        contract_file=contract_file,
        source=source,
    )
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
