# LangGraph capture example

Automatic export via LangChain callbacks — no manual `record_*` hooks.

**Full guide:** [docs/recipes/capture-langgraph-export.md](../../docs/recipes/capture-langgraph-export.md)

```bash
uv sync --group langgraph
uv run python examples/langgraph_capture/run.py
uv run varly verify examples/langgraph_capture/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source langgraph
```

Uses `FakeListLLM` and a local `search` tool — no API keys required.
