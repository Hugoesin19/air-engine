"""Normalize recorded OpenAI payloads into openai.run.v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from air_engine.adapters.errors import AdapterValidationError

OPENAI_RUN_V1 = "openai.run.v1"


def is_openai_run_v1(payload: Mapping[str, Any]) -> bool:
    return payload.get("format_version") == OPENAI_RUN_V1


def is_openai_responses(payload: Mapping[str, Any]) -> bool:
    return payload.get("object") == "response" and isinstance(
        payload.get("output"), list
    )


def normalize_responses_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Translate an OpenAI Responses API object into openai.run.v1."""
    run_id = payload.get("id")
    output = payload.get("output")
    if not isinstance(run_id, str) or not run_id:
        msg = "OpenAI Responses payload requires non-empty string id"
        raise AdapterValidationError(msg)
    if not isinstance(output, list) or not output:
        msg = "OpenAI Responses payload requires non-empty output list"
        raise AdapterValidationError(msg)

    total_tokens = _usage_total_tokens(payload.get("usage"))
    steps: list[dict[str, Any]] = [
        {"id": f"{run_id}:start", "step_type": "run_start", "timestamp_ms": 0},
    ]
    timestamp_ms = 100
    last_llm_id: str | None = None
    reads: list[dict[str, str]] = []
    has_message = any(
        isinstance(item, dict) and item.get("type") == "message" for item in output
    )

    if not has_message:
        last_llm_id = f"{run_id}:llm"
        steps.append(
            _llm_step(last_llm_id, timestamp_ms, total_tokens),
        )
        timestamp_ms += 100

    for index, item in enumerate(output):
        if not isinstance(item, dict):
            msg = f"output[{index}] must be an object"
            raise AdapterValidationError(msg)
        item_type = item.get("type")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            item_id = f"{run_id}:output-{index}"

        if item_type == "message":
            last_llm_id = item_id
            steps.append(_llm_step(item_id, timestamp_ms, total_tokens))
            timestamp_ms += 100
        elif item_type == "function_call":
            name = item.get("name")
            if not isinstance(name, str) or not name:
                msg = f"output[{index}] function_call requires a non-empty name"
                raise AdapterValidationError(msg)
            steps.append(
                {
                    "id": item_id,
                    "step_type": "tool_call",
                    "name": name,
                    "timestamp_ms": timestamp_ms,
                }
            )
            if last_llm_id is not None:
                reads.append({"source": item_id, "target": last_llm_id})
            timestamp_ms += 300
        elif item_type == "function_call_output":
            name = _tool_name_for_output(item, steps)
            steps.append(
                {
                    "id": item_id,
                    "step_type": "tool_output",
                    "name": name,
                    "timestamp_ms": timestamp_ms,
                }
            )
            timestamp_ms += 100
        else:
            msg = f"output[{index}] has unsupported type: {item_type!r}"
            raise AdapterValidationError(msg)

    steps.append(
        {
            "id": f"{run_id}:end",
            "step_type": "run_end",
            "timestamp_ms": timestamp_ms,
        }
    )
    return {
        "format_version": OPENAI_RUN_V1,
        "run_id": run_id,
        "steps": steps,
        "reads": reads,
    }


def _llm_step(
    item_id: str,
    timestamp_ms: int,
    total_tokens: int | float | None,
) -> dict[str, Any]:
    step: dict[str, Any] = {
        "id": item_id,
        "step_type": "llm_call",
        "timestamp_ms": timestamp_ms,
    }
    if total_tokens is not None:
        step["usage"] = {"total_tokens": total_tokens}
    return step


def _usage_total_tokens(usage: object) -> int | float | None:
    if not isinstance(usage, Mapping):
        return None
    total = usage.get("total_tokens")
    if isinstance(total, (int, float)) and not isinstance(total, bool):
        return total
    return None


def _tool_name_for_output(item: Mapping[str, Any], steps: list[dict[str, Any]]) -> str:
    name = item.get("name")
    if isinstance(name, str) and name:
        return name
    call_id = item.get("call_id")
    if isinstance(call_id, str) and call_id:
        for step in reversed(steps):
            if step.get("step_type") == "tool_call":
                found = step.get("name")
                if isinstance(found, str) and found:
                    return found
    for step in reversed(steps):
        if step.get("step_type") == "tool_call":
            found = step.get("name")
            if isinstance(found, str) and found:
                return found
    return "unknown"
