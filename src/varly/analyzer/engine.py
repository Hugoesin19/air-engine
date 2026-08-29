"""Verification engine orchestration (Layer 3)."""

from __future__ import annotations

from varly.analyzer.diagnostic import Diagnostic
from varly.analyzer.evaluator import evaluate_contract
from varly.contracts.model import Contract
from varly.core.trace import Trace


def verify_trace(trace: Trace, contract: Contract) -> Diagnostic:
    """Verify a trace against a contract and return a deterministic diagnostic."""
    violations = evaluate_contract(trace, contract)
    return Diagnostic(
        trace_id=trace.trace_id,
        passed=not violations,
        violations=violations,
    )
