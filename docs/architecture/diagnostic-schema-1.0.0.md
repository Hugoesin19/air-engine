# Diagnostic Schema 1.0.0

JSON serialization format for verification **Diagnostics** produced by air-engine.

**Status:** Draft (Product Sprint 8)  
**Version:** `1.0.0`  
**Producer:** `air-engine verify --output` · library `write_diagnostic_json()`

---

## Overview

A Diagnostic is a **deterministic, immutable result** of evaluating one AIR Trace against one Contract policy. It contains no trace payload — only pass/fail status and violation evidence.

```
Diagnostic = (trace_id, passed, violations[])
```

Violations are ordered by contract invariant declaration order, then by message order within each invariant.

---

## Top-Level Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `diagnostic_schema_version` | string | yes | Must be `"1.0.0"` for this spec |
| `trace_id` | string | yes | Trace identifier from the verified AIR trace |
| `passed` | boolean | yes | `true` when `violation_count` is 0 |
| `violation_count` | integer | yes | Number of violations (≥ 0) |
| `violations` | array | yes | List of violation objects (empty when passed) |

---

## Violation Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `invariant_id` | string | yes | Contract invariant that failed (e.g. `max_trace_duration`) |
| `message` | string | yes | Human-readable evidence string |
| `node_id` | string \| null | yes | Related node when applicable; `null` for trace-level violations |

---

## Example — PASS

```json
{
  "diagnostic_schema_version": "1.0.0",
  "trace_id": "01930000-0000-7000-8000-000000000001",
  "passed": true,
  "violation_count": 0,
  "violations": []
}
```

## Example — FAIL

```json
{
  "diagnostic_schema_version": "1.0.0",
  "trace_id": "01930000-0000-7000-8000-000000000001",
  "passed": false,
  "violation_count": 2,
  "violations": [
    {
      "invariant_id": "max_trace_duration",
      "message": "Trace duration 600ms exceeds limit 500ms (from timestamp_ms labels)",
      "node_id": null
    },
    {
      "invariant_id": "token_budget",
      "message": "Token usage 150 exceeds budget 100",
      "node_id": null
    }
  ]
}
```

---

## CLI usage

```bash
uv run air-engine verify trace.json \
  --contract examples/policies/strict.yaml \
  --output diagnostic.json
```

- Exit code `0` when `passed` is `true`; exit code `1` when `passed` is `false`.
- The diagnostic file is written on both pass and fail (unless verification errors before evaluation).

---

## Library usage

```python
from pathlib import Path
from air_engine.interfaces.library import verify, write_diagnostic_json

diagnostic = verify("trace.json", "policy.yaml")
write_diagnostic_json(diagnostic, Path("diagnostic.json"))
```

---

## Determinism guarantees

Given the same trace bytes and contract policy:

1. Violation set is identical across runs.
2. Violation order is stable (contract order → message order).
3. JSON field order follows the schema table above.

---

## Related documents

- [Policy packs reference](../policies/README.md)
- [AIR Schema 1.0.0](air-schema-1.0.0.md)
- [Product Roadmap](../PRODUCT_ROADMAP.md)
