"""Capture event log adapter."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from varly.adapters._sequential import adapt_sequential_events
from varly.adapters.errors import AdapterValidationError, UnsupportedFormatError
from varly.adapters.json.adapter import load_external_json
from varly.capture import CAPTURE_EVENT_LOG_VERSION
from varly.core.trace import Trace


def adapt_file(path: Path) -> Trace:
    """Translate a capture event log file into an AIR trace."""
    payload = load_external_json(path)
    return adapt_payload(payload)


def adapt_payload(payload: Mapping[str, Any]) -> Trace:
    """Translate a capture event log payload into an AIR trace."""
    version = payload.get("format_version")
    if version != CAPTURE_EVENT_LOG_VERSION:
        msg = (
            f"Unsupported capture format_version: {version!r} "
            f"(expected {CAPTURE_EVENT_LOG_VERSION!r})"
        )
        raise UnsupportedFormatError(msg)

    run_id = payload.get("run_id")
    steps = payload.get("steps")
    if not isinstance(run_id, str) or not run_id:
        msg = "Capture payload requires non-empty string run_id"
        raise AdapterValidationError(msg)
    if not isinstance(steps, list) or not steps:
        msg = "Capture payload requires non-empty steps list"
        raise AdapterValidationError(msg)

    reads_raw = payload.get("reads", [])
    if reads_raw is None:
        reads_raw = []
    if not isinstance(reads_raw, list):
        msg = "Capture payload field reads must be a list when provided"
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
        events=steps,
        reads=reads,
        type_field="event_type",
        tokens_field="total_tokens",
    )
