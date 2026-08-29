"""LangGraph reference adapter."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from varly.adapters._sequential import adapt_sequential_events
from varly.adapters.errors import AdapterValidationError, UnsupportedFormatError
from varly.adapters.json.adapter import load_external_json
from varly.adapters.langgraph.normalize import (
    LANGGRAPH_RUN_V1,
    is_langgraph_callbacks,
    is_langgraph_run_v1,
    normalize_callbacks_payload,
)
from varly.core.trace import Trace


def adapt_file(path: Path) -> Trace:
    """Translate a LangGraph run export file into an AIR trace."""
    payload = load_external_json(path)
    return adapt_payload(payload)


def adapt_payload(payload: Mapping[str, Any]) -> Trace:
    """Translate a LangGraph run export payload into an AIR trace."""
    if is_langgraph_callbacks(payload):
        payload = normalize_callbacks_payload(payload)
    elif not is_langgraph_run_v1(payload):
        version = payload.get("format_version")
        msg = (
            "Unsupported LangGraph payload: expected format_version "
            f"{LANGGRAPH_RUN_V1!r} or callback events "
            f"(got format_version={version!r})"
        )
        raise UnsupportedFormatError(msg)

    run_id = payload.get("run_id")
    events = payload.get("events")
    if not isinstance(run_id, str) or not run_id:
        msg = "LangGraph payload requires non-empty string run_id"
        raise AdapterValidationError(msg)
    if not isinstance(events, list) or not events:
        msg = "LangGraph payload requires non-empty events list"
        raise AdapterValidationError(msg)

    reads_raw = payload.get("reads", [])
    if reads_raw is None:
        reads_raw = []
    if not isinstance(reads_raw, list):
        msg = "LangGraph payload field reads must be a list when provided"
        raise AdapterValidationError(msg)

    reads: list[dict[str, str]] = []
    for index, item in enumerate(reads_raw):
        if not isinstance(item, dict):
            msg = f"reads[{index}] must be an object"
            raise AdapterValidationError(msg)
        source = item.get("source")
        target = item.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            msg = f"reads[{index}] requires string source and target"
            raise AdapterValidationError(msg)
        reads.append({"source": source, "target": target})

    return adapt_sequential_events(
        trace_id=run_id,
        events=events,
        reads=reads,
        type_field="type",
    )
