"""Shared event-type normalization for reference adapters."""

from __future__ import annotations

from varly.core.types import ControlEdgeKind, SemanticNodeType

_EVENT_ALIASES: dict[str, str] = {
    "run_start": "run_start",
    "chain_start": "run_start",
    "on_chain_start": "run_start",
    "llm_invoke": "llm_invoke",
    "llm_call": "llm_invoke",
    "on_chat_model_start": "llm_invoke",
    "on_chat_model_end": "llm_invoke",
    "on_llm_start": "llm_invoke",
    "on_llm_end": "llm_invoke",
    "tool_call": "tool_call",
    "on_tool_start": "tool_call",
    "function_call": "tool_call",
    "tool_return": "tool_return",
    "tool_output": "tool_return",
    "on_tool_end": "tool_return",
    "function_call_output": "tool_return",
    "run_end": "run_end",
    "chain_end": "run_end",
    "on_chain_end": "run_end",
}


def normalize_event_type(raw_type: str) -> str:
    """Map a framework-specific event name to the AIR domain event_type."""
    normalized = _EVENT_ALIASES.get(raw_type)
    if normalized is None:
        msg = f"Unsupported event type: {raw_type!r}"
        raise ValueError(msg)
    return normalized


def semantic_type_for(event_type: str) -> str:
    if event_type in {"tool_call", "tool_return"}:
        return SemanticNodeType.RESOURCE
    return SemanticNodeType.SEMANTIC


def control_kind_for(source_event: str, target_event: str) -> ControlEdgeKind:
    if target_event == "tool_call":
        return ControlEdgeKind.INVOKES
    if source_event == "tool_call" and target_event == "tool_return":
        return ControlEdgeKind.PRODUCES
    return ControlEdgeKind.CAUSES
