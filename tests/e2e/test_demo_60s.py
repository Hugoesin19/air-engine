"""E2E: 60-second onboarding demo script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "scripts" / "demo_60s.py"


def test_demo_60s_script_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Demo complete" in result.stdout
