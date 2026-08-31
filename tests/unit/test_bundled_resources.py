"""Tests for bundled PyPI wheel resources."""

from __future__ import annotations

import pytest

from varly.resources import bundled_fixture, bundled_policy


@pytest.mark.parametrize(
    "name",
    ["mvp", "strict", "dev", "live"],
)
def test_bundled_policies_exist(name: str) -> None:
    path = bundled_policy(name)
    assert path.is_file()
    assert path.suffix == ".yaml"


@pytest.mark.parametrize(
    "name",
    [
        "mock_run",
        "trace_valid_minimal",
        "trace_invalid_missing_tool_return",
    ],
)
def test_bundled_fixtures_exist(name: str) -> None:
    path = bundled_fixture(name)
    assert path.is_file()
    assert path.suffix == ".json"


def test_unknown_bundled_policy_raises() -> None:
    with pytest.raises(ValueError, match="Unknown bundled policy"):
        bundled_policy("does-not-exist")


def test_unknown_bundled_fixture_raises() -> None:
    with pytest.raises(ValueError, match="Unknown bundled fixture"):
        bundled_fixture("does-not-exist")
