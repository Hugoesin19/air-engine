"""Structural validation and graph queries over AIR traces."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Mapping

from air_engine.core.errors import (
    CycleDetectedError,
    DuplicateIdError,
    InvalidRootError,
    OverlappingEdgeIdError,
    StructuralValidationError,
    UnknownNodeReferenceError,
    UnreachableNodeError,
)
from air_engine.core.trace import ControlEdge, Trace
from air_engine.core.types import NodeId


def validate_trace_structure(trace: Trace) -> None:
    """Validate all structural axioms required before analysis.

    Raises:
        StructuralValidationError: If any axiom is violated.
    """
    node_ids = _validate_unique_node_ids(trace)
    _validate_unique_edge_ids(trace)
    _validate_edge_endpoints(trace, node_ids)
    _validate_root_exists(trace, node_ids)
    adjacency = _build_control_adjacency(trace.control_edges)
    _validate_control_dag(trace, adjacency)
    _validate_reachability(trace, adjacency)
    _validate_unique_control_root(trace)


def _validate_unique_node_ids(trace: Trace) -> set[NodeId]:
    seen: set[NodeId] = set()
    duplicates: list[NodeId] = []
    for node in trace.nodes:
        if node.id in seen:
            duplicates.append(node.id)
        seen.add(node.id)
    if duplicates:
        duplicate = duplicates[0]
        msg = f"Duplicate node id: {duplicate}"
        raise DuplicateIdError(msg)
    if not seen:
        msg = "Trace must contain at least one node"
        raise StructuralValidationError(msg)
    return seen


def _validate_unique_edge_ids(trace: Trace) -> None:
    seen: set[str] = set()
    for control_edge in trace.control_edges:
        edge_key = str(control_edge.id)
        if edge_key in seen:
            msg = f"Duplicate edge id: {control_edge.id}"
            raise DuplicateIdError(msg)
        seen.add(edge_key)
    for referential_edge in trace.referential_edges:
        edge_key = str(referential_edge.id)
        if edge_key in seen:
            msg = f"Duplicate edge id: {referential_edge.id}"
            raise DuplicateIdError(msg)
        seen.add(edge_key)

    control_ids = {str(edge.id) for edge in trace.control_edges}
    referential_ids = {str(edge.id) for edge in trace.referential_edges}
    overlap = control_ids & referential_ids
    if overlap:
        edge_id = next(iter(overlap))
        msg = f"Edge id appears in both E_c and E_r: {edge_id}"
        raise OverlappingEdgeIdError(msg)


def _validate_edge_endpoints(trace: Trace, node_ids: set[NodeId]) -> None:
    for control_edge in trace.control_edges:
        if control_edge.source not in node_ids:
            msg = (
                f"Edge {control_edge.id} references unknown source node: "
                f"{control_edge.source}"
            )
            raise UnknownNodeReferenceError(msg)
        if control_edge.target not in node_ids:
            msg = (
                f"Edge {control_edge.id} references unknown target node: "
                f"{control_edge.target}"
            )
            raise UnknownNodeReferenceError(msg)
    for referential_edge in trace.referential_edges:
        if referential_edge.source not in node_ids:
            msg = (
                f"Edge {referential_edge.id} references unknown source node: "
                f"{referential_edge.source}"
            )
            raise UnknownNodeReferenceError(msg)
        if referential_edge.target not in node_ids:
            msg = (
                f"Edge {referential_edge.id} references unknown target node: "
                f"{referential_edge.target}"
            )
            raise UnknownNodeReferenceError(msg)


def _validate_root_exists(trace: Trace, node_ids: set[NodeId]) -> None:
    if trace.root_id not in node_ids:
        msg = f"root_id does not reference an existing node: {trace.root_id}"
        raise InvalidRootError(msg)


def _validate_unique_control_root(trace: Trace) -> None:
    incoming: dict[NodeId, int] = {node.id: 0 for node in trace.nodes}
    for edge in trace.control_edges:
        incoming[edge.target] = incoming.get(edge.target, 0) + 1

    root_incoming = incoming[trace.root_id]
    if root_incoming != 0:
        msg = f"root_id must have zero incoming control edges: {trace.root_id}"
        raise InvalidRootError(msg)

    roots = [node_id for node_id, count in incoming.items() if count == 0]
    if len(roots) != 1:
        msg = f"Expected exactly one control root, found {len(roots)}: {roots}"
        raise InvalidRootError(msg)

    if roots[0] != trace.root_id:
        msg = (
            f"root_id {trace.root_id} does not match the unique control root {roots[0]}"
        )
        raise InvalidRootError(msg)


def _build_control_adjacency(
    control_edges: Iterable[ControlEdge],
) -> dict[NodeId, list[NodeId]]:
    adjacency: dict[NodeId, list[NodeId]] = {}
    for edge in control_edges:
        adjacency.setdefault(edge.source, []).append(edge.target)
    return adjacency


def _validate_control_dag(
    trace: Trace,
    adjacency: Mapping[NodeId, list[NodeId]],
) -> None:
    visiting: set[NodeId] = set()
    visited: set[NodeId] = set()

    def visit(node_id: NodeId) -> None:
        if node_id in visiting:
            msg = f"Cycle detected in control edges at node: {node_id}"
            raise CycleDetectedError(msg)
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in adjacency.get(node_id, []):
            visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node in trace.nodes:
        visit(node.id)


def _validate_reachability(
    trace: Trace,
    adjacency: Mapping[NodeId, list[NodeId]],
) -> None:
    reachable = _reachable_from_root(trace.root_id, adjacency)
    unreachable = [node.id for node in trace.nodes if node.id not in reachable]
    if unreachable:
        orphan = unreachable[0]
        msg = f"Node not reachable from root via E_c: {orphan}"
        raise UnreachableNodeError(msg)


def _reachable_from_root(
    root_id: NodeId,
    adjacency: Mapping[NodeId, list[NodeId]],
) -> set[NodeId]:
    reachable: set[NodeId] = set()
    queue: deque[NodeId] = deque([root_id])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(adjacency.get(current, []))
    return reachable


def causal_ancestors(trace: Trace, node_id: NodeId) -> frozenset[NodeId]:
    """Return all nodes that can reach ``node_id`` via control edges."""
    incoming: dict[NodeId, list[NodeId]] = {}
    for edge in trace.control_edges:
        incoming.setdefault(edge.target, []).append(edge.source)

    ancestors: set[NodeId] = set()
    queue: deque[NodeId] = deque(incoming.get(node_id, []))
    while queue:
        current = queue.popleft()
        if current in ancestors:
            continue
        ancestors.add(current)
        queue.extend(incoming.get(current, []))
    return frozenset(ancestors)
