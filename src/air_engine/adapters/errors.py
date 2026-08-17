"""Adapter translation errors."""

from __future__ import annotations

from air_engine.core.errors import AirEngineError


class AdapterError(AirEngineError):
    """Base error for adapter translation failures."""


class UnsupportedFormatError(AdapterError):
    """Raised when an external payload format is not recognized."""


class AdapterValidationError(AdapterError):
    """Raised when an external payload is missing required fields."""
