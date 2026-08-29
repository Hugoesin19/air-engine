"""Parser-specific errors."""

from __future__ import annotations

from varly.core.errors import VarlyError


class ParseError(VarlyError):
    """Raised when trace input cannot be parsed or deserialized."""


class SchemaValidationError(ParseError):
    """Raised when JSON payload violates the AIR schema shape."""
