"""Metric invariant evaluators."""

from __future__ import annotations

from collections.abc import Callable

from air_engine.contracts.errors import InvalidInvariantParamError
from air_engine.contracts.model import InvariantSpec
from air_engine.core.trace import Trace
from air_engine.core.types import LabelValue, SemanticLabels

InvariantEvaluator = Callable[[Trace, InvariantSpec], tuple[str, ...]]

_LLM_INVOKE = "llm_invoke"
_TIMESTAMP_KEY = "timestamp_ms"
_TOKENS_KEY = "tokens"


def _require_numeric_param(spec: InvariantSpec, key: str) -> float:
    value = spec.params.get(key)
    if value is None:
        msg = f"Invariant {spec.id!r} requires param {key!r}"
        raise InvalidInvariantParamError(msg)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        msg = f"Invariant {spec.id!r} param {key!r} must be a number"
        raise InvalidInvariantParamError(msg)
    if value < 0:
        msg = f"Invariant {spec.id!r} param {key!r} must be non-negative"
        raise InvalidInvariantParamError(msg)
    return float(value)


def _numeric_label(labels: SemanticLabels, key: str) -> float | None:
    value: LabelValue = labels.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def evaluate_max_trace_duration(trace: Trace, spec: InvariantSpec) -> tuple[str, ...]:
    """Fail when trace wall-clock span exceeds ``max_ms``."""
    max_ms = _require_numeric_param(spec, "max_ms")
    timestamps = [
        ts
        for node in trace.nodes
        if (ts := _numeric_label(node.labels, _TIMESTAMP_KEY)) is not None
    ]
    if not timestamps:
        return ()

    duration_ms = max(timestamps) - min(timestamps)
    if duration_ms <= max_ms:
        return ()
    message = (
        f"Trace duration {duration_ms}ms exceeds limit {max_ms}ms "
        f"(from {_TIMESTAMP_KEY} labels)"
    )
    return (message,)


def evaluate_token_budget(trace: Trace, spec: InvariantSpec) -> tuple[str, ...]:
    """Fail when summed LLM token usage exceeds ``max_tokens``."""
    max_tokens = _require_numeric_param(spec, "max_tokens")
    total_tokens = 0.0
    counted_nodes = 0

    for node in trace.nodes:
        if node.labels.get("event_type") != _LLM_INVOKE:
            continue
        tokens = _numeric_label(node.labels, _TOKENS_KEY)
        if tokens is None:
            continue
        total_tokens += tokens
        counted_nodes += 1

    if counted_nodes == 0 or total_tokens <= max_tokens:
        return ()
    total_display = (
        int(total_tokens) if total_tokens.is_integer() else total_tokens
    )
    budget_display = int(max_tokens) if max_tokens.is_integer() else max_tokens
    message = (
        f"Token usage {total_display} exceeds budget {budget_display}"
    )
    return (message,)


METRICS_EVALUATORS: dict[str, InvariantEvaluator] = {
    "max_trace_duration": evaluate_max_trace_duration,
    "token_budget": evaluate_token_budget,
}
