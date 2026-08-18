"""Verify golden trace fixtures using stable CLI exit codes."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "examples" / "policies" / "mvp.yaml"
CLI = [sys.executable, "-m", "air_engine.interfaces.cli.main"]


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


def main() -> int:
    failures = verify_fixtures()
    if failures:
        print("Golden fixture verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(f"Golden fixture verification passed ({len(FIXTURES)} cases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
