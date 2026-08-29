"""Deterministic comparison of verification diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

from varly.analyzer.diagnostic import Diagnostic, Violation
from varly.core.types import TraceId

ViolationKey = tuple[str, str, str | None]


def violation_key(violation: Violation) -> ViolationKey:
    """Stable identity for a violation (invariant, message, node)."""
    node = str(violation.node_id) if violation.node_id is not None else None
    return (violation.invariant_id, violation.message, node)


@dataclass(frozen=True, slots=True)
class DiagnosticDiff:
    """Set difference between baseline and current diagnostics."""

    baseline_trace_id: TraceId
    current_trace_id: TraceId
    added: tuple[Violation, ...]
    removed: tuple[Violation, ...]
    unchanged: tuple[Violation, ...]

    @property
    def is_regression(self) -> bool:
        return len(self.added) > 0

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def _sorted_violations(violations: tuple[Violation, ...]) -> tuple[Violation, ...]:
    return tuple(sorted(violations, key=violation_key))


def compare_diagnostics(
    baseline: Diagnostic,
    current: Diagnostic,
) -> DiagnosticDiff:
    """Return added/removed/unchanged violations in canonical order."""
    baseline_map = {violation_key(item): item for item in baseline.violations}
    current_map = {violation_key(item): item for item in current.violations}
    added_keys = set(current_map) - set(baseline_map)
    removed_keys = set(baseline_map) - set(current_map)
    unchanged_keys = set(baseline_map) & set(current_map)
    return DiagnosticDiff(
        baseline_trace_id=baseline.trace_id,
        current_trace_id=current.trace_id,
        added=_sorted_violations(tuple(current_map[key] for key in added_keys)),
        removed=_sorted_violations(tuple(baseline_map[key] for key in removed_keys)),
        unchanged=_sorted_violations(tuple(current_map[key] for key in unchanged_keys)),
    )
