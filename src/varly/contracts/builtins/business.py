"""Business-rule invariant evaluators."""

from __future__ import annotations

from collections.abc import Callable

from varly.capture.args import args_from_json_label
from varly.contracts.errors import InvalidInvariantParamError
from varly.contracts.model import InvariantSpec
from varly.core.ordering import canonical_linear_extension
from varly.core.trace import Trace
from varly.core.types import NodeId, SemanticLabels

InvariantEvaluator = Callable[[Trace, InvariantSpec], tuple[str, ...]]

_LLM_INVOKE = "llm_invoke"
_TOOL_CALL = "tool_call"


def _require_int_param(spec: InvariantSpec, key: str) -> int:
    value = spec.params.get(key)
    if value is None:
        msg = f"Invariant {spec.id!r} requires param {key!r}"
        raise InvalidInvariantParamError(msg)
    if not isinstance(value, int) or isinstance(value, bool):
        msg = f"Invariant {spec.id!r} param {key!r} must be an integer"
        raise InvalidInvariantParamError(msg)
    if value < 0:
        msg = f"Invariant {spec.id!r} param {key!r} must be non-negative"
        raise InvalidInvariantParamError(msg)
    return value


def _require_string_tuple(spec: InvariantSpec, key: str) -> tuple[str, ...]:
    value = spec.params.get(key)
    if value is None:
        msg = f"Invariant {spec.id!r} requires param {key!r}"
        raise InvalidInvariantParamError(msg)
    if isinstance(value, str) or not isinstance(value, tuple) or not value:
        msg = f"Invariant {spec.id!r} param {key!r} must be a non-empty list"
        raise InvalidInvariantParamError(msg)
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            msg = (
                f"Invariant {spec.id!r} param {key!r}[{index}] "
                "must be a non-empty string"
            )
            raise InvalidInvariantParamError(msg)
        items.append(item)
    return tuple(items)


def _event_type(labels: SemanticLabels) -> str | None:
    event_type = labels.get("event_type")
    return event_type if isinstance(event_type, str) else None


def _tool_name(labels: SemanticLabels) -> str | None:
    name = labels.get("name")
    return name if isinstance(name, str) else None


def _canonical_nodes(trace: Trace) -> tuple[NodeId, ...]:
    try:
        return canonical_linear_extension(trace, trace.node_ids)
    except ValueError:
        return ()


def _count_event_overflow(
    trace: Trace,
    event_type: str,
    max_count: int,
    noun: str,
) -> tuple[str, ...]:
    nodes_by_id = {node.id: node for node in trace.nodes}
    ordered = _canonical_nodes(trace) or tuple(node.id for node in trace.nodes)
    count = 0
    for node_id in ordered:
        node = nodes_by_id[node_id]
        if _event_type(node.labels) != event_type:
            continue
        count += 1
        if count > max_count:
            message = f"{noun} count {count} exceeds max {max_count} at node: {node_id}"
            return (message,)
    return ()


def evaluate_max_llm_invocations(
    trace: Trace,
    spec: InvariantSpec,
) -> tuple[str, ...]:
    """Fail when the number of ``llm_invoke`` nodes exceeds ``max``."""
    max_count = _require_int_param(spec, "max")
    return _count_event_overflow(trace, _LLM_INVOKE, max_count, "LLM invocation")


def evaluate_max_tool_calls(trace: Trace, spec: InvariantSpec) -> tuple[str, ...]:
    """Fail when the number of ``tool_call`` nodes exceeds ``max``."""
    max_count = _require_int_param(spec, "max")
    return _count_event_overflow(trace, _TOOL_CALL, max_count, "Tool call")


def evaluate_tool_name_allowlist(
    trace: Trace,
    spec: InvariantSpec,
) -> tuple[str, ...]:
    """Fail when a ``tool_call`` name is missing or not in ``allowed``."""
    allowed = _require_string_tuple(spec, "allowed")
    allowed_set = frozenset(allowed)
    messages: list[str] = []
    for node in trace.nodes:
        if _event_type(node.labels) != _TOOL_CALL:
            continue
        name = _tool_name(node.labels)
        if name is None:
            messages.append(f"ToolCall is missing name label at node: {node.id}")
            continue
        if name not in allowed_set:
            messages.append(
                f"ToolCall name {name!r} is not in allowlist at node: {node.id}"
            )
    return tuple(messages)


def _is_subsequence(needle: tuple[str, ...], haystack: tuple[str, ...]) -> bool:
    iterator = iter(haystack)
    return all(any(item == current for current in iterator) for item in needle)


def evaluate_required_event_sequence(
    trace: Trace,
    spec: InvariantSpec,
) -> tuple[str, ...]:
    """Fail when ``sequence`` is not a subsequence of canonical event types."""
    sequence = _require_string_tuple(spec, "sequence")
    nodes_by_id = {node.id: node for node in trace.nodes}
    ordered = _canonical_nodes(trace)
    if not ordered:
        ordered = tuple(node.id for node in trace.nodes)
    events: list[str] = []
    for node_id in ordered:
        event_type = _event_type(nodes_by_id[node_id].labels)
        if event_type is not None:
            events.append(event_type)
    if _is_subsequence(sequence, tuple(events)):
        return ()
    rendered = ", ".join(sequence)
    message = f"Required event sequence [{rendered}] is not present in canonical order"
    return (message,)


def _require_scalar_param(
    spec: InvariantSpec, key: str
) -> str | int | float | bool | None:
    value = spec.params.get(key)
    if value is None:
        msg = f"Invariant {spec.id!r} requires param {key!r}"
        raise InvalidInvariantParamError(msg)
    if not isinstance(value, (str, int, float, bool)):
        msg = f"Invariant {spec.id!r} param {key!r} must be a primitive JSON value"
        raise InvalidInvariantParamError(msg)
    return value


def evaluate_tool_args_keys_allowlist(
    trace: Trace,
    spec: InvariantSpec,
) -> tuple[str, ...]:
    """Fail when a ``tool_call`` includes argument keys outside ``allowed``."""
    allowed = _require_string_tuple(spec, "allowed")
    allowed_set = frozenset(allowed)
    messages: list[str] = []
    for node in trace.nodes:
        if _event_type(node.labels) != _TOOL_CALL:
            continue
        args = args_from_json_label(node.labels.get("args_json"))
        if args is None:
            continue
        for key in args:
            if key not in allowed_set:
                messages.append(
                    f"ToolCall arg key {key!r} is not in allowlist at node: {node.id}"
                )
    return tuple(messages)


def evaluate_tool_arg_equals(
    trace: Trace,
    spec: InvariantSpec,
) -> tuple[str, ...]:
    """Fail when a ``tool_call`` arg ``key`` is missing or not equal to ``value``."""
    key = _require_scalar_param(spec, "key")
    if not isinstance(key, str) or not key:
        msg = f"Invariant {spec.id!r} param 'key' must be a non-empty string"
        raise InvalidInvariantParamError(msg)
    expected = _require_scalar_param(spec, "value")
    messages: list[str] = []
    for node in trace.nodes:
        if _event_type(node.labels) != _TOOL_CALL:
            continue
        args = args_from_json_label(node.labels.get("args_json"))
        if args is None:
            messages.append(
                "ToolCall is missing args_json for required key "
                f"{key!r} at node: {node.id}"
            )
            continue
        if key not in args:
            messages.append(f"ToolCall arg {key!r} is missing at node: {node.id}")
            continue
        if args[key] != expected:
            messages.append(
                f"ToolCall arg {key!r}={args[key]!r} expected {expected!r} "
                f"at node: {node.id}"
            )
    return tuple(messages)


BUSINESS_EVALUATORS: dict[str, InvariantEvaluator] = {
    "max_llm_invocations": evaluate_max_llm_invocations,
    "max_tool_calls": evaluate_max_tool_calls,
    "tool_name_allowlist": evaluate_tool_name_allowlist,
    "tool_args_keys_allowlist": evaluate_tool_args_keys_allowlist,
    "tool_arg_equals": evaluate_tool_arg_equals,
    "required_event_sequence": evaluate_required_event_sequence,
}
