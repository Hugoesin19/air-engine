"""LangGraph reference adapter."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from air_engine.adapters._sequential import adapt_sequential_events
from air_engine.adapters.errors import AdapterValidationError, UnsupportedFormatError
from air_engine.adapters.json.adapter import load_external_json
from air_engine.core.trace import Trace

_FORMAT_VERSION = "langgraph.run.v1"


def adapt_file(path: Path) -> Trace:
    """Translate a LangGraph run export file into an AIR trace."""
    payload = load_external_json(path)
    return adapt_payload(payload)


def adapt_payload(payload: Mapping[str, Any]) -> Trace:
    """Translate a LangGraph run export payload into an AIR trace."""
    version = payload.get("format_version")
    if version != _FORMAT_VERSION:
        msg = (
            f"Unsupported LangGraph format_version: {version!r} "
            f"(expected {_FORMAT_VERSION!r})"
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
