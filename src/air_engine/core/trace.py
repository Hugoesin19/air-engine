"""Immutable AIR trace model (Layer 1 and Layer 2)."""

from __future__ import annotations

from dataclasses import dataclass

from air_engine.core.types import (
    ControlEdgeKind,
    EdgeId,
    NodeId,
    ReferentialEdgeKind,
    SemanticLabels,
    TraceId,
)


@dataclass(frozen=True, slots=True)
class Node:
    """Structural vertex with semantic projection labels (Event = (v, λ_V(v)))."""

    id: NodeId
    labels: SemanticLabels


@dataclass(frozen=True, slots=True)
class ControlEdge:
    """Directed control causality edge belonging to E_c."""

    id: EdgeId
    source: NodeId
    target: NodeId
    kind: ControlEdgeKind


@dataclass(frozen=True, slots=True)
class ReferentialEdge:
    """Directed referential information edge belonging to E_r."""

    id: EdgeId
    source: NodeId
    target: NodeId
    kind: ReferentialEdgeKind


@dataclass(frozen=True, slots=True)
class Trace:
    """Immutable representation of a completed execution.

    Formal model: T = (V, E_c, E_r, λ_V, λ_E).
    Labels and edge kinds materialize the semantic labeling functions.
    """

    air_schema_version: str
    trace_id: TraceId
    root_id: NodeId
    nodes: tuple[Node, ...]
    control_edges: tuple[ControlEdge, ...]
    referential_edges: tuple[ReferentialEdge, ...]

    @property
    def node_ids(self) -> frozenset[NodeId]:
        return frozenset(node.id for node in self.nodes)

    def node_by_id(self, node_id: NodeId) -> Node | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
