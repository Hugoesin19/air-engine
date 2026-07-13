"""AIR core: immutable trace model and structural validation."""

from air_engine.core.errors import (
    AirEngineError,
    CycleDetectedError,
    DuplicateIdError,
    InvalidRootError,
    OverlappingEdgeIdError,
    StructuralValidationError,
    UnknownNodeReferenceError,
    UnreachableNodeError,
)
from air_engine.core.topology import causal_ancestors, validate_trace_structure
from air_engine.core.trace import ControlEdge, Node, ReferentialEdge, Trace
from air_engine.core.types import (
    AIR_SCHEMA_VERSION,
    ControlEdgeKind,
    EdgeId,
    NodeId,
    ReferentialEdgeKind,
    SemanticNodeType,
    TraceId,
)

__all__ = [
    "AIR_SCHEMA_VERSION",
    "AirEngineError",
    "ControlEdge",
    "ControlEdgeKind",
    "CycleDetectedError",
    "DuplicateIdError",
    "EdgeId",
    "InvalidRootError",
    "Node",
    "NodeId",
    "OverlappingEdgeIdError",
    "ReferentialEdge",
    "ReferentialEdgeKind",
    "SemanticNodeType",
    "StructuralValidationError",
    "Trace",
    "TraceId",
    "UnreachableNodeError",
    "UnknownNodeReferenceError",
    "causal_ancestors",
    "validate_trace_structure",
]
