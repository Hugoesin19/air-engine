"""AIR JSON schema validation (syntactic layer)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from air_engine.core.types import (
    AIR_SCHEMA_VERSION,
    ControlEdgeKind,
    ReferentialEdgeKind,
)
from air_engine.parser.errors import SchemaValidationError

_REQUIRED_TOP_LEVEL_FIELDS = (
    "air_schema_version",
    "trace_id",
    "root_id",
    "nodes",
    "control_edges",
    "referential_edges",
)


def validate_payload_schema(payload: Mapping[str, Any]) -> None:
    """Validate the syntactic shape of a trace JSON payload.

    Raises:
        SchemaValidationError: If required fields or value types are invalid.
    """
    _require_mapping(payload, "trace payload")
    for field in _REQUIRED_TOP_LEVEL_FIELDS:
        if field not in payload:
            msg = f"Missing required field: {field}"
            raise SchemaValidationError(msg)

    version = _require_non_empty_string(
        payload["air_schema_version"], "air_schema_version"
    )
    if version != AIR_SCHEMA_VERSION:
        msg = (
            f"Unsupported air_schema_version: {version!r} "
            f"(expected {AIR_SCHEMA_VERSION!r})"
        )
        raise SchemaValidationError(msg)

    _require_non_empty_string(payload["trace_id"], "trace_id")
    _require_non_empty_string(payload["root_id"], "root_id")
    _validate_nodes(payload["nodes"])
    _validate_control_edges(payload["control_edges"])
    _validate_referential_edges(payload["referential_edges"])


def _validate_nodes(nodes: object) -> None:
    if not isinstance(nodes, list):
        msg = "Field 'nodes' must be a list"
        raise SchemaValidationError(msg)
    if not nodes:
        msg = "Field 'nodes' must contain at least one node"
        raise SchemaValidationError(msg)
    for index, node in enumerate(nodes):
        _validate_node(node, index)


def _validate_node(node: object, index: int) -> None:
    prefix = f"nodes[{index}]"
    mapping = _require_mapping(node, prefix)
    _require_non_empty_string(mapping.get("id"), f"{prefix}.id")
    labels = mapping.get("labels")
    if not isinstance(labels, dict):
        msg = f"{prefix}.labels must be an object"
        raise SchemaValidationError(msg)


def _validate_control_edges(edges: object) -> None:
    if not isinstance(edges, list):
        msg = "Field 'control_edges' must be a list"
        raise SchemaValidationError(msg)
    for index, edge in enumerate(edges):
        _validate_edge(
            edge,
            index,
            field_name="control_edges",
            allowed_kinds={kind.value for kind in ControlEdgeKind},
        )


def _validate_referential_edges(edges: object) -> None:
    if not isinstance(edges, list):
        msg = "Field 'referential_edges' must be a list"
        raise SchemaValidationError(msg)
    for index, edge in enumerate(edges):
        _validate_edge(
            edge,
            index,
            field_name="referential_edges",
            allowed_kinds={kind.value for kind in ReferentialEdgeKind},
        )


def _validate_edge(
    edge: object,
    index: int,
    *,
    field_name: str,
    allowed_kinds: set[str],
) -> None:
    prefix = f"{field_name}[{index}]"
    mapping = _require_mapping(edge, prefix)
    _require_non_empty_string(mapping.get("id"), f"{prefix}.id")
    _require_non_empty_string(mapping.get("source"), f"{prefix}.source")
    _require_non_empty_string(mapping.get("target"), f"{prefix}.target")
    kind = _require_non_empty_string(mapping.get("kind"), f"{prefix}.kind")
    if kind not in allowed_kinds:
        msg = f"{prefix}.kind has invalid value: {kind!r}"
        raise SchemaValidationError(msg)


def _require_mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        msg = f"{context} must be an object"
        raise SchemaValidationError(msg)
    return value


def _require_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        msg = f"Field '{field_name}' must be a string"
        raise SchemaValidationError(msg)
    if not value:
        msg = f"Field '{field_name}' must not be empty"
        raise SchemaValidationError(msg)
    return value
