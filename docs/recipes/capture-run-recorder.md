# Recipe: Capture with RunRecorder

**Goal:** Produce a verifiable `run.json` from **any Python agent** in ~10 minutes.  
**Stack:** `varly.capture.RunRecorder` → `verify --source capture`  
**Cost:** Zero API calls (this recipe uses a deterministic mock agent).

For LangGraph/OpenAI **file export** paths, see [architecture mappings](../architecture/README.md).  
This recipe is the zero-dependency path proven in the [pilot](../../pilot/README.md).

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Clone of [varly](https://github.com/Hugoesin19/air-engine)

```bash
git clone https://github.com/Hugoesin19/air-engine.git
cd varly
uv sync
```

---

## Step 1 — Run the template (see it work)

```bash
uv run python examples/capture_recipe/run.py
uv run varly verify examples/capture_recipe/artifacts/run.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

Expect `PASS` and `violations: 0`.

The template lives at [`examples/capture_recipe/run.py`](../../examples/capture_recipe/run.py).  
Read the `# HOOK:` comments — that is where you wire your real agent.

---

## Step 2 — Copy into your project

Copy these pieces:

1. `from varly.capture import RunRecorder` (after `uv sync` in your env)
2. The hook pattern from `run.py` (start → LLM → tool → tool output → end)
3. `recorder.write_json(path)` at the end

Minimal skeleton:

```python
from pathlib import Path
from varly.capture import RunRecorder

recorder = RunRecorder(run_id="my-run-001")

# HOOK: run start
recorder.record_run_start(step_id="step-001", timestamp_ms=0)

# HOOK: after each LLM response (use real token count when available)
recorder.record_llm_call(step_id="step-002", timestamp_ms=100, total_tokens=150)

# HOOK: before tool execution
recorder.record_tool_call(step_id="step-003", timestamp_ms=200, name="search")

# HOOK: after tool returns
recorder.record_tool_output(step_id="step-004", timestamp_ms=500, name="search")

# HOOK: optional causal read (tool used LLM output)
recorder.record_read(source="step-003", target="step-002")

# HOOK: run end
recorder.record_run_end(step_id="step-005", timestamp_ms=600)

recorder.write_json(Path("run.json"))
```

**Rules:**

| Rule | Why |
|------|-----|
| Unique `step_id` per event | Duplicate IDs raise `ValueError` |
| `name` on tools must match policy allowlist | e.g. `mvp.yaml` allows `search` only |
| Every `tool_call` needs a `tool_output` | Or `tool_call_has_return` fails |
| Use `timestamp_ms` in order | Duration invariants use first→last timestamp |

---

## Step 3 — Verify

```bash
uv run varly verify run.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

| Result | Meaning |
|--------|---------|
| `PASS` | No contract violations |
| `FAIL` | Read violation list; fix capture or policy |

**Live LLM runs** often exceed the mvp 10s duration cap. Use a relaxed policy (see [`pilot/policies/live.yaml`](../../pilot/policies/live.yaml)) or tune `max_trace_duration` in your contract.

---

## Step 4 — Regression gate (optional)

Keep a known-good `run.json` as baseline:

```bash
uv run varly diff baseline.json current.json \
  --contract examples/policies/mvp.yaml \
  --source capture
```

See [Baseline workflow](../workflows/baseline.md).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Unsupported capture format_version` | Use `RunRecorder`; do not hand-edit `format_version` |
| `tool_call_has_return` | Add `record_tool_output` for each `record_tool_call` |
| `tool_name_allowlist` | Rename tool in capture or add name to policy `allowed` list |
| `max_trace_duration` | Increase `max_ms` in policy or use logical timestamps for tests |
| Wrong adapter | Capture logs need `--source capture`, not `air` or `openai` |

---

## Known limitations (from pilot)

- **Manual hooks** — you call `record_*` at each step; no auto-instrumentation from Gemini/OpenAI SDK yet.
- **No `--source gemini`** — use RunRecorder or export LangGraph/OpenAI JSON (see architecture docs).
- **Policy coupling** — tool names and SLAs live in YAML; align capture with your contract.

---

## Related

- [Capture Event Log spec](../architecture/capture-event-log-1.0.0.md)
- [ADR-006: Capture boundaries](../adrs/006-capture-boundaries.md)
- [Pilot (live Gemini)](../../pilot/README.md)
- [Policy packs](../policies/README.md)
