"""air-engine command-line interface."""

from __future__ import annotations

import argparse

from air_engine.interfaces.cli.commands import diff, validate, verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="air-engine",
        description="Deterministic runtime verification engine for AI agents.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate.register(subparsers)
    verify.register(subparsers)
    diff.register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 2
    return int(handler(args))


if __name__ == "__main__":
    main()
