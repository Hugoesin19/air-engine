"""Semantic invariant evaluators."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable

from varly.contracts.model import InvariantSpec
from varly.core.trace import Trace
from varly.core.types import NodeId, SemanticLabels

InvariantEvaluator = Callable[[Trace, InvariantSpec], tuple[str, ...]]

_TOOL_CALL = "tool_call"
_TOOL_RETURN = "tool_return"


def _build_control_adjacency(trace: Trace) -> dict[NodeId, list[NodeId]]:
    adjacency: dict[NodeId, list[NodeId]] = {}
    for edge in trace.control_edges:
        adjacency.setdefault(edge.source, []).append(edge.target)
    return adjacency


def _reachable_via_control(trace: Trace, start: NodeId) -> frozenset[NodeId]:
    adjacency = _build_control_adjacency(trace)
    reachable: set[NodeId] = set()
    queue: deque[NodeId] = deque([start])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(adjacency.get(current, []))
    return frozenset(reachable)


def _event_type(labels: SemanticLabels) -> str | None:
    event_type = labels.get("event_type")
    return event_type if isinstance(event_type, str) else None


def _tool_name(labels: SemanticLabels) -> str | None:
    name = labels.get("name")
    return name if isinstance(name, str) else None


def evaluate_tool_call_has_return(
    trace: Trace,
    _spec: InvariantSpec,
) -> tuple[str, ...]:
    """Every ToolCall must have a reachable ToolReturn downstream in E_c."""
    nodes_by_id = {node.id: node for node in trace.nodes}
    messages: list[str] = []

    for node in trace.nodes:
        if _event_type(node.labels) != _TOOL_CALL:
            continue

        reachable = _reachable_via_control(trace, node.id)
        call_name = _tool_name(node.labels)
        has_return = False
        for candidate_id in reachable:
            if candidate_id == node.id:
                continue
            candidate = nodes_by_id[candidate_id]
            if _event_type(candidate.labels) != _TOOL_RETURN:
                continue
            if call_name is not None and _tool_name(candidate.labels) != call_name:
                continue
            has_return = True
            break

        if not has_return:
            messages.append(
                f"ToolCall at node: {node.id} has no reachable ToolReturn via E_c"
            )

    return tuple(messages)


SEMANTIC_EVALUATORS: dict[str, InvariantEvaluator] = {
    "tool_call_has_return": evaluate_tool_call_has_return,
}
