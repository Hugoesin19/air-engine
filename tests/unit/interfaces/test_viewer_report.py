"""Tests for viewer report enrichment."""

from __future__ import annotations

from pathlib import Path

from varly.interfaces.library import verify
from varly.interfaces.viewer.report import (
    build_viewer_report,
    trace_summary,
    trace_timeline,
)

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"
MOCK_CAPTURE = EXAMPLES / "demo_agent" / "artifacts" / "mock_run.json"
POLICY = EXAMPLES / "policies" / "mvp.yaml"


def test_trace_summary_and_timeline_from_mock_capture() -> None:
    from varly.interfaces.library.api import load_trace

    trace = load_trace(MOCK_CAPTURE, source="capture")
    summary = trace_summary(trace)
    timeline = trace_timeline(trace)

    assert summary["steps"] == len(trace.nodes)
    assert summary["llm_calls"] >= 1
    assert summary["tool_calls"] >= 1
    assert len(timeline) == len(trace.nodes)
    assert timeline[0]["event_type"] == "run_start"
    assert timeline[-1]["event_type"] == "run_end"


def test_build_viewer_report_includes_summary() -> None:
    diagnostic = verify(MOCK_CAPTURE, POLICY, source="capture")
    from varly.interfaces.library.api import load_trace

    trace = load_trace(MOCK_CAPTURE, source="capture")
    report = build_viewer_report(
        diagnostic,
        trace,
        trace_file=MOCK_CAPTURE,
        contract_file=POLICY,
        source="capture",
    )
    assert report["passed"] is True
    assert "summary" in report
    assert "timeline" in report
    assert "causal_graph" in report
    assert report["meta"]["source"] == "capture"
