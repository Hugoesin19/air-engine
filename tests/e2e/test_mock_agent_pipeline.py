"""End-to-end tests for the mock agent capture pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from air_engine.interfaces.library import load_trace, verify

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
DEMO_AGENT = EXAMPLES_DIR / "demo_agent" / "run.py"
POLICY = EXAMPLES_DIR / "policies" / "mvp.yaml"


def test_mock_agent_pipeline_generates_verifiable_capture_log(tmp_path: Path) -> None:
    output = tmp_path / "mock_run.json"
    result = subprocess.run(
        [sys.executable, str(DEMO_AGENT), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output.exists()

    diagnostic = verify(output, POLICY, source="capture")
    assert diagnostic.passed is True

    trace = load_trace(output, source="capture")
    event_types = [node.labels["event_type"] for node in trace.nodes]
    assert event_types == [
        "run_start",
        "llm_invoke",
        "tool_call",
        "tool_return",
        "run_end",
    ]
