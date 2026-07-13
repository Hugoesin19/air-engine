"""Validate command for the air-engine CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from air_engine.core.errors import AirEngineError
from air_engine.parser import parse_trace_file


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
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    trace_file: Path = args.trace_file
    try:
        trace = parse_trace_file(trace_file)
    except AirEngineError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    node_count = len(trace.nodes)
    control_count = len(trace.control_edges)
    referential_count = len(trace.referential_edges)
    print(f"Valid AIR trace: {trace_file}")
    print(f"  trace_id: {trace.trace_id}")
    print(f"  nodes: {node_count}")
    print(f"  control_edges: {control_count}")
    print(f"  referential_edges: {referential_count}")
    return 0
