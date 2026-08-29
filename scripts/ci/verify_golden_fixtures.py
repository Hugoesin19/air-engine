"""Verify golden trace fixtures using stable CLI exit codes."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "examples" / "policies" / "mvp.yaml"
CLI = [sys.executable, "-m", "varly.interfaces.cli.main"]


@dataclass(frozen=True, slots=True)
class FixtureCase:
    name: str
    trace: Path
    source: str
    expect_validate: int | None
    expect_verify: int | None
    contract: Path = POLICY


FIXTURES: tuple[FixtureCase, ...] = (
    FixtureCase(
        name="valid_air_trace",
        trace=ROOT / "examples" / "trace_valid_minimal.json",
        source="air",
        expect_validate=0,
        expect_verify=0,
    ),
    FixtureCase(
        name="invalid_cycle_trace",
        trace=ROOT / "examples" / "trace_invalid_cycle.json",
        source="air",
        expect_validate=1,
        expect_verify=None,
    ),
    FixtureCase(
        name="invalid_orphan_trace",
        trace=ROOT / "examples" / "trace_invalid_orphan.json",
        source="air",
        expect_validate=1,
        expect_verify=None,
    ),
    FixtureCase(
        name="invalid_missing_tool_return",
        trace=ROOT / "examples" / "trace_invalid_missing_tool_return.json",
        source="air",
        expect_validate=0,
        expect_verify=1,
    ),
    FixtureCase(
        name="langgraph_adapter_fixture",
        trace=ROOT / "examples" / "langgraph_run_minimal.json",
        source="langgraph",
        expect_validate=None,
        expect_verify=0,
    ),
    FixtureCase(
        name="openai_adapter_fixture",
        trace=ROOT / "examples" / "openai_run_minimal.json",
        source="openai",
        expect_validate=None,
        expect_verify=0,
    ),
    FixtureCase(
        name="valid_trace_strict_policy",
        trace=ROOT / "examples" / "trace_valid_minimal.json",
        source="air",
        expect_validate=None,
        expect_verify=1,
        contract=ROOT / "examples" / "policies" / "strict.yaml",
    ),
    FixtureCase(
        name="valid_trace_dev_policy",
        trace=ROOT / "examples" / "trace_valid_minimal.json",
        source="air",
        expect_validate=None,
        expect_verify=0,
        contract=ROOT / "examples" / "policies" / "dev.yaml",
    ),
    FixtureCase(
        name="recorded_openai_responses",
        trace=ROOT
        / "examples"
        / "fixtures"
        / "recorded"
        / "openai_responses_search.json",
        source="openai",
        expect_validate=None,
        expect_verify=0,
    ),
    FixtureCase(
        name="recorded_langgraph_callbacks",
        trace=ROOT
        / "examples"
        / "fixtures"
        / "recorded"
        / "langgraph_callbacks_search.json",
        source="langgraph",
        expect_validate=None,
        expect_verify=0,
    ),
    FixtureCase(
        name="cookbook_rag_shaped_capture",
        trace=ROOT / "examples" / "cookbook" / "artifacts" / "rag_shaped_run.json",
        source="capture",
        expect_validate=None,
        expect_verify=0,
        contract=ROOT / "examples" / "policies" / "rag.yaml",
    ),
)


def _run_cli(args: list[str]) -> int:
    result = subprocess.run(CLI + args, cwd=ROOT, check=False)
    return int(result.returncode)


def verify_fixtures() -> list[str]:
    failures: list[str] = []

    for case in FIXTURES:
        if case.expect_validate is not None:
            exit_code = _run_cli(["validate", str(case.trace)])
            if exit_code != case.expect_validate:
                failures.append(
                    f"{case.name}: validate expected "
                    f"{case.expect_validate}, got {exit_code}"
                )

        if case.expect_verify is not None:
            exit_code = _run_cli(
                [
                    "verify",
                    str(case.trace),
                    "--contract",
                    str(case.contract),
                    "--source",
                    case.source,
                ]
            )
            if exit_code != case.expect_verify:
                failures.append(
                    f"{case.name}: verify expected "
                    f"{case.expect_verify}, got {exit_code}"
                )

    return failures


def verify_diff_gates() -> list[str]:
    failures: list[str] = []
    baseline = ROOT / "examples" / "trace_valid_minimal.json"
    broken = ROOT / "examples" / "trace_invalid_missing_tool_return.json"

    same = _run_cli(["diff", str(baseline), str(baseline), "--contract", str(POLICY)])
    if same != 0:
        failures.append(f"diff_same_baseline: expected 0, got {same}")

    worse = _run_cli(["diff", str(baseline), str(broken), "--contract", str(POLICY)])
    if worse != 1:
        failures.append(f"diff_broken_vs_baseline: expected 1, got {worse}")

    return failures


def main() -> int:
    failures = verify_fixtures() + verify_diff_gates()
    if failures:
        print("Golden fixture verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    total = len(FIXTURES) + 2
    print(f"Golden fixture verification passed ({total} cases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
