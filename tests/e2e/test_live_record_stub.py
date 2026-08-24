"""Tests for the optional live-recording stub (no network)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "examples" / "live" / "record_run.py"


def test_live_stub_refuses_without_opt_in() -> None:
    env = {key: value for key, value in os.environ.items() if key != "AIR_ENGINE_LIVE"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 2
    assert "AIR_ENGINE_LIVE=1" in result.stderr


def test_live_stub_requires_api_key_when_opted_in() -> None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"AIR_ENGINE_LIVE", "OPENAI_API_KEY"}
    }
    env["AIR_ENGINE_LIVE"] = "1"
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 1
    assert "OPENAI_API_KEY" in result.stderr


def test_live_stub_does_not_call_api_when_key_present() -> None:
    env = {key: value for key, value in os.environ.items()}
    env["AIR_ENGINE_LIVE"] = "1"
    env["OPENAI_API_KEY"] = "sk-test-not-a-real-key"
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "does not call" in result.stdout
