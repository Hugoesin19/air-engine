"""Detect likely trace source from a JSON payload (onboarding hints)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from air_engine.adapters.langgraph.normalize import (
    is_langgraph_callbacks,
    is_langgraph_run_v1,
)
from air_engine.adapters.openai.normalize import is_openai_responses, is_openai_run_v1
from air_engine.capture.model import CAPTURE_EVENT_LOG_VERSION

TraceSource = Literal["air", "capture", "langgraph", "openai"]


def detect_trace_source(payload: Mapping[str, Any]) -> TraceSource | None:
    """Return the most likely adapter source for a JSON object, if recognizable."""
    if payload.get("format_version") == CAPTURE_EVENT_LOG_VERSION:
        return "capture"
    if is_openai_responses(payload) or is_openai_run_v1(payload):
        return "openai"
    if is_langgraph_callbacks(payload) or is_langgraph_run_v1(payload):
        return "langgraph"
    if "air_schema_version" in payload and "nodes" in payload:
        return "air"
    return None


def wrong_source_message(
    path: str,
    *,
    used: TraceSource,
    detected: TraceSource,
) -> str:
    """Human-readable hint when --source does not match the file shape."""
    return (
        f"File {path!r} looks like a {detected} trace, but --source {used!r} was used. "
        f"Try: air-engine verify {path} --source {detected} --contract <policy.yaml>"
    )
