"""Layer-3 state reconstruction orchestration."""

from __future__ import annotations

from air_engine.core.state import ExecutionState, reconstruct_state
from air_engine.core.trace import Trace
from air_engine.core.types import NodeId


def build_state_at_node(trace: Trace, node_id: NodeId) -> ExecutionState:
    """Build the reconstructed execution state at the given node."""
    return reconstruct_state(trace, node_id)
