"""Analysis and derived computations over AIR traces."""

from air_engine.analyzer.diagnostic import Diagnostic, Violation
from air_engine.analyzer.diff import DiagnosticDiff, compare_diagnostics
from air_engine.analyzer.engine import verify_trace
from air_engine.analyzer.export import (
    DIAGNOSTIC_SCHEMA_VERSION,
    diagnostic_to_dict,
    diagnostic_to_json,
    write_diagnostic_json,
)
from air_engine.analyzer.reports import (
    diagnostic_to_junit,
    diagnostic_to_sarif,
    write_report,
)
from air_engine.analyzer.state_builder import build_state_at_node

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
