"""Capture-side event log model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

CAPTURE_EVENT_LOG_VERSION = "capture-event-log-1.0.0"


@dataclass(frozen=True, slots=True)
class CaptureStep:
    """A single ordered execution step recorded during runtime."""

    id: str
    event_type: str
    timestamp_ms: int | float
    name: str | None = None
    total_tokens: int | float | None = None
    args: dict[str, Any] | None = field(default=None, compare=False)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(frozen=True, slots=True)
class CaptureRead:
    """Informational read relationship between two recorded steps."""

    source: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target}
