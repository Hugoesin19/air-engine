# Baseline traces (regression gate)

Keep a **known-good** AIR (or capture) file in the repo and fail CI when a new run introduces violations that the baseline did not have.

This is the Sprint 12 workflow: same contract, two traces, deterministic violation-set diff.

## Command

```bash
# No new violations → exit 0
uv run varly diff \
  examples/trace_valid_minimal.json \
  examples/trace_valid_minimal.json \
  --contract examples/policies/mvp.yaml

# Broken fixture vs golden baseline → exit 1 (REGRESSION)
uv run varly diff \
  examples/trace_valid_minimal.json \
  examples/trace_invalid_missing_tool_return.json \
  --contract examples/policies/mvp.yaml
```

Adapters:

```bash
uv run varly diff baseline.json current.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

`--baseline-source` overrides the adapter for the first file only (defaults to `--source`).

## What counts as a regression

A violation is identified by `(invariant_id, message, node_id)`.

| Change | Gate |
|--------|------|
| New keys in current | **Fail** (`REGRESSION`) |
| Keys only in baseline (fixed) | Pass (`NO REGRESSION`) |
| Same set | Pass |

Resolved issues are printed as `resolved` but do not fail the command.

## Team workflow

1. Commit a golden trace (`examples/trace_valid_minimal.json` or a recorded fixture).
2. On each PR, generate or check in the current run.
3. Run `varly diff baseline current --contract policies/mvp.yaml`.
4. Update the baseline **only** when the team accepts a new contract or a legitimate behavior change.

Library:

```python
from varly.interfaces.library import compare_traces

diff = compare_traces("baseline.json", "current.json", "examples/policies/mvp.yaml")
assert not diff.is_regression
```
