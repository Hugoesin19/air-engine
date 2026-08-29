"""Deterministic mock agent that emits a capture event log."""

from __future__ import annotations

import argparse
from pathlib import Path

from varly.capture import RunRecorder

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "artifacts" / "mock_run.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a deterministic mock agent and write a capture log.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to the capture log JSON file",
    )
    return parser


def run(output: Path) -> Path:
    recorder = RunRecorder(run_id="demo-run-01930000-0001")
    recorder.record_run_start(step_id="demo-step-010", timestamp_ms=0)
    recorder.record_llm_call(
        step_id="demo-step-011",
        timestamp_ms=100,
        total_tokens=150,
    )
    recorder.record_tool_call(
        step_id="demo-step-012",
        timestamp_ms=200,
        name="search",
    )
    recorder.record_tool_output(
        step_id="demo-step-013",
        timestamp_ms=500,
        name="search",
    )
    recorder.record_run_end(step_id="demo-step-014", timestamp_ms=600)
    recorder.record_read(source="demo-step-012", target="demo-step-011")
    return recorder.write_json(output)


def main() -> None:
    args = build_parser().parse_args()
    output = run(args.output)
    print(f"Mock agent run written to: {output}")


if __name__ == "__main__":
    main()
