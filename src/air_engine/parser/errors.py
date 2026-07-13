"""Parser-specific errors."""

from __future__ import annotations

from air_engine.core.errors import AirEngineError


class ParseError(AirEngineError):
    """Raised when trace input cannot be parsed or deserialized."""


class SchemaValidationError(ParseError):
    """Raised when JSON payload violates the AIR schema shape."""
