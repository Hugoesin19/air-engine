"""Functional state reconstruction over causal closures."""

from __future__ import annotations

from dataclasses import dataclass

from air_engine.core.labeling import project_event
from air_engine.core.ordering import canonical_linear_extension, causal_closure
from air_engine.core.trace import Node, Trace
from air_engine.core.types import NodeId, SemanticLabels


@dataclass(frozen=True, slots=True)
class ProjectedEvent:
    """A single semantic projection materialized during state reduction."""

    node_id: NodeId
    labels: SemanticLabels


@dataclass(frozen=True, slots=True)
class ExecutionState:
    """Ephemeral Layer-3 state derived from a trace."""

    events: tuple[ProjectedEvent, ...]


def empty_state() -> ExecutionState:
    """Return the initial state S_0."""
    return ExecutionState(events=())


def node_contribution(node: Node) -> ProjectedEvent:
    """Compute δ(u, S) for a single node projection."""
    node_id, labels = project_event(node)
    return ProjectedEvent(node_id=node_id, labels=labels)


def reduce_state(state: ExecutionState, contribution: ProjectedEvent) -> ExecutionState:
    """Combine state with a node contribution using associative reduction ⊕."""
    return ExecutionState(events=(*state.events, contribution))


def reconstruct_state(trace: Trace, node_id: NodeId) -> ExecutionState:
    """Reconstruct state at ``node_id`` via reduction over its causal closure.

    Implements:
        state(v) = ⊕_{u ∈ O_can(closure(v))} δ(u, S_0)
    """
    closure = causal_closure(trace, node_id)
    ordered_nodes = canonical_linear_extension(trace, closure)

    state = empty_state()
    for ordered_node_id in ordered_nodes:
        node = trace.node_by_id(ordered_node_id)
        if node is None:
            msg = f"Node not found while reconstructing state: {ordered_node_id}"
            raise ValueError(msg)
        state = reduce_state(state, node_contribution(node))
    return state
