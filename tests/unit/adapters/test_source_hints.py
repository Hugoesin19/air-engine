"""Tests for trace source detection hints."""

from __future__ import annotations

from pathlib import Path

import pytest

from air_engine.adapters._source_hints import detect_trace_source, wrong_source_message
from air_engine.adapters.errors import UnsupportedFormatError
from air_engine.adapters.json.adapter import load_external_json
from air_engine.interfaces.library.api import load_trace

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def test_detect_capture_log() -> None:
    mock_run = EXAMPLES / "demo_agent" / "artifacts" / "mock_run.json"
    payload = load_external_json(mock_run)
    assert detect_trace_source(payload) == "capture"


def test_detect_air_trace() -> None:
    payload = load_external_json(EXAMPLES / "trace_valid_minimal.json")
    assert detect_trace_source(payload) == "air"


def test_detect_openai_responses() -> None:
    payload = load_external_json(
        EXAMPLES / "fixtures" / "recorded" / "openai_responses_search.json"
    )
    assert detect_trace_source(payload) == "openai"


def test_wrong_source_message_format() -> None:
    msg = wrong_source_message("run.json", used="air", detected="capture")
    assert "--source capture" in msg
    assert "run.json" in msg


def test_load_trace_hints_when_source_is_wrong() -> None:
    path = EXAMPLES / "demo_agent" / "artifacts" / "mock_run.json"
    with pytest.raises(UnsupportedFormatError, match="looks like a capture trace"):
        load_trace(path, source="air")
