"""Canonical linear extensions over control causality (O_can)."""

from __future__ import annotations

import heapq
from collections.abc import Iterable

from varly.core.topology import causal_ancestors
from varly.core.trace import Trace
from varly.core.types import NodeId


def causal_closure(trace: Trace, node_id: NodeId) -> frozenset[NodeId]:
    """Return ancestors of ``node_id`` together with the node itself."""
    return causal_ancestors(trace, node_id) | {node_id}


def causally_precedes(trace: Trace, before: NodeId, after: NodeId) -> bool:
    """Return True when ``before`` can reach ``after`` via control edges."""
    if before == after:
        return False
    return before in causal_ancestors(trace, after)


def canonical_node_key(node_id: NodeId) -> str:
    """Lexicographic key used for UUIDv7 tie-breaking among concurrent nodes."""
    return str(node_id)


def canonical_linear_extension(
    trace: Trace,
    node_ids: Iterable[NodeId],
) -> tuple[NodeId, ...]:
    """Return O_can(A): a deterministic topological order over ``node_ids``.

    The sequence preserves all causal precedences induced by E_c. Concurrent
    nodes are ordered lexicographically by their identifiers (ADR-005).
    """
    nodes = frozenset(node_ids)
    if not nodes:
        return ()

    in_degree: dict[NodeId, int] = {node_id: 0 for node_id in nodes}
    adjacency: dict[NodeId, list[NodeId]] = {node_id: [] for node_id in nodes}

    for edge in trace.control_edges:
        if edge.source in nodes and edge.target in nodes:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1

    ready: list[tuple[str, NodeId]] = []
    for node_id, degree in in_degree.items():
        if degree == 0:
            heapq.heappush(ready, (canonical_node_key(node_id), node_id))

    ordered: list[NodeId] = []
    while ready:
        _, current = heapq.heappop(ready)
        ordered.append(current)
        for target in adjacency[current]:
            in_degree[target] -= 1
            if in_degree[target] == 0:
                heapq.heappush(ready, (canonical_node_key(target), target))

    if len(ordered) != len(nodes):
        msg = "Cannot linearize node set: causal subgraph contains a cycle"
        raise ValueError(msg)

    return tuple(ordered)
