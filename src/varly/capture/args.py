"""Normalize tool argument payloads for capture and AIR labels."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from varly.core.types import LabelValue

PrimitiveArg = str | int | float | bool | None


def normalize_tool_args(value: object) -> dict[str, PrimitiveArg] | None:
    """Return a flat primitive-only args dict, or None when not a mapping."""
    if not isinstance(value, Mapping):
        return None
    normalized: dict[str, PrimitiveArg] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            msg = "tool args keys must be non-empty strings"
            raise ValueError(msg)
        if item is None or isinstance(item, (str, int, float, bool)):
            normalized[key] = item
            continue
        msg = f"tool args[{key!r}] must be a primitive JSON value"
        raise ValueError(msg)
    return normalized


def parse_tool_input_string(raw: str) -> dict[str, PrimitiveArg] | None:
    """Parse LangChain tool input strings into primitive args when possible."""
    stripped = raw.strip()
    if not stripped:
        return None
    if stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return {"input": raw}
        if isinstance(parsed, dict):
            return normalize_tool_args(parsed)
        return {"input": raw}
    return {"input": raw}


def args_to_json_label(args: Mapping[str, PrimitiveArg]) -> str:
    """Serialize tool args for the AIR ``args_json`` node label."""
    return json.dumps(dict(args), sort_keys=True, separators=(",", ":"))


def args_from_json_label(raw: LabelValue) -> dict[str, PrimitiveArg] | None:
    """Deserialize tool args from an AIR node label."""
    if not isinstance(raw, str) or not raw:
        return None
    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    try:
        return normalize_tool_args(parsed)
    except ValueError:
        return None
