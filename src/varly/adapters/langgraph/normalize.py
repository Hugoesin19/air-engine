"""Normalize recorded LangGraph callback dumps into langgraph.run.v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from varly.adapters.errors import AdapterValidationError

LANGGRAPH_RUN_V1 = "langgraph.run.v1"


def is_langgraph_run_v1(payload: Mapping[str, Any]) -> bool:
    return payload.get("format_version") == LANGGRAPH_RUN_V1


def is_langgraph_callbacks(payload: Mapping[str, Any]) -> bool:
    if payload.get("object") == "langgraph.callback_events":
        return isinstance(payload.get("events"), list)
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        return False
    first = events[0]
    return isinstance(first, dict) and "event" in first and "type" not in first


def normalize_callbacks_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Translate LangChain/LangGraph callback events into langgraph.run.v1."""
    events_raw = payload.get("events")
    if not isinstance(events_raw, list) or not events_raw:
        msg = "LangGraph callback payload requires a non-empty events list"
        raise AdapterValidationError(msg)

    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        run_id = _root_run_id(events_raw)
    if not isinstance(run_id, str) or not run_id:
        msg = "LangGraph callback payload requires a run_id"
        raise AdapterValidationError(msg)

    events: list[dict[str, Any]] = []
    llm_index: dict[str, int] = {}
    timestamp_ms = 0
    last_llm_id: str | None = None
    reads: list[dict[str, str]] = []

    for index, item in enumerate(events_raw):
        if not isinstance(item, dict):
            msg = f"events[{index}] must be an object"
            raise AdapterValidationError(msg)
        event_name = item.get("event")
        if not isinstance(event_name, str) or not event_name:
            msg = f"events[{index}].event must be a non-empty string"
            raise AdapterValidationError(msg)

        item_run_id = item.get("run_id")
        if not isinstance(item_run_id, str) or not item_run_id:
            item_run_id = f"{run_id}:event-{index}"

        if event_name == "on_chain_start" and _is_root(item):
            events.append(
                {
                    "id": f"{run_id}:start",
                    "type": "chain_start",
                    "timestamp_ms": timestamp_ms,
                }
            )
            timestamp_ms += 100
        elif event_name in {"on_chat_model_start", "on_llm_start"}:
            last_llm_id = item_run_id
            events.append(
                {
                    "id": item_run_id,
                    "type": "on_chat_model_start",
                    "timestamp_ms": timestamp_ms,
                }
            )
            llm_index[item_run_id] = len(events) - 1
            timestamp_ms += 100
        elif event_name in {"on_chat_model_end", "on_llm_end"}:
            tokens = _tokens_from_callback(item)
            existing = llm_index.get(item_run_id)
            if existing is not None:
                if tokens is not None:
                    events[existing]["tokens"] = tokens
            else:
                last_llm_id = item_run_id
                event: dict[str, Any] = {
                    "id": item_run_id,
                    "type": "on_chat_model_start",
                    "timestamp_ms": timestamp_ms,
                }
                if tokens is not None:
                    event["tokens"] = tokens
                events.append(event)
                timestamp_ms += 100
        elif event_name == "on_tool_start":
            name = _callback_name(item, index, "on_tool_start")
            events.append(
                {
                    "id": item_run_id,
                    "type": "on_tool_start",
                    "name": name,
                    "timestamp_ms": timestamp_ms,
                }
            )
            if last_llm_id is not None:
                reads.append({"source": item_run_id, "target": last_llm_id})
            timestamp_ms += 300
        elif event_name == "on_tool_end":
            name = _callback_name(item, index, "on_tool_end")
            events.append(
                {
                    "id": f"{item_run_id}:end",
                    "type": "on_tool_end",
                    "name": name,
                    "timestamp_ms": timestamp_ms,
                }
            )
            timestamp_ms += 100
        elif event_name == "on_chain_end" and _is_root(item):
            events.append(
                {
                    "id": f"{run_id}:end",
                    "type": "chain_end",
                    "timestamp_ms": timestamp_ms,
                }
            )
        elif event_name in {"on_chain_start", "on_chain_end"}:
            continue
        else:
            msg = f"events[{index}] has unsupported event: {event_name!r}"
            raise AdapterValidationError(msg)

    if not events:
        msg = "LangGraph callback payload produced no mapped events"
        raise AdapterValidationError(msg)

    return {
        "format_version": LANGGRAPH_RUN_V1,
        "run_id": run_id,
        "events": events,
        "reads": reads,
    }


def _is_root(item: Mapping[str, Any]) -> bool:
    parent_ids = item.get("parent_ids")
    if parent_ids is None:
        return True
    if isinstance(parent_ids, list):
        return len(parent_ids) == 0
    return False


def _root_run_id(events: list[object]) -> str | None:
    for item in events:
        if isinstance(item, dict) and item.get("event") == "on_chain_start":
            if _is_root(item):
                run_id = item.get("run_id")
                if isinstance(run_id, str) and run_id:
                    return run_id
    return None


def _callback_name(item: Mapping[str, Any], index: int, event_name: str) -> str:
    name = item.get("name")
    if isinstance(name, str) and name:
        return name
    msg = f"events[{index}] {event_name} requires a non-empty name"
    raise AdapterValidationError(msg)


def _tokens_from_callback(item: Mapping[str, Any]) -> int | float | None:
    data = item.get("data")
    if not isinstance(data, Mapping):
        return None
    output = data.get("output")
    if not isinstance(output, Mapping):
        return None
    for usage_container in (
        output.get("llm_output"),
        output.get("usage"),
        output,
    ):
        if not isinstance(usage_container, Mapping):
            continue
        usage = usage_container.get("token_usage", usage_container)
        if not isinstance(usage, Mapping):
            continue
        total = usage.get("total_tokens")
        if isinstance(total, (int, float)) and not isinstance(total, bool):
            return total
    return None
