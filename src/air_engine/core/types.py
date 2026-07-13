"""Core type aliases and enumerations for the AIR metamodel."""

from __future__ import annotations

from enum import StrEnum
from typing import NewType

AIR_SCHEMA_VERSION = "1.0.0"

NodeId = NewType("NodeId", str)
EdgeId = NewType("EdgeId", str)
TraceId = NewType("TraceId", str)

LabelValue = str | int | float | bool | None
SemanticLabels = dict[str, LabelValue]


class ControlEdgeKind(StrEnum):
    """Semantic types for control causality edges (E_c)."""

    CAUSES = "causes"
    INVOKES = "invokes"
    PRODUCES = "produces"
    CONTAINS = "contains"


class ReferentialEdgeKind(StrEnum):
    """Semantic types for referential information edges (E_r)."""

    READS = "reads"
    WRITES = "writes"
    REFERENCES = "references"


class SemanticNodeType(StrEnum):
    """Layer-2 semantic classifications for node labels."""

    PRIMITIVE = "primitive"
    COMPOSITE = "composite"
    REFERENCE = "reference"
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    RESOURCE = "resource"
    CONTRACT = "contract"
