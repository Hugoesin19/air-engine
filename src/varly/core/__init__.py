"""AIR core: immutable trace model and structural validation."""

from varly.core.errors import (
    CycleDetectedError,
    DuplicateIdError,
    InvalidRootError,
    OverlappingEdgeIdError,
    StructuralValidationError,
    UnknownNodeReferenceError,
    UnreachableNodeError,
    VarlyError,
)
from varly.core.labeling import (
    project_control_edge,
    project_event,
    project_referential_edge,
    project_vertex,
)
from varly.core.ordering import (
    canonical_linear_extension,
    canonical_node_key,
    causal_closure,
    causally_precedes,
)
from varly.core.state import (
    ExecutionState,
    ProjectedEvent,
    empty_state,
    node_contribution,
    reconstruct_state,
    reduce_state,
)
from varly.core.topology import causal_ancestors, validate_trace_structure
from varly.core.trace import ControlEdge, Node, ReferentialEdge, Trace
from varly.core.types import (
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
    "VarlyError",
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
