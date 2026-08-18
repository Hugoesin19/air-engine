"""Verify command for the air-engine CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from air_engine.analyzer import verify_trace
from air_engine.analyzer.export import write_diagnostic_json
from air_engine.contracts import load_policy_file
from air_engine.core.errors import AirEngineError
from air_engine.interfaces.cli.render import render_control_dag, summarize_trace_metrics
from air_engine.interfaces.library.api import TraceSource, load_trace


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
    parser.add_argument(
        "--show-dag",
        action="store_true",
        help="Print an ASCII render of the control-flow DAG",
    )
    parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Print derived duration and token metrics",
    )
    parser.add_argument(
        "--source",
        choices=["air", "capture", "langgraph", "openai"],
        default="air",
        help="External trace format adapter to use before verification",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the verification diagnostic as JSON to this file",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    trace_file: Path = args.trace_file
    contract_file: Path = args.contract
    source: TraceSource = args.source
    try:
        trace = load_trace(trace_file, source=source)
        contract = load_policy_file(contract_file)
        diagnostic = verify_trace(trace, contract)
    except AirEngineError as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    if args.output is not None:
        try:
            write_diagnostic_json(diagnostic, args.output)
        except OSError as exc:
            print(f"Unable to write diagnostic: {exc}", file=sys.stderr)
            return 1

    if diagnostic.passed:
        print(f"PASS: {trace_file}")
        print(f"  trace_id: {diagnostic.trace_id}")
        print(f"  contract: {contract_file}")
        print("  violations: 0")
        if args.show_metrics:
            print("  metrics:")
            for line in summarize_trace_metrics(trace).splitlines():
                print(f"    {line}")
        if args.show_dag:
            print("  control_dag:")
            for line in render_control_dag(trace).splitlines():
                print(f"    {line}")
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
    if args.show_metrics:
        print("  metrics:", file=sys.stderr)
        for line in summarize_trace_metrics(trace).splitlines():
            print(f"    {line}", file=sys.stderr)
    if args.show_dag:
        print("  control_dag:", file=sys.stderr)
        for line in render_control_dag(trace).splitlines():
            print(f"    {line}", file=sys.stderr)
    return 1
