"""Tests for the local diagnostic viewer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from air_engine.interfaces.cli.commands.view import (
    REPORT_FILE,
    VIEWER_DIR,
    prepare_report,
)
from air_engine.interfaces.library import verify

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
POLICY = EXAMPLES / "policies" / "mvp.yaml"
MOCK_CAPTURE = EXAMPLES / "demo_agent" / "artifacts" / "mock_run.json"


@pytest.fixture(autouse=True)
def _cleanup_report() -> None:
    yield
    report = VIEWER_DIR / REPORT_FILE
    if report.exists():
        report.unlink()


def test_prepare_report_from_trace() -> None:
    directory = prepare_report(
        diagnostic_file=None,
        trace_file=MOCK_CAPTURE,
        contract_file=POLICY,
        source="capture",
    )
    report_path = directory / REPORT_FILE
    assert report_path.is_file()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    assert payload["violation_count"] == 0
    assert "summary" in payload
    assert "timeline" in payload
    assert payload["summary"]["llm_calls"] >= 1


def test_prepare_report_from_diagnostic_file(tmp_path: Path) -> None:
    diagnostic = verify(MOCK_CAPTURE, POLICY, source="capture")
    diag_path = tmp_path / "diag.json"
    diag_path.write_text(
        json.dumps(
            {
                "diagnostic_schema_version": "1.0.0",
                "trace_id": str(diagnostic.trace_id),
                "passed": diagnostic.passed,
                "violation_count": diagnostic.violation_count,
                "violations": [],
            }
        ),
        encoding="utf-8",
    )
    prepare_report(
        diagnostic_file=diag_path,
        trace_file=None,
        contract_file=None,
        source="air",
    )
    assert (VIEWER_DIR / REPORT_FILE).is_file()


def test_viewer_index_is_served(tmp_path: Path) -> None:
    prepare_report(
        diagnostic_file=None,
        trace_file=MOCK_CAPTURE,
        contract_file=POLICY,
        source="capture",
    )
    index = VIEWER_DIR / "index.html"
    assert index.is_file()
    assert "diagnostic viewer" in index.read_text(encoding="utf-8").lower()
