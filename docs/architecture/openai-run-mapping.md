# OpenAI run mapping

How OpenAI telemetry becomes AIR. **Status:** Draft (Sprint 10).

air-engine does not call OpenAI. Adapters consume **files**: either the internal `openai.run.v1` export or a recorded **Responses API** object.

---

## `openai.run.v1` (reference export)

Top-level fields: `format_version`, `run_id`, `steps[]`, optional `reads[]`.

| `step_type` | AIR `event_type` |
|-------------|------------------|
| `run_start` | `run_start` |
| `llm_call` | `llm_invoke` |
| `tool_call` | `tool_call` |
| `tool_output` | `tool_return` |
| `run_end` | `run_end` |

Tokens: `usage.total_tokens` or `total_tokens` on the LLM step. Tool names: `name`.

Example: [`examples/openai_run_minimal.json`](../../examples/openai_run_minimal.json).

---

## Responses API (`object: "response"`)

Recorded completed [Responses](https://platform.openai.com/docs/api-reference/responses) payloads (anonymized). Detection: `object == "response"` and `output` is a list.

| Responses field | Mapping |
|-----------------|--------|
| `id` | AIR `trace_id` / `run_id` |
| synthetic `{id}:start` | `run_start` |
| `output[]` `type: message` | `llm_invoke` (`llm_call`) |
| `output[]` `type: function_call` | `tool_call` (`name`) |
| `output[]` `type: function_call_output` | `tool_return` |
| synthetic `{id}:end` | `run_end` |
| `usage.total_tokens` | `tokens` on the LLM node |
| `function_call` → last LLM | referential `reads` edge |

If `output` has no `message` item, a synthetic LLM step is inserted so tool calls still sit after an invoke.

Unsupported `output[].type` values fail adapter validation (no silent drop).

Example: [`examples/fixtures/recorded/openai_responses_search.json`](../../examples/fixtures/recorded/openai_responses_search.json).

```bash
uv run air-engine verify examples/fixtures/recorded/openai_responses_search.json \
  --contract examples/policies/mvp.yaml --source openai
```

---

## Live recording (optional)

CI never uses this path. See [`examples/live/record_run.py`](../../examples/live/record_run.py): set `AIR_ENGINE_LIVE=1` and `OPENAI_API_KEY` locally. The stub does not send requests; paste an anonymized JSON into `examples/fixtures/recorded/`.
