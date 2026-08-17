"""Structural invariant evaluators."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable

from air_engine.contracts.model import InvariantSpec
from air_engine.core.trace import Trace
from air_engine.core.types import NodeId

InvariantEvaluator = Callable[[Trace, InvariantSpec], tuple[str, ...]]


def _build_control_adjacency(trace: Trace) -> dict[NodeId, list[NodeId]]:
    adjacency: dict[NodeId, list[NodeId]] = {}
    for edge in trace.control_edges:
        adjacency.setdefault(edge.source, []).append(edge.target)
    return adjacency


def _detect_control_cycle(trace: Trace) -> NodeId | None:
    adjacency = _build_control_adjacency(trace)
    visiting: set[NodeId] = set()
    visited: set[NodeId] = set()

    def visit(node_id: NodeId) -> NodeId | None:
        if node_id in visiting:
            return node_id
        if node_id in visited:
            return None
        visiting.add(node_id)
        for target in adjacency.get(node_id, []):
            cycle_node = visit(target)
            if cycle_node is not None:
                return cycle_node
        visiting.remove(node_id)
        visited.add(node_id)
        return None

    for node in trace.nodes:
        cycle_node = visit(node.id)
        if cycle_node is not None:
            return cycle_node
    return None


def _unreachable_control_nodes(trace: Trace) -> tuple[NodeId, ...]:
    adjacency = _build_control_adjacency(trace)
    reachable: set[NodeId] = set()
    queue: deque[NodeId] = deque([trace.root_id])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(adjacency.get(current, []))
    return tuple(node.id for node in trace.nodes if node.id not in reachable)


def evaluate_no_causal_cycles(trace: Trace, _spec: InvariantSpec) -> tuple[str, ...]:
    cycle_node = _detect_control_cycle(trace)
    if cycle_node is None:
        return ()
    message = f"Cycle detected in control edges at node: {cycle_node}"
    return (message,)


def evaluate_root_reachability(trace: Trace, _spec: InvariantSpec) -> tuple[str, ...]:
    unreachable = _unreachable_control_nodes(trace)
    if not unreachable:
        return ()
    messages = [
        f"Node not reachable from root via E_c: {node_id}" for node_id in unreachable
    ]
    return tuple(messages)


STRUCTURAL_EVALUATORS: dict[str, InvariantEvaluator] = {
    "no_causal_cycles": evaluate_no_causal_cycles,
    "root_reachability": evaluate_root_reachability,
}
