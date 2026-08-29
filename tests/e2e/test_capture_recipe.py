"""E2E: capture recipe produces a verifiable log."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECIPE_SCRIPT = ROOT / "examples" / "capture_recipe" / "run.py"
CAPTURE = ROOT / "examples" / "capture_recipe" / "artifacts" / "run.json"
POLICY = ROOT / "examples" / "policies" / "mvp.yaml"


def test_capture_recipe_verify_passes() -> None:
    subprocess.run(
        [sys.executable, str(RECIPE_SCRIPT)],
        cwd=ROOT,
        check=True,
    )
    assert CAPTURE.is_file()

    verify = subprocess.run(
        [
            sys.executable,
            "-m",
            "air_engine.interfaces.cli.main",
            "verify",
            str(CAPTURE),
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
