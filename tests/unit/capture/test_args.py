"""Tests for tool argument capture helpers."""

from __future__ import annotations

import pytest

from varly.capture.args import (
    args_from_json_label,
    args_to_json_label,
    normalize_tool_args,
    parse_tool_input_string,
)


def test_normalize_tool_args_accepts_primitives() -> None:
    assert normalize_tool_args({"query": "x", "limit": 3, "debug": False}) == {
        "query": "x",
        "limit": 3,
        "debug": False,
    }


def test_normalize_tool_args_rejects_nested_values() -> None:
    with pytest.raises(ValueError, match="primitive"):
        normalize_tool_args({"query": {"nested": True}})


def test_parse_tool_input_string_json_object() -> None:
    assert parse_tool_input_string('{"query": "paris"}') == {"query": "paris"}


def test_parse_tool_input_string_plain_text() -> None:
    assert parse_tool_input_string("paris") == {"input": "paris"}


def test_args_json_label_round_trip() -> None:
    args = {"endpoint": "https://api.example.com/search", "query": "x"}
    label = args_to_json_label(args)
    assert args_from_json_label(label) == args
