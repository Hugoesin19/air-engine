"""Semantic projection functions (Layer 2 labeling)."""

from __future__ import annotations

from air_engine.core.trace import ControlEdge, Node, ReferentialEdge
from air_engine.core.types import (
    ControlEdgeKind,
    NodeId,
    ReferentialEdgeKind,
    SemanticLabels,
)


def project_vertex(node: Node) -> SemanticLabels:
    """Apply the vertex labeling function λ_V to a structural node."""
    return dict(node.labels)


def project_event(node: Node) -> tuple[NodeId, SemanticLabels]:
    """Materialize Event(v) = (v, λ_V(v))."""
    return node.id, project_vertex(node)


def project_control_edge(edge: ControlEdge) -> ControlEdgeKind:
    """Apply the edge labeling function λ_E on a control edge."""
    return edge.kind


def project_referential_edge(edge: ReferentialEdge) -> ReferentialEdgeKind:
    """Apply the edge labeling function λ_E on a referential edge."""
    return edge.kind
