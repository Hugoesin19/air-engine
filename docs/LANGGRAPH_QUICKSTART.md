# LangGraph quickstart (golden path)

> **Recommended path** — automatic capture, no manual `record_*` hooks.  
> **Time:** ~30 minutes from `pip install` to a verified trace (or CI gate).  
> **Overview:** [Getting started](GETTING_STARTED.md) lists all capture paths and capabilities.

**Python 3.12+** required.

---

## 1. Install

```bash
pip install "varly[langgraph]"
varly try    # optional: see PASS / FAIL / regression demo first
```

---

## 2. Capture a run (mock, no API keys)

Clone the repo for the runnable example, or copy the pattern into your project:

```bash
git clone https://github.com/Hugoesin19/varly.git
cd varly
uv sync --group langgraph
uv run python examples/langgraph_capture/run.py
```

Writes `examples/langgraph_capture/artifacts/run.json`.

---

## 3. Verify

```bash
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml \
  --source langgraph
```

Expect **PASS** and `violations: 0`.

### Policy packs by scenario

| Your agent | Policy file |
|------------|-------------|
| Default tool agent | [`mvp.yaml`](../examples/policies/mvp.yaml) |
| Support / FAQ bot | [`support-bot.yaml`](../examples/policies/support-bot.yaml) |
| RAG / retrieval | [`rag.yaml`](../examples/policies/rag.yaml) |
| Many tools | [`tool-heavy.yaml`](../examples/policies/tool-heavy.yaml) |
| Tool arg keys / endpoint | [`api-guard.yaml`](../examples/policies/api-guard.yaml) |
| Live API runs (slow) | bundled `live` via `bundled_policy("live")` |

Full reference: [Policy packs](policies/README.md).

---

## 4. Wire into your LangGraph agent

```python
from varly.capture.langgraph_callbacks import LangGraphCallbackCollector

collector = LangGraphCallbackCollector(run_id="my-run-001")
graph.invoke(
    {"query": "..."},
    config={"callbacks": [collector]},
)
collector.write_json("run.json")
```

```bash
varly verify run.json --contract policies/mvp.yaml --source langgraph
```

| Rule | Why |
|------|-----|
| `config={"callbacks": [collector]}` | Events must propagate to LLM and tool nodes |
| `--source langgraph` | Not `capture` or `air` |
| Tool names match policy allowlist | e.g. `mvp` allows `search` only |

---

## 5. Gate PRs in CI

Copy the workflow template from [`examples/starter-ci/`](../examples/starter-ci/README.md) into your repo as `.github/workflows/varly.yml`.

Or use the published action (pin to a release tag):

```yaml
- uses: Hugoesin19/varly/.github/actions/verify-trace@v1.2.0
  with:
    trace-file: artifacts/run.json
    contract-file: policies/mvp.yaml
    source: langgraph
```

Regression gate on PRs: [Team CI workflow](workflows/team-ci.md) (`diff` baseline vs current).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `tool_call_has_return` | Tool start/end must share the same name in callbacks |
| `tool_name_allowlist` | Rename tool or edit policy `allowed` list |
| `ImportError` (langchain) | `pip install "varly[langgraph]"` |
| Empty events | Pass `config={"callbacks": [collector]}` on `invoke` |

---

## Related

- [Getting started](GETTING_STARTED.md) · [Full LangGraph recipe](recipes/capture-langgraph-export.md)
- [Cookbook](cookbook/README.md) · [Capture with RunRecorder](recipes/capture-run-recorder.md) (non-LangGraph)
