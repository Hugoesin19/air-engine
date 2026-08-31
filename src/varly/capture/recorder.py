"""Append-only recorder for deterministic capture event logs."""

from __future__ import annotations

import json
from pathlib import Path

from varly.capture.args import PrimitiveArg, normalize_tool_args
from varly.capture.model import (
    CAPTURE_EVENT_LOG_VERSION,
    CaptureRead,
    CaptureStep,
)


class RunRecorder:
    """Record a run as a serializable, ordered capture event log."""

    def __init__(self, run_id: str) -> None:
        if not run_id:
            msg = "run_id must be non-empty"
            raise ValueError(msg)
        self._run_id = run_id
        self._steps: list[CaptureStep] = []
        self._reads: list[CaptureRead] = []
        self._step_ids: set[str] = set()

    @property
    def run_id(self) -> str:
        return self._run_id

    def record_run_start(self, *, step_id: str, timestamp_ms: int | float) -> None:
        self.record_step(
            step_id=step_id,
            event_type="run_start",
            timestamp_ms=timestamp_ms,
        )

    def record_llm_call(
        self,
        *,
        step_id: str,
        timestamp_ms: int | float,
        total_tokens: int | float,
    ) -> None:
        self.record_step(
            step_id=step_id,
            event_type="llm_call",
            timestamp_ms=timestamp_ms,
            total_tokens=total_tokens,
        )

    def record_tool_call(
        self,
        *,
        step_id: str,
        timestamp_ms: int | float,
        name: str,
        args: dict[str, PrimitiveArg] | None = None,
    ) -> None:
        normalized_args = normalize_tool_args(args) if args is not None else None
        self.record_step(
            step_id=step_id,
            event_type="tool_call",
            timestamp_ms=timestamp_ms,
            name=name,
            args=normalized_args,
        )

    def record_tool_output(
        self,
        *,
        step_id: str,
        timestamp_ms: int | float,
        name: str,
    ) -> None:
        self.record_step(
            step_id=step_id,
            event_type="tool_output",
            timestamp_ms=timestamp_ms,
            name=name,
        )

    def record_run_end(self, *, step_id: str, timestamp_ms: int | float) -> None:
        self.record_step(
            step_id=step_id,
            event_type="run_end",
            timestamp_ms=timestamp_ms,
        )

    def record_step(
        self,
        *,
        step_id: str,
        event_type: str,
        timestamp_ms: int | float,
        name: str | None = None,
        total_tokens: int | float | None = None,
        args: dict[str, PrimitiveArg] | None = None,
    ) -> None:
        if not step_id:
            msg = "step_id must be non-empty"
            raise ValueError(msg)
        if step_id in self._step_ids:
            msg = f"Duplicate capture step id: {step_id}"
            raise ValueError(msg)
        if not event_type:
            msg = "event_type must be non-empty"
            raise ValueError(msg)
        if isinstance(timestamp_ms, bool) or not isinstance(timestamp_ms, (int, float)):
            msg = "timestamp_ms must be numeric"
            raise ValueError(msg)
        if total_tokens is not None and (
            isinstance(total_tokens, bool) or not isinstance(total_tokens, (int, float))
        ):
            msg = "total_tokens must be numeric when provided"
            raise ValueError(msg)
        if args is not None and event_type != "tool_call":
            msg = "args are only supported on tool_call steps"
            raise ValueError(msg)

        self._steps.append(
            CaptureStep(
                id=step_id,
                event_type=event_type,
                timestamp_ms=timestamp_ms,
                name=name,
                total_tokens=total_tokens,
                args=args,
            )
        )
        self._step_ids.add(step_id)

    def record_read(self, *, source: str, target: str) -> None:
        if source not in self._step_ids or target not in self._step_ids:
            msg = "read edges must reference existing step ids"
            raise ValueError(msg)
        self._reads.append(CaptureRead(source=source, target=target))

    def to_payload(self) -> dict[str, object]:
        return {
            "format_version": CAPTURE_EVENT_LOG_VERSION,
            "run_id": self._run_id,
            "steps": [step.to_dict() for step in self._steps],
            "reads": [read.to_dict() for read in self._reads],
        }

    def write_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_payload(), indent=2) + "\n", encoding="utf-8"
        )
        return path
