"""Contract loading and evaluation errors."""

from __future__ import annotations

from air_engine.core.errors import AirEngineError


class ContractError(AirEngineError):
    """Base error for contract-related failures."""


class ContractLoadError(ContractError):
    """Raised when a contract file cannot be loaded or parsed."""


class UnknownInvariantError(ContractError):
    """Raised when a contract references an unsupported invariant id."""


class InvalidInvariantParamError(ContractError):
    """Raised when an invariant is missing or has invalid parameters."""
