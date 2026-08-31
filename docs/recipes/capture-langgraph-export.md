# Recipe: LangGraph automatic capture

**Goal:** Export a verifiable trace from a LangGraph/LangChain run **without** manual `record_*` hooks.  
**Stack:** `LangGraphCallbackCollector` → `verify --source langgraph`  
**Cost:** Zero API calls (this recipe uses `FakeListLLM` + a local tool).

For framework-agnostic manual instrumentation, see [capture-run-recorder.md](capture-run-recorder.md).

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- LangGraph optional deps

```bash
git clone https://github.com/Hugoesin19/varly.git
cd varly
uv sync --group langgraph
```

Or after `pip install "varly[langgraph]"` — see [LangGraph quickstart](../LANGGRAPH_QUICKSTART.md).

---

## Step 1 — Run the template

```bash
uv run python examples/langgraph_capture/run.py
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml \
  --source langgraph
```

Expect `PASS` and `violations: 0`.

The example lives at [`examples/langgraph_capture/run.py`](../../examples/langgraph_capture/run.py).

---

## Step 2 — Wire into your LangGraph agent

Attach a collector to the graph invocation:

```python
from varly.capture.langgraph_callbacks import LangGraphCallbackCollector

collector = LangGraphCallbackCollector(run_id="my-run-001")
graph.invoke(
    {"query": "..."},
    config={"callbacks": [collector]},
)
collector.write_json("run.json")
```

Then verify:

```bash
varly verify run.json --contract policies/mvp.yaml --source langgraph
```

**Rules:**

| Rule | Why |
|------|-----|
| Pass `config={"callbacks": [collector]}` | Callbacks must propagate to LLM and tool nodes |
| Tool names must match policy allowlist | e.g. `mvp.yaml` allows `search` only |
| Use `--source langgraph` | Not `capture` or `air` |

---

## Step 3 — Live runs (optional)

For a real LLM stack, keep the same collector pattern. Save the JSON export, strip secrets/PII, then verify offline.

See [`examples/live/record_run.py`](../../examples/live/record_run.py) for the live-recording stub checklist.

---

## When to use which capture path

| Path | Use when |
|------|----------|
| **LangGraph export** (this recipe) | You run LangGraph/LangChain and can attach callbacks |
| **OpenAI export** | You have Responses API JSON (`--source openai`) |
| **RunRecorder** | Any Python agent, no framework callbacks, or custom stacks (Gemini pilot) |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `tool_call_has_return` | Ensure tool start/end share the same tool name in callbacks |
| `tool_name_allowlist` | Rename tool or update policy `allowed` list |
| `ImportError` for langchain | `uv sync --group langgraph` or `pip install varly[langgraph]` |
| Empty events list | Confirm `config={"callbacks": [collector]}` on `invoke` |

---

## Related

- [LangGraph mapping spec](../architecture/langgraph-run-mapping.md)
- [Capture with RunRecorder](capture-run-recorder.md)
- [Policy packs](../policies/README.md)
