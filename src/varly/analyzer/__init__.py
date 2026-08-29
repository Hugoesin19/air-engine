"""Analysis and derived computations over AIR traces."""

from varly.analyzer.diagnostic import Diagnostic, Violation
from varly.analyzer.diff import DiagnosticDiff, compare_diagnostics
from varly.analyzer.engine import verify_trace
from varly.analyzer.export import (
    DIAGNOSTIC_SCHEMA_VERSION,
    diagnostic_to_dict,
    diagnostic_to_json,
    write_diagnostic_json,
)
from varly.analyzer.reports import (
    diagnostic_to_junit,
    diagnostic_to_sarif,
    write_report,
)
from varly.analyzer.state_builder import build_state_at_node

__all__ = [
    "DIAGNOSTIC_SCHEMA_VERSION",
    "Diagnostic",
    "DiagnosticDiff",
    "Violation",
    "build_state_at_node",
    "compare_diagnostics",
    "diagnostic_to_dict",
    "diagnostic_to_json",
    "diagnostic_to_junit",
    "diagnostic_to_sarif",
    "verify_trace",
    "write_diagnostic_json",
    "write_report",
]
