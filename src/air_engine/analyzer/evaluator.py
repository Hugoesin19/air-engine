"""Pure evaluation of contract invariants against a trace."""

from __future__ import annotations

import re

from air_engine.analyzer.diagnostic import Violation
from air_engine.contracts.builtins import BUILTIN_EVALUATORS
from air_engine.contracts.errors import UnknownInvariantError
from air_engine.contracts.model import Contract, InvariantSpec
from air_engine.core.trace import Trace
from air_engine.core.types import NodeId

_NODE_ID_PATTERNS = (
    re.compile(r"at node: (\S+)$"),
    re.compile(r"via E_c: (\S+)$"),
    re.compile(r"ToolCall at node: (\S+) has"),
)


def evaluate_invariant(trace: Trace, spec: InvariantSpec) -> tuple[Violation, ...]:
    """Evaluate a single invariant against a trace."""
    evaluator = BUILTIN_EVALUATORS.get(spec.id)
    if evaluator is None:
        msg = f"Unknown invariant id: {spec.id}"
        raise UnknownInvariantError(msg)

    messages = evaluator(trace, spec)
    violations: list[Violation] = []
    for message in messages:
        node_id = _extract_node_id(message)
        violations.append(
            Violation(
                invariant_id=spec.id,
                message=message,
                node_id=node_id,
            )
        )
    return tuple(violations)


def evaluate_contract(trace: Trace, contract: Contract) -> tuple[Violation, ...]:
    """Evaluate all invariants declared in a contract."""
    violations: list[Violation] = []
    for spec in contract.invariants:
        violations.extend(evaluate_invariant(trace, spec))
    return tuple(violations)


def _extract_node_id(message: str) -> NodeId | None:
    for pattern in _NODE_ID_PATTERNS:
        match = pattern.search(message)
        if match is not None:
            return NodeId(match.group(1))
    return None
