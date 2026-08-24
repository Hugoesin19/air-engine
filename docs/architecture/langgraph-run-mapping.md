# LangGraph run mapping

How LangGraph/LangChain callback telemetry becomes AIR. **Status:** Draft (Sprint 10).

air-engine does not import LangGraph. Adapters consume **files**: either the internal `langgraph.run.v1` export or a recorded **callback event dump**.

---

## `langgraph.run.v1` (reference export)

Top-level fields: `format_version`, `run_id`, `events[]` (`type` field), optional `reads[]`.

| `type` | AIR `event_type` |
|--------|------------------|
| `chain_start` | `run_start` |
| `on_chat_model_start` | `llm_invoke` |
| `on_tool_start` | `tool_call` |
| `on_tool_end` | `tool_return` |
| `chain_end` | `run_end` |

`on_chat_model_end` is also an alias for `llm_invoke` in the sequential mapper. Prefer the recorded normalizer (below) so start/end pairs collapse to one node.

Example: [`examples/langgraph_run_minimal.json`](../../examples/langgraph_run_minimal.json).

---

## Callback dump (`object: "langgraph.callback_events"`)

Shape used by LangChain `astream_events` / callback handlers: each item has `event`, `run_id`, optional `parent_ids`, `name`, `data`.

Detection: `object == "langgraph.callback_events"`, or `events[0]` has `event` and no `type`.

| Callback `event` | Mapping |
|------------------|--------|
| `on_chain_start` (root, empty `parent_ids`) | `run_start` |
| `on_chat_model_start` / `on_llm_start` | `llm_invoke` |
| `on_chat_model_end` / `on_llm_end` | merge tokens onto the start node with the same `run_id` (no second node) |
| `on_tool_start` | `tool_call` (`name`) |
| `on_tool_end` | `tool_return` (id `{run_id}:end` so it is unique) |
| `on_chain_end` (root) | `run_end` |
| nested `on_chain_start` / `on_chain_end` | ignored |

Tokens: `data.output.llm_output.token_usage.total_tokens` (or `usage.total_tokens`).

Example: [`examples/fixtures/recorded/langgraph_callbacks_search.json`](../../examples/fixtures/recorded/langgraph_callbacks_search.json).

```bash
uv run air-engine verify examples/fixtures/recorded/langgraph_callbacks_search.json \
  --contract examples/policies/mvp.yaml --source langgraph
```

---

## Live recording (optional)

Same opt-in stub as OpenAI: [`examples/live/record_run.py`](../../examples/live/record_run.py). CI never sets `AIR_ENGINE_LIVE`.
