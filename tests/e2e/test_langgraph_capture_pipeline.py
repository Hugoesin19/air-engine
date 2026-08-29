"""End-to-end tests for the LangGraph automatic capture pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("langgraph")

from varly.interfaces.library import load_trace, verify

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
LANGGRAPH_CAPTURE = EXAMPLES_DIR / "langgraph_capture" / "run.py"
POLICY = EXAMPLES_DIR / "policies" / "mvp.yaml"


def test_langgraph_capture_pipeline_exports_verifiable_trace(tmp_path: Path) -> None:
    output = tmp_path / "langgraph_run.json"
    result = subprocess.run(
        [sys.executable, str(LANGGRAPH_CAPTURE), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output.exists()

    diagnostic = verify(output, POLICY, source="langgraph")
    assert diagnostic.passed is True

    trace = load_trace(output, source="langgraph")
    event_types = [node.labels["event_type"] for node in trace.nodes]
    assert "run_start" in event_types
    assert "llm_invoke" in event_types
    assert "tool_return" in event_types
    assert "run_end" in event_types
