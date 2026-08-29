"""E2E: pilot diff regression gate (baseline vs broken)."""

from __future__ import annotations

from pathlib import Path

from varly.interfaces.cli.main import run

PILOT_DIR = Path(__file__).resolve().parents[2] / "pilot"
POLICY = PILOT_DIR / "policies" / "live.yaml"
BASELINE = PILOT_DIR / "artifacts" / "baseline_research_run.json"
BROKEN = PILOT_DIR / "artifacts" / "broken_research_run.json"
CURRENT = PILOT_DIR / "artifacts" / "research_run.json"


def test_pilot_diff_same_baseline_not_regression() -> None:
    exit_code = run(
        [
            "diff",
            str(BASELINE),
            str(BASELINE),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 0


def test_pilot_diff_broken_capture_is_regression() -> None:
    exit_code = run(
        [
            "diff",
            str(BASELINE),
            str(BROKEN),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 1


def test_pilot_current_matches_baseline_not_regression() -> None:
    exit_code = run(
        [
            "diff",
            str(BASELINE),
            str(CURRENT),
            "--contract",
            str(POLICY),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 0
