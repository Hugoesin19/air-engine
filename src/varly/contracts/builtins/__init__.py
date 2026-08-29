"""Built-in invariant evaluators for the MVP contract catalog."""

from __future__ import annotations

from varly.contracts.builtins.business import BUSINESS_EVALUATORS
from varly.contracts.builtins.metrics import METRICS_EVALUATORS
from varly.contracts.builtins.semantic import SEMANTIC_EVALUATORS
from varly.contracts.builtins.structural import STRUCTURAL_EVALUATORS

BUILTIN_EVALUATORS = {
    **STRUCTURAL_EVALUATORS,
    **SEMANTIC_EVALUATORS,
    **METRICS_EVALUATORS,
    **BUSINESS_EVALUATORS,
}

__all__ = [
    "BUSINESS_EVALUATORS",
    "BUILTIN_EVALUATORS",
    "METRICS_EVALUATORS",
    "SEMANTIC_EVALUATORS",
    "STRUCTURAL_EVALUATORS",
]
