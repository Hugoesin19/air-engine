"""Verify command for the air-engine CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from air_engine.analyzer import verify_trace
from air_engine.contracts import load_policy_file
from air_engine.core.errors import AirEngineError
from air_engine.parser import parse_trace_file


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "verify",
        help="Verify an AIR trace against a contract policy",
    )
    parser.add_argument(
        "trace_file",
        type=Path,
        help="Path to the AIR trace JSON file",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        required=True,
        help="Path to the contract policy YAML or JSON file",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    trace_file: Path = args.trace_file
    contract_file: Path = args.contract
    try:
        trace = parse_trace_file(trace_file)
        contract = load_policy_file(contract_file)
        diagnostic = verify_trace(trace, contract)
    except AirEngineError as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    if diagnostic.passed:
        print(f"PASS: {trace_file}")
        print(f"  trace_id: {diagnostic.trace_id}")
        print(f"  contract: {contract_file}")
        print("  violations: 0")
        return 0

    print(f"FAIL: {trace_file}", file=sys.stderr)
    print(f"  trace_id: {diagnostic.trace_id}", file=sys.stderr)
    print(f"  contract: {contract_file}", file=sys.stderr)
    print(f"  violations: {diagnostic.violation_count}", file=sys.stderr)
    for violation in diagnostic.violations:
        location = (
            f" (node: {violation.node_id})" if violation.node_id is not None else ""
        )
        print(
            f"  - [{violation.invariant_id}]{location}: {violation.message}",
            file=sys.stderr,
        )
    return 1
