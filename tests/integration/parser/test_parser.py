"""Integration tests for AIR JSON parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from varly.core.errors import CycleDetectedError, UnreachableNodeError
from varly.parser import (
    ParseError,
    SchemaValidationError,
    parse_trace_file,
    parse_trace_payload,
)
from varly.parser.json_loader import load_json_object

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples"


def test_parse_valid_minimal_example_file() -> None:
    trace = parse_trace_file(EXAMPLES_DIR / "trace_valid_minimal.json")
    assert len(trace.nodes) == 5
    assert len(trace.control_edges) == 4
    assert len(trace.referential_edges) == 1


def test_parse_invalid_cycle_example_file() -> None:
    with pytest.raises(CycleDetectedError):
        parse_trace_file(EXAMPLES_DIR / "trace_invalid_cycle.json")


def test_parse_invalid_orphan_example_file() -> None:
    with pytest.raises(UnreachableNodeError):
        parse_trace_file(EXAMPLES_DIR / "trace_invalid_orphan.json")


def test_parse_trace_payload_round_trip() -> None:
    payload = load_json_object(EXAMPLES_DIR / "trace_valid_minimal.json")
    trace = parse_trace_payload(payload)
    assert trace.trace_id == payload["trace_id"]


def test_unsupported_schema_version_raises() -> None:
    payload = load_json_object(EXAMPLES_DIR / "trace_valid_minimal.json")
    payload["air_schema_version"] = "9.9.9"
    with pytest.raises(SchemaValidationError, match="Unsupported air_schema_version"):
        parse_trace_payload(payload)


def test_missing_required_field_raises() -> None:
    payload = load_json_object(EXAMPLES_DIR / "trace_valid_minimal.json")
    del payload["nodes"]
    with pytest.raises(SchemaValidationError, match="Missing required field"):
        parse_trace_payload(payload)


def test_invalid_json_file_raises(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not valid", encoding="utf-8")
    with pytest.raises(ParseError, match="Invalid JSON"):
        parse_trace_file(broken)
