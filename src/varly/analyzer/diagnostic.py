"""Diagnostic artifacts produced by verification."""

from __future__ import annotations

from dataclasses import dataclass

from varly.core.types import NodeId, TraceId


@dataclass(frozen=True, slots=True)
class Violation:
    """A single invariant violation with explanatory evidence."""

    invariant_id: str
    message: str
    node_id: NodeId | None = None


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Deterministic verification result for a trace against a contract."""

    trace_id: TraceId
    passed: bool
    violations: tuple[Violation, ...]

    @property
    def violation_count(self) -> int:
        return len(self.violations)
