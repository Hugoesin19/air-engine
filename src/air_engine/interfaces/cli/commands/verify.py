"""Verify command for the air-engine CLI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from air_engine.analyzer import verify_trace
from air_engine.analyzer.reports import (
    ReportFormat,
    github_error_annotations,
    render_report,
    write_report,
)
from air_engine.contracts import load_policy_file
from air_engine.core.errors import AirEngineError
from air_engine.interfaces.cli.render import render_control_dag, summarize_trace_metrics
from air_engine.interfaces.library.api import TraceSource, load_trace

_MACHINE_FORMATS = ("json", "junit", "sarif")


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "verify",
        help="Verify an AIR trace against a contract policy",
    )
    parser.add_argument(
        "trace_file",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the AIR trace JSON file (omit when using --demo)",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=None,
        help="Path to the contract policy YAML or JSON file",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Verify the bundled mock capture and mvp policy (pip install smoke test)",
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
        "--format",
        choices=["text", "json", "junit", "sarif"],
        default="text",
        dest="report_format",
        help="Stdout report format (text, json, junit, or sarif)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write a diagnostic report to this file",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    if args.demo:
        from air_engine.resources import bundled_fixture, bundled_policy

        trace_file: Path = bundled_fixture("mock_run")
        contract_file: Path = bundled_policy("mvp")
        source: TraceSource = "capture"
    else:
        if args.trace_file is None or args.contract is None:
            print(
                "verify requires trace_file and --contract (or use --demo)",
                file=sys.stderr,
            )
            return 2
        trace_file = args.trace_file
        contract_file = args.contract
        source = args.source
    report_format: str = args.report_format
    try:
        trace = load_trace(trace_file, source=source)
        contract = load_policy_file(contract_file)
        diagnostic = verify_trace(trace, contract)
    except AirEngineError as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    if args.output is not None:
        file_format: ReportFormat = "json"
        if report_format == "junit":
            file_format = "junit"
        elif report_format == "sarif":
            file_format = "sarif"
        elif report_format == "json":
            file_format = "json"
        try:
            write_report(diagnostic, args.output, fmt=file_format)
        except OSError as exc:
            print(f"Unable to write diagnostic: {exc}", file=sys.stderr)
            return 1

    if os.environ.get("GITHUB_ACTIONS") == "true":
        for line in github_error_annotations(diagnostic):
            print(line, file=sys.stderr)

    if report_format in _MACHINE_FORMATS:
        machine_format: ReportFormat = (
            "junit"
            if report_format == "junit"
            else "sarif"
            if report_format == "sarif"
            else "json"
        )
        print(render_report(diagnostic, machine_format))
        return 0 if diagnostic.passed else 1

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
