# Capture recipe

Copy-paste template for instrumenting **any Python agent** with `RunRecorder`.

**Full guide:** [docs/recipes/capture-run-recorder.md](../../docs/recipes/capture-run-recorder.md)

```bash
uv run python examples/capture_recipe/run.py
uv run air-engine verify examples/capture_recipe/artifacts/run.json \
  --contract examples/policies/mvp.yaml --source capture
```

Open `run.py` and search for `# HOOK:` — those are the lines you replicate in your agent.
