"""End-to-end MVP pipeline tests."""

from __future__ import annotations

from pathlib import Path

from air_engine.analyzer import verify_trace
from air_engine.contracts import load_policy_file
from air_engine.core import NodeId, reconstruct_state
from air_engine.interfaces.cli.main import run
from air_engine.parser import parse_trace_file

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_mvp_pipeline_valid_trace_passes_full_policy() -> None:
    trace_path = EXAMPLES_DIR / "trace_valid_minimal.json"
    policy_path = EXAMPLES_DIR / "policy_mvp.yaml"

    trace = parse_trace_file(trace_path)
    contract = load_policy_file(policy_path)

    tool_call = NodeId("01930000-0000-7000-8000-000000000012")
    state = reconstruct_state(trace, tool_call)
    assert [event.labels["event_type"] for event in state.events] == [
        "run_start",
        "llm_invoke",
        "tool_call",
    ]

    first = verify_trace(trace, contract)
    second = verify_trace(trace, contract)
    assert first.passed is True
    assert first == second


def test_mvp_pipeline_semantic_failure_via_cli() -> None:
    exit_code = run(
        [
            "verify",
            str(EXAMPLES_DIR / "trace_invalid_missing_tool_return.json"),
            "--contract",
            str(EXAMPLES_DIR / "policy_mvp.yaml"),
        ],
    )
    assert exit_code == 1


def test_mvp_pipeline_validate_and_verify_cli() -> None:
    trace_path = EXAMPLES_DIR / "trace_valid_minimal.json"
    policy_path = EXAMPLES_DIR / "policy_mvp.yaml"

    validate_code = run(["validate", str(trace_path)])
    verify_code = run(["verify", str(trace_path), "--contract", str(policy_path)])

    assert validate_code == 0
    assert verify_code == 0
