"""Validate command for the varly CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from varly.core.errors import VarlyError
from varly.interfaces.cli.render import render_control_dag, summarize_trace_metrics
from varly.parser import parse_trace_file


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "validate",
        help="Validate an AIR trace JSON file",
    )
    parser.add_argument(
        "trace_file",
        type=Path,
        help="Path to the AIR trace JSON file",
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
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    trace_file: Path = args.trace_file
    try:
        trace = parse_trace_file(trace_file)
    except VarlyError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Valid AIR trace: {trace_file}")
    print(f"  trace_id: {trace.trace_id}")
    print(summarize_trace_metrics(trace))

    if args.show_dag:
        print("  control_dag:")
        for line in render_control_dag(trace).splitlines():
            print(f"    {line}")
    return 0
