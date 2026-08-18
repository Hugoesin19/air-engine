"""Built-in invariant evaluators for the MVP contract catalog."""

from __future__ import annotations

from air_engine.contracts.builtins.business import BUSINESS_EVALUATORS
from air_engine.contracts.builtins.metrics import METRICS_EVALUATORS
from air_engine.contracts.builtins.semantic import SEMANTIC_EVALUATORS
from air_engine.contracts.builtins.structural import STRUCTURAL_EVALUATORS

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
