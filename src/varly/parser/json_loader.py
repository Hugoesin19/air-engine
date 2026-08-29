"""JSON file loading utilities for AIR traces."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from varly.core.trace import Trace
from varly.parser.builder import build_trace
from varly.parser.errors import ParseError


def load_json_object(path: Path) -> dict[str, Any]:
    """Load a JSON file and return its top-level object.

    Raises:
        ParseError: If the file cannot be read or does not contain a JSON object.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"Unable to read trace file: {path}"
        raise ParseError(msg) from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON in trace file: {path}"
        raise ParseError(msg) from exc

    if not isinstance(payload, dict):
        msg = f"Trace file must contain a JSON object: {path}"
        raise ParseError(msg)
    return payload


def parse_trace_file(path: Path) -> Trace:
    """Load and validate a trace from a JSON file."""
    payload = load_json_object(path)
    return build_trace(payload)


def parse_trace_payload(payload: Mapping[str, Any]) -> Trace:
    """Validate and build a trace from an in-memory JSON payload."""
    return build_trace(payload)
