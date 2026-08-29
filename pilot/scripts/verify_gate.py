"""Pilot regression gate: diff current capture against the frozen baseline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "artifacts" / "baseline_research_run.json"
CURRENT = ROOT / "artifacts" / "research_run.json"
POLICY = ROOT / "policies" / "live.yaml"


def main() -> int:
    if not BASELINE.is_file():
        print(f"Missing baseline: {BASELINE}", file=sys.stderr)
        return 1
    if not CURRENT.is_file():
        print(f"Missing current capture: {CURRENT}", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "air_engine.interfaces.cli.main",
        "diff",
        str(BASELINE),
        str(CURRENT),
        "--contract",
        str(POLICY),
        "--source",
        "capture",
    ]
    result = subprocess.run(cmd, cwd=ROOT.parents[0])
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
