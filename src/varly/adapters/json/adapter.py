"""Static JSON adapter for canonical AIR trace files."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from varly.core.trace import Trace
from varly.parser import load_json_object, parse_trace_file, parse_trace_payload


def adapt_file(path: Path) -> Trace:
    """Load a canonical AIR JSON trace file."""
    return parse_trace_file(path)


def adapt_payload(payload: Mapping[str, Any]) -> Trace:
    """Build a trace from an in-memory canonical AIR payload."""
    return parse_trace_payload(payload)


def load_external_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk without assuming AIR schema."""
    return load_json_object(path)
