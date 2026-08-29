"""Diff command: compare current verification against a baseline trace."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from varly.analyzer import compare_diagnostics, verify_trace
from varly.contracts import load_policy_file
from varly.core.errors import VarlyError
from varly.interfaces.library.api import TraceSource, load_trace


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "diff",
        help="Compare current trace violations against a baseline (regression gate)",
    )
    parser.add_argument(
        "baseline_file",
        type=Path,
        help="Path to the baseline trace or capture log",
    )
    parser.add_argument(
        "current_file",
        type=Path,
        help="Path to the current trace or capture log",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        required=True,
        help="Path to the contract policy YAML or JSON file",
    )
    parser.add_argument(
        "--source",
        choices=["air", "capture", "langgraph", "openai"],
        default="air",
        help="Adapter for the current file (and baseline unless --baseline-source)",
    )
    parser.add_argument(
        "--baseline-source",
        choices=["air", "capture", "langgraph", "openai"],
        default=None,
        help="Adapter for the baseline file (defaults to --source)",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    baseline_file: Path = args.baseline_file
    current_file: Path = args.current_file
    contract_file: Path = args.contract
    current_source: TraceSource = args.source
    baseline_source: TraceSource = args.baseline_source or current_source
    try:
        contract = load_policy_file(contract_file)
        baseline_trace = load_trace(baseline_file, source=baseline_source)
        current_trace = load_trace(current_file, source=current_source)
        baseline = verify_trace(baseline_trace, contract)
        current = verify_trace(current_trace, contract)
        diff = compare_diagnostics(baseline, current)
    except VarlyError as exc:
        print(f"Diff failed: {exc}", file=sys.stderr)
        return 1

    print(f"baseline: {baseline_file} ({diff.baseline_trace_id})")
    print(f"current:  {current_file} ({diff.current_trace_id})")
    print(f"  unchanged: {len(diff.unchanged)}")
    print(f"  removed:   {diff.removed_count}")
    print(f"  added:     {diff.added_count}")

    for violation in diff.removed:
        location = (
            f" (node: {violation.node_id})" if violation.node_id is not None else ""
        )
        print(f"  - resolved [{violation.invariant_id}]{location}: {violation.message}")

    if not diff.is_regression:
        print("NO REGRESSION")
        return 0

    print("REGRESSION: new violations vs baseline", file=sys.stderr)
    for violation in diff.added:
        location = (
            f" (node: {violation.node_id})" if violation.node_id is not None else ""
        )
        print(
            f"  + [{violation.invariant_id}]{location}: {violation.message}",
            file=sys.stderr,
        )
    return 1
