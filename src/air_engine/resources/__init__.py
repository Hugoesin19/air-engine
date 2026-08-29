"""Bundled policies and fixtures shipped with the PyPI wheel."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def bundled_policy(name: str = "mvp") -> Path:
    """Return a policy YAML file shipped inside the package."""
    return Path(str(files("air_engine.resources.policies") / f"{name}.yaml"))


def bundled_fixture(name: str = "mock_run") -> Path:
    """Return a fixture JSON file shipped inside the package."""
    return Path(str(files("air_engine.resources.fixtures") / f"{name}.json"))
