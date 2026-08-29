"""Adapter translation errors."""

from __future__ import annotations

from varly.core.errors import VarlyError


class AdapterError(VarlyError):
    """Base error for adapter translation failures."""


class UnsupportedFormatError(AdapterError):
    """Raised when an external payload format is not recognized."""


class AdapterValidationError(AdapterError):
    """Raised when an external payload is missing required fields."""
