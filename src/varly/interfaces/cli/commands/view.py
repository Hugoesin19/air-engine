"""Local diagnostic viewer — serve HTML report in the browser."""

from __future__ import annotations

import argparse
import http.server
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path

from varly.analyzer import verify_trace
from varly.contracts import load_policy_file
from varly.core.errors import VarlyError
from varly.interfaces.library.api import TraceSource, load_trace
from varly.interfaces.viewer.report import write_viewer_report

VIEWER_DIR = Path(__file__).resolve().parents[2] / "viewer"
REPORT_FILE = ".report.json"
DEFAULT_PORT = 8765


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "view",
        help="Open the local diagnostic viewer in a browser",
    )
    parser.add_argument(
        "diagnostic_file",
        nargs="?",
        type=Path,
        help="Diagnostic JSON from verify --output (optional if --trace is set)",
    )
    parser.add_argument(
        "--trace",
        type=Path,
        help="Trace or capture file to verify before viewing",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Contract policy (required with --trace)",
    )
    parser.add_argument(
        "--source",
        choices=["air", "capture", "langgraph", "openai"],
        default="air",
        help="Adapter when using --trace",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Local port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open a browser tab automatically",
    )
    parser.set_defaults(handler=run)


def prepare_report(
    *,
    diagnostic_file: Path | None,
    trace_file: Path | None,
    contract_file: Path | None,
    source: TraceSource,
) -> Path:
    """Write the report JSON next to the viewer assets. Returns viewer directory."""
    if not VIEWER_DIR.is_dir():
        msg = f"Viewer assets not found: {VIEWER_DIR}"
        raise FileNotFoundError(msg)

    dest = VIEWER_DIR / REPORT_FILE
    if trace_file is not None:
        if contract_file is None:
            msg = "--contract is required when using --trace"
            raise ValueError(msg)
        trace = load_trace(trace_file, source=source)
        contract = load_policy_file(contract_file)
        diagnostic = verify_trace(trace, contract)
        write_viewer_report(
            diagnostic,
            trace,
            dest,
            trace_file=trace_file,
            contract_file=contract_file,
            source=source,
        )
        return VIEWER_DIR

    if diagnostic_file is None:
        msg = "Provide diagnostic_file or --trace with --contract"
        raise ValueError(msg)

    dest.write_text(
        diagnostic_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return VIEWER_DIR


def serve_viewer(
    *,
    directory: Path,
    port: int,
    open_browser: bool,
) -> None:
    """Start a local HTTP server for the static viewer."""
    viewer_root = str(directory)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(
            self,
            request: socket.socket,
            client_address: tuple[str, int],
            server: socketserver.BaseServer,
        ) -> None:
            super().__init__(request, client_address, server, directory=viewer_root)

        def log_message(self, format: str, *args: object) -> None:
            return

    url = f"http://127.0.0.1:{port}/"
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"varly viewer at {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nViewer stopped.")


def run(args: argparse.Namespace) -> int:
    try:
        directory = prepare_report(
            diagnostic_file=args.diagnostic_file,
            trace_file=args.trace,
            contract_file=args.contract,
            source=args.source,
        )
    except (VarlyError, OSError, ValueError, FileNotFoundError) as exc:
        print(f"View failed: {exc}", file=sys.stderr)
        return 1

    try:
        serve_viewer(
            directory=directory,
            port=args.port,
            open_browser=not args.no_open,
        )
    except OSError as exc:
        print(f"Unable to start viewer server: {exc}", file=sys.stderr)
        return 1
    return 0
