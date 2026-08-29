"""Build immutable AIR traces from validated JSON payloads."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from varly.core.topology import validate_trace_structure
from varly.core.trace import ControlEdge, Node, ReferentialEdge, Trace
from varly.core.types import (
    ControlEdgeKind,
    EdgeId,
    LabelValue,
    NodeId,
    ReferentialEdgeKind,
    SemanticLabels,
    TraceId,
)
from varly.parser.errors import SchemaValidationError
from varly.parser.schema import validate_payload_schema


def build_trace(payload: Mapping[str, Any]) -> Trace:
    """Deserialize a JSON payload into a validated immutable Trace.

    Raises:
        SchemaValidationError: If the payload violates the AIR JSON schema.
        StructuralValidationError: If the trace violates structural axioms.
    """
    validate_payload_schema(payload)
    trace = _materialize_trace(payload)
    validate_trace_structure(trace)
    return trace


def _materialize_trace(payload: Mapping[str, Any]) -> Trace:
    nodes = tuple(_materialize_node(node) for node in payload["nodes"])
    control_edges = tuple(
        _materialize_control_edge(edge) for edge in payload["control_edges"]
    )
    referential_edges = tuple(
        _materialize_referential_edge(edge) for edge in payload["referential_edges"]
    )
    return Trace(
        air_schema_version=str(payload["air_schema_version"]),
        trace_id=TraceId(str(payload["trace_id"])),
        root_id=NodeId(str(payload["root_id"])),
        nodes=nodes,
        control_edges=control_edges,
        referential_edges=referential_edges,
    )


def _materialize_node(node: object) -> Node:
    if not isinstance(node, dict):
        msg = "Each node must be an object"
        raise SchemaValidationError(msg)
    labels_raw = node.get("labels")
    if not isinstance(labels_raw, dict):
        msg = "Each node must include an object 'labels' field"
        raise SchemaValidationError(msg)
    labels = _materialize_labels(labels_raw)
    node_id = node.get("id")
    if not isinstance(node_id, str):
        msg = "Each node must include a string 'id' field"
        raise SchemaValidationError(msg)
    return Node(id=NodeId(node_id), labels=labels)


def _materialize_labels(labels: Mapping[str, object]) -> SemanticLabels:
    materialized: SemanticLabels = {}
    for key, value in labels.items():
        if not isinstance(key, str):
            msg = "Node label keys must be strings"
            raise SchemaValidationError(msg)
        materialized[key] = _materialize_label_value(value)
    return materialized


def _materialize_label_value(value: object) -> LabelValue:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    msg = (
        "Node label values must be primitive JSON types in schema 1.0.0 "
        f"(got {type(value).__name__})"
    )
    raise SchemaValidationError(msg)


def _materialize_control_edge(edge: object) -> ControlEdge:
    mapping = _require_edge_mapping(edge)
    return ControlEdge(
        id=EdgeId(str(mapping["id"])),
        source=NodeId(str(mapping["source"])),
        target=NodeId(str(mapping["target"])),
        kind=ControlEdgeKind(str(mapping["kind"])),
    )


def _materialize_referential_edge(edge: object) -> ReferentialEdge:
    mapping = _require_edge_mapping(edge)
    return ReferentialEdge(
        id=EdgeId(str(mapping["id"])),
        source=NodeId(str(mapping["source"])),
        target=NodeId(str(mapping["target"])),
        kind=ReferentialEdgeKind(str(mapping["kind"])),
    )


def _require_edge_mapping(edge: object) -> Mapping[str, object]:
    if not isinstance(edge, dict):
        msg = "Each edge must be an object"
        raise SchemaValidationError(msg)
    return edge
