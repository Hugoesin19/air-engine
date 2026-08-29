"""CLI integration tests for verify command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from varly.interfaces.cli.main import run

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_cli_verify_passes_on_valid_trace() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policy_mvp.yaml"),
        ],
    )
    assert exit_code == 0


def test_cli_verify_fails_on_missing_contract() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "does_not_exist.yaml"),
        ],
    )
    assert exit_code == 1


def test_cli_verify_capture_source_passes_on_mock_run() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "demo_agent" / "artifacts" / "mock_run.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "mvp.yaml"),
            "--source",
            "capture",
        ],
    )
    assert exit_code == 0


def test_cli_verify_demo_flag_passes() -> None:
    exit_code = run(["verify", "--demo"])
    assert exit_code == 0


def test_cli_verify_requires_contract_without_demo() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
        ],
    )
    assert exit_code == 2


def test_cli_verify_output_writes_diagnostic_json(tmp_path: Path) -> None:
    output = tmp_path / "diagnostic.json"
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "mvp.yaml"),
            "--output",
            str(output),
        ],
    )
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    assert payload["diagnostic_schema_version"] == "1.0.0"
    assert payload["violation_count"] == 0


def test_cli_verify_output_on_failure(tmp_path: Path) -> None:
    output = tmp_path / "diagnostic.json"
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "strict.yaml"),
            "--output",
            str(output),
        ],
    )
    assert exit_code == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["passed"] is False
    assert payload["violation_count"] >= 1


def test_cli_verify_format_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "mvp.yaml"),
            "--format",
            "json",
        ],
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["passed"] is True
    assert payload["diagnostic_schema_version"] == "1.0.0"


def test_cli_verify_format_junit_on_failure(tmp_path: Path) -> None:
    output = tmp_path / "report.xml"
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "strict.yaml"),
            "--format",
            "junit",
            "--output",
            str(output),
        ],
    )
    assert exit_code == 1
    xml = output.read_text(encoding="utf-8")
    assert "<testsuite" in xml
    assert 'failures="' in xml
    assert "max_trace_duration" in xml


def test_cli_verify_format_sarif_on_failure(tmp_path: Path) -> None:
    output = tmp_path / "report.sarif"
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_valid_minimal.json"),
            "--contract",
            str(EXAMPLES_DIR / "policies" / "strict.yaml"),
            "--format",
            "sarif",
            "--output",
            str(output),
        ],
    )
    assert exit_code == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["results"]
