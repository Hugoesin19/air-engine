#!/usr/bin/env python3
"""~60-second demo: mock agent PASS, broken trace FAIL, diff REGRESSION."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "examples" / "policies" / "mvp.yaml"
MOCK_SCRIPT = ROOT / "examples" / "demo_agent" / "run.py"
MOCK_CAPTURE = ROOT / "examples" / "demo_agent" / "artifacts" / "mock_run.json"
BASELINE = ROOT / "examples" / "trace_valid_minimal.json"
BROKEN = ROOT / "examples" / "trace_invalid_missing_tool_return.json"


def _run(cmd: list[str], *, expect: int, label: str) -> None:
    print(f"\n==> {label}")
    print(f"    {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != expect:
        print(
            f"FAILED: expected exit {expect}, got {result.returncode}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"    OK (exit {expect})")


def main() -> int:
    py = sys.executable
    cli = [py, "-m", "air_engine.interfaces.cli.main"]

    _run([py, str(MOCK_SCRIPT)], expect=0, label="Generate mock agent capture")
    _run(
        [
            *cli,
            "verify",
            str(MOCK_CAPTURE),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
        expect=0,
        label="Verify mock capture (expect PASS)",
    )
    _run(
        [
            *cli,
            "verify",
            str(BROKEN),
            "--contract",
            str(POLICY),
        ],
        expect=1,
        label="Verify broken AIR trace (expect FAIL)",
    )
    _run(
        [
            *cli,
            "diff",
            str(BASELINE),
            str(BROKEN),
            "--contract",
            str(POLICY),
        ],
        expect=1,
        label="Diff baseline vs broken (expect REGRESSION)",
    )
    _run(
        [
            *cli,
            "diff",
            str(BASELINE),
            str(BASELINE),
            "--contract",
            str(POLICY),
        ],
        expect=0,
        label="Diff baseline vs itself (expect NO REGRESSION)",
    )

    print("\nDemo complete: PASS, FAIL, and REGRESSION all behaved as expected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
