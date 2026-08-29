"""Helpers to assemble canonical AIR JSON payloads from adapter inputs."""

from __future__ import annotations

from typing import Any

from varly.core.types import AIR_SCHEMA_VERSION

AirNode = dict[str, Any]
AirEdge = dict[str, Any]
AirRead = dict[str, str]


def build_air_payload(
    *,
    trace_id: str,
    root_id: str,
    nodes: list[AirNode],
    control_edges: list[AirEdge],
    referential_edges: list[AirRead] | None = None,
) -> dict[str, Any]:
    """Build an AIR 1.0.0 payload ready for the parser."""
    return {
        "air_schema_version": AIR_SCHEMA_VERSION,
        "trace_id": trace_id,
        "root_id": root_id,
        "nodes": nodes,
        "control_edges": control_edges,
        "referential_edges": referential_edges or [],
    }
