"""Verify multiple trace files against one policy (team CI helper)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = [sys.executable, "-m", "varly.interfaces.cli.main"]


@dataclass(frozen=True, slots=True)
class BatchResult:
    path: Path
    exit_code: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify multiple traces against one contract policy.",
    )
    parser.add_argument(
        "trace_files",
        nargs="+",
        type=Path,
        help="Trace or capture JSON files to verify",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        required=True,
        help="Contract policy YAML or JSON",
    )
    parser.add_argument(
        "--source",
        choices=["air", "capture", "langgraph", "openai"],
        default="air",
        help="Adapter for all trace files",
    )
    return parser


def verify_one(trace: Path, *, contract: Path, source: str) -> BatchResult:
    exit_code = subprocess.run(
        CLI
        + [
            "verify",
            str(trace),
            "--contract",
            str(contract),
            "--source",
            source,
        ],
        cwd=ROOT,
        check=False,
    ).returncode
    return BatchResult(path=trace, exit_code=int(exit_code))


def run_batch(
    trace_files: list[Path],
    *,
    contract: Path,
    source: str,
) -> list[BatchResult]:
    return [
        verify_one(trace, contract=contract, source=source) for trace in trace_files
    ]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_batch(
        args.trace_files,
        contract=args.contract,
        source=args.source,
    )
    passed = sum(result.exit_code == 0 for result in results)
    failed = len(results) - passed

    for result in results:
        status = "PASS" if result.exit_code == 0 else "FAIL"
        print(f"{status}: {result.path}")

    print(f"Batch verify: {passed} passed, {failed} failed (of {len(results)})")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
