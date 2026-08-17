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
from air_engine.core.labeling import (
    project_control_edge,
    project_event,
    project_referential_edge,
    project_vertex,
)
from air_engine.core.ordering import (
    canonical_linear_extension,
    canonical_node_key,
    causal_closure,
    causally_precedes,
)
from air_engine.core.state import (
    ExecutionState,
    ProjectedEvent,
    empty_state,
    node_contribution,
    reconstruct_state,
    reduce_state,
)
from air_engine.core.topology import causal_ancestors, validate_trace_structure
from air_engine.core.trace import ControlEdge, Node, ReferentialEdge, Trace
from air_engine.core.types import (
    AIR_SCHEMA_VERSION,
    ControlEdgeKind,
    EdgeId,
    LabelValue,
    NodeId,
    ReferentialEdgeKind,
    SemanticLabels,
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
    "ExecutionState",
    "InvalidRootError",
    "LabelValue",
    "Node",
    "NodeId",
    "OverlappingEdgeIdError",
    "ProjectedEvent",
    "ReferentialEdge",
    "ReferentialEdgeKind",
    "SemanticLabels",
    "SemanticNodeType",
    "StructuralValidationError",
    "Trace",
    "TraceId",
    "UnreachableNodeError",
    "UnknownNodeReferenceError",
    "canonical_linear_extension",
    "canonical_node_key",
    "causal_ancestors",
    "causal_closure",
    "causally_precedes",
    "empty_state",
    "node_contribution",
    "project_control_edge",
    "project_event",
    "project_referential_edge",
    "project_vertex",
    "reconstruct_state",
    "reduce_state",
    "validate_trace_structure",
]
