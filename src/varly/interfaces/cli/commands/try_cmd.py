"""Try command: bundled PASS, FAIL, and regression demo (pip install, no clone)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from varly.interfaces.cli.commands import diff, verify
from varly.resources import bundled_fixture, bundled_policy


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "try",
        help="Run bundled PASS, FAIL, and diff regression demo (no repo clone)",
    )
    parser.set_defaults(handler=run)


def _step(label: str, handler, args: argparse.Namespace, *, expect: int) -> int:
    print(f"\n==> {label}", flush=True)
    exit_code = handler(args)
    if exit_code != expect:
        print(
            f"try failed: expected exit {expect}, got {exit_code}",
            file=sys.stderr,
            flush=True,
        )
        return exit_code
    print(f"    OK (exit {expect})", flush=True)
    return 0


def run(_args: argparse.Namespace) -> int:
    policy: Path = bundled_policy("mvp")
    mock_run: Path = bundled_fixture("mock_run")
    baseline: Path = bundled_fixture("trace_valid_minimal")
    broken: Path = bundled_fixture("trace_invalid_missing_tool_return")

    steps: list[tuple[str, object, argparse.Namespace, int]] = [
        (
            "Verify bundled mock capture (expect PASS)",
            verify.run,
            argparse.Namespace(
                demo=False,
                trace_file=mock_run,
                contract=policy,
                source="capture",
                show_dag=False,
                show_metrics=False,
                report_format="text",
                output=None,
            ),
            0,
        ),
        (
            "Verify broken trace (expect FAIL)",
            verify.run,
            argparse.Namespace(
                demo=False,
                trace_file=broken,
                contract=policy,
                source="air",
                show_dag=False,
                show_metrics=False,
                report_format="text",
                output=None,
            ),
            1,
        ),
        (
            "Diff baseline vs broken (expect REGRESSION)",
            diff.run,
            argparse.Namespace(
                baseline_file=baseline,
                current_file=broken,
                contract=policy,
                source="air",
                baseline_source=None,
            ),
            1,
        ),
        (
            "Diff baseline vs itself (expect NO REGRESSION)",
            diff.run,
            argparse.Namespace(
                baseline_file=baseline,
                current_file=baseline,
                contract=policy,
                source="air",
                baseline_source=None,
            ),
            0,
        ),
    ]

    for label, handler, step_args, expect in steps:
        if _step(label, handler, step_args, expect=expect) != 0:
            return 1

    print(
        "\nTry complete: PASS, FAIL, and REGRESSION behaved as expected.",
        flush=True,
    )
    print("Next: docs/GETTING_STARTED.md - verify your own agent run.", flush=True)
    return 0
