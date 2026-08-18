"""Serialize verification diagnostics to JSON."""

from __future__ import annotations

import json
from pathlib import Path

from air_engine.analyzer.diagnostic import Diagnostic

DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"


def diagnostic_to_dict(diagnostic: Diagnostic) -> dict[str, object]:
    """Convert a diagnostic to a JSON-serializable mapping."""
    return {
        "diagnostic_schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "trace_id": str(diagnostic.trace_id),
        "passed": diagnostic.passed,
        "violation_count": diagnostic.violation_count,
        "violations": [
            {
                "invariant_id": violation.invariant_id,
                "message": violation.message,
                "node_id": (
                    str(violation.node_id) if violation.node_id is not None else None
                ),
            }
            for violation in diagnostic.violations
        ],
    }


def diagnostic_to_json(diagnostic: Diagnostic, *, indent: int = 2) -> str:
    """Serialize a diagnostic to a formatted JSON string."""
    return json.dumps(
        diagnostic_to_dict(diagnostic),
        indent=indent,
        ensure_ascii=False,
    )


def write_diagnostic_json(diagnostic: Diagnostic, path: Path | str) -> None:
    """Write a diagnostic JSON artifact to disk."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{diagnostic_to_json(diagnostic)}\n", encoding="utf-8")
