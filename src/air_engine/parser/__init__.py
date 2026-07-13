"""AIR trace parser: JSON deserialization and structural validation."""

from air_engine.parser.builder import build_trace
from air_engine.parser.errors import ParseError, SchemaValidationError
from air_engine.parser.json_loader import (
    load_json_object,
    parse_trace_file,
    parse_trace_payload,
)
from air_engine.parser.schema import validate_payload_schema

__all__ = [
    "ParseError",
    "SchemaValidationError",
    "build_trace",
    "load_json_object",
    "parse_trace_file",
    "parse_trace_payload",
    "validate_payload_schema",
]
