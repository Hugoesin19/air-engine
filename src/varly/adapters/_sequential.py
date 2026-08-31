"""Build AIR traces from ordered external event lists."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from varly.adapters._mapping import (
    control_kind_for,
    normalize_event_type,
    semantic_type_for,
)
from varly.adapters._payload import build_air_payload
from varly.adapters.errors import AdapterValidationError
from varly.capture.args import args_to_json_label, normalize_tool_args
from varly.core.trace import Trace
from varly.parser import build_trace

ExternalEvent = Mapping[str, Any]
ExternalRead = Mapping[str, str]


def adapt_sequential_events(
    *,
    trace_id: str,
    events: list[ExternalEvent],
    reads: Sequence[ExternalRead] | None = None,
    type_field: str,
    tokens_field: str = "tokens",
) -> Trace:
    """Translate a linear external event log into a validated AIR trace."""
    if not events:
        msg = "Event log must contain at least one event"
        raise AdapterValidationError(msg)

    nodes: list[dict[str, Any]] = []
    normalized_types: list[str] = []

    for index, event in enumerate(events):
        event_id = event.get("id")
        raw_type = event.get(type_field)
        if not isinstance(event_id, str) or not event_id:
            msg = f"events[{index}].id must be a non-empty string"
            raise AdapterValidationError(msg)
        if not isinstance(raw_type, str) or not raw_type:
            msg = f"events[{index}].{type_field} must be a non-empty string"
            raise AdapterValidationError(msg)
        try:
            event_type = normalize_event_type(raw_type)
        except ValueError as exc:
            msg = f"events[{index}].{type_field}: {exc}"
            raise AdapterValidationError(msg) from exc

        labels: dict[str, Any] = {
            "semantic_type": semantic_type_for(event_type),
            "event_type": event_type,
        }
        timestamp_ms = event.get("timestamp_ms")
        if isinstance(timestamp_ms, (int, float)) and not isinstance(
            timestamp_ms, bool
        ):
            labels["timestamp_ms"] = timestamp_ms

        name = event.get("name")
        if isinstance(name, str) and name:
            labels["name"] = name

        tokens = _extract_tokens(event, tokens_field)
        if tokens is not None and event_type == "llm_invoke":
            labels["tokens"] = tokens

        if event_type == "tool_call":
            raw_args = event.get("args")
            if raw_args is not None:
                try:
                    normalized_args = normalize_tool_args(raw_args)
                except ValueError as exc:
                    msg = f"events[{index}].args: {exc}"
                    raise AdapterValidationError(msg) from exc
                if normalized_args:
                    labels["args_json"] = args_to_json_label(normalized_args)

        nodes.append({"id": event_id, "labels": labels})
        normalized_types.append(event_type)

    if normalized_types[0] != "run_start":
        msg = "First event must represent run_start"
        raise AdapterValidationError(msg)

    root_id = str(events[0]["id"])
    control_edges: list[dict[str, Any]] = []
    for index in range(len(events) - 1):
        source_id = str(events[index]["id"])
        target_id = str(events[index + 1]["id"])
        source_type = normalized_types[index]
        target_type = normalized_types[index + 1]
        control_edges.append(
            {
                "id": f"ec-{index:04d}",
                "source": source_id,
                "target": target_id,
                "kind": control_kind_for(source_type, target_type),
            }
        )

    referential_edges: list[dict[str, str]] = []
    for read_index, read in enumerate(reads or ()):
        source = read.get("source")
        target = read.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            msg = f"reads[{read_index}] requires string source and target"
            raise AdapterValidationError(msg)
        referential_edges.append(
            {
                "id": f"er-{read_index:04d}",
                "source": source,
                "target": target,
                "kind": "reads",
            }
        )

    payload = build_air_payload(
        trace_id=trace_id,
        root_id=root_id,
        nodes=nodes,
        control_edges=control_edges,
        referential_edges=referential_edges,
    )
    return build_trace(payload)


def _extract_tokens(event: ExternalEvent, tokens_field: str) -> int | float | None:
    direct = event.get(tokens_field)
    if isinstance(direct, (int, float)) and not isinstance(direct, bool):
        return direct
    usage = event.get("usage")
    if isinstance(usage, Mapping):
        total = usage.get("total_tokens")
        if isinstance(total, (int, float)) and not isinstance(total, bool):
            return total
    return None
