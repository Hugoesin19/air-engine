"""CI report serializers for verification diagnostics (stdlib only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal
from xml.etree.ElementTree import Element, SubElement, tostring

from varly.analyzer.diagnostic import Diagnostic
from varly.analyzer.export import diagnostic_to_json

ReportFormat = Literal["json", "junit", "sarif"]
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def diagnostic_to_junit(diagnostic: Diagnostic) -> str:
    """Serialize a diagnostic as JUnit XML for CI test summaries."""
    suite = Element(
        "testsuite",
        {
            "name": "varly.verify",
            "tests": str(max(diagnostic.violation_count, 1)),
            "failures": str(diagnostic.violation_count),
            "trace_id": str(diagnostic.trace_id),
        },
    )
    if diagnostic.passed:
        SubElement(
            suite,
            "testcase",
            {
                "classname": "varly.verify",
                "name": str(diagnostic.trace_id),
            },
        )
    else:
        for index, violation in enumerate(diagnostic.violations):
            case = SubElement(
                suite,
                "testcase",
                {
                    "classname": "varly.verify",
                    "name": f"{violation.invariant_id}[{index}]",
                },
            )
            failure = SubElement(
                case,
                "failure",
                {
                    "message": violation.message,
                    "type": violation.invariant_id,
                },
            )
            location = (
                f"node={violation.node_id}"
                if violation.node_id is not None
                else "trace"
            )
            failure.text = f"{violation.invariant_id} ({location}): {violation.message}"

    xml = tostring(suite, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml}\n'


def diagnostic_to_sarif(diagnostic: Diagnostic) -> str:
    """Serialize a diagnostic as SARIF 2.1.0 for code-scanning tabs."""
    rules: list[dict[str, object]] = []
    seen: set[str] = set()
    results: list[dict[str, object]] = []
    for violation in diagnostic.violations:
        if violation.invariant_id not in seen:
            seen.add(violation.invariant_id)
            rules.append(
                {
                    "id": violation.invariant_id,
                    "name": violation.invariant_id,
                    "shortDescription": {"text": violation.invariant_id},
                }
            )
        result: dict[str, object] = {
            "ruleId": violation.invariant_id,
            "level": "error",
            "message": {"text": violation.message},
        }
        if violation.node_id is not None:
            result["locations"] = [
                {"logicalLocations": [{"fullyQualifiedName": str(violation.node_id)}]}
            ]
        results.append(result)

    payload = {
        "version": "2.1.0",
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "varly",
                        "informationUri": "https://github.com/Hugoesin19/varly",
                        "rules": rules,
                    }
                },
                "results": results,
                "invocations": [
                    {
                        "executionSuccessful": diagnostic.passed,
                    }
                ],
            }
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def render_report(diagnostic: Diagnostic, fmt: ReportFormat) -> str:
    """Render a diagnostic in a CI-consumable format."""
    if fmt == "json":
        return diagnostic_to_json(diagnostic)
    if fmt == "junit":
        return diagnostic_to_junit(diagnostic)
    if fmt == "sarif":
        return diagnostic_to_sarif(diagnostic)
    msg = f"Unsupported report format: {fmt!r}"
    raise ValueError(msg)


def write_report(
    diagnostic: Diagnostic,
    path: Path | str,
    *,
    fmt: ReportFormat,
) -> None:
    """Write a diagnostic report (json, junit, or sarif) to disk."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{render_report(diagnostic, fmt).rstrip()}\n", encoding="utf-8")


def github_error_annotations(diagnostic: Diagnostic) -> tuple[str, ...]:
    """GitHub workflow commands so failures appear as check annotations."""
    if diagnostic.passed:
        return ()
    lines: list[str] = []
    for violation in diagnostic.violations:
        title = _escape_github(violation.invariant_id)
        message = _escape_github(violation.message)
        if violation.node_id is not None:
            message = f"{_escape_github(str(violation.node_id))}: {message}"
        lines.append(f"::error title={title}::{message}")
    return tuple(lines)


def _escape_github(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
    )
