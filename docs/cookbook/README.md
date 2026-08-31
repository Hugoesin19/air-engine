# varly Cookbook

Three end-to-end scenarios you can run from docs alone: **capture → verify → view → diff**.

Each scenario uses mock or recorded fixtures — no API keys in CI.

---

## Scenario 1 — Tool agent (LangGraph auto-capture)

**Use case:** A tool-calling agent; verify structure and tool allowlist automatically.

```bash
uv sync --group langgraph
uv run python examples/langgraph_capture/run.py
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source langgraph
uv run varly view \
  --trace examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source langgraph
```

Expect **PASS**, then the browser viewer with timeline + causal graph.

**Policy:** [`mvp.yaml`](../examples/policies/mvp.yaml) — default CI gate.

---

## Scenario 2 — RAG-shaped run (retrieve → answer)

**Use case:** Agent with a `retrieve` tool before synthesis; stricter RAG policy.

```bash
uv run varly verify examples/cookbook/artifacts/rag_shaped_run.json \
  --contract examples/policies/rag.yaml --source capture
uv run varly view \
  --trace examples/cookbook/artifacts/rag_shaped_run.json \
  --contract examples/policies/rag.yaml --source capture
```

Expect **PASS** with `retrieve` in the tool allowlist.

**Policy:** [`rag.yaml`](../examples/policies/rag.yaml) — allows `retrieve` and `search`.

---

## Scenario 3 — Regression break (`diff` gate)

**Use case:** CI fails when a new run introduces violations the baseline did not have.

```bash
# Baseline passes
uv run varly verify examples/trace_valid_minimal.json \
  --contract examples/policies/mvp.yaml

# Current run breaks tool_call_has_return
uv run varly diff \
  examples/trace_valid_minimal.json \
  examples/trace_invalid_missing_tool_return.json \
  --contract examples/policies/mvp.yaml
```

Expect **exit code 1** — new violations vs baseline.

See [baseline workflow](../workflows/baseline.md) for team CI.

---

## Scenario 4 — Tool argument gates (`api-guard`)

**Use case:** Enforce allowed tool argument keys and a fixed endpoint value (finer than tool-name allowlists).

```bash
uv run varly verify examples/cookbook/artifacts/tool_args_valid.json \
  --contract examples/policies/api-guard.yaml --source capture

uv run varly verify examples/cookbook/artifacts/tool_args_invalid.json \
  --contract examples/policies/api-guard.yaml --source capture
```

Expect **PASS** then **FAIL** (`debug` arg key is not allowed).

**Policy:** [`api-guard.yaml`](../examples/policies/api-guard.yaml) — `tool_args_keys_allowlist` + `tool_arg_equals`.

Capture args in your agent with `RunRecorder.record_tool_call(..., args={...})`.

---

## Policy packs by scenario

| Scenario | Policy | File |
|----------|--------|------|
| Default CI / PR gate | `mvp` | [`mvp.yaml`](../examples/policies/mvp.yaml) |
| Customer support bot | `support-bot` | [`support-bot.yaml`](../examples/policies/support-bot.yaml) |
| RAG / retrieval agents | `rag` | [`rag.yaml`](../examples/policies/rag.yaml) |
| Many tools (orchestrator) | `tool-heavy` | [`tool-heavy.yaml`](../examples/policies/tool-heavy.yaml) |
| API endpoint / arg keys | `api-guard` | [`api-guard.yaml`](../examples/policies/api-guard.yaml) |
| Tight production guardrails | `strict` | [`strict.yaml`](../examples/policies/strict.yaml) |
| Local debugging | `dev` | [`dev.yaml`](../examples/policies/dev.yaml) |

Full reference: [Policy packs](../policies/README.md).

---

## Capture paths (reminder)

| Stack | Recipe |
|-------|--------|
| LangGraph / LangChain | [capture-langgraph-export.md](../recipes/capture-langgraph-export.md) |
| Any Python agent | [capture-run-recorder.md](../recipes/capture-run-recorder.md) |
| OpenAI Responses export | [architecture/openai-run-mapping.md](../architecture/openai-run-mapping.md) |

---

## Related

- [Onboarding checklist](../ONBOARDING.md)
- [Viewer](../VIEWER.md)
- [Install](../INSTALL.md)
