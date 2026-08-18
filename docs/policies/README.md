# Policy Packs

Ready-made contract policies for common verification scenarios. Swap the policy file only — no code changes required.

## Available packs

| File | Use case | Metric limits |
|------|----------|---------------|
| [`mvp.yaml`](../../examples/policies/mvp.yaml) | Default CI / balanced gate | 10 s duration, 10 000 tokens |
| [`strict.yaml`](../../examples/policies/strict.yaml) | Tight production guardrails | 500 ms duration, 100 tokens |
| [`dev.yaml`](../../examples/policies/dev.yaml) | Local development / debugging | 1 h duration, 1 000 000 tokens |

All packs include the same structural and semantic invariants; only metric thresholds differ.

## Usage

```bash
# Strict gate (fails on trace_valid_minimal.json — 600 ms, 150 tokens)
uv run air-engine verify examples/trace_valid_minimal.json \
  --contract examples/policies/strict.yaml

# Relaxed local gate
uv run air-engine verify examples/trace_valid_minimal.json \
  --contract examples/policies/dev.yaml

# Export structured diagnostic for CI parsers
uv run air-engine verify examples/trace_valid_minimal.json \
  --contract examples/policies/mvp.yaml \
  --output diagnostic.json
```

Programmatic:

```python
from pathlib import Path
from air_engine.interfaces.library import verify, write_diagnostic_json

diagnostic = verify("trace.json", "examples/policies/strict.yaml")
write_diagnostic_json(diagnostic, Path("diagnostic.json"))
```

---

## Policy file format

```yaml
air_schema_version: "1.0.0"
invariants:
  - id: <invariant_id>
    params:        # optional, required for metric invariants
      <key>: <value>
```

- `air_schema_version` must be `"1.0.0"`.
- `invariants` is an ordered list; every listed invariant is evaluated.
- `params` values must be JSON primitives (string, number, boolean, or null).

---

## Built-in invariants

### Structural (no params)

| ID | Description | Failure signal |
|----|-------------|----------------|
| `no_causal_cycles` | Control edges `E_c` form a DAG | Cycle detected at a node |
| `root_reachability` | Every node reachable from `root_id` via `E_c` | Unreachable node ID |
| `no_orphans` | Alias of `root_reachability` | Same as above |

### Semantic (no params)

| ID | Description | Failure signal |
|----|-------------|----------------|
| `tool_call_has_return` | Each `tool_call` node has a downstream `tool_return` with matching `name` via `E_c` | ToolCall node without return |

### Metrics (params required)

| ID | Param | Type | Description |
|----|-------|------|-------------|
| `max_trace_duration` | `max_ms` | number (≥ 0) | Max wall-clock span from `timestamp_ms` labels across all nodes |
| `token_budget` | `max_tokens` | number (≥ 0) | Max sum of `tokens` labels on `llm_invoke` nodes |

#### Example

```yaml
invariants:
  - id: max_trace_duration
    params:
      max_ms: 5000
  - id: token_budget
    params:
      max_tokens: 2000
```

---

## Choosing a pack

| Scenario | Recommended pack |
|----------|------------------|
| PR gate on agent fixtures | `mvp.yaml` |
| Cost/latency regression detection | `strict.yaml` |
| Iterating locally with verbose agents | `dev.yaml` |
| Custom business rules | Copy a pack and edit `invariants` |

See also: [Diagnostic JSON schema](../architecture/diagnostic-schema-1.0.0.md) for `--output` format.
