# Recorded fixtures

Anonymized, **real-shaped** captures used by Sprint 10 adapter tests. CI never calls paid APIs.

| File | Native shape | Adapter `--source` |
|------|----------------|--------------------|
| [`openai_responses_search.json`](openai_responses_search.json) | OpenAI Responses API (`object: response`) | `openai` |
| [`langgraph_callbacks_search.json`](langgraph_callbacks_search.json) | LangGraph/LangChain callback dump | `langgraph` |

Both map to the same AIR event sequence as [`trace_valid_minimal.json`](../../trace_valid_minimal.json).

To add a new recording locally, see `examples/live/record_run.py` (`AIR_ENGINE_LIVE=1`). Strip secrets and PII before committing.
