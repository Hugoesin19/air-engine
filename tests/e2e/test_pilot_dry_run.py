"""E2E: pilot dry-run produces a verifiable capture log."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_SCRIPT = ROOT / "pilot" / "gemini_research_assistant" / "run.py"
POLICY = ROOT / "examples" / "policies" / "mvp.yaml"


def _dry_run_env() -> dict[str, str]:
    """Force dry-run even when the developer has PILOT_LIVE=1 in a local `.env`."""
    env = os.environ.copy()
    env["PILOT_LIVE"] = "0"
    env.pop("GOOGLE_API_KEY", None)
    env.pop("GEMINI_API_KEY", None)
    return env


def test_pilot_dry_run_verify_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "dry_run.json"
        subprocess.run(
            [sys.executable, str(PILOT_SCRIPT), "--output", str(output)],
            cwd=ROOT,
            check=True,
            env=_dry_run_env(),
        )
        assert output.is_file()

        verify = subprocess.run(
            [
                sys.executable,
                "-m",
                "air_engine.interfaces.cli.main",
                "verify",
                str(output),
                "--contract",
                str(POLICY),
                "--source",
                "capture",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert verify.returncode == 0, verify.stdout + verify.stderr
        assert "PASS" in verify.stdout
