"""Bundled policies and fixtures shipped with the PyPI wheel."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

_POLICY_NAMES = frozenset({"mvp", "strict", "dev", "live"})
_FIXTURE_NAMES = frozenset(
    {
        "mock_run",
        "trace_valid_minimal",
        "trace_invalid_missing_tool_return",
    },
)


def bundled_policy(name: str = "mvp") -> Path:
    """Return a policy YAML file shipped inside the package."""
    if name not in _POLICY_NAMES:
        msg = f"Unknown bundled policy {name!r}; choose from {sorted(_POLICY_NAMES)}"
        raise ValueError(msg)
    return Path(str(files("varly.resources.policies") / f"{name}.yaml"))


def bundled_fixture(name: str = "mock_run") -> Path:
    """Return a fixture JSON file shipped inside the package."""
    if name not in _FIXTURE_NAMES:
        msg = f"Unknown bundled fixture {name!r}; choose from {sorted(_FIXTURE_NAMES)}"
        raise ValueError(msg)
    return Path(str(files("varly.resources.fixtures") / f"{name}.json"))
