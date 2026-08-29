"""Capture recipe template — copy the HOOK blocks into your own agent.

Run:
    uv run python examples/capture_recipe/run.py
    uv run air-engine verify examples/capture_recipe/artifacts/run.json \\
        --contract examples/policies/mvp.yaml --source capture
"""

from __future__ import annotations

import argparse
import time
import uuid
from pathlib import Path

from air_engine.capture import RunRecorder

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "artifacts" / "run.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture recipe: write a verifiable event log with RunRecorder.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Where to write the capture JSON",
    )
    return parser


def run_agent(recorder: RunRecorder, *, clock: float) -> str:
    """Simulated agent loop. Replace the HOOK blocks with your real logic."""

    def ts() -> float:
        return round((time.perf_counter() - clock) * 1000, 3)

    # HOOK: call once when your agent run starts
    recorder.record_run_start(step_id="step-001", timestamp_ms=ts())

    # HOOK: after each LLM call (use response.usage.total_tokens when available)
    recorder.record_llm_call(
        step_id="step-002",
        timestamp_ms=ts(),
        total_tokens=120,
    )

    # HOOK: before executing a tool
    tool_name = "search"
    recorder.record_tool_call(
        step_id="step-003",
        timestamp_ms=ts(),
        name=tool_name,
    )

    # HOOK: after the tool returns (same name as tool_call)
    tool_result = "Paris is the capital of France."
    recorder.record_tool_output(
        step_id="step-004",
        timestamp_ms=ts(),
        name=tool_name,
    )

    # HOOK: optional — tool read LLM output (informational edge)
    recorder.record_read(source="step-003", target="step-002")

    # HOOK: second LLM synthesizing the tool result
    recorder.record_llm_call(
        step_id="step-005",
        timestamp_ms=ts(),
        total_tokens=80,
    )
    recorder.record_read(source="step-004", target="step-005")

    # HOOK: call once when your agent run finishes
    recorder.record_run_end(step_id="step-006", timestamp_ms=ts())

    return tool_result


def main() -> None:
    args = build_parser().parse_args()
    run_id = f"capture-recipe-{uuid.uuid4().hex[:8]}"
    recorder = RunRecorder(run_id=run_id)
    started = time.perf_counter()
    run_agent(recorder, clock=started)
    output = recorder.write_json(args.output)
    print(f"Capture written: {output}")
    print(f"run_id: {run_id}")
    print("Verify with:")
    print(
        f"  uv run air-engine verify {output} "
        "--contract examples/policies/mvp.yaml --source capture"
    )


if __name__ == "__main__":
    main()
