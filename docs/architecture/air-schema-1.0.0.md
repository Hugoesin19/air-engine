# AIR Schema 1.0.0

Minimal JSON serialization format for the Analysis Intermediate Representation (AIR) Trace.

**Status:** Draft (MVP Sprint 0)  
**Version:** `1.0.0`  
**Formal model:** Project Bible Part VI · [ADR-001](../adrs/001-air-immutable.md) · [ADR-003](../adrs/003-two-edge-domains.md)

---

## Overview

A Trace is a **finite, immutable, closed universe** representing one completed execution:

```
T = (V, E_c, E_r, λ_V, λ_E)
```

In JSON, semantic labeling (`λ_V`, `λ_E`) is materialized as `labels` on nodes and `kind` on edges.

---

## Top-Level Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `air_schema_version` | string | yes | Must be `"1.0.0"` for this spec |
| `trace_id` | string | yes | Unique trace identifier (UUIDv7 recommended) |
| `root_id` | string | yes | ID of the unique causal root node |
| `nodes` | array | yes | Non-empty list of nodes |
| `control_edges` | array | yes | Control causality edges (`E_c`) |
| `referential_edges` | array | yes | Information reference edges (`E_r`) |

---

## Node

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Globally unique node ID (UUIDv7 recommended) |
| `labels` | object | yes | Semantic projection `λ_V(v)` — arbitrary JSON object |

The structural node has no intrinsic meaning; semantics live only in `labels`.

### Recommended label keys (non-normative for 1.0.0)

| Key | Example | Purpose |
|-----|---------|---------|
| `semantic_type` | `"semantic"` | Layer-2 type classification |
| `event_type` | `"tool_call"` | Domain event name |
| `name` | `"search"` | Human-readable identifier |

---

## Control Edge (`E_c`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique edge ID |
| `source` | string | yes | Origin node ID |
| `target` | string | yes | Destination node ID |
| `kind` | string | yes | One of: `causes`, `invokes`, `produces`, `contains` |

**Invariant:** `(V, E_c)` must be a DAG with a single root reachable to all nodes.

---

## Referential Edge (`E_r`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique edge ID |
| `source` | string | yes | Origin node ID |
| `target` | string | yes | Destination node ID |
| `kind` | string | yes | One of: `reads`, `writes`, `references` |

**Invariant:** `E_r` may contain cycles. It must not alter the partial order of `E_c`.

---

## Structural Axioms (validated before analysis)

1. **Unique identity** — all node and edge IDs are unique within the trace.
2. **Closed references** — every edge `source`/`target` references an existing node.
3. **Single root** — `root_id` exists and has zero incoming `E_c` edges.
4. **DAG** — `E_c` is acyclic.
5. **Reachability** — every node is reachable from `root_id` via `E_c`.
6. **Disjoint edge identity** — control and referential edge IDs do not overlap.

---

## Example Files

| File | Purpose |
|------|---------|
| [`examples/trace_valid_minimal.json`](../../examples/trace_valid_minimal.json) | Minimal valid trace |
| [`examples/trace_invalid_cycle.json`](../../examples/trace_invalid_cycle.json) | Violates DAG axiom |
| [`examples/trace_invalid_orphan.json`](../../examples/trace_invalid_orphan.json) | Violates reachability axiom |

---

## Evolution

Schema 1.0.0 allows **additive** changes only (new label keys, new edge kinds). Breaking changes require a new schema version and a new ADR.
