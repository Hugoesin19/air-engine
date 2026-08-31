# Capture Event Log 1.0.0

Deterministic serialization format for **recorded agent runs** before they are
translated into AIR.

**Status:** Draft (Sprint 6)  
**Version:** `1.0.0`  
**Formal role:** Capture-side event log consumed by adapters, not by the core
verification engine directly.

---

## Overview

The capture layer writes a **framework-neutral ordered event log**:

```
L = (run_id, steps, reads)
```

This log is:

- **append-only** during recording,
- **serializable** to JSON,
- **deterministic** for replay fixtures,
- **external** to AIR.

AIR is still the verification representation. Capture logs are only an ingress
format.

---

## Top-Level Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format_version` | string | yes | Must be `"capture-event-log-1.0.0"` |
| `run_id` | string | yes | Stable execution identifier |
| `steps` | array | yes | Ordered list of recorded execution steps |
| `reads` | array | yes | Explicit information reads between step IDs |

---

## Step

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique step identifier |
| `event_type` | string | yes | Recorded event name |
| `timestamp_ms` | number | yes | Wall-clock offset in milliseconds |
| `name` | string | no | Human-readable tool or resource name |
| `total_tokens` | number | no | Token usage for LLM calls |
| `args` | object | no | Primitive JSON map of tool call arguments (`tool_call` only) |

### Supported `event_type` values in 1.0.0

- `run_start`
- `llm_call`
- `tool_call`
- `tool_output`
- `run_end`

These names are intentionally close to adapter-facing event names so a thin
translation layer can reuse the existing sequential adapter pipeline.

---

## Read Edge

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | Step that performed the read |
| `target` | string | yes | Step whose information was read |

Reads are informational only. They become referential AIR edges (`E_r`) during
adaptation and must never impose new control causality.

---

## Invariants

The capture log enforces only **light structural rules**:

1. `steps` is non-empty.
2. Step IDs are unique.
3. `steps` remains in observed execution order.
4. `reads[*].source` and `reads[*].target` reference existing step IDs.

AIR axioms such as single root, DAG validation, and reachability remain the
responsibility of the AIR parser / verifier pipeline.

---

## Relationship to AIR

The flow is:

```
Mock Agent / Runtime
    ↓
Capture Event Log 1.0.0
    ↓
Capture Adapter
    ↓
AIR Trace 1.0.0
    ↓
Verification
```

This preserves the Project Bible layering:

- capture records facts,
- adapters translate formats,
- AIR remains the canonical analysis representation.

---

## Example

```json
{
  "format_version": "capture-event-log-1.0.0",
  "run_id": "demo-run-001",
  "steps": [
    {"id": "s1", "event_type": "run_start", "timestamp_ms": 0},
    {"id": "s2", "event_type": "llm_call", "timestamp_ms": 100, "total_tokens": 150},
    {"id": "s3", "event_type": "tool_call", "timestamp_ms": 200, "name": "search"},
    {"id": "s4", "event_type": "tool_output", "timestamp_ms": 500, "name": "search"},
    {"id": "s5", "event_type": "run_end", "timestamp_ms": 600}
  ],
  "reads": [
    {"source": "s3", "target": "s2"}
  ]
}
```
